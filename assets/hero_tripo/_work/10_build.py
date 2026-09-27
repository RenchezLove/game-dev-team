"""Tripo hero (hero.glb) -> 3 skinned slot meshes on our 21-bone RootAnim.
Deterministic: always starts from armor_wearables/_work/wearables_work.blend
(T0 rig, rest pose) + the Tripo glb.
Steps: import+orient -> weld -> decimate -> measure Tripo joints -> build a
Tripo-proportioned copy of RootAnim -> heat-skin -> pose it onto OUR rest
(bone-by-bone, length scale) -> bake -> heat-skin to RootAnim -> cut slots by
Z zones with overlap -> one textured material -> save _work/hero_work.blend.
Run: blender.exe -b --factory-startup --python 10_build.py
"""
import bpy, bmesh, sys, os, math
sys.path.insert(0, 'E:/game-dev-team/assets/hero_tripo/_work')
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import hcommon as H
import wcommon as W
from mathutils import Vector, Matrix

OUTDIR = 'E:/game-dev-team/assets/hero_tripo/'
WORK = OUTDIR + '_work/'
TARGET_TRIS = 800           # before cuts; bisect planes + overlap add ~30%, final <= 1200 (Rinat 09-27)
THICK = 1.18                # body thickness factor (Rinat: "чуть толще"), head+hands+feet untouched
TEX = OUTDIR + 'T_HeroTripo_D.png'
MAT = 'M_HeroTripo'
HAND_L = 0.5                # hand length scale (0.20 m -> 0.10 m, like T0)
HAND_W = 0.7                # hand width/thickness scale (0.045 -> ~0.032, like T0)

bpy.ops.wm.open_mainfile(filepath=H.WEAR)
import addon_utils; addon_utils.enable('io_scene_fbx')
rig = bpy.data.objects['RootAnim']
for o in [o for o in bpy.data.objects if o.type == 'MESH']:
    bpy.data.objects.remove(o, do_unlink=True)
if rig.animation_data:
    rig.animation_data.action = None
for pb in rig.pose.bones:
    pb.matrix_basis = Matrix.Identity(4)

# ---------- import + orient (face -Y, left +X, feet on Z0) ----------
bpy.ops.import_scene.gltf(filepath=H.GLB)
hero = [o for o in bpy.context.selected_objects if o.type == 'MESH'][0]
for o in list(bpy.context.selected_objects):
    if o is not hero:
        bpy.data.objects.remove(o, do_unlink=True)
bpy.context.view_layer.update()
hero.data.transform(Matrix.Rotation(math.radians(-90), 4, 'Z') @ hero.matrix_world)
hero.parent = None
hero.matrix_world = Matrix.Identity(4)
vs = hero.data.vertices
zmin = min(v.co.z for v in vs)
chest = [v.co for v in vs if 1.0 < v.co.z - zmin < 1.3]
xc = (min(c.x for c in chest) + max(c.x for c in chest)) / 2
yc = (min(c.y for c in chest) + max(c.y for c in chest)) / 2
hero.data.transform(Matrix.Translation((-xc, -0.001 - yc, -zmin)))
hero.name = hero.data.name = 'HeroTripo'
me = hero.data
me.calc_loop_triangles()
print('TRIPO raw tris=%d verts=%d shift=(%.3f,%.3f,%.3f)' % (
    len(me.loop_triangles), len(me.vertices), -xc, -0.001 - yc, -zmin))

# weld (glTF splits verts on UV seams; UVs live on loops and survive)
bm = bmesh.new(); bm.from_mesh(me)
n0 = len(bm.verts)
bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
bm.to_mesh(me); bm.free(); me.update()
print('WELD %d -> %d verts' % (n0, len(me.vertices)))

# ---------- measure Tripo joints ----------
cos = [v.co.copy() for v in me.vertices]


