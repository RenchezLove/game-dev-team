import unreal
ar=unreal.AssetRegistryHelpers.get_asset_registry()
for a in ar.get_assets_by_path('/Game/Environment/Props/LowPolyMarket',recursive=True):
    o=unreal.load_asset(str(a.package_name))
    extra=''
    if isinstance(o,unreal.StaticMesh):
        b=o.get_bounding_box(); s=b.max-b.min
        extra='size %d %d %d tris %d mats %s'%(s.x,s.y,s.z,o.get_num_triangles(0),[m.material_interface.get_path_name() if m.material_interface else None for m in o.get_editor_property('static_materials')])
    print('A',a.package_name,str(a.asset_class_path.asset_name),type(o).__name__,extra)
for p in ['/Game/Environment/Props/SM_BanditCrate','/Game/Environment/Nature/SM_Rock_01','/Game/Environment/Nature/SM_Rock_02','/Game/Environment/Nature/SM_Rock_03']:
    o=unreal.load_asset(p); print('R',p,o.get_num_triangles(0),[m.material_interface.get_path_name() for m in o.get_editor_property('static_materials')])
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
print('PLACED',[a.get_actor_label() for a in eas.get_all_level_actors() if any((c.get_editor_property('static_mesh') and 'LowPolyMarket/SM_' in c.get_editor_property('static_mesh').get_path_name()) for c in a.get_components_by_class(unreal.StaticMeshComponent))])
