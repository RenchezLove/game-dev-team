import unreal
eal=unreal.EditorAssetLibrary
for n in ['SM_BusStop','SM_BusStopUrn']:
    sm=unreal.load_asset('/Game/Environment/Props/BusStop/'+n); bs=sm.get_editor_property('body_setup')
    bs.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE); sm.modify()
    print(n,bs.get_editor_property('collision_trace_flag'),'save',eal.save_loaded_asset(sm,False))
print('PIE',unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor())
print('LVL',unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level(),'ALL',unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True))
print('DIRTY',[p.get_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()],[p.get_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()])
