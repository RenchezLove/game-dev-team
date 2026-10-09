import unreal
# Перезагрузка одной текстуры поверх прежней (сетка и материал не трогаются).
SRC = 'E:/game-dev-team/assets/scientist_base/SM_ArmyTent/T_ArmyTent_D.png'
DEST = '/Game/Environment/Props/ScientistBase'; NAME = 'T_ArmyTent_D'
print('PIE', unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor())
t = unreal.AssetImportTask()
for k, v in [('filename', SRC), ('destination_path', DEST), ('destination_name', NAME), ('replace_existing', True), ('automated', True), ('save', False)]: t.set_editor_property(k, v)
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
tex = unreal.load_asset(DEST + '/' + NAME)
print('IMPORTED', list(t.get_editor_property('imported_object_paths')), tex.blueprint_get_size_x(), tex.blueprint_get_size_y(), 'SAVE', unreal.EditorAssetLibrary.save_loaded_asset(tex, False))
