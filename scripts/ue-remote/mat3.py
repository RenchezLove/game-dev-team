import unreal
L=unreal.MaterialEditingLibrary
path='/Game/Materials/M_GroundAutumn'
mat=unreal.load_asset(path)
lp=L.get_material_property_input_node(mat,unreal.MaterialProperty.MP_BASE_COLOR)
g2=L.get_inputs_for_material_expression(mat,lp)[0]
g1,gt=L.get_inputs_for_material_expression(mat,g2)[:2]
gm,mc=L.get_inputs_for_material_expression(mat,g1)[:2]
print(g1.get_class().get_name(),gm.get_class().get_name(),mc.get_class().get_name())
x=gm.get_editor_property('material_expression_editor_x'); y=gm.get_editor_property('material_expression_editor_y')
avg=L.create_material_expression(mat,unreal.MaterialExpressionVectorParameter,x,y-250); avg.set_editor_property('parameter_name','GrassAverage'); avg.set_editor_property('default_value',unreal.LinearColor(0.074,0.051,0.014,1))
dc=L.create_material_expression(mat,unreal.MaterialExpressionScalarParameter,x,y-120); dc.set_editor_property('parameter_name','GrassDetailContrast'); dc.set_editor_property('default_value',0.6)
lr=L.create_material_expression(mat,unreal.MaterialExpressionLinearInterpolate,x+150,y-150)
L.connect_material_expressions(avg,'',lr,'A'); L.connect_material_expressions(gm,'',lr,'B'); L.connect_material_expressions(dc,'',lr,'Alpha')
L.connect_material_expressions(lr,'',g1,'A')
for o in unreal.ObjectIterator(unreal.MaterialExpressionScalarParameter):
    if o.get_outer()==mat and o.get_editor_property('parameter_name')=='TileBlendSharpness': o.set_editor_property('default_value',6.0)
L.recompile_material(mat)
print('SAVED',unreal.EditorAssetLibrary.save_asset(path,only_if_is_dirty=False))
