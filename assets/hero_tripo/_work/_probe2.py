import bpy, addon_utils
addon_utils.enable('io_scene_fbx')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath='E:/ForGameLead(Materials)/Порядок (PipeLine) создания мешей,анимаций AMasterHumanoidCharacter импорт и экспорт/Anim_Run_Humanoid .fbx')
a=[o for o in bpy.data.objects if o.type=='ARMATURE'][0]
act=a.animation_data.action
print('RANGE', tuple(act.frame_range), getattr(act,'curve_frame_range',None), act.use_frame_range, bpy.context.scene.frame_start, bpy.context.scene.frame_end)
sc=bpy.context.scene
for i in range(0,21):
    sc.frame_set(1, subframe=i/20)
    l=a.matrix_world@a.pose.bones['L_Foot'].head; r=a.matrix_world@a.pose.bones['R_Foot'].head
    print('SUB %.2f Lfoot=(%.3f,%.3f) Rfoot=(%.3f,%.3f)'%(1+i/20,l.y,l.z,r.y,r.z))
from collections import Counter
cb = act.layers[0].strips[0].channelbags[0]
ks = Counter(len(fc.keyframe_points) for fc in cb.fcurves)
print('KEYS per fcurve', ks, [ (round(fc.keyframe_points[0].co.x,3), round(fc.keyframe_points[-1].co.x,3)) for fc in cb.fcurves[:3]])
