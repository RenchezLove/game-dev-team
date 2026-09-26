import unreal
bp=unreal.load_asset('/Game/Environment/Lighting/BP_WorldLook')
sds=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem); lib=unreal.SubobjectDataBlueprintFunctionLibrary
for h in sds.k2_gather_subobject_data_for_blueprint(bp):
    o=lib.get_object(lib.get_data(h))
    if isinstance(o,unreal.SceneComponent):
        print('TPL',o.get_name(),o.get_class().get_name(),o.get_editor_property('mobility'))
        if o.get_class().get_name()=='SceneComponent': o.set_editor_property('mobility',unreal.ComponentMobility.STATIC)
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
print('SAVED',unreal.EditorAssetLibrary.save_asset('/Game/Environment/Lighting/BP_WorldLook',only_if_is_dirty=False))
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
a=[x for x in eas.get_all_level_actors() if x.get_class().get_name()=='BP_WorldLook_C'][0]
a.root_component.set_mobility(unreal.ComponentMobility.STATIC)
for c in a.get_components_by_class(unreal.LightComponentBase):
    c.set_mobility(unreal.ComponentMobility.STATIONARY)
for c in a.get_components_by_class(unreal.SceneComponent): print('INST',c.get_name(),c.get_editor_property('mobility'))
print('LVL',unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level())
