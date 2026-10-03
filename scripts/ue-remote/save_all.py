import unreal
print('LVL',unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level())
print('ALL',unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True))
