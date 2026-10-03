"""Tripo wolf (wolf.glb, 976 tris) -> skinned mesh SK_Wolf on the EXISTING WolfRig (22 bones, faces +Y).
The rig, its rest pose and the four takes are not touched: the model is bent into the rig's rest pose.
Steps: open the rig blend (rig + old wolf + takes) -> import glb, turn to +Y, feet on Z0 -> measure
leg centre lines -> a copy of WolfRig with joints on the Tripo wolf -> heat-skin -> pose the copy
onto the real rest (bone by bone, length scale, no twist) -> bake -> paws put back flat ->
heat-skin to WolfRig -> texture 1024 -> save _work/wolf_work.blend.
Run: blender.exe -b --factory-startup --python 10_build.py
"""
import bpy, bmesh, sys, os, math
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W
from mathutils import Vector, Matrix, kdtree

RIGBLEND = 'E:/game-dev-team/assets/anim_wolf/_work/_qc_wolf_death.blend'     # WolfRig + old SK_Wolf + Idle/Run/Bite/Death
GLB = 'E:/ContrarySurvior/ContrarySurvivor/Saved/Tripo/wolf/wolf.glb'
OUTDIR = 'E:/game-dev-team/assets/wolf_tripo/'
TEX = OUTDIR + 'T_WolfTripo_D.png'
PRE = float(os.environ.get('WOLF_SCALE', '1.0'))        # uniform scale of the Tripo wolf before the fit

bpy.ops.wm.open_mainfile(filepath=RIGBLEND)
rig = bpy.data.objects['WolfRig']
rig.animation_data.action = None
for pb in rig.pose.bones:
    pb.matrix_basis = Matrix.Identity(4)
old = bpy.data.objects['SK_Wolf']
old.name = old.data.name = 'SK_Wolf_old'
bpy.context.view_layer.update()

bpy.ops.import_scene.gltf(filepath=GLB)
wolf = [o for o in bpy.context.selected_objects if o.type == 'MESH'][0]
for o in list(bpy.context.selected_objects):
    if o is not wolf:
        bpy.data.objects.remove(o, do_unlink=True)
bpy.context.view_layer.update()
me = wolf.data
me.transform(Matrix.Scale(PRE, 4) @ Matrix.Rotation(math.radians(90), 4, 'Z') @ wolf.matrix_world)   # model faces +X -> +Y
wolf.parent = None
wolf.matrix_world = Matrix.Identity(4)
xs = [v.co.x for v in me.vertices]
me.transform(Matrix.Translation((-(min(xs) + max(xs)) / 2, 0, -min(v.co.z for v in me.vertices))))
bm = bmesh.new(); bm.from_mesh(me)
n0 = len(bm.verts)
bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
bmesh.ops.triangulate(bm, faces=bm.faces[:])
bm.to_mesh(me); bm.free(); me.update()
me.calc_loop_triangles()
cs = [v.co.copy() for v in me.vertices]
print('TRIPO tris=%d verts %d -> %d  x %.3f..%.3f y %.3f..%.3f z %.3f..%.3f' % (len(me.loop_triangles), n0, len(me.vertices),
      min(c.x for c in cs), max(c.x for c in cs), min(c.y for c in cs), max(c.y for c in cs), min(c.z for c in cs), max(c.z for c in cs)))
RAW = [v.co.copy() for v in me.vertices]


def section(z):
    """Closed outlines of the model at height z -> list of (centre, size)."""
    b = bmesh.new(); b.from_mesh(me)
    r = bmesh.ops.bisect_plane(b, geom=b.verts[:] + b.edges[:] + b.faces[:], dist=1e-6, plane_co=(0, 0, z), plane_no=(0, 0, 1))
    es = [e for e in r['geom_cut'] if isinstance(e, bmesh.types.BMEdge)]
    adj = {}
    for e in es:
        for v in e.verts:
            adj.setdefault(v, []).append(e)
    seen = set(); out = []
    for v in adj:
        if v in seen:
            continue
        st = [v]; seen.add(v); c = []
        while st:
            a = st.pop(); c.append(a.co.copy())
            for e in adj[a]:
                q = e.other_vert(a)
                if q not in seen:
                    seen.add(q); st.append(q)
        mn = Vector((min(p.x for p in c), min(p.y for p in c))); mx = Vector((max(p.x for p in c), max(p.y for p in c)))
        out.append(((mn + mx) / 2, mx - mn))
    b.free()
    return out


def leg_at(z, side, front):
    """Centre of the leg outline at height z (side +1 left / -1 right, front or rear)."""
    best = None
    for c, s in section(z * PRE):
        if c.x * side > 0.02 and (c.y > 0) == front and s.x < 0.25 * PRE and s.y < 0.35 * PRE:
            if best is None or s.x * s.y > best[1].x * best[1].y:
                best = (c, s)
    return Vector((best[0].x, best[0].y, z * PRE))


