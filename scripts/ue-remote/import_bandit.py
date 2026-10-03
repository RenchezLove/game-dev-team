import unreal
SRC='E:/game-dev-team/assets/bandit_tripo/'; DEST='/Game/Characters/Bandit'; PREFIX='SK_Bandit_'; TEX='T_BanditTripo_D'; MAT='M_BanditTripo'; MATDIR='/Game/Characters/Bandit'
at=unreal.AssetToolsHelpers.get_asset_tools(); eal=unreal.EditorAssetLibrary; mel=unreal.MaterialEditingLibrary
print('PIE',unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor())
skel=unreal.load_asset('/Game/Characters/Shared/Humanoid/HeadAndSkeletonfbx_Head_Skeleton')
ar=unreal.AssetRegistryHelpers.get_asset_registry()
for s in ['Head','Torso','Legs']:
    d=ar.get_asset_by_object_path('%s/%s%s.%s%s'%(DEST,PREFIX,s,PREFIX,s))
    print('OLD',s,'tris',d.get_tag_value('Triangles') if d.is_valid() else 'NO ASSET')
tt=unreal.AssetImportTask()
for k,v in [('filename',SRC+TEX+'.png'),('destination_path',MATDIR),('destination_name',TEX),('replace_existing',True),('automated',True),('save',False)]: tt.set_editor_property(k,v)
at.import_asset_tasks([tt])
tex=unreal.load_asset(MATDIR+'/'+TEX); tex.set_editor_property('max_texture_size',1024)
mp=MATDIR+'/'+MAT
mat=unreal.load_asset(mp) if eal.does_asset_exist(mp) else at.create_asset(MAT,MATDIR,unreal.Material,unreal.MaterialFactoryNew())
mel.delete_all_material_expressions(mat)
ts=mel.create_material_expression(mat,unreal.MaterialExpressionTextureSample,-400,0); ts.set_editor_property('texture',tex)
r=mel.create_material_expression(mat,unreal.MaterialExpressionConstant,-400,250); r.set_editor_property('r',0.9)
print('CONN',mel.connect_material_property(ts,'RGB',unreal.MaterialProperty.MP_BASE_COLOR),mel.connect_material_property(r,'',unreal.MaterialProperty.MP_ROUGHNESS))
mat.set_editor_property('used_with_skeletal_mesh',True)
mel.recompile_material(mat)
tasks=[]
for s in ['Head','Torso','Legs']:
    ui=unreal.FbxImportUI()
    for k,v in [('import_mesh',True),('import_as_skeletal',True),('mesh_type_to_import',unreal.FBXImportType.FBXIT_SKELETAL_MESH),('skeleton',skel),('import_materials',False),('import_textures',False),('import_animations',False),('create_physics_asset',False),('automated_import_should_detect_type',False)]: ui.set_editor_property(k,v)
    t=unreal.AssetImportTask()
    for k,v in [('filename',SRC+PREFIX+s+'.fbx'),('destination_path',DEST),('destination_name',PREFIX+s),('replace_existing',True),('automated',True),('save',False),('options',ui)]: t.set_editor_property(k,v)
    tasks.append(t)
at.import_asset_tasks(tasks)
for t in tasks: print('IMPORTED',list(t.get_editor_property('imported_object_paths')))
print('SAVE',eal.save_loaded_asset(tex,False),eal.save_loaded_asset(mat,False))
for s in ['Head','Torso','Legs']:
    sk=unreal.load_asset(DEST+'/'+PREFIX+s)
    new=[]
    for x in sk.get_editor_property('materials'):
        y=unreal.SkeletalMaterial(); y.set_editor_property('material_interface',mat); y.set_editor_property('material_slot_name',x.get_editor_property('material_slot_name')); new.append(y)
    sk.set_editor_property('materials',new)
    ok=eal.save_loaded_asset(sk,False)
    b=sk.get_bounds()
    print('NEW',s,'save',ok,'skel',sk.get_editor_property('skeleton').get_name(),'mats',[(str(x.get_editor_property('material_slot_name')),x.get_editor_property('material_interface').get_name()) for x in sk.get_editor_property('materials')],'origin',[round(v) for v in (b.origin.x,b.origin.y,b.origin.z)],'ext',[round(v) for v in (b.box_extent.x,b.box_extent.y,b.box_extent.z)],'phys',sk.get_editor_property('physics_asset').get_name() if sk.get_editor_property('physics_asset') else None)
for s in ['Head','Torso','Legs']:
    d=ar.get_asset_by_object_path('%s/%s%s.%s%s'%(DEST,PREFIX,s,PREFIX,s)); print('TRIS',s,d.get_tag_value('Triangles'))
