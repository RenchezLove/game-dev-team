import unreal
mel=unreal.MaterialEditingLibrary
D='/Game/Environment/Props/LowPolyMarket/'
for n in ('MI_Prop_01','MI_Rock_01'):
    mi=unreal.load_asset(D+n)
    print(n,'parent',mi.get_editor_property('parent').get_name())
    for s in mel.get_scalar_parameter_names(mi): print('   scalar',s,mel.get_material_instance_scalar_parameter_value(mi,s))
    for s in mel.get_vector_parameter_names(mi): print('   vector',s,mel.get_material_instance_vector_parameter_value(mi,s))
    for s in mel.get_texture_parameter_names(mi):
        t=mel.get_material_instance_texture_parameter_value(mi,s); print('   texture',s,t.get_name() if t else None)
    for s in mel.get_static_switch_parameter_names(mi): print('   switch',s,mel.get_material_instance_static_switch_parameter_value(mi,s))
