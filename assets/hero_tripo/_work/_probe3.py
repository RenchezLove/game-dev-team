import bpy
for p in ('E:/game-dev-team/assets/armor_wearables/_work/master.blend','E:/game-dev-team/assets/armor_wearables/_work/wearables_work.blend'):
    bpy.ops.wm.open_mainfile(filepath=p)
    for a in bpy.data.actions:
        print('ACT', p[-22:], a.name, tuple(a.frame_range), a.users)
