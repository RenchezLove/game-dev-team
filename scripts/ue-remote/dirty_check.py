import unreal
print('PIE',unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor())
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(); print('WORLD',w.get_path_name() if w else None)
print('DIRTY content',[p.get_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()])
print('DIRTY maps',[p.get_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()])
