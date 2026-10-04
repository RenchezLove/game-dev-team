import unreal
mel=unreal.MaterialEditingLibrary
m=unreal.load_asset('/Game/Materials/M_WindTrees')
for p in ['MP_BASE_COLOR','MP_ROUGHNESS','MP_SPECULAR','MP_WORLD_POSITION_OFFSET','MP_EMISSIVE_COLOR']:
    n=mel.get_material_property_input_node(m,getattr(unreal.MaterialProperty,p))
    print(p,n.get_class().get_name() if n else None,n.get_name() if n else '',mel.get_material_property_input_node_output_name(m,getattr(unreal.MaterialProperty,p)) if n else '')
    if n:
        for i in mel.get_inputs_for_material_expression(m,n): print('     in',i.get_class().get_name() if i else None)
print('usage foliage',m.get_editor_property('used_with_instanced_static_meshes'))
g=unreal.load_asset('/Game/Materials/M_GrassWind'); print('grass params',[str(x) for x in mel.get_scalar_parameter_names(g)],[str(x) for x in mel.get_vector_parameter_names(g)])