def band(pred):
    s = [c for c in cos if pred(c)]
    mn = Vector((min(c.x for c in s), min(c.y for c in s), min(c.z for c in s)))
    mx = Vector((max(c.x for c in s), max(c.y for c in s), max(c.z for c in s)))
    return mn, mx, (mn + mx) / 2


tree, _ = H.bvh_of([hero])
crotch = H.ray(tree, (0, -0.001, 0.3), (0, 0, 1)).z
HIP_Z = crotch + 0.03
# arm: centre of vertical extent per x (widest over y), sleeve end = thickness drop
arm = {}
for i in range(15, 90):
    x = i * 0.01
    best = None
    for dy in [j * 0.01 - 0.08 for j in range(17)]:
        up = H.ray(tree, (x, dy, 1.1), (0, 0, 1)); dn = H.ray(tree, (x, dy, 2.2), (0, 0, -1))
        if up and dn and 0 < dn.z - up.z < 0.4:
            if best is None or dn.z - up.z > best[0]:
                best = (dn.z - up.z, (up.z + dn.z) / 2)
    if best:
        f = H.ray(tree, (x, -2, best[1]), (0, 1, 0)); k = H.ray(tree, (x, 2, best[1]), (0, -1, 0))
        if f and k:
            arm[i] = (best[0], best[1], (f.y + k.y) / 2)
tip = max(c.x for c in cos)
SH_X = 0.21                     # arm becomes a cylinder here (profile, 03_diag)
xs = sorted(arm)
drops = [(arm[a][0] - arm[b][0], b) for a, b in zip(xs, xs[1:]) if 0.55 < b * 0.01 < 0.8]
WR_X = max(drops)[1] * 0.01 - 0.005      # sleeve end / hand start
EL_X = SH_X + 0.5637 * (WR_X - SH_X)     # our elbow fraction (0.631-0.286)/(0.898-0.286)


def arm_at(x):
    i = min(arm, key=lambda k: abs(k * 0.01 - x))
    return Vector((x, arm[i][2], arm[i][1]))


SH = arm_at(SH_X); EL = arm_at(EL_X); WR = arm_at(WR_X)
TIPP = arm_at(tip - 0.02)
SP2_Z = SH.z
NECK_Z = 1.50                   # inside the sweater collar (profile 03_diag)
HEAD_Z = 1.545                  # chin line (profile 03_diag)
# legs
_, _, th = band(lambda p: p.x > 0.02 and abs(p.z - (HIP_Z - 0.08)) < 0.02)
KN_Z = HIP_Z * (0.458 / 0.837)
_, _, kn = band(lambda p: p.x > 0.02 and abs(p.z - KN_Z) < 0.02)
fmn, fmx, fc = band(lambda p: p.x > 0.02 and p.z < 0.06)
AN_Z = HIP_Z * (0.037 / 0.837)
AN_Y = fmx.y - (0.112 - (-0.001)) / (0.112 - (-0.243)) * (fmx.y - fmn.y)   # T0 ankle ratio
AN = Vector((fc.x, AN_Y, AN_Z))
print('TRIPO joints: crotch=%.3f hip=%.3f thigh=%s knee=(%.3f,%.3f,%.3f) ankle=%s foot_y=[%.3f..%.3f]' % (
    crotch, HIP_Z, tuple(round(a, 3) for a in th), kn.x, kn.y, KN_Z, tuple(round(a, 3) for a in AN), fmn.y, fmx.y))
print('TRIPO arm: shoulder=%s elbow=%s wrist=%s tip=%.3f' % (
    tuple(round(a, 3) for a in SH), tuple(round(a, 3) for a in EL), tuple(round(a, 3) for a in WR), tip))

src = hero.copy(); src.data = me.copy(); src.name = 'TripoSrc'
bpy.context.collection.objects.link(src)   # full-res bake source

# decimate to budget
me.calc_loop_triangles()
t0 = len(me.loop_triangles)
if t0 > TARGET_TRIS:
    md = hero.modifiers.new('Dec', 'DECIMATE')
    md.ratio = TARGET_TRIS / t0
    md.use_collapse_triangulate = True
    bpy.context.view_layer.objects.active = hero
    bpy.ops.object.modifier_apply(modifier=md.name)
