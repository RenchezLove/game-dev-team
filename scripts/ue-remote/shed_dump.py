import unreal
sms=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
ar=unreal.AssetRegistryHelpers.get_asset_registry()
for a in ar.get_assets_by_path('/Game',recursive=True):
    if 'Shed' in str(a.asset_name): print('ASSET',a.package_name,a.asset_class_path.asset_name)
p='/Game/Environment/Props/SM_BanditShed'
if not unreal.EditorAssetLibrary.does_asset_exist(p):
    print('NO',p)
else:
    sm=unreal.load_asset(p); b=sm.get_bounding_box()
    print('OLD min',[round(v) for v in (b.min.x,b.min.y,b.min.z)],'max',[round(v) for v in (b.max.x,b.max.y,b.max.z)],'tris',sm.get_num_triangles(0),'mats',[x.material_interface.get_name() for x in sm.get_editor_property('static_materials')],'lm',sm.get_editor_property('light_map_coordinate_index'),sm.get_editor_property('light_map_resolution'),'uv',sms.get_num_uv_channels(sm,0),'simple',sms.get_simple_collision_count(sm),'trace',sm.get_editor_property('body_setup').get_editor_property('collision_trace_flag'))
    print('REFS',unreal.EditorAssetLibrary.find_package_referencers_for_asset(p,False))
    for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            if c.static_mesh==sm: print('USE',a.get_actor_label(),a.get_class().get_name(),c.get_name(),'scale',c.get_world_scale(),'mob',c.mobility,'ovr',[m.get_name() if m else None for m in c.get_editor_property('override_materials')])
