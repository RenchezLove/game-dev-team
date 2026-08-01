"""Round-trip + container proof for Anim_Death_Humanoid.fbx:
  1) re-import into clean Blender: bone list, hierarchy root, per-bone travel,
     final-frame flatness (did the fall survive the bake);
  2) take length straight from the FBX AnimationStack/Takes (Unreal reads that,
     the re-imported scene range can lie - lesson 14_take_length).
Run:  blender.exe -b --factory-startup --python 22_verify_death.py
"""
import bpy, os, addon_utils
from mathutils import Vector

addon_utils.enable('io_scene_fbx')
from io_scene_fbx import parse_fbx

OUT = 'E:/game-dev-team/assets/anim_humanoid/'
NAME = 'Anim_Death_Humanoid'
PATH = OUT + NAME + '.fbx'
KTIME = 46186158000
EXPECT_21 = ['C_Root', 'C_Spine01', 'C_Spine02', 'C_Neck', 'C_Head',
             'L_UpperArm', 'L_Shoulder', 'L_Arm', 'L_Hand',
             'R_UpperArm', 'R_Arm', 'Pelvis_009_R_002', 'R_Hand',
             'L_Pelvis', 'L_Thigh', 'L_Claf', 'L_Foot',
             'R_Pelvis', 'R_Thigh', 'R_Claf', 'R_Foot']

fails = 0

# ---- container ----
root, version = parse_fbx.parse(PATH)
print('==== container %s  fbx_version=%d  bytes=%d' % (NAME, version, os.path.getsize(PATH)))
for child in root.elems:
    if child.id == b'Objects':
        for e in child.elems:
            if e.id == b'AnimationStack':
                for sub in e.elems:
                    if sub.id == b'Properties70':
                        vals = {}
                        for p in sub.elems:
                            if p.props[0] in (b'LocalStart', b'LocalStop'):
                                vals[p.props[0]] = p.props[-1]
                        if len(vals) == 2:
                            secs = (vals[b'LocalStop'] - vals[b'LocalStart']) / float(KTIME)
                            print('  AnimationStack: %.4f s -> %.1f frames @30fps' % (secs, secs * 30))
                            if not (1.0 <= secs <= 1.5):
                                fails += 1
                                print('  FAIL take length outside 1.0-1.5 s')
    elif child.id == b'Takes':
        for e in child.elems:
            if e.id == b'Take':
                for sub in e.elems:
                    if sub.id == b'LocalTime':
                        print('  Take LocalTime: %.4f s' % ((sub.props[1] - sub.props[0]) / float(KTIME)))
    elif child.id == b'GlobalSettings':
        for sub in child.elems:
            if sub.id == b'Properties70':
                for p in sub.elems:
                    if p.props[0] in (b'UpAxis', b'FrontAxis', b'CoordAxis', b'UnitScaleFactor'):
                        print('  global %-16s = %s' % (p.props[0].decode(), p.props[-1]))

# ---- round trip ----
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
print('==== roundtrip %s' % NAME)
print('  armature object: %s  bones=%d  meshes_in_file=%d' % (ao.name, len(names), len(meshes)))
missing = [b for b in EXPECT_21 if b not in names]
extra = [b for b in names if b not in EXPECT_21]
print('  missing: %s  unexpected: %s' % (missing or 'none', extra or 'none'))
print('  scene frame range: %d..%d fps=%s' % (fs, fe, sc.render.fps))
if missing or extra or len(meshes) != 0:
    fails += 1
    print('  FAIL bone set / stray meshes')

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
print('  moving bones (%d/21): top %s' % (len(moving), ', '.join('%s %.2f' % (k, v) for v, k in moving[:6])))
if len(moving) < 18:
    fails += 1
    print('  FAIL full-body fall should move nearly every bone')

sc.frame_set(fe)
dg = bpy.context.evaluated_depsgraph_get()
ae = ao.evaluated_get(dg)
zs = [(ae.matrix_world @ pb.tail).z for pb in ae.pose.bones]
hipy = (ae.matrix_world @ ae.pose.bones['C_Root'].head).y
print('  final frame: max_bone_z=%.3f (must be <0.45)  hip_y=%.3f (moved back)' % (max(zs), hipy))
if max(zs) > 0.45:
    fails += 1
    print('  FAIL corpse not flat in the exported file')

print('VERIFY_DEATH_DONE failures=%d' % fails)
