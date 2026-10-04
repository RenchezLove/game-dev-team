import unreal
eal=unreal.EditorAssetLibrary; OLD='/Game/Materials/M_TreeAutumn'
print('exists',eal.does_asset_exist(OLD),'refs',eal.find_package_referencers_for_asset(OLD,False))
if eal.does_asset_exist(OLD): print('DEL',eal.delete_asset(OLD))
mi=unreal.load_asset('/Game/Materials/MI_TreesAutumn'); mel=unreal.MaterialEditingLibrary
print('MI params',[str(x) for x in mel.get_scalar_parameter_names(mi)],[str(x) for x in mel.get_vector_parameter_names(mi)])
