import unreal
eal = unreal.EditorAssetLibrary; at = unreal.AssetToolsHelpers.get_asset_tools()
print('PIE', unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor())
ref = unreal.load_asset('/Game/UI/Icons/Items/T_Item_Pistol')
PROPS = ['compression_settings', 'lod_group', 'mip_gen_settings', 'srgb', 'never_stream', 'filter']
print('REF', [(k, ref.get_editor_property(k)) for k in PROPS])
for n in ['T_Item_Shotgun', 'T_Item_Ammo12g', 'T_Item_WalkieTalkie']:
    t = unreal.AssetImportTask()
    for k, v in [('filename', 'E:/game-dev-team/assets/icons_1010/' + n + '.png'), ('destination_path', '/Game/UI/Icons/Items'), ('destination_name', n), ('replace_existing', True), ('automated', True), ('save', False)]: t.set_editor_property(k, v)
    at.import_asset_tasks([t]); tex = unreal.load_asset('/Game/UI/Icons/Items/' + n)
    for k in PROPS: tex.set_editor_property(k, ref.get_editor_property(k))
    print('ICON', n, tex.blueprint_get_size_x(), tex.blueprint_get_size_y(), eal.save_loaded_asset(tex, False))
p = '/Game/Items/BP_GuardRadio'
if not eal.does_asset_exist(p):
    f = unreal.BlueprintFactory(); f.set_editor_property('parent_class', unreal.QuestItem)
    bp = at.create_asset('BP_GuardRadio', '/Game/Items', unreal.Blueprint, f)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp); print('SAVE BP_GuardRadio', eal.save_loaded_asset(bp, False))
