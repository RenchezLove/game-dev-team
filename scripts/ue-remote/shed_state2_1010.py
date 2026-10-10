import unreal, re
mel = unreal.MaterialEditingLibrary
mi = unreal.load_asset('/Game/Environment/Props/MI_BanditShed')
par = mi.get_editor_property('parent'); print('PARENT', par.get_path_name())
print('S', [(str(x.parameter_info.name), round(x.parameter_value, 3)) for x in mi.get_editor_property('scalar_parameter_values')])
print('V', [(str(x.parameter_info.name), [round(v, 3) for v in (x.parameter_value.r, x.parameter_value.g, x.parameter_value.b)]) for x in mi.get_editor_property('vector_parameter_values')])
print('T', [(str(x.parameter_info.name), x.parameter_value.get_name()) for x in mi.get_editor_property('texture_parameter_values')])
base = par
while isinstance(base, unreal.MaterialInstance): base = base.get_editor_property('parent')
print('BASE', base.get_path_name(), 'vec', mel.get_vector_parameter_names(base), 'sc', mel.get_scalar_parameter_names(base))
for n in mel.get_vector_parameter_names(base): print('   def', n, mel.get_material_default_vector_parameter_value(base, n))
for p in ['/Game/Environment/Props/SM_BanditShed', '/Game/Environment/Buildings/SM_Shed']:
    sm = unreal.load_asset(p); b = sm.get_bounding_box()
    txt = sm.get_editor_property('body_setup').get_editor_property('agg_geom').export_text()
    print(p, 'min', [round(v) for v in (b.min.x, b.min.y, b.min.z)], 'max', [round(v) for v in (b.max.x, b.max.y, b.max.z)], 'tris', sm.get_num_triangles(0), 'coll', txt[:300])
