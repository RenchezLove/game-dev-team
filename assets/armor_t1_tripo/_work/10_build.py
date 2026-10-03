"""Tripo clothing set T1 (cap + leather jacket + jeans, cloth_t1.glb) -> 3 skinned slot meshes on
our 21-bone RootAnim, fitted to the T0 Tripo hero (ADR-095). Same route as hero_tripo/_work/10_build.py:
import+orient -> weld -> decimate -> rebake -> Tripo-proportioned rig -> heat-skin -> pose onto OUR
rest -> bake -> thicken -> FIT TO T0 at the slot cuts (waist / neck) -> heat-skin to RootAnim ->
clavicle weight fix -> cut slots by the T0 Z zones -> save _work/t1_work.blend.
Run: blender.exe -b --factory-startup --python 10_build.py
"""
import bpy, bmesh, sys, os, math
sys.path.insert(0, 'E:/game-dev-team/assets/hero_tripo/_work')
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import hcommon as H
import wcommon as W
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

GLB = 'E:/ContrarySurvior/ContrarySurvivor/Saved/Tripo/cloth_t1/cloth_t1.glb'
HERO = 'E:/game-dev-team/assets/hero_tripo/_work/hero_work.blend'
OUTDIR = 'E:/game-dev-team/assets/armor_t1_tripo/'
WORK = OUTDIR + '_work/'
TARGET_TRIS = int(os.environ.get('T1_TARGET', '1130'))   # before cuts; bisect planes + overlap add ~45%
THICK = 1.18                # same body thickness factor as the T0 hero
TEX = OUTDIR + 'T_ArmorT1Tripo_D.png'
TEXRES = 1024
MAT = 'M_ArmorT1Tripo'
HAND_L, HAND_W = 0.5, 0.7   # Tripo hand 0.20 m -> T0 size, as on the hero
YAW = -89.5                 # model faces +X; arm axis measured 89.5 deg from +X (00_inspect)
NECK_Z, HEAD_Z = 1.465, 1.510      # raw: inside the collar / chin line (03_diag profile)
SH_X = 0.21                 # arm becomes a cylinder here (03_diag)
HEM_Z = 0.914               # jacket hem lands just above the waist overlap 0.900..0.910
COLLAR_TOP = 1.528          # collar stays under the head slot (cut at 1.532)

# ---------- T0 hero surface (the body standard) ----------
bpy.ops.wm.open_mainfile(filepath=HERO)
bm0 = bmesh.new()
for n in ('SK_Cloth_T0_Head', 'SK_Cloth_T0_Torso', 'SK_Cloth_T0_Legs'):
    bm0.from_mesh(bpy.data.objects[n].data)
T0 = BVHTree.FromBMesh(bm0)
bm0.free()
WAIST_AX, NECK_AX = -0.001, -0.03          # y of the vertical axes the rings are measured from


def t0_r(axy, co, z):
    """Radius of the T0 surface seen from the axis towards co at height z (innermost surface)."""
    d = Vector((co.x, co.y - axy, 0.0))
    if d.length < 1e-6:
        return None
    hit = T0.ray_cast(Vector((0.0, axy, z)), d.normalized(), 0.6)[0]
    return math.hypot(hit.x, hit.y - axy) if hit else None


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
bpy.ops.import_scene.gltf(filepath=GLB)
hero = [o for o in bpy.context.selected_objects if o.type == 'MESH'][0]
for o in list(bpy.context.selected_objects):
    if o is not hero:
        bpy.data.objects.remove(o, do_unlink=True)
