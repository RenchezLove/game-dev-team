import bpy
bpy.ops.wm.open_mainfile(filepath='E:/ForGameLead(Materials)/Порядок (PipeLine) создания мешей,анимаций AMasterHumanoidCharacter импорт и экспорт/RunAnimation.blend')
for a in bpy.data.actions:
    print('ACT', a.name, tuple(a.frame_range), a.users)
for o in bpy.data.objects:
    print('OBJ', o.name, o.type, o.animation_data.action.name if o.animation_data and o.animation_data.action else None, tuple(round(x,3) for x in o.matrix_world.to_scale()))
    if o.type=='ARMATURE': print('  bones', len(o.data.bones), [b.name for b in o.data.bones][:8])