bm = bmesh.new(); bm.from_mesh(me)
bmesh.ops.triangulate(bm, faces=bm.faces[:])
bm.to_mesh(me); bm.free(); me.update()
me.calc_loop_triangles()
print('DECIMATE %d -> %d tris' % (t0, len(me.loop_triangles)))

# rebake the texture onto the decimated mesh: Tripo UVs are shattered (1066 of
# 1277 verts sit on UV seams, _dec_test.py), so the collapse smears them
while me.uv_layers:
    me.uv_layers.remove(me.uv_layers[0])
me.uv_layers.new(name='UVMap')
W.smart_uv(hero)
bimg = bpy.data.images.new('T_HeroTripo_D', 2048, 2048, alpha=False)
bmat = bpy.data.materials.new('_bake')
bmat.use_nodes = True
bn_ = bmat.node_tree.nodes.new('ShaderNodeTexImage')
bn_.image = bimg
bmat.node_tree.nodes.active = bn_
me.materials.clear()
me.materials.append(bmat)
scn = bpy.context.scene
scn.render.engine = 'CYCLES'
scn.cycles.samples = 4
scn.cycles.device = 'CPU'
bk = scn.render.bake
bk.use_selected_to_active = True
bk.cage_extrusion = 0.012
bk.max_ray_distance = 0.04
bk.margin = 16
bk.use_pass_direct = False
bk.use_pass_indirect = False
bk.use_pass_color = True
bpy.ops.object.select_all(action='DESELECT')
src.select_set(True); hero.select_set(True)
bpy.context.view_layer.objects.active = hero
bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'})
bpy.data.objects.remove(src, do_unlink=True)
print('REBAKE diffuse colour 2048 onto %d tris, UV islands re-projected' % W.tri_count(hero))
# neck faces lie inside the source sweater collar after the collapse, so bake
# rays catch collar wool (dark smears). Paint them flat skin: point their UVs
# at the texel under the chin.
uvl = me.uv_layers['UVMap'].data
def fdist(p, q):
    return (Vector(p.center) - Vector(q)).length
chin = min(me.polygons, key=lambda p: fdist(p, (0, -0.14, 1.585)))
cuv = sum((uvl[li].uv for li in chin.loop_indices), Vector((0, 0))) / len(chin.loop_indices)
nneck = 0
for p in me.polygons:
    c = Vector(p.center)
    vv = [me.vertices[vi].co for vi in p.vertices]; c = Vector(p.center)
    if (1.45 < c.z < 1.57 and math.hypot(c.x, c.y + 0.02) < 0.08 and min(v.z for v in vv) > 1.445
            and max(math.hypot(v.x, v.y + 0.02) for v in vv) < 0.095):
        for li in p.loop_indices:
            uvl[li].uv = cuv
        nneck += 1
print('NECK skin fill: %d faces -> uv %s' % (nneck, tuple(round(a, 3) for a in cuv)))
# collar front: a collapsed face sank under the sweater rim and baked skin
# (V-neck wedge). Faces below the neck ring that baked skin -> chest wool texel.
W_, H_ = bimg.size
px = bimg.pixels[:]
def texel(uv):
    x = min(W_ - 1, max(0, int(uv.x * W_))); y = min(H_ - 1, max(0, int(uv.y * H_)))
    i = (y * W_ + x) * 4
    return px[i], px[i + 1], px[i + 2]
chest = min(me.polygons, key=lambda p: fdist(p, (0, -0.12, 1.33)))
wuv = sum((uvl[li].uv for li in chest.loop_indices), Vector((0, 0))) / len(chest.loop_indices)
ncol = 0
for p in me.polygons:
    c = Vector(p.center)
    if 1.38 < c.z < 1.50 and abs(c.x) < 0.14:
        uv = sum((uvl[li].uv for li in p.loop_indices), Vector((0, 0))) / len(p.loop_indices)
        r, g, b = texel(uv)
        if r > 0.35 and r > g * 1.2 and g > b:
            for li in p.loop_indices:
                uvl[li].uv = wuv
            ncol += 1
