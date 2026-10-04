import unreal
eal=unreal.EditorAssetLibrary; sms=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
for a in unreal.AssetRegistryHelpers.get_asset_registry().get_assets_by_class(unreal.TopLevelAssetPath('/Script/Engine','StaticMesh')):
    if 'tent' in str(a.asset_name).lower():
        sm=a.get_asset(); b=sm.get_bounding_box(); bs=sm.get_editor_property('body_setup')
        print(a.package_name,'tris',sm.get_num_triangles(0),'min',[round(v) for v in (b.min.x,b.min.y,b.min.z)],'max',[round(v) for v in (b.max.x,b.max.y,b.max.z)],'mats',[x.material_interface.get_path_name() if x.material_interface else None for x in sm.get_editor_property('static_materials')],'uv',sms.get_num_uv_channels(sm,0),'trace',bs.get_editor_property('collision_trace_flag'),'simple',sms.get_simple_collision_count(sm),'lm',sm.get_editor_property('light_map_resolution'),sm.get_editor_property('light_map_coordinate_index'))
        print('   REFS',eal.find_package_referencers_for_asset(str(a.package_name),False))
