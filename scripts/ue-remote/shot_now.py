import unreal
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
p=unreal.get_default_object(unreal.load_object(None,'/Game/Characters/Player/BP_PlayerCharacter.BP_PlayerCharacter_C'))
g=p.get_editor_property
cams=[x for x in eas.get_all_level_actors() if x.get_actor_label()=='TMP_LookCam']
c=cams[0] if cams else eas.spawn_actor_from_class(unreal.CameraActor,unreal.Vector(0,0,0),unreal.Rotator(0,0,0),transient=True)
c.set_actor_label('TMP_LookCam')
cc=c.camera_component
cc.set_editor_property('field_of_view',g('camera_field_of_view'))
pp=cc.get_editor_property('post_process_settings')
HW=g('pp_highlight_warmth'); SC=g('pp_shadow_coolness'); SAT=g('pp_saturation')
for n,v in [('override_vignette_intensity',True),('vignette_intensity',g('pp_vignette_intensity')),('override_color_saturation',True),('color_saturation',unreal.Vector4(SAT,SAT,SAT,1)),('override_color_gain_highlights',True),('color_gain_highlights',unreal.Vector4(1+HW,1,1-HW,1)),('override_color_gain_shadows',True),('color_gain_shadows',unreal.Vector4(1-SC,1,1+SC,1)),('override_film_grain_intensity',True),('film_grain_intensity',g('pp_film_grain_intensity')),('override_auto_exposure_method',True),('auto_exposure_method',unreal.AutoExposureMethod.AEM_MANUAL),('override_auto_exposure_bias',True),('auto_exposure_bias',g('pp_exposure_compensation')),('override_auto_exposure_apply_physical_camera_exposure',True),('auto_exposure_apply_physical_camera_exposure',False)]:
    pp.set_editor_property(n,v)
cc.set_editor_property('post_process_settings',pp)
cc.set_editor_property('post_process_blend_weight',1.0)
r=g('camera_boom_rotation'); L=g('camera_arm_length')
for name,(X,Y,Z) in [('v4_village.png',(-3880,-4320,90))]:
    f=r.get_forward_vector()
    c.set_actor_location(unreal.Vector(X-f.x*L,Y-f.y*L,Z-f.z*L),False,False)
    c.set_actor_rotation(r,False)
    unreal.AutomationLibrary.take_high_res_screenshot(1920,1080,'E:/ContrarySurvior/ContrarySurvivor/Saved/Screenshots/look/'+name,camera=c)
    print('SHOT',name)
