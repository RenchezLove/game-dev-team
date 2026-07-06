import bpy, sys
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W
for f in ('_work/master.blend', '_work/wearables_work.blend'):
    bpy.ops.wm.open_mainfile(filepath=W.WORKDIR + f)
    rig = bpy.data.objects['RootAnim']
    b = rig.data.bones['C_Neck']
    loc, rot, sc = rig.matrix_world.decompose()
    print('FILE %s C_Neck_local_z=%.3f obj_scale=%.3f users=%d' % (
        f, b.matrix_local.translation.z, sc.z, rig.data.users))
print('OK')
