import unreal
eal=unreal.EditorAssetLibrary
sms=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
print('WORLD',w.get_path_name())
print('PIE',unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor())
p='/Game/Environment/Buildings/SM_VillageHouse'
sm=unreal.load_asset(p); b=sm.get_bounding_box()
print('OLD min',b.min,'max',b.max,'tris',sm.get_num_triangles(0),'lods',sm.get_num_lods(),'uv',sms.get_num_uv_channels(sm,0))
print('OLD mats',[(str(m.material_slot_name),m.material_interface.get_path_name() if m.material_interface else None) for m in sm.get_editor_property('static_materials')])
print('OLD lm idx',sm.get_editor_property('light_map_coordinate_index'),'res',sm.get_editor_property('light_map_resolution'))
print('OLD coll simple',sms.get_simple_collision_count(sm),'convex',sms.get_convex_collision_count(sm))
bs=sm.get_editor_property('body_setup')
print('OLD trace flag',bs.get_editor_property('collision_trace_flag') if bs else None)
print('OLD nanite',sm.get_editor_property('nanite_settings').enabled)
n=0
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        if c.static_mesh==sm:
            n+=1
            print('USE',a.get_actor_label(),a.get_class().get_name(),'loc',a.get_actor_location(),'rot',a.get_actor_rotation(),'scale',a.get_actor_scale3d(),'mob',c.mobility,'ovr',[m.get_name() if m else None for m in c.get_editor_property('override_materials')],'lmres',c.get_editor_property('overridden_light_map_res') if c.get_editor_property('override_light_map_res') else '-')
print('USES',n)
print('REFS',eal.find_package_referencers_for_asset(p,False))
