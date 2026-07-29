"""Round-trip proof: re-import each exported FBX into a clean Blender and measure what
is actually inside the file - bone names, hierarchy, take length, per-bone motion.
A file existing on disk proves nothing about whether the animation survived the bake.
"""
import bpy, sys, os, math, addon_utils
from mathutils import Vector

OUT = 'E:/game-dev-team/assets/anim_humanoid/'
EXPECT_21 = ['C_Root', 'C_Spine01', 'C_Spine02', 'C_Neck', 'C_Head',
             'L_UpperArm', 'L_Shoulder', 'L_Arm', 'L_Hand',
             'R_UpperArm', 'R_Arm', 'Pelvis_009_R_002', 'R_Hand',
             'L_Pelvis', 'L_Thigh', 'L_Claf', 'L_Foot',
             'R_Pelvis', 'R_Thigh', 'R_Claf', 'R_Foot']
LOWER = ['C_Root', 'L_Pelvis', 'L_Thigh', 'L_Claf', 'L_Foot',
         'R_Pelvis', 'R_Thigh', 'R_Claf', 'R_Foot']
FILES = ['Anim_AimPistol_Humanoid', 'Anim_FirePistol_Humanoid', 'Anim_MeleeSlash_Humanoid']

fails = 0
for name in FILES:
    path = OUT + name + '.fbx'
    bpy.ops.wm.read_homefile(use_factory_startup=True)
    addon_utils.enable('io_scene_fbx')
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    if not os.path.exists(path):
        print('MISSING', path)
        fails += 1
        continue
    bpy.ops.import_scene.fbx(filepath=path)
    objs = list(bpy.context.scene.objects)
    arms = [o for o in objs if o.type == 'ARMATURE']
    meshes = [o for o in objs if o.type == 'MESH']
    ao = arms[0]
    names = [b.name for b in ao.data.bones]
    sc = bpy.context.scene
    fs, fe = int(sc.frame_start), int(sc.frame_end)

    print('==== %s  (%d bytes)' % (os.path.basename(path), os.path.getsize(path)))
    print('  objects: %s   meshes_in_file=%d' % ([o.name for o in objs], len(meshes)))
    print('  armature object name: %s   bones=%d' % (ao.name, len(names)))
    missing = [b for b in EXPECT_21 if b not in names]
    extra = [b for b in names if b not in EXPECT_21]
    print('  missing bones: %s' % (missing or 'none'))
    print('  unexpected bones: %s' % (extra or 'none'))
    roots = [b.name for b in ao.data.bones if b.parent is None]
    print('  root bones in file: %s' % roots)
    print('  scene frame range: %d..%d  fps=%s' % (fs, fe, sc.render.fps))
    act = ao.animation_data.action if ao.animation_data else None
    print('  bound action: %s' % (act.name if act else None))

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
    moving = sorted([(v, k) for k, v in travel.items() if v > 1e-4], reverse=True)
    still_lower = max((travel.get(b, 0.0) for b in LOWER))
    print('  moving bones (%d): %s' % (len(moving), ', '.join('%s %.3f' % (k, v) for v, k in moving[:8])))
    print('  max travel on root/legs: %.6f m  (must be 0)' % still_lower)

    ok = (not missing and not extra and len(names) == 21 and still_lower < 1e-4
          and len(meshes) == 0)
    if name != 'Anim_AimPistol_Humanoid':
        ok = ok and len(moving) > 0
    print('  VERDICT %s' % ('OK' if ok else 'FAIL'))
    if not ok:
        fails += 1

print('VERIFY_DONE failures=%d' % fails)
