import unreal
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
sds=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem); lib=unreal.SubobjectDataBlueprintFunctionLibrary
for a in eas.get_all_level_actors():
    if a.get_class().get_name()=='StaticMeshActor':
        sm=a.static_mesh_component.get_editor_property('static_mesh')
        if sm and sm.get_name()=='SM_TripoHero_Raw':
            print('DEL',a.get_name(),a.get_actor_label(),sm.get_path_name(),eas.destroy_actor(a))
bps=set()
for a in eas.get_all_level_actors():
    if a.get_class().get_name() in ('BP_Trader_C','BP_Elder_C'):
        bps.add(a.get_class().get_path_name()[:-2].split('.')[0])
for p in sorted(bps):
    bp=unreal.load_asset(p); n=[]
    for h in sds.k2_gather_subobject_data_for_blueprint(bp):
        o=lib.get_object(lib.get_data(h))
        if isinstance(o,unreal.SkeletalMeshComponent) or isinstance(o,unreal.StaticMeshComponent):
            o.set_editor_property('cast_shadow',False); n.append(o.get_name())
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    print('BP',p,sorted(set(n)),unreal.EditorAssetLibrary.save_asset(p,only_if_is_dirty=False))
for a in eas.get_all_level_actors():
    if a.get_class().get_name() in ('BP_Trader_C','BP_Elder_C'):
        a.modify()
        for c in a.get_components_by_class(unreal.MeshComponent):
            c.set_editor_property('cast_shadow',False)
        print('INST',a.get_actor_label(),[(c.get_name(),c.get_editor_property('cast_shadow')) for c in a.get_components_by_class(unreal.MeshComponent)])
print('LEFT',[a.get_name() for a in eas.get_all_level_actors() if a.get_class().get_name()=='StaticMeshActor' and a.static_mesh_component.get_editor_property('static_mesh') and a.static_mesh_component.get_editor_property('static_mesh').get_name()=='SM_TripoHero_Raw'])
print('LVL',unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level())
print('ALL',unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True))