bpy.context.view_layer.update()
hero.data.transform(Matrix.Rotation(math.radians(YAW), 4, 'Z') @ hero.matrix_world)
hero.parent = None
hero.matrix_world = Matrix.Identity(4)
vs = hero.data.vertices
zmin = min(v.co.z for v in vs)
chest = [v.co for v in vs if 1.0 < v.co.z - zmin < 1.3]
xc = (min(c.x for c in chest) + max(c.x for c in chest)) / 2
yc = (min(c.y for c in chest) + max(c.y for c in chest)) / 2
hero.data.transform(Matrix.Translation((-xc, -0.001 - yc, -zmin)))
hero.name = hero.data.name = 'T1Tripo'
me = hero.data
me.calc_loop_triangles()
print('TRIPO raw tris=%d verts=%d shift=(%.3f,%.3f,%.3f)' % (
    len(me.loop_triangles), len(me.vertices), -xc, -0.001 - yc, -zmin))

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
xs = sorted(arm)
drops = [(arm[a][0] - arm[b][0], b) for a, b in zip(xs, xs[1:]) if 0.55 < b * 0.01 < 0.8]
WR_X = max(drops)[1] * 0.01 - 0.005      # cuff end / hand start
EL_X = SH_X + 0.5637 * (WR_X - SH_X)     # our elbow fraction


def arm_at(x):
    i = min(arm, key=lambda k: abs(k * 0.01 - x))
    return Vector((x, arm[i][2], arm[i][1]))


SH = arm_at(SH_X); EL = arm_at(EL_X); WR = arm_at(WR_X)
TIPP = arm_at(tip - 0.02)
SP2_Z = SH.z
def leg_centre(z):
    """Centre of the left leg section at height z by rays (the mesh is too sparse for vertex bands)."""
    a = H.ray(tree, (2, -0.001, z), (-1, 0, 0)); b = H.ray(tree, (0.0005, -0.001, z), (1, 0, 0))
    cx = (a.x + b.x) / 2
    f = H.ray(tree, (cx, -2, z), (0, 1, 0)); k = H.ray(tree, (cx, 2, z), (0, -1, 0))
    return Vector((cx, (f.y + k.y) / 2, z))


th = leg_centre(HIP_Z - 0.08)
KN_Z = HIP_Z * (0.458 / 0.837)
kn = leg_centre(KN_Z)
fmn, fmx, fc = band(lambda p: p.x > 0.02 and p.z < 0.10)
AN_Z = HIP_Z * (0.037 / 0.837)
AN_Y = fmx.y - (0.112 - (-0.001)) / (0.112 - (-0.243)) * (fmx.y - fmn.y)   # T0 ankle ratio
AN = Vector((fc.x, AN_Y, AN_Z))
print('TRIPO joints: crotch=%.3f hip=%.3f thigh=%s knee=(%.3f,%.3f,%.3f) ankle=%s foot_y=[%.3f..%.3f]' % (
    crotch, HIP_Z, tuple(round(a, 3) for a in th), kn.x, kn.y, KN_Z, tuple(round(a, 3) for a in AN), fmn.y, fmx.y))
print('TRIPO arm: shoulder=%s elbow=%s wrist=%s tip=%.3f' % (
    tuple(round(a, 3) for a in SH), tuple(round(a, 3) for a in EL), tuple(round(a, 3) for a in WR), tip))

src = hero.copy(); src.data = me.copy(); src.name = 'TripoSrc'
bpy.context.collection.objects.link(src)   # full-res bake source

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

# rebake the texture onto the decimated mesh (Tripo UVs are shattered, collapse smears them)
while me.uv_layers:
    me.uv_layers.remove(me.uv_layers[0])
me.uv_layers.new(name='UVMap')
W.smart_uv(hero)
bimg = bpy.data.images.new('T_ArmorT1Tripo_D', TEXRES, TEXRES, alpha=False)
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
bk.margin = 8
bk.use_pass_direct = False
bk.use_pass_indirect = False
bk.use_pass_color = True
bpy.ops.object.select_all(action='DESELECT')
src.select_set(True); hero.select_set(True)
bpy.context.view_layer.objects.active = hero
bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'})
bpy.data.objects.remove(src, do_unlink=True)
print('REBAKE diffuse colour %d onto %d tris' % (TEXRES, W.tri_count(hero)))

# face classes from the baked colour (stored sRGB values)
px = bimg.pixels[:]
def texel(uv):
    x = min(TEXRES - 1, max(0, int(uv.x * TEXRES))); y = min(TEXRES - 1, max(0, int(uv.y * TEXRES)))
    i = (y * TEXRES + x) * 4
    return Vector((px[i], px[i + 1], px[i + 2]))
