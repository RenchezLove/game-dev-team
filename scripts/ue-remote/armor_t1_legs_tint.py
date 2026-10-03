import unreal
mel=unreal.MaterialEditingLibrary; eal=unreal.EditorAssetLibrary
mi=unreal.load_asset('/Game/Characters/Shared/Armor/MI_ArmorT1_Legs')
mel.set_material_instance_vector_parameter_value(mi,'Tint',unreal.LinearColor(0.82,0.95,1.25,1.0)); mel.update_material_instance(mi)
print('Legs tint',mel.get_material_instance_vector_parameter_value(mi,'Tint'),'sat',mel.get_material_instance_scalar_parameter_value(mi,'Saturation'),'save',eal.save_loaded_asset(mi,False))
