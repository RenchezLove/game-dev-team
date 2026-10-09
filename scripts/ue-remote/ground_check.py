import unreal
mel = unreal.MaterialEditingLibrary
mi = unreal.load_asset('/Game/Materials/MI_GroundAutumn')
for n in ('GrassTint', 'GrassMacroLight', 'GrassMacroDark'):
    v = mel.get_material_instance_vector_parameter_value(mi, n)
    print(n, [round(x, 3) for x in (v.r, v.g, v.b)])
print('overrides', [(str(p.parameter_info.name), [round(x, 3) for x in (p.parameter_value.r, p.parameter_value.g, p.parameter_value.b)]) for p in mi.get_editor_property('vector_parameter_values')])
print('parent', mi.get_editor_property('parent').get_name())
