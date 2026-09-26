import unreal
bp=unreal.load_asset('/Game/Environment/Lighting/BP_WorldLook')
sds=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem); lib=unreal.SubobjectDataBlueprintFunctionLibrary
comps={}
for h in sds.k2_gather_subobject_data_for_blueprint(bp):
    o=lib.get_object(lib.get_data(h))
    if o: comps[o.get_class().get_name()]=o
def apply(fog,sky,pp):
    fog.set_editor_property('fog_density',0.008)
    fog.set_editor_property('fog_inscattering_luminance',unreal.LinearColor(0.40,0.36,0.30,1))
    fog.set_editor_property('directional_inscattering_luminance',unreal.LinearColor(0.90,0.55,0.30,1))
    fog.set_editor_property('directional_inscattering_exponent',6.0)
    sky.set_editor_property('intensity',1.1)
    sky.set_editor_property('light_color',unreal.Color(r=190,g=215,b=255,a=255))
    s=pp.get_editor_property('settings')
    s.set_editor_property('bloom_intensity',0.4)
    s.set_editor_property('color_contrast',unreal.Vector4(1.12,1.12,1.12,1))
    s.set_editor_property('color_gain',unreal.Vector4(1.03,0.99,0.94,1))
    pp.set_editor_property('settings',s)
apply(comps['ExponentialHeightFogComponent'],comps['SkyLightComponent'],comps['PostProcessComponent'])
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
print('SAVED',unreal.EditorAssetLibrary.save_asset('/Game/Environment/Lighting/BP_WorldLook',only_if_is_dirty=False))
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
a=[x for x in eas.get_all_level_actors() if x.get_class().get_name()=='BP_WorldLook_C'][0]
apply(a.get_components_by_class(unreal.ExponentialHeightFogComponent)[0],a.get_components_by_class(unreal.SkyLightComponent)[0],a.get_components_by_class(unreal.PostProcessComponent)[0])
pb=unreal.load_asset('/Game/Characters/Player/BP_PlayerCharacter')
cdo=unreal.get_default_object(pb.generated_class())
cdo.set_editor_property('pp_saturation',0.92); cdo.set_editor_property('pp_highlight_warmth',0.08); cdo.set_editor_property('pp_shadow_coolness',0.08)
print('SAVEDP',unreal.EditorAssetLibrary.save_asset('/Game/Characters/Player/BP_PlayerCharacter',only_if_is_dirty=False))
for x in eas.get_all_level_actors():
    if x.get_class().get_name()=='BP_PlayerCharacter_C':
        print('PLACED',x.get_actor_label(),x.get_editor_property('pp_saturation'),x.get_editor_property('pp_highlight_warmth'),x.get_editor_property('pp_shadow_coolness'))
print('LVL',unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level())