# ---------- joints of the Tripo wolf (heights from 04_sections.py: elbow / wrist / knee / hock) ----------
O = {b.name: (b.head_local.copy(), b.tail_local.copy()) for b in rig.data.bones}
P = lambda x, y, z: Vector((x, y, z)) * PRE
T = {'root': O['root'],
     'hips': (P(0, -0.50, 0.72), P(0, -0.10, 0.80)),
     'spine': (P(0, -0.10, 0.80), P(0, 0.2125, 0.81)),
     'chest': (P(0, 0.2125, 0.81), P(0, 0.55, 0.82)),
     'neck': (P(0, 0.55, 0.82), P(0, 0.77, 0.95)),
     'head': (P(0, 0.77, 0.95), P(0, 1.03, 0.86)),
     'tail_01': (P(0, -0.60, 0.72), P(0, -0.82, 0.48)),
     'tail_02': (P(0, -0.82, 0.48), P(0, -1.04, 0.33))}
PAWT = {}
for s, sx in (('L', 1), ('R', -1)):
    elbow = leg_at(0.46, sx, True); wrist = leg_at(0.21, sx, True); fpaw = leg_at(0.05, sx, True)
    knee = leg_at(0.56, sx, False); hock = leg_at(0.30, sx, False); rpaw = leg_at(0.05, sx, False)
    fpaw.z = rpaw.z = 0.058                     # the rig keeps the paw bone tails 5.8 cm above the ground
    sh0 = Vector((sx * 0.09 * PRE, elbow.y + 0.04 * PRE, 0.72 * PRE)); sh1 = Vector((sx * 0.13 * PRE, elbow.y + 0.03 * PRE, 0.62 * PRE))
    hip = Vector((sx * 0.10 * PRE, knee.y - 0.04 * PRE, 0.74 * PRE))
    T['shoulder_' + s] = (sh0, sh1)
    T['frontupper_' + s] = (sh1, elbow)
    T['frontlower_' + s] = (elbow, wrist)
    T['frontpaw_' + s] = (wrist, fpaw)
    T['thigh_' + s] = (hip, knee)
    T['shin_' + s] = (knee, hock)
    T['rearpaw_' + s] = (hock, rpaw)
    PAWT['frontpaw_' + s] = fpaw; PAWT['rearpaw_' + s] = rpaw
    print('TRIPO leg %s: elbow %s wrist %s front paw %s | knee %s hock %s rear paw %s' % (
        s, *[tuple(round(a, 3) for a in p) for p in (elbow, wrist, fpaw, knee, hock, rpaw)]))
assert sorted(T) == sorted(O), set(O) ^ set(T)

trig = rig.copy(); trig.data = rig.data.copy()
trig.name = trig.data.name = 'TripoRig'
trig.animation_data_clear()
bpy.context.collection.objects.link(trig)
bpy.ops.object.select_all(action='DESELECT')
bpy.context.view_layer.objects.active = trig
trig.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
for eb in trig.data.edit_bones:
    eb.use_connect = False
for eb in trig.data.edit_bones:
    rb = rig.data.bones[eb.name]
    d0 = (O[eb.name][1] - O[eb.name][0]).normalized()
    eb.head, eb.tail = T[eb.name]
    d1 = (T[eb.name][1] - T[eb.name][0]).normalized()
    eb.align_roll(d0.rotation_difference(d1) @ rb.z_axis)        # same roll as the rig bone, carried by the shortest turn: no twist in the fit
    eb.inherit_scale = 'NONE'
bpy.ops.object.mode_set(mode='OBJECT')


def heat_skin(mesh, arm_ob):
    for vg in list(mesh.vertex_groups):
        mesh.vertex_groups.remove(vg)
    for md in [m for m in mesh.modifiers if m.type == 'ARMATURE']:
        mesh.modifiers.remove(md)
    mesh.parent = None
    bpy.ops.object.select_all(action='DESELECT')
    mesh.select_set(True); arm_ob.select_set(True)
    bpy.context.view_layer.objects.active = arm_ob
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    un = [v for v in mesh.data.vertices if not any(g.weight > 1e-4 for g in v.groups)]
    print('HEAT %s -> %s groups=%d unweighted=%d' % (mesh.name, arm_ob.name, len(mesh.vertex_groups), len(un)))
    assert len(mesh.vertex_groups) == 22, 'heat skin failed'
    if un:
        src = [v for v in mesh.data.vertices if any(g.weight > 1e-4 for g in v.groups)]
        kd = kdtree.KDTree(len(src))
        for i, v in enumerate(src):
            kd.insert(v.co, i)
        kd.balance()
        gn = [g.name for g in mesh.vertex_groups]
        for v in un:
            _, i, _ = kd.find(v.co)
            for g in src[i].groups:
                mesh.vertex_groups[gn[g.group]].add([v.index], g.weight, 'REPLACE')
        print('  filled %d unweighted verts from the nearest skinned vertex' % len(un))


wolf.name = me.name = 'SK_Wolf'
heat_skin(wolf, trig)
order = []
def walk(b):
    order.append(b.name)
    for c in b.children:
        walk(c)
for b in trig.data.bones:
    if b.parent is None:
        walk(b)
