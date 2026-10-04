import unreal
mel=unreal.MaterialEditingLibrary
seen=set()
for n in ['SM_Tree_Birch_01','SM_Tree_02','SM_Tree_03','SM_Tree_Pine_01','SM_Tree_Pine_02','SM_Bush']:
    ad=[a for a in unreal.AssetRegistryHelpers.get_asset_registry().get_assets_by_class(unreal.TopLevelAssetPath('/Script/Engine','StaticMesh')) if str(a.asset_name)==n]
    for a in ad:
        sm=a.get_asset(); print(a.package_name,'tris',sm.get_num_triangles(0),'vcol?')
        for s in sm.get_editor_property('static_materials'):
            m=s.material_interface; print('   slot',s.material_slot_name,'->',m.get_path_name() if m else None)
            if m and m.get_path_name() not in seen:
                seen.add(m.get_path_name()); base=m.get_base_material()
                print('      base',base.get_path_name(),'two_sided',base.get_editor_property('two_sided'),'scalars',[str(x) for x in mel.get_scalar_parameter_names(m)],'vectors',[str(x) for x in mel.get_vector_parameter_names(m)],'tex',[str(x) for x in mel.get_texture_parameter_names(m)],'nexpr',mel.get_num_material_expressions(base))
