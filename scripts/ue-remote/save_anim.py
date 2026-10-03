import unreal
P='/Game/Characters/Shared/Humanoid/Anim_PistolIdle_Humanoid'
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
print('PIE',les.is_in_play_in_editor())
print('SAVE',unreal.EditorAssetLibrary.save_asset(P,only_if_is_dirty=False))