def klass(c):
    r, g, b = c
    if r > 0.5 and r > b * 1.25:
        return 'skin'
    if max(c) < 0.13:
        return 'dark'
    if r > b * 1.18:
        return 'brown'
    return 'grey'

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
    un = [v for v in mesh.data.vertices if not any(g.weight > 1e-4 for g in v.groups)]
    print('HEAT %s -> %s groups=%d unweighted=%d' % (mesh.name, arm.name, len(mesh.vertex_groups), len(un)))
    if un:                                  # loose shells the heat solver skipped: weights of the nearest skinned vertex
        from mathutils import kdtree
        kd_src = [v for v in mesh.data.vertices if any(g.weight > 1e-4 for g in v.groups)]
        kd = kdtree.KDTree(len(kd_src))
        for i, v in enumerate(kd_src):
            kd.insert(v.co, i)
        kd.balance()
        gn = [g.name for g in mesh.vertex_groups]
        zs_ = [v.co.z for v in un]
        for v in un:
            _, i, _ = kd.find(v.co)
            for g in kd_src[i].groups:
                mesh.vertex_groups[gn[g.group]].add([v.index], g.weight, 'REPLACE')
        print('  filled %d unweighted verts from the nearest skinned vertex (z %.3f..%.3f)' % (len(un), min(zs_), max(zs_)))
    return 0


heat_skin(hero, trig)

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
              0 if bn in ("L_Hand", "R_Hand") else (pb.tail - O[bn][1]).length)
    print('  conform %-18s len T=%.3f O=%.3f scale=%.2f' % (
        bn, (T[bn][1] - T[bn][0]).length, rig.data.bones[bn].length,
        rig.data.bones[bn].length / (T[bn][1] - T[bn][0]).length))
print('CONFORM max joint error = %.5f m' % err)

bpy.ops.object.select_all(action='DESELECT')
hero.select_set(True)
bpy.context.view_layer.objects.active = hero
md = [m for m in hero.modifiers if m.type == 'ARMATURE'][0]
bpy.ops.object.modifier_apply(modifier=md.name)
hero.parent = None
hero.matrix_world = Matrix.Identity(4)

# ---------- thicken body (radial from bone axes, blended by conform weights) ----------
AXIAL = {'C_Root', 'C_Spine01', 'C_Spine02', 'L_Pelvis', 'R_Pelvis'}
RADIAL = {'L_UpperArm', 'R_UpperArm', 'L_Shoulder', 'L_Arm', 'R_Arm', 'Pelvis_009_R_002',
          'L_Thigh', 'R_Thigh', 'L_Claf', 'R_Claf'}


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

