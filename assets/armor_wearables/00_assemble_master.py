"""Assemble master scene for wearables batch:
- rig = RootAnim from SK_Cloth_L1_Torso.fbx (21 bones, T-pose bind), meters, identity
- meshes: L1_Torso, L1_Legs, L1_Head, BaseHead — normalized, rebound to rig
- probe: compare C_Spine02/C_Neck/C_Head rest matrices (base-head rig vs L1 rig)
- save master blend + raw source preview renders (front -Y, front +Y, side, top)
Run: blender.exe -b --factory-startup --python 00_assemble_master.py
"""
import bpy, sys, os
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W
from mathutils import Vector

W.fresh()

# --- rig + torso (bake mesh FIRST, then apply rig transform, then rebind) ---
meshes, arms, rest = W.import_fbx(W.HANDOFF + 'SK_Cloth_L1_Torso.fbx')
rig = arms[0]
torso = meshes[0]
W.bake_world(torso)
W.apply_armature_transform(rig)
rig.name = 'RootAnim'
W.rebind(torso, rig)
torso.name = 'L1_Torso'
for o in rest:
    bpy.data.objects.remove(o, do_unlink=True)

probe = {}


def pull(fbx, mesh_name):
    meshes, arms, rest = W.import_fbx(W.HANDOFF + fbx)
    a = arms[0]
    ob = meshes[0]
    W.bake_world(ob)                 # detach mesh before touching its armature
    W.apply_armature_transform(a)    # to meters, for the bone-matrix probe
    probe[fbx] = {b.name: a.data.bones[b.name].matrix_local.copy()
                  for b in a.data.bones if b.name in ('C_Spine02', 'C_Neck', 'C_Head')}
    W.rebind(ob, rig)
    ob.name = mesh_name
    for o in rest + [a]:
        bpy.data.objects.remove(o, do_unlink=True)
    return ob


legs = pull('SK_Cloth_L1_Legs.fbx', 'L1_Legs')
l1head = pull('SK_Cloth_L1_Head.fbx', 'L1_Head')
bhead = pull('HeadAndSkeletonfbx_Head.fbx', 'BaseHead')

# --- bone rest matrix probe (head bones must match across bind poses) ---
print('\n--- HEAD BONE REST MATRIX PROBE ---')
ref = {b.name: rig.data.bones[b.name].matrix_local for b in rig.data.bones
       if b.name in ('C_Spine02', 'C_Neck', 'C_Head')}
for src, mats in probe.items():
    for bn, m in mats.items():
        d = max(abs(m[i][j] - ref[bn][i][j]) for i in range(4) for j in range(4))
        print('  %s %s maxdelta=%.6f %s' % (src, bn, d, 'OK' if d < 1e-4 else 'MISMATCH'))

print('\nRIG bones=%d names=%s' % (len(rig.data.bones), sorted(b.name for b in rig.data.bones)))

# --- mesh facts ---
for ob in (torso, legs, l1head, bhead):
    me = ob.data
    xs = [v.co.x for v in me.vertices]
    ys = [v.co.y for v in me.vertices]
    zs = [v.co.z for v in me.vertices]
    print('MESH %-9s tris=%d verts=%d x=[%.3f..%.3f] y=[%.3f..%.3f] z=[%.3f..%.3f]' % (
        ob.name, W.tri_count(ob), len(me.vertices),
        min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)))

# nose direction probe: extreme-Y verts of BaseHead around eye/nose height
me = bhead.data
front = sorted(me.vertices, key=lambda v: v.co.y)[:3]
back = sorted(me.vertices, key=lambda v: -v.co.y)[:3]
print('BaseHead most -Y verts:', [(round(v.co.x, 3), round(v.co.y, 3), round(v.co.z, 3)) for v in front])
print('BaseHead most +Y verts:', [(round(v.co.x, 3), round(v.co.y, 3), round(v.co.z, 3)) for v in back])

for ob in (rig, torso, legs, l1head, bhead):
    W.assert_identity(ob)

os.makedirs(W.WORKDIR + '_work', exist_ok=True)
bpy.ops.wm.save_mainfile(filepath=W.WORKDIR + '_work/master.blend')
print('SAVED', W.WORKDIR + '_work/master.blend')

# --- raw preview renders ---
OUT = W.WORKDIR + '_ref_renders/'
os.makedirs(OUT, exist_ok=True)
# give every mesh a vcol preview material so colors show
for ob in (torso, legs, l1head, bhead):
    W.ensure_col(ob.data)
    me = ob.data
    mat = bpy.data.materials.new('PRE_' + ob.name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    b.inputs['Roughness'].default_value = 0.7
    vc = nt.nodes.new('ShaderNodeVertexColor')
    vc.layer_name = 'Col'
    nt.links.new(vc.outputs['Color'], b.inputs['Base Color'])
    nt.links.new(b.outputs['BSDF'], out.inputs['Surface'])
    me.materials.clear()
    me.materials.append(mat)

sc, cam, suns = W.setup_render()
ALL = [torso, legs, l1head, bhead]
VIEWS = {'ym': (0, -1, 0.12), 'yp': (0, 1, 0.12), 'side': (1, 0, 0.12),
         'top': (0, 0.001, 1), 'tq': (0.7, -1, 0.55)}
for ob in ALL:
    for other in ALL:
        other.hide_render = (other is not ob)
    for vn, vd in VIEWS.items():
        W.frame_and_shoot([ob], vd, OUT + 'src_%s_%s.png' % (ob.name, vn), suns=suns)
# full set (L1 set + base head above it is duplicated head zone; render L1 trio)
for ob in ALL:
    ob.hide_render = (ob is bhead)
for vn, vd in VIEWS.items():
    W.frame_and_shoot([torso, legs, l1head], vd, OUT + 'src_L1set_%s.png' % vn, suns=suns)
print('PREVIEWS DONE')
