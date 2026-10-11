import unreal
# Две картинки синей метки побочного задания (11.10.2026): ромб над целью и стрелка у края экрана.
# Настройки — как у значка кнопки смартфона (pda_phone_import_1011.py): картинка интерфейса без
# уменьшенных копий и без подгрузки по частям.
eal = unreal.EditorAssetLibrary; at = unreal.AssetToolsHelpers.get_asset_tools()
for name in ['T_QuestSideMarker', 'T_QuestEdgeArrow']:
    t = unreal.AssetImportTask()
    for k, v in [('filename', 'E:/game-dev-team/assets/quest_marker_1011/%s.png' % name), ('destination_path', '/Game/UI/Textures'), ('destination_name', name), ('replace_existing', True), ('automated', True), ('save', False)]: t.set_editor_property(k, v)
    at.import_asset_tasks([t]); tex = unreal.load_asset('/Game/UI/Textures/' + name)
    tex.set_editor_property('lod_group', unreal.TextureGroup.TEXTUREGROUP_UI)
    tex.set_editor_property('mip_gen_settings', unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
    tex.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_EDITOR_ICON); tex.set_editor_property('never_stream', True); tex.set_editor_property('srgb', True)
    print('MARKERIMPORT', name, tex.blueprint_get_size_x(), tex.blueprint_get_size_y(), eal.save_loaded_asset(tex, False))
