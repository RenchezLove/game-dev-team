import unreal
mel=unreal.MaterialEditingLibrary; eal=unreal.EditorAssetLibrary
D='/Game/Environment/Props/LowPolyMarket/'
print('PIE',unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor())
m=unreal.load_asset(D+'M_Prop_Master')
mi=unreal.load_asset(D+'MI_Prop_01')
if 'Tint' in [str(s) for s in mel.get_vector_parameter_names(mi)]:
    print('ALREADY')
else:
    node=mel.get_material_property_input_node(m,unreal.MaterialProperty.MP_BASE_COLOR)
    out=mel.get_material_property_input_node_output_name(m,unreal.MaterialProperty.MP_BASE_COLOR)
    print('BASE INPUT',node.get_class().get_name() if node else None,repr(out))
    tint=mel.create_material_expression(m,unreal.MaterialExpressionVectorParameter,-300,-500)
    tint.set_editor_property('parameter_name','Tint'); tint.set_editor_property('default_value',unreal.LinearColor(1,1,1,1))
    mu=mel.create_material_expression(m,unreal.MaterialExpressionMultiply,-100,-400)
    print('C1',mel.connect_material_expressions(node,out,mu,'A'))
    print('C2',mel.connect_material_expressions(tint,'',mu,'B'))
    print('C3',mel.connect_material_property(mu,'',unreal.MaterialProperty.MP_BASE_COLOR))
    mel.recompile_material(m)
    print('SAVE M',eal.save_loaded_asset(m,False))
print('VEC',[str(s) for s in mel.get_vector_parameter_names(mi)])
print('NOW',mel.get_material_property_input_node(m,unreal.MaterialProperty.MP_BASE_COLOR).get_class().get_name())