# ---------- FIT TO T0 at the slot cuts ----------
def smooth(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def classes():
    """Per-face / per-vertex colour classes from the baked texture (current mesh)."""
    uvl = me.uv_layers['UVMap'].data
    def face_rgb(p):
        c = sum((uvl[li].uv for li in p.loop_indices), Vector((0, 0))) / len(p.loop_indices)
        pts = [c] + [c.lerp(uvl[li].uv, 0.5) for li in p.loop_indices]
        return sum((texel(q) for q in pts), Vector((0, 0, 0))) / len(pts)
    fcl = [klass(face_rgb(p)) for p in me.polygons]
    vc = [set() for _ in me.vertices]
    for p, k in zip(me.polygons, fcl):
        for vi in p.vertices:
            vc[vi].add(k)
    return fcl, vc


FCL, vcl = classes()
# waist: the jacket hem goes down to HEM_Z (brown verts well below the hem are the belt, i.e. jeans)
low = sorted(v.co.z for v in me.vertices if 'brown' in vcl[v.index] and 0.86 < v.co.z < 1.05 and abs(v.co.x) < 0.33)
hem = low[int(len(low) * 0.06)]
jset = {v.index for v in me.vertices if 'brown' in vcl[v.index] and hem - 0.02 < v.co.z < 1.05 and abs(v.co.x) < 0.33}
print('WAIST jacket hem measured at z=%.3f -> %.3f (%d hem verts, %d brown verts below = belt)' % (
    hem, HEM_Z, len(jset), sum(1 for z in low if z <= hem - 0.02)))
PW = [(0.84, 0.84), (hem, HEM_Z), (hem + 0.16, hem + 0.16)]
for v in me.vertices:
    if 0.84 < v.co.z < hem + 0.16 and abs(v.co.x) < 0.33:
        v.co.z = H.pwl(v.co.z, PW)
nclamp = 0
for v in me.vertices:
    if v.index in jset and v.co.z < HEM_Z:
        v.co.z = HEM_Z; nclamp += 1

# neck: collar = brown faces connected to the jacket body, outside the T0 neck column
bm = bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
def collar_ok(f):
    c = f.calc_center_median()
    if FCL[f.index] != 'brown' or max(v.co.z for v in f.verts) > 1.60 or abs(c.x) > 0.25:
        return False
    if c.z > 1.50:
        r0 = t0_r(NECK_AX, c, min(c.z, 1.531))
        return r0 is None or math.hypot(c.x, c.y - NECK_AX) > r0 + 0.006
    return True
seeds = [f for f in bm.faces if FCL[f.index] == 'brown' and 1.30 < f.calc_center_median().z < 1.44 and abs(f.calc_center_median().x) < 0.2]
got = set(f.index for f in seeds); st = list(seeds)
while st:
    f = st.pop()
    for e in f.edges:
        for g in e.link_faces:
            if g.index not in got and collar_ok(g):
                got.add(g.index); st.append(g)
cset = {v.index for fi in got for v in bm.faces[fi].verts if v.co.z > 1.44}
bm.free()
ctop = max([me.vertices[i].co.z for i in cset] or [0])
nsq = 0
if ctop > COLLAR_TOP:
    for i in cset:
        c = me.vertices[i].co
        if c.z > 1.47:
            c.z = 1.47 + (c.z - 1.47) * (COLLAR_TOP - 1.47) / (ctop - 1.47); nsq += 1
print('NECK collar: %d verts, top %.3f -> %.3f (%d squeezed)' % (len(cset), ctop, min(ctop, COLLAR_TOP), nsq))

# loops exactly on the slot planes, so the rings at the cuts can take the T0 shape
PLANES = (0.900, 0.910, 1.532, 1.549)
nold = len(me.vertices)
old = [v.co.copy() for v in me.vertices]
bm = bmesh.new(); bm.from_mesh(me)
for z in PLANES:
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=(0, 0, z), plane_no=(0, 0, 1))
bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])
bm.to_mesh(me); bm.free(); me.update()
assert max((me.vertices[i].co - old[i]).length for i in range(nold)) < 1e-6      # old indices kept, new verts appended
print("CUT whole mesh tris after bisect = %d (+%d verts on the planes)" % (W.tri_count(hero), len(me.vertices) - nold))

nw = nn = npw = npn = 0
for v in me.vertices:
    c = v.co
    if v.index in jset:
        if c.z < 1.0:                                     # hem stays outside the T0 trousers
            r0 = t0_r(WAIST_AX, c, 0.905); r = math.hypot(c.x, c.y - WAIST_AX)
            if r0 and r < r0 + 0.014:
                k = (r0 + 0.014) / r
                c.x *= k; c.y = WAIST_AX + (c.y - WAIST_AX) * k; npw += 1
    elif 0.84 < c.z < HEM_Z - 0.0005 and abs(c.x) < 0.33:  # jeans + belt take the T0 trouser ring
        w = smooth(0.84, 0.885, c.z)
        r0 = t0_r(WAIST_AX, c, min(max(c.z, 0.89), 0.911)); r = math.hypot(c.x, c.y - WAIST_AX)
        if r0 and r > 1e-4:
            k = 1 + w * (r0 / r - 1)
            c.x *= k; c.y = WAIST_AX + (c.y - WAIST_AX) * k; nw += 1
    elif v.index in cset:
        r0 = t0_r(NECK_AX, c, min(max(c.z, 1.50), 1.531)); r = math.hypot(c.x, c.y - NECK_AX)
        if r0 and c.z > 1.49 and r < r0 + 0.012:           # collar stays outside the T0 neck
            k = (r0 + 0.012) / r
            c.x *= k; c.y = NECK_AX + (c.y - NECK_AX) * k; npn += 1
    elif 1.49 < c.z < 1.60 and abs(c.x) < 0.2:             # neck / chin skin takes the T0 surface
        w = smooth(1.49, 1.525, c.z) * (1 - smooth(1.556, 1.60, c.z))
        r0 = t0_r(NECK_AX, c, c.z); r = math.hypot(c.x, c.y - NECK_AX)
        if r0 and r > 1e-4 and w > 0:
            k = 1 + w * (r0 / r - 1)
            c.x *= k; c.y = NECK_AX + (c.y - NECK_AX) * k; nn += 1
