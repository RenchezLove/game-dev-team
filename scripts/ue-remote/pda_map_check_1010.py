import unreal
tex = unreal.load_asset('/Game/UI/Textures/T_PdaMap')
print('MAP', tex.blueprint_get_size_x(), tex.blueprint_get_size_y(), tex.get_editor_property('max_texture_size'), tex.get_editor_property('lod_group'))
