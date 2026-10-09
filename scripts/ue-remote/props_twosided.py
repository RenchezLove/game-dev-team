import unreal
# Временная мера до правки сеток моделлером: приборы рисуются с обеих сторон (у осциллографа нет дна, Ринат положил его набок).
for p in ('/Game/Environment/Props/ScientistBase/MI_Oscilloscope', '/Game/Environment/Props/ScientistBase/MI_Radio'):
    mi = unreal.load_asset(p)
    o = mi.get_editor_property('base_property_overrides')
    o.set_editor_property('override_two_sided', True); o.set_editor_property('two_sided', True)
    mi.set_editor_property('base_property_overrides', o)
    unreal.MaterialEditingLibrary.update_material_instance(mi)
    print(p, 'two_sided', mi.get_editor_property('base_property_overrides').get_editor_property('two_sided'), 'SAVE', unreal.EditorAssetLibrary.save_loaded_asset(mi, False))