print('COLLAR wool fill: %d faces, chest texel %s' % (ncol, tuple(round(a, 2) for a in texel(wuv))))

# ---------- Tripo-proportioned copy of RootAnim ----------
O = {b.name: (b.head_local.copy(), b.tail_local.copy()) for b in rig.data.bones}
T = {}
y0 = -0.001
root = Vector((0, y0, HIP_Z))
sp2 = Vector((0, y0, SP2_Z))
T['C_Root'] = (root, root.lerp(sp2, 0.509))
T['C_Spine01'] = (T['C_Root'][1], sp2)
T['C_Spine02'] = (sp2, Vector((0, y0, NECK_Z)))
T['C_Neck'] = (Vector((0, y0, NECK_Z)), Vector((0, y0, HEAD_Z)))
T['C_Head'] = (Vector((0, y0, HEAD_Z)), Vector((0, y0, HEAD_Z)) + (O['C_Head'][1] - O['C_Head'][0]))
for s, sx in (('L', 1), ('R', -1)):
    m = lambda v: Vector((v.x * sx, v.y, v.z))
    names = (('L_UpperArm', 'L_Shoulder', 'L_Arm', 'L_Hand') if s == 'L' else
             ('R_UpperArm', 'R_Arm', 'Pelvis_009_R_002', 'R_Hand'))
    hand_len = (O[names[3]][1] - O[names[3]][0]).length
    hdir = (m(TIPP) - m(WR)).normalized()
    T[names[0]] = (sp2, m(SH))
    T[names[1]] = (m(SH), m(EL))
    T[names[2]] = (m(EL), m(WR))
    T[names[3]] = (m(WR), m(WR) + hdir * hand_len)
    thigh = Vector((th.x * sx, th.y, HIP_Z))
    knee = Vector((kn.x * sx, kn.y, KN_Z))
    ank = m(AN)
    T[s + '_Pelvis'] = (root, thigh)
    T[s + '_Thigh'] = (thigh, knee)
    T[s + '_Claf'] = (knee, ank)
    T[s + '_Foot'] = (ank, ank + (O[s + '_Foot'][1] - O[s + '_Foot'][0]))
assert sorted(T) == sorted(O), set(O) ^ set(T)

trig = rig.copy(); trig.data = rig.data.copy()
trig.name = trig.data.name = 'TripoRig'
bpy.context.collection.objects.link(trig)
bpy.ops.object.select_all(action='DESELECT')
bpy.context.view_layer.objects.active = trig
trig.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
for eb in trig.data.edit_bones:
    eb.use_connect = False
for eb in trig.data.edit_bones:
    eb.head, eb.tail = T[eb.name]
    eb.inherit_scale = 'NONE'
bpy.ops.object.mode_set(mode='OBJECT')

# heat-skin hero to TripoRig


def heat_skin(mesh, arm):
    for vg in list(mesh.vertex_groups):
        mesh.vertex_groups.remove(vg)
    for md in [m for m in mesh.modifiers if m.type == 'ARMATURE']:
        mesh.modifiers.remove(md)
    mesh.parent = None
    bpy.ops.object.select_all(action='DESELECT')
    mesh.select_set(True); arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    un = sum(1 for v in mesh.data.vertices if not any(g.weight > 1e-4 for g in v.groups))
    print('HEAT %s -> %s groups=%d unweighted=%d' % (mesh.name, arm.name, len(mesh.vertex_groups), un))
    return un


heat_skin(hero, trig)

# pose TripoRig onto OUR rest: world bone frame = O frame, stretched along length
order = []
def walk(b):
    order.append(b.name)
    for c in b.children:
        walk(c)
for b in trig.data.bones:
    if b.parent is None:
        walk(b)
