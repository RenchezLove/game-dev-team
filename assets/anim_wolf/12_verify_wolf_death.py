"""Round-trip + container proof for Anim_Wolf_Death.fbx.
Wolf batch contract: the file carries MESH + ARMATURE (22 bones, WolfRig).
Run:  blender.exe -b --factory-startup --python 12_verify_wolf_death.py
"""
import bpy, os, addon_utils

addon_utils.enable('io_scene_fbx')
from io_scene_fbx import parse_fbx

PATH = 'E:/game-dev-team/assets/anim_wolf/Anim_Wolf_Death.fbx'
KTIME = 46186158000
EXPECT_22 = ['root', 'hips', 'spine', 'chest', 'neck', 'head', 'tail_01', 'tail_02',
             'shoulder_L', 'frontupper_L', 'frontlower_L', 'frontpaw_L',
             'shoulder_R', 'frontupper_R', 'frontlower_R', 'frontpaw_R',
             'thigh_L', 'shin_L', 'rearpaw_L', 'thigh_R', 'shin_R', 'rearpaw_R']

fails = 0
root, version = parse_fbx.parse(PATH)
print('==== container fbx_version=%d bytes=%d' % (version, os.path.getsize(PATH)))
for child in root.elems:
    if child.id == b'Takes':
        for e in child.elems:
            if e.id == b'Take':
                for sub in e.elems:
                    if sub.id == b'LocalTime':
                        secs = (sub.props[1] - sub.props[0]) / float(KTIME)
                        print('  Take LocalTime: %.4f s' % secs)
                        if not (0.8 <= secs <= 1.2):
                            fails += 1
                            print('  FAIL take length outside 0.8-1.2 s')
    elif child.id == b'GlobalSettings':
        for sub in child.elems:
            if sub.id == b'Properties70':
                for p in sub.elems:
                    if p.props[0] in (b'UpAxis', b'FrontAxis', b'CoordAxis', b'UnitScaleFactor'):
                        print('  global %-16s = %s' % (p.props[0].decode(), p.props[-1]))

bpy.ops.wm.read_homefile(use_factory_startup=True)
addon_utils.enable('io_scene_fbx')
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.import_scene.fbx(filepath=PATH)
objs = list(bpy.context.scene.objects)
arms = [o for o in objs if o.type == 'ARMATURE']
meshes = [o for o in objs if o.type == 'MESH']
ao = arms[0]
names = [b.name for b in ao.data.bones]
sc = bpy.context.scene
fs, fe = int(sc.frame_start), int(sc.frame_end)
print('==== roundtrip')
print('  armature: %s bones=%d  meshes_in_file=%d (%s)' % (
    ao.name, len(names), len(meshes), [m.name for m in meshes]))
missing = [b for b in EXPECT_22 if b not in names]
extra = [b for b in names if b not in EXPECT_22]
print('  missing: %s  unexpected: %s' % (missing or 'none', extra or 'none'))
if missing or extra or len(meshes) != 1:
    fails += 1
    print('  FAIL bone set / mesh count (wolf files must carry the mesh)')

prev, travel = {}, {}
for f in range(fs, fe + 1):
    sc.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get()
    ae = ao.evaluated_get(dg)
    for pb in ae.pose.bones:
        wt = (ae.matrix_world @ pb.tail).copy()
        if pb.name in prev:
            travel[pb.name] = travel.get(pb.name, 0.0) + (wt - prev[pb.name]).length
        prev[pb.name] = wt
moving = sorted([(v, k) for k, v in travel.items() if v > 1e-3], reverse=True)
print('  moving bones (%d/22): top %s' % (len(moving), ', '.join('%s %.2f' % (k, v) for v, k in moving[:6])))
if len(moving) < 18:
    fails += 1
    print('  FAIL full-body fall should move nearly every bone')

sc.frame_set(fe)
dg = bpy.context.evaluated_depsgraph_get()
ae = ao.evaluated_get(dg)
zs = [(ae.matrix_world @ pb.tail).z for pb in ae.pose.bones]
print('  final frame: max_bone_z=%.3f (lying on the side => <0.45)' % max(zs))
if max(zs) > 0.45:
    fails += 1
    print('  FAIL corpse not on its side in the exported file')

print('VERIFY_WOLF_DEATH_DONE failures=%d' % fails)
