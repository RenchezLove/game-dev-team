import bpy
bpy.ops.wm.open_mainfile(filepath='E:/game-dev-team/assets/armor_wearables/_work/wearables_work.blend')
ob=bpy.data.objects['SK_Cloth_T0_Legs']; me=ob.data
f=[v.co for v in me.vertices if v.co.z<0.12 and v.co.x>0]
print('T0 FOOT y=[%.3f..%.3f] x=[%.3f..%.3f] z=[%.3f..%.3f]'%(min(c.y for c in f),max(c.y for c in f),min(c.x for c in f),max(c.x for c in f),min(c.z for c in f),max(c.z for c in f)))
for n in ('SK_Cloth_T0_Head','SK_Cloth_T0_Torso','SK_Cloth_T0_Legs'):
    o=bpy.data.objects[n]; print('VG',n,sorted(g.name for g in o.vertex_groups))
rig=bpy.data.objects['RootAnim']
print('ROLL',[(b.name, round(b.matrix_local.to_3x3().col[0].x,2)) for b in rig.data.bones][:6])
print('INH',set(b.inherit_scale for b in rig.data.bones), set(b.use_connect for b in rig.data.bones))
