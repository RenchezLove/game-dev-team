import unreal
sms=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
sm=unreal.load_asset('/Game/Environment/Props/SM_WolfDenCave'); b=sm.get_bounding_box()
print('OLD min',[round(v) for v in (b.min.x,b.min.y,b.min.z)],'max',[round(v) for v in (b.max.x,b.max.y,b.max.z)],'tris',sm.get_num_triangles(0),'mats',[x.material_interface.get_name() for x in sm.get_editor_property('static_materials')],'lm',sm.get_editor_property('light_map_coordinate_index'),sm.get_editor_property('light_map_resolution'),'uv',sms.get_num_uv_channels(sm,0),'simple',sms.get_simple_collision_count(sm),'trace',sm.get_editor_property('body_setup').get_editor_property('collision_trace_flag'))
print('REFS',unreal.EditorAssetLibrary.find_package_referencers_for_asset('/Game/Environment/Props/SM_WolfDenCave',False))
for bpn in ['BP_WolfDen','BP_WolfDen2']:
    bp=unreal.load_asset('/Game/Characters/Wolf/'+bpn); cdo=unreal.get_default_object(bp.generated_class())
    for c in cdo.get_components_by_class(unreal.StaticMeshComponent):
        print(bpn,'CDO',c.get_name(),c.static_mesh.get_name() if c.static_mesh else None,'ovr',[m.get_name() if m else None for m in c.get_editor_property('override_materials')])
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        if c.static_mesh==sm: print('USE',a.get_actor_label(),a.get_class().get_name(),c.get_name(),'relloc',c.get_editor_property('relative_location'),'relrot',c.get_editor_property('relative_rotation'),'scale',c.get_world_scale(),'mob',c.mobility,'ovr',[m.get_name() if m else None for m in c.get_editor_property('override_materials')])