for bn in order:
    ob_b = rig.data.bones[bn]
    lt = (T[bn][1] - T[bn][0]).length
    lo = ob_b.length
    if bn in ("L_Hand", "R_Hand"):   # Tripo hand ~0.20 m vs T0 ~0.10 m: shrink to T0 size
        S = Matrix.Diagonal((HAND_W, HAND_L, HAND_W, 1.0))
    else:
        S = Matrix.Diagonal((1.0, lo / lt, 1.0, 1.0))
    trig.pose.bones[bn].matrix = ob_b.matrix_local @ S
    bpy.context.view_layer.update()
err = 0.0
for bn in order:
    pb = trig.pose.bones[bn]
    err = max(err, (pb.head - O[bn][0]).length,
              0 if bn in ("L_Hand", "R_Hand") else (pb.tail - O[bn][1]).length)  # hand tails shrunk on purpose
    print('  conform %-18s len T=%.3f O=%.3f scale=%.2f' % (
        bn, (T[bn][1] - T[bn][0]).length, rig.data.bones[bn].length,
        rig.data.bones[bn].length / (T[bn][1] - T[bn][0]).length))
print('CONFORM max joint error = %.5f m' % err)

# bake deformed shape into the mesh
bpy.ops.object.select_all(action='DESELECT')
hero.select_set(True)
bpy.context.view_layer.objects.active = hero
md = [m for m in hero.modifiers if m.type == 'ARMATURE'][0]
bpy.ops.object.modifier_apply(modifier=md.name)
hero.parent = None
hero.matrix_world = Matrix.Identity(4)

# ---------- thicken body (radial from bone axes, blended by conform weights) ----------
AXIAL = {'C_Root', 'C_Spine01', 'C_Spine02', 'L_Pelvis', 'R_Pelvis'}      # scale X/Y about spine
RADIAL = {'L_UpperArm', 'R_UpperArm', 'L_Shoulder', 'L_Arm', 'R_Arm', 'Pelvis_009_R_002',
          'L_Thigh', 'R_Thigh', 'L_Claf', 'R_Claf'}                        # scale about segment
# identity: C_Neck, C_Head, L_Hand, R_Hand, L_Foot, R_Foot


def thick_at(bn, co):
    if bn in AXIAL:
        return Vector((co.x * THICK, -0.001 + (co.y + 0.001) * THICK, co.z))
    if bn in RADIAL:
        a, b = O[bn]
        ab = b - a
        t = max(0.0, min(1.0, (co - a).dot(ab) / ab.length_squared))
        p = a + ab * t
        return p + (co - p) * THICK
    return co.copy()


gname = {g.index: g.name for g in hero.vertex_groups}
moved = 0
for v in me.vertices:
    ws = [(gname[g.group], g.weight) for g in v.groups if g.weight > 1e-4]
    tot = sum(w for _, w in ws)
    if tot <= 0:
        continue
    new = Vector((0, 0, 0))
    for bn, w in ws:
        new += thick_at(bn, v.co) * (w / tot)
    if (new - v.co).length > 1e-6:
        moved += 1
    v.co = new
me.update()
zs = [v.co.z for v in me.vertices]
print('THICKEN x%.2f: moved %d/%d verts, z=[%.3f..%.3f]' % (THICK, moved, len(me.vertices), min(zs), max(zs)))
bpy.data.objects.remove(trig, do_unlink=True)

# ---------- final skin on RootAnim ----------
un = heat_skin(hero, rig)
bpy.ops.object.select_all(action='DESELECT')
hero.select_set(True)
bpy.context.view_layer.objects.active = hero
bpy.ops.object.vertex_group_clean(group_select_mode='ALL', limit=0.05)
bpy.ops.object.vertex_group_limit_total(group_select_mode='ALL', limit=4)
bpy.ops.object.vertex_group_normalize_all(group_select_mode='ALL', lock_active=False)
if un:
    kd_src = [v for v in me.vertices if v.groups]
    from mathutils import kdtree
    kd = kdtree.KDTree(len(kd_src))
    for i, v in enumerate(kd_src):
        kd.insert(v.co, i)
    kd.balance()
    gn = [g.name for g in hero.vertex_groups]
    for v in me.vertices:
        if not v.groups:
            _, i, _ = kd.find(v.co)
            for g in kd_src[i].groups:
                hero.vertex_groups[gn[g.group]].add([v.index], g.weight, 'REPLACE')
    print('FILLED unweighted from nearest:', un)
