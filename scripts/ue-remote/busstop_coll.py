import unreal
SRC='E:/game-dev-team/assets/bus_stop/'; DEST='/Game/Environment/Props/BusStop'
at=unreal.AssetToolsHelpers.get_asset_tools(); eal=unreal.EditorAssetLibrary; sms=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
mi=unreal.load_asset(DEST+'/MI_BusStop')
for mesh,lm in [('SM_BusStop',128),('SM_BusStopUrn',32)]:
    ui=unreal.FbxImportUI()
    for k,v in [('import_mesh',True),('import_as_skeletal',False),('import_materials',False),('import_textures',False),('import_animations',False),('mesh_type_to_import',unreal.FBXImportType.FBXIT_STATIC_MESH)]: ui.set_editor_property(k,v)
    d=ui.get_editor_property('static_mesh_import_data')
    for k,v in [('combine_meshes',False),('auto_generate_collision',False),('one_convex_hull_per_ucx',True),('generate_lightmap_u_vs',False),('remove_degenerates',True),('normal_import_method',unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)]: d.set_editor_property(k,v)
    t=unreal.AssetImportTask()
    for k,v in [('filename',SRC+mesh+'.fbx'),('destination_path',DEST),('destination_name',mesh),('replace_existing',True),('automated',True),('save',False),('options',ui)]: t.set_editor_property(k,v)
    at.import_asset_tasks([t]); print('IMP',list(t.get_editor_property('imported_object_paths')))
    sm=unreal.load_asset(DEST+'/'+mesh)
    for i in range(len(sm.get_editor_property('static_materials'))): sm.set_material(i,mi)
    sm.set_editor_property('light_map_coordinate_index',1); sm.set_editor_property('light_map_resolution',lm); sm.modify()
    b=sm.get_bounding_box()
    print(mesh,'min',[round(v) for v in (b.min.x,b.min.y,b.min.z)],'max',[round(v) for v in (b.max.x,b.max.y,b.max.z)],'tris',sm.get_num_triangles(0),'simple',sms.get_simple_collision_count(sm),'convex',sms.get_convex_collision_count(sm),'trace',sm.get_editor_property('body_setup').get_editor_property('collision_trace_flag'),'save',eal.save_loaded_asset(sm,False))
print([str(a) for a in eal.list_assets(DEST)])
