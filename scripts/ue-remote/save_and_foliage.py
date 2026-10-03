import unreal
print('LVL',unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level())
print('ALL',unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True))
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
tot=0
for a in eas.get_all_level_actors():
    for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        sm=c.get_editor_property('static_mesh')
        n=c.get_instance_count(); tot+=n
        mats=[m.get_name() if m else None for m in c.get_materials()]
        print('FOL',sm.get_name() if sm else None,'n',n,'tris',sm.get_num_triangles(0) if sm else 0,'lods',sm.get_num_lods() if sm else 0,'cull',c.get_editor_property('instance_start_cull_distance'),c.get_editor_property('instance_end_cull_distance'),'shadow',c.get_editor_property('cast_shadow'),'mats',mats)
print('FOLTOTAL',tot)
n=0; tris=0
for a in eas.get_all_level_actors():
    if a.get_class().get_name()=='StaticMeshActor':
        c=a.static_mesh_component; sm=c.get_editor_property('static_mesh')
        if sm: n+=1; tris+=sm.get_num_triangles(0)
print('SMA',n,'tris',tris)
for a in eas.get_all_level_actors():
    for c in a.get_components_by_class(unreal.SkeletalMeshComponent):
        print('SK',a.get_actor_label(),c.get_name(),'shadow',c.get_editor_property('cast_shadow'))
