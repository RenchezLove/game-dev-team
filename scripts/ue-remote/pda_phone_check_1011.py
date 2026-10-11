import unreal
eal = unreal.EditorAssetLibrary
# Как у принятой картинки карты: без сжатия с потерями (чёткие края и прозрачность).
for name in ['T_PdaPhone', 'T_PdaButtonIcon']:
    tex = unreal.load_asset('/Game/UI/Textures/' + name)
    tex.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_EDITOR_ICON)
    print('PHONESAVE', name, eal.save_loaded_asset(tex, False))
for name in ['T_PdaMap', 'T_PdaPhone', 'T_PdaButtonIcon']:
    tex = unreal.load_asset('/Game/UI/Textures/' + name)
    print('PHONECHECK', name, tex.blueprint_get_size_x(), tex.blueprint_get_size_y(), tex.get_editor_property('lod_group'), tex.get_editor_property('compression_settings'), tex.get_editor_property('srgb'))
