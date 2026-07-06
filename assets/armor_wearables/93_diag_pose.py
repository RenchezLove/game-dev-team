"""Diag: which bone rotation explodes the meshes."""
import bpy, sys, math
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W

bpy.ops.wm.open_mainfile(filepath=W.WORKDIR + '_work/wearables_work.blend')
rig = bpy.data.objects['RootAnim']
T1 = [bpy.data.objects[n] for n in ('SK_Armor_T1_Head', 'SK_Armor_T1_Torso', 'SK_Armor_T1_Legs')]

for bn in ('C_Neck', 'L_Shoulder', 'L_Arm', 'L_Thigh', 'L_Claf'):
    b = rig.data.bones[bn]
    loc, rot, sc = b.matrix_local.decompose()
    print('BONE %-12s headloc=(%.3f,%.3f,%.3f) scale=(%.3f,%.3f,%.3f) len=%.3f connected=%s' % (
        bn, loc.x, loc.y, loc.z, sc.x, sc.y, sc.z, b.length, b.use_connect))


def eval_ranges(tag):
    bpy.context.view_layer.update()
    deps = bpy.context.evaluated_depsgraph_get()
    for o in T1:
        oe = o.evaluated_get(deps)
        me = oe.to_mesh()
        pts = [oe.matrix_world @ v.co for v in me.vertices]
        print('%s %-20s x=[%.2f..%.2f] z=[%.2f..%.2f]' % (
            tag, o.name, min(p.x for p in pts), max(p.x for p in pts),
            min(p.z for p in pts), max(p.z for p in pts)))
        oe.to_mesh_clear()


def reset():
    for pb in rig.pose.bones:
        pb.rotation_mode = 'XYZ'
        pb.rotation_euler = (0, 0, 0)


reset()
eval_ranges('REST')
for bn, eul in (('C_Neck', (math.radians(15), 0, 0)),
                ('L_Shoulder', (0, 0, math.radians(40))),
                ('L_Arm', (0, 0, math.radians(45))),
                ('L_Thigh', (math.radians(-30), 0, 0)),
                ('L_Claf', (math.radians(30), 0, 0))):
    reset()
    pb = rig.pose.bones[bn]
    pb.rotation_euler = eul
    eval_ranges('POSE:' + bn)
print('DIAGPOSE DONE')
