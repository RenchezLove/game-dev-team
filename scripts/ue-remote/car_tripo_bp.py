import unreal
bp=unreal.load_asset('/Game/Environment/Props/AbandonedCar/BP_AbandonedCar')
V=unreal.Vector
MOUNTS={'door_fl_mount':V(-76,-92,34),'door_fr_mount':V(76,-92,34),'door_rl_mount':V(-76,1,34),'door_rr_mount':V(76,1,34),'hood_mount':V(0,-97.5,94.6),'trunk_mount':V(0,142,95.7)}
LOCS={'WheelFL':V(-66,-144,28.5),'WheelFR':V(66,-144,28.5),'WheelRL':V(-66,97,28.5),'WheelRR':V(66,97,28.5),'Block':V(55,-144,0)}
cdo=unreal.get_default_object(bp.generated_class())
for k,v in MOUNTS.items(): cdo.set_editor_property(k,v)
sds=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
for h in sds.k2_gather_subobject_data_for_blueprint(bp):
    o=unreal.SubobjectDataBlueprintFunctionLibrary.get_object(unreal.SubobjectDataBlueprintFunctionLibrary.get_data(h))
    if isinstance(o,unreal.StaticMeshComponent) and o.get_name() in LOCS:
        o.modify(); o.set_editor_property('relative_location',LOCS[o.get_name()]); print('TPL',o.get_name(),o.get_editor_property('relative_location').to_tuple())
bp.modify()
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
print('SAVE_BP',unreal.EditorAssetLibrary.save_loaded_asset(bp,False))
OLD={'door_fl_mount':(-80,-47,31.5),'hood_mount':(0,-59,88)}
cls=unreal.load_class(None,'/Script/ContrarySurvivor.AbandonedCar')
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
for a in unreal.GameplayStatics.get_all_actors_of_class(w,cls):
    a.modify()
    for k,v in MOUNTS.items(): a.set_editor_property(k,v)
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        if c.get_name() in LOCS and [round(x,1) for x in c.get_editor_property('relative_location').to_tuple()]!=[round(x,1) for x in LOCS[c.get_name()].to_tuple()]:
            c.modify(); c.set_editor_property('relative_location',LOCS[c.get_name()])
    print('CAR',a.get_actor_label(),a.get_editor_property('hood_mount').to_tuple(),[(c.get_name(),[round(x,1) for x in c.get_editor_property('relative_location').to_tuple()]) for c in a.get_components_by_class(unreal.StaticMeshComponent) if c.get_name() in ('WheelFL','Block','DoorFL','Hood')])
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level(); print('SAVED')
