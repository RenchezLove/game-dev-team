import unreal
ar=unreal.AssetRegistryHelpers.get_asset_registry()
eal=unreal.EditorAssetLibrary
sms=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
def info(p):
    sm=unreal.load_asset(p)
    if not isinstance(sm,unreal.StaticMesh): return
    b=sm.get_bounding_box(); s=b.max-b.min
    ag=sm.get_editor_property('body_setup').get_editor_property('agg_geom')
    col=len(ag.get_editor_property('convex_elems'))+len(ag.get_editor_property('box_elems'))+len(ag.get_editor_property('sphere_elems'))
    mats=[m.material_interface.get_path_name() if m.material_interface else None for m in sm.get_editor_property('static_materials')]
    print('SM',p,'size',[round(x) for x in (s.x,s.y,s.z)],'minz',round(b.min.z,1),'ctr',[round((b.min.x+b.max.x)/2),round((b.min.y+b.max.y)/2)],'tris',sm.get_num_triangles(0),'lods',sm.get_num_lods(),'uv',sms.get_num_uv_channels(sm,0),'lmres',sm.get_editor_property('light_map_resolution'),'lmidx',sm.get_editor_property('light_map_coordinate_index'),'col',col,'nanite',sm.get_editor_property('nanite_settings').enabled,'mats',mats)
for n in ['Box_01','Crate_01','Rock_01','Rock_02','Rock_03','Rock_Scatter_01','Rock_Scatter_02','Rock_Scatter_03','Table_01','Table_02','Bench_01']:
    info('/Game/LowPolyMarket/Meshes/SM_'+n)
print('--- OURS')
for a in ar.get_assets_by_path('/Game',recursive=True):
    n=str(a.asset_name); pk=str(a.package_name)
    if pk.startswith('/Game/LowPolyMarket') or pk.startswith('/Game/AnimStarterPack'): continue
    cls=str(a.asset_class_path.asset_name)
    if cls=='StaticMesh' and any(k in n for k in ('Crate','Box','Rock','Stone','Table','Bench')):
        info(pk)
        print('   REFS',[str(r) for r in ar.get_referencers(a.package_name,unreal.AssetRegistryDependencyOptions())])
print('--- MATS')
for p in ['/Game/LowPolyMarket/Materials/Props/MI_Prop_01','/Game/LowPolyMarket/Materials/Rocks/MI_Rock_01','/Game/LowPolyMarket/Materials/M_Prop_Master','/Game/LowPolyMarket/Materials/M_Rock_Master']:
    def deps(pk,seen):
        for d in ar.get_dependencies(pk,unreal.AssetRegistryDependencyOptions()):
            d=str(d)
            if d.startswith('/Game') and d not in seen: seen.add(d); deps(d,seen)
        return seen
    print('DEPS',p,sorted(deps(p,set())))
print('--- ANIM')
for a in ar.get_assets_by_path('/Game',recursive=True):
    cls=str(a.asset_class_path.asset_name)
    if cls in ('Skeleton','IKRigDefinition','IKRetargeter','AnimBlueprint'):
        print(cls,a.package_name)
for a in ar.get_assets_by_path('/Game/Characters',recursive=True):
    if str(a.asset_class_path.asset_name)=='AnimSequence':
        an=unreal.load_asset(str(a.package_name))
        print('ANIM',a.package_name,'skel',an.get_editor_property('skeleton').get_name(),'len',round(an.get_play_length(),2))
for p in ['/Game/AnimStarterPack/Idle_Pistol','/Game/AnimStarterPack/Equip_Pistol_Standing','/Game/AnimStarterPack/Reload_Pistol']:
    an=unreal.load_asset(p); print('PACKANIM',p,'len',round(an.get_play_length(),2),'skel',an.get_editor_property('skeleton').get_path_name())
