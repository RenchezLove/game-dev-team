import unreal
mel=unreal.MaterialEditingLibrary
m=unreal.load_asset('/Game/Characters/Shared/M_CorpseDissolve')
print('blend',m.get_editor_property('blend_mode'),'scalars',[str(x) for x in mel.get_scalar_parameter_names(m)],'vectors',[str(x) for x in mel.get_vector_parameter_names(m)],'textures',[str(x) for x in mel.get_texture_parameter_names(m)])
print('BASE node',mel.get_material_property_input_node(m,unreal.MaterialProperty.MP_BASE_COLOR))
print('OPMASK node',mel.get_material_property_input_node(m,unreal.MaterialProperty.MP_OPACITY_MASK))
print('NUM expr',mel.get_num_material_expressions(m))