for bn in order:
    rb = rig.data.bones[bn]
    lt = (T[bn][1] - T[bn][0]).length
    trig.pose.bones[bn].matrix = rb.matrix_local @ Matrix.Diagonal((1.0, rb.length / lt, 1.0, 1.0))
    bpy.context.view_layer.update()
err = 0.0
for bn in order:
    pb = trig.pose.bones[bn]
    err = max(err, (pb.head - O[bn][0]).length, (pb.tail - O[bn][1]).length)
    d0 = (T[bn][1] - T[bn][0]).normalized(); d1 = (O[bn][1] - O[bn][0]).normalized()
    print('  fit %-13s length Tripo %.3f rig %.3f scale %.2f turn %5.1f deg' % (bn, (T[bn][1] - T[bn][0]).length, rig.data.bones[bn].length,
          rig.data.bones[bn].length / (T[bn][1] - T[bn][0]).length, math.degrees(d0.angle(d1))))
print('FIT max joint error = %.5f m' % err)
bpy.ops.object.select_all(action='DESELECT')
wolf.select_set(True)
bpy.context.view_layer.objects.active = wolf
md = [m for m in wolf.modifiers if m.type == 'ARMATURE'][0]
bpy.ops.object.modifier_apply(modifier=md.name)
wolf.parent = None
wolf.matrix_world = Matrix.Identity(4)
bpy.data.objects.remove(trig, do_unlink=True)

# paws back flat: the foot keeps its Tripo shape and sits at the rig paw point (the fit turned it with the paw bone)
def smooth(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)
nf = 0
for v in me.vertices:
    r = RAW[v.index]
    if r.z > 0.15 * PRE:
        continue
    bn = min(PAWT, key=lambda k: (Vector((PAWT[k].x, PAWT[k].y)) - Vector((r.x, r.y))).length)
    if (Vector((PAWT[bn].x, PAWT[bn].y)) - Vector((r.x, r.y))).length > 0.2 * PRE:
        continue
    w = 1 - smooth(0.07 * PRE, 0.15 * PRE, r.z)
    v.co = v.co.lerp(r + (O[bn][1] - PAWT[bn]), w); nf += 1
me.update()
print('PAWS %d foot verts put back flat at the rig paw points, lowest z %.3f' % (nf, min(v.co.z for v in me.vertices)))

# ---------- final skin on the real WolfRig ----------
heat_skin(wolf, rig)
bpy.ops.object.select_all(action='DESELECT')
wolf.select_set(True)
bpy.context.view_layer.objects.active = wolf
bpy.ops.object.vertex_group_clean(group_select_mode='ALL', limit=0.03)
bpy.ops.object.vertex_group_limit_total(group_select_mode='ALL', limit=4)
bpy.ops.object.vertex_group_normalize_all(group_select_mode='ALL', lock_active=False)
wolf.parent = rig
wolf.matrix_parent_inverse = Matrix.Identity(4)
wolf.matrix_basis = Matrix.Identity(4)
for m in [m for m in wolf.modifiers if m.type == 'ARMATURE']:
    m.object = rig

# ---------- texture 1024 + one material ----------
img = [n.image for m in me.materials if m and m.node_tree for n in m.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image][0]
img.scale(1024, 1024)
img.name = 'T_WolfTripo_D'
img.filepath_raw = TEX; img.file_format = 'PNG'; img.save()
if img.packed_file:
    img.unpack(method='REMOVE')
img.filepath = TEX
mat = bpy.data.materials.new('M_WolfTripo')
mat.use_nodes = True
nt = mat.node_tree
nt.nodes.clear()
out = nt.nodes.new('ShaderNodeOutputMaterial')
bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
bsdf.inputs['Metallic'].default_value = 0.0
bsdf.inputs['Roughness'].default_value = 0.85
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

cs = [v.co for v in me.vertices]; oc = [v.co for v in old.data.vertices]
print('BUILD SK_Wolf tris=%d verts=%d x %.3f..%.3f y %.3f..%.3f z %.3f..%.3f | old wolf x %.3f..%.3f y %.3f..%.3f z %.3f..%.3f' % (
    W.tri_count(wolf), len(me.vertices), min(c.x for c in cs), max(c.x for c in cs), min(c.y for c in cs), max(c.y for c in cs), min(c.z for c in cs), max(c.z for c in cs),
    min(c.x for c in oc), max(c.x for c in oc), min(c.y for c in oc), max(c.y for c in oc), min(c.z for c in oc), max(c.z for c in oc)))
gn = {g.index: g.name for g in wolf.vertex_groups}
use = {}
for v in me.vertices:
    for g in v.groups:
        if g.weight > 0.05:
            use[gn[g.group]] = use.get(gn[g.group], 0) + 1
print('WEIGHTS verts per bone (>0.05): %s' % sorted(use.items()))
bpy.ops.wm.save_as_mainfile(filepath=OUTDIR + '_work/wolf_work.blend')
print('SAVED', OUTDIR + '_work/wolf_work.blend')