me.update()
print('FIT waist: %d verts to the T0 trouser ring, %d hem verts clamped to z %.3f, %d pushed outside' % (nw, nclamp, HEM_Z, npw))
print('FIT neck: %d verts to the T0 neck/chin surface, %d collar verts pushed outside' % (nn, npn))

# nape / sides of the neck: faces of the neck column that baked collar leather or hair shadow
# (read as a dark band under the head, same defect as on the hero 09-27) -> skin texel under the chin.
# Chosen by geometry: on the T0 neck surface (not the collar), below the hairline (T0 hair starts at 1.559).
FCL, vcl = classes()
uvl = me.uv_layers['UVMap'].data
skinf = [p for p, k in zip(me.polygons, FCL) if k == 'skin']
chin = min(skinf, key=lambda p: (Vector(p.center) - Vector((0, -0.11, 1.585))).length)
cuv = sum((uvl[li].uv for li in chin.loop_indices), Vector((0, 0))) / len(chin.loop_indices)
nnape = 0
for p in me.polygons:
    vv = [me.vertices[vi] for vi in p.vertices]
    c = Vector(p.center)
    if c.y <= -0.04 or any(v.index in cset for v in vv):
        continue
    if min(v.co.z for v in vv) < 1.499 or max(v.co.z for v in vv) > 1.61 or c.z > 1.565:
        continue
    ok = True
    for v in vv:
        r0 = t0_r(NECK_AX, v.co, min(v.co.z, 1.556))
        if r0 is None or math.hypot(v.co.x, v.co.y - NECK_AX) > r0 + (0.008 if v.co.z < 1.556 else 0.03):   # above 1.556 the fit to T0 fades out
            ok = False
    if ok:
        for li in p.loop_indices:
            uvl[li].uv = cuv
        nnape += 1
print('NAPE skin fill: %d faces -> texel %s at uv %s' % (nnape, tuple(round(a, 2) for a in texel(cuv)), tuple(round(a, 3) for a in cuv)))

# ---------- final skin on RootAnim ----------
un = heat_skin(hero, rig)
bpy.ops.object.select_all(action='DESELECT')
hero.select_set(True)
bpy.context.view_layer.objects.active = hero
bpy.ops.object.vertex_group_clean(group_select_mode='ALL', limit=0.05)
bpy.ops.object.vertex_group_limit_total(group_select_mode='ALL', limit=4)
bpy.ops.object.vertex_group_normalize_all(group_select_mode='ALL', lock_active=False)

# ---------- upper-body weight fix (same as the hero, 09-27: clavicles roll ~90 deg in melee/aim) ----------
CLAV = {'L_UpperArm': 'L_Shoulder', 'R_UpperArm': 'R_Arm'}
SH_A, SH_B = 0.20, 0.32
SP_A, SP_B = 1.22, 1.34
for bn in ('C_Spine01', 'C_Spine02', 'C_Neck', 'L_Shoulder', 'R_Arm'):
    if bn not in hero.vertex_groups:
        hero.vertex_groups.new(name=bn)
