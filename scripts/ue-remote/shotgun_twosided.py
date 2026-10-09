import unreal
# Временная мера до правки сетки моделлером: материал ружья рисует грани с обеих сторон (тонкие детали не пропадают).
mi = unreal.load_asset('/Game/Weapons/Shotgun/MI_Shotgun_TOZ34')
o = mi.get_editor_property('base_property_overrides')
o.set_editor_property('override_two_sided', True); o.set_editor_property('two_sided', True)
mi.set_editor_property('base_property_overrides', o)
unreal.MaterialEditingLibrary.update_material_instance(mi)
print('two_sided', mi.get_editor_property('base_property_overrides').get_editor_property('two_sided'), 'SAVE', unreal.EditorAssetLibrary.save_loaded_asset(mi, False))
