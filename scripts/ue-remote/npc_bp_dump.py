import unreal
for bp in ['/Game/Characters/Trader/BP_Trader','/Game/Characters/Elder/BP_Elder']:
    cls=unreal.load_asset(bp).generated_class(); cdo=unreal.get_default_object(cls)
    print('BP',bp,'parent',cls.get_super_class().get_name() if hasattr(cls,'get_super_class') else '')
    for c in cdo.get_components_by_class(unreal.SkeletalMeshComponent):
        sk=c.get_skeletal_mesh_asset()
        print('  CDO comp',c.get_name(),'mesh',sk.get_path_name() if sk else None,'override',[m.get_name() if m else None for m in c.get_editor_property('override_materials')])
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    n=a.get_class().get_name()
    if 'Trader' in n or 'Elder' in n:
        for c in a.get_components_by_class(unreal.SkeletalMeshComponent):
            sk=c.get_skeletal_mesh_asset()
            print('LEVEL',a.get_actor_label(),n,c.get_name(),'mesh',sk.get_name() if sk else None,'override',[m.get_name() if m else None for m in c.get_editor_property('override_materials')],'mats',[m.get_name() if m else None for m in c.get_materials()])