VG = {g.name: g for g in hero.vertex_groups}
gname = {g.index: g.name for g in hero.vertex_groups}
nclav = nhead = 0
for v in me.vertices:
    w = {gname[g.group]: g.weight for g in v.groups if g.weight > 0}
    add = {}
    for cl, armb in CLAV.items():
        wc = w.pop(cl, 0.0)
        if wc <= 0:
            continue
        nclav += 1
        s = smooth(SH_A, SH_B, abs(v.co.x))
        t = smooth(SP_A, SP_B, v.co.z)
        add[armb] = add.get(armb, 0.0) + wc * s
        add['C_Spine02'] = add.get('C_Spine02', 0.0) + wc * (1 - s) * t
        add['C_Spine01'] = add.get('C_Spine01', 0.0) + wc * (1 - s) * (1 - t)
    if v.co.z < 1.50 and w.get('C_Head', 0) > 0:
        nhead += 1
        add['C_Neck'] = add.get('C_Neck', 0.0) + w.pop('C_Head')
    if not add:
        continue
    for k, a in add.items():
        w[k] = w.get(k, 0.0) + a
    for cl in CLAV:
        VG[cl].remove([v.index])
    if 'C_Head' not in w:
        VG['C_Head'].remove([v.index])
    for k, a in w.items():
        VG[k].add([v.index], a, 'REPLACE')
bpy.ops.object.vertex_group_clean(group_select_mode='ALL', limit=0.02)
bpy.ops.object.vertex_group_limit_total(group_select_mode='ALL', limit=4)
bpy.ops.object.vertex_group_normalize_all(group_select_mode='ALL', lock_active=False)
left = sum(1 for v in me.vertices for g in v.groups if gname[g.group] in CLAV and g.weight > 0)
print('WEIGHT FIX: clavicle weights moved on %d verts (left %d), head->neck below chin on %d verts' % (nclav, left, nhead))
W.rebind(hero, rig)

# ---------- material (one texture) ----------
bimg.filepath_raw = TEX
bimg.file_format = 'PNG'
bimg.save()
bimg.filepath = TEX
mat = bpy.data.materials.new(MAT)
mat.use_nodes = True
nt = mat.node_tree
nt.nodes.clear()
out = nt.nodes.new('ShaderNodeOutputMaterial')
bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
bsdf.inputs['Metallic'].default_value = 0.0
bsdf.inputs['Roughness'].default_value = 0.8
tx = nt.nodes.new('ShaderNodeTexImage')
tx.image = bimg
nt.links.new(tx.outputs['Color'], bsdf.inputs['Base Color'])
nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
me.materials.clear()
me.materials.append(mat)
for p in me.polygons:
    p.material_index = 0
    p.use_smooth = False

# ---------- split into slots (the T0 Z zones with overlap; loops are already on the planes) ----------

SLOTS = {'SK_Armor_T1_Head': lambda z: z > 1.532,
         'SK_Armor_T1_Torso': lambda z: 0.900 < z < 1.549,
         'SK_Armor_T1_Legs': lambda z: z < 0.910}
parts = []
for name, keep in SLOTS.items():
    ob = hero.copy(); ob.data = me.copy()
    ob.name = ob.data.name = name
    bpy.context.collection.objects.link(ob)
    bm = bmesh.new(); bm.from_mesh(ob.data)
    doomed = [f for f in bm.faces if not keep(f.calc_center_median().z)]
    bmesh.ops.delete(bm, geom=doomed, context='FACES')
    bm.to_mesh(ob.data); bm.free(); ob.data.update()
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
bpy.ops.wm.save_as_mainfile(filepath=WORK + 't1_work.blend')
print('SAVED', WORK + 't1_work.blend')
tor = bpy.data.objects['SK_Armor_T1_Torso']
hx = [v.co for v in tor.data.vertices if v.co.x > 0.89]
print('HAND left: tip x=%.3f (T0 0.993), z=[%.3f..%.3f] y=[%.3f..%.3f]' % (
    max(c.x for c in hx), min(c.z for c in hx), max(c.z for c in hx), min(c.y for c in hx), max(c.y for c in hx)))
