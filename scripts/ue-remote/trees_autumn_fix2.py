import unreal
mel=unreal.MaterialEditingLibrary; eal=unreal.EditorAssetLibrary
sm=unreal.load_asset('/Game/Environment/Nature/SM_Tree_02'); old=unreal.load_asset('/Game/Materials/M_WindTrees')
sm.set_material(0,old); sm.modify(); print('TREE_02',sm.get_material(0).get_name(),'save',eal.save_loaded_asset(sm,False))
mat=unreal.load_asset('/Game/Materials/M_TreeAutumn')
out=mel.get_material_property_input_node(mat,unreal.MaterialProperty.MP_BASE_COLOR)
pw,a2,al2=mel.get_inputs_for_material_expression(mat,out)
a1,bright=mel.get_inputs_for_material_expression(mat,a2)
print('PARAM',bright.get_editor_property('parameter_name'),'was',bright.get_editor_property('default_value'))
bright.set_editor_property('default_value',5.0)
mel.recompile_material(mat); print('now',mel.get_material_default_scalar_parameter_value(mat,'AutumnBrightness'),'share',mel.get_material_default_scalar_parameter_value(mat,'AutumnShare'),'save',eal.save_loaded_asset(mat,False))
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.InstancedFoliageActor):
    for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        if 'Tree' in c.static_mesh.get_name(): print(c.static_mesh.get_name(),c.get_material(0).get_name())