W.rebind(hero, rig)

# ---------- material (one, Tripo texture) ----------
img = bpy.data.images['T_HeroTripo_D']
img.filepath_raw = TEX
img.file_format = 'PNG'
img.save()
img.filepath = TEX
mat = bpy.data.materials.new(MAT)
mat.use_nodes = True
nt = mat.node_tree
nt.nodes.clear()
out = nt.nodes.new('ShaderNodeOutputMaterial')
bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
bsdf.inputs['Metallic'].default_value = 0.0
bsdf.inputs['Roughness'].default_value = 0.8
tx = nt.nodes.new('ShaderNodeTexImage')
tx.image = img
nt.links.new(tx.outputs['Color'], bsdf.inputs['Base Color'])
nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
me.materials.clear()
me.materials.append(mat)
for p in me.polygons:
    p.material_index = 0
    p.use_smooth = False
while len(me.uv_layers) > 1:
    me.uv_layers.remove(me.uv_layers[1])
me.uv_layers[0].name = 'UVMap'

# ---------- cut into slots (Z zones with overlap) ----------
PLANES = (0.900, 0.910, 1.532, 1.549)
bm = bmesh.new(); bm.from_mesh(me)
for z in PLANES:
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=(0, 0, z), plane_no=(0, 0, 1))
bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])
bm.to_mesh(me); bm.free(); me.update()
print("CUT whole mesh tris after bisect = %d" % W.tri_count(hero))

SLOTS = {'SK_Cloth_T0_Head': lambda z: z > 1.532,
         'SK_Cloth_T0_Torso': lambda z: 0.900 < z < 1.549,
         'SK_Cloth_T0_Legs': lambda z: z < 0.910}
parts = []
for name, keep in SLOTS.items():
    ob = hero.copy(); ob.data = me.copy()
    ob.name = ob.data.name = name
    bpy.context.collection.objects.link(ob)
    bm = bmesh.new(); bm.from_mesh(ob.data)
    doomed = [f for f in bm.faces if not keep(f.calc_center_median().z)]
    bmesh.ops.delete(bm, geom=doomed, context='FACES')
    bm.to_mesh(ob.data); bm.free(); ob.data.update()
    # drop groups with no weights
    used = {ob.vertex_groups[g.group].name for v in ob.data.vertices for g in v.groups if g.weight > 1e-4}
    for vg in list(ob.vertex_groups):
        if vg.name not in used:
            ob.vertex_groups.remove(vg)
    W.rebind(ob, rig)
    zs = [v.co.z for v in ob.data.vertices]
    print('SLOT %-18s tris=%d verts=%d z=[%.3f..%.3f] groups=%s' % (
        name, W.tri_count(ob), len(ob.data.vertices), min(zs), max(zs),
        sorted(g.name for g in ob.vertex_groups)))
    parts.append(ob)
print('TOTAL tris = %d' % sum(W.tri_count(o) for o in parts))
bpy.data.objects.remove(hero, do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=WORK + 'hero_work.blend')
print('SAVED', WORK + 'hero_work.blend')
tor = bpy.data.objects['SK_Cloth_T0_Torso']
hx = [v.co for v in tor.data.vertices if v.co.x > 0.89]
print('HAND left: tip x=%.3f (T0 0.999), z=[%.3f..%.3f] y=[%.3f..%.3f]' % (
    max(c.x for c in hx), min(c.z for c in hx), max(c.z for c in hx), min(c.y for c in hx), max(c.y for c in hx)))
