import unreal
at=unreal.AssetToolsHelpers.get_asset_tools(); eal=unreal.EditorAssetLibrary
sms=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
SRC='E:/ContrarySurvior/ContrarySurvivor/Content/LowPolyMarket/Meshes/'
NEW='/Game/Environment/Props/LowPolyMarket'
MOVE={'/Game/LowPolyMarket/Materials/Props/MI_Prop_01':'MI_Prop_01','/Game/LowPolyMarket/Materials/M_Prop_Master':'M_Prop_Master','/Game/LowPolyMarket/Textures/T_PropColorMap':'T_PropColorMap','/Game/LowPolyMarket/Materials/Rocks/MI_Rock_01':'MI_Rock_01','/Game/LowPolyMarket/Materials/M_Rock_Master':'M_Rock_Master','/Game/LowPolyMarket/Materials/MF_SnowCoverage':'MF_SnowCoverage','/Game/LowPolyMarket/Data/MPC_GlobalSettings':'MPC_GlobalSettings','/Game/LowPolyMarket/Meshes/SM_Box_01':'SM_Box_01','/Game/LowPolyMarket/Meshes/SM_Table_01':'SM_Table_01','/Game/LowPolyMarket/Meshes/SM_Table_02':'SM_Table_02','/Game/LowPolyMarket/Meshes/SM_Bench_01':'SM_Bench_01'}
for o,n in MOVE.items():
    if eal.does_asset_exist(o) and not eal.does_asset_exist(NEW+'/'+n): print('MOVE',n,eal.rename_asset(o,NEW+'/'+n))
def imp(fbx,dest,name,scale,tz):
    ui=unreal.FbxImportUI()
    ui.set_editor_property('import_mesh',True); ui.set_editor_property('import_as_skeletal',False); ui.set_editor_property('import_materials',False); ui.set_editor_property('import_textures',False); ui.set_editor_property('import_animations',False)
    ui.set_editor_property('mesh_type_to_import',unreal.FBXImportType.FBXIT_STATIC_MESH)
    d=ui.get_editor_property('static_mesh_import_data')
    d.set_editor_property('combine_meshes',True); d.set_editor_property('import_uniform_scale',scale); d.set_editor_property('import_translation',unreal.Vector(0,0,tz))
    d.set_editor_property('auto_generate_collision',False); d.set_editor_property('generate_lightmap_u_vs',True); d.set_editor_property('remove_degenerates',True)
    t=unreal.AssetImportTask()
    for k,v in [('filename',SRC+fbx),('destination_path',dest),('destination_name',name),('replace_existing',True),('automated',True),('save',False),('options',ui)]: t.set_editor_property(k,v)
    at.import_asset_tasks([t])
    return list(t.get_editor_property('imported_object_paths'))
def box(p):
    sm=unreal.load_asset(p); b=sm.get_bounding_box(); return sm,b
JOBS=[('SM_Crate_01.fbx','/Game/Environment/Props','SM_BanditCrate',74.0,0.0,'MI_Prop_01',32,'box'),
      ('SM_Rock_Scatter_03.fbx','/Game/Environment/Nature','SM_Rock_01',55.0,0.08,'MI_Rock_01',16,'hull'),
      ('SM_Rock_02.fbx','/Game/Environment/Nature','SM_Rock_02',95.0,0.08,'MI_Rock_01',16,'hull'),
      ('SM_Rock_01.fbx','/Game/Environment/Nature','SM_Rock_03',136.0,0.08,'MI_Rock_01',16,'hull')]
for fbx,dest,name,width,sink,mat,lm,col in JOBS:
    p=dest+'/'+name
    print('IMP1',name,imp(fbx,dest,name,1.0,0.0))
    sm,b=box(p); s=b.max-b.min; w=max(s.x,s.y)
    k=width/w
    tz=-(b.min.z*k)-sink*(s.z*k)
    print('   pass1 size',[round(s.x),round(s.y),round(s.z)],'minz',round(b.min.z,1),'-> scale',round(k,3),'tz',round(tz,1))
    print('IMP2',name,imp(fbx,dest,name,k,tz))
    sm,b=box(p); s=b.max-b.min
    if abs(max(s.x,s.y)-width)>2:
        k2=k*width/max(s.x,s.y); print('   retry scale',k2); imp(fbx,dest,name,k2,tz); sm,b=box(p); s=b.max-b.min
    want=-sink*s.z
    if abs(b.min.z-want)>1.5:
        tz2=tz+(want-b.min.z); print('   retry tz',tz2,'minz was',b.min.z); imp(fbx,dest,name,max(s.x,s.y) and (k if abs(max(s.x,s.y)-width)<=2 else k2),tz2); sm,b=box(p); s=b.max-b.min
    m=unreal.load_asset(NEW+'/'+mat)
    for i in range(len(sm.get_editor_property('static_materials'))): sm.set_material(i,m)
    sms.set_generate_lightmap_uv(sm,True)
    sm.set_editor_property('light_map_coordinate_index',1); sm.set_editor_property('light_map_resolution',lm)
    sms.remove_collisions(sm)
    sms.add_simple_collisions(sm,unreal.ScriptCollisionShapeType.BOX if col=='box' else unreal.ScriptCollisionShapeType.NDOP10_Z)
    sm.modify(); print('   SAVE',eal.save_loaded_asset(sm,False))
    print('RESULT',name,'size',[round(s.x),round(s.y),round(s.z)],'minz',round(b.min.z,1),'tris',sm.get_num_triangles(0),'lods',sm.get_num_lods(),'uv',sms.get_num_uv_channels(sm,0),'slots',len(sm.get_editor_property('static_materials')),'nanite',sm.get_editor_property('nanite_settings').enabled)
print('ALL',unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True))
