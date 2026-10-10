import unreal
eal = unreal.EditorAssetLibrary; at = unreal.AssetToolsHelpers.get_asset_tools(); mel = unreal.MaterialEditingLibrary
print('PIE', unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor())
D = '/Game/Environment/Props/UAZ452'
t = unreal.AssetImportTask()
for k, v in [('filename', 'E:/game-dev-team/assets/scientist_base/SM_UAZ452_kit/T_UAZ452Kit_Peel.png'), ('destination_path', D), ('destination_name', 'T_UAZ452Kit_Peel'), ('replace_existing', True), ('automated', True), ('save', False)]: t.set_editor_property(k, v)
at.import_asset_tasks([t]); tex = unreal.load_asset(D + '/T_UAZ452Kit_Peel')
tex.set_editor_property('srgb', True); tex.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_DEFAULT)
mi = unreal.load_asset(D + '/MI_UAZ452Kit')
print('set', mel.set_material_instance_texture_parameter_value(mi, 'PeelMask', tex), mel.set_material_instance_scalar_parameter_value(mi, 'PaintBase', 0.68))
mel.update_material_instance(mi)
print('SAVE', eal.save_loaded_asset(tex, False), eal.save_loaded_asset(mi, False), 'mask', mel.get_material_instance_texture_parameter_value(mi, 'PeelMask').get_name(), 'peel', mel.get_material_instance_scalar_parameter_value(mi, 'PaintPeel'))
