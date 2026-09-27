import unreal
skel=unreal.load_asset('/Game/Characters/Shared/Humanoid/HeadAndSkeletonfbx_Head_Skeleton')
tasks=[]
for s in ['Head','Torso','Legs']:
    ui=unreal.FbxImportUI()
    ui.set_editor_property('import_mesh',True)
    ui.set_editor_property('import_as_skeletal',True)
    ui.set_editor_property('mesh_type_to_import',unreal.FBXImportType.FBXIT_SKELETAL_MESH)
    ui.set_editor_property('skeleton',skel)
    ui.set_editor_property('import_materials',s=='Head')
    ui.set_editor_property('import_textures',s=='Head')
    ui.set_editor_property('import_animations',False)
    ui.set_editor_property('create_physics_asset',False)
    ui.set_editor_property('automated_import_should_detect_type',False)
    t=unreal.AssetImportTask()
    t.set_editor_property('filename','E:/game-dev-team/assets/hero_tripo/SK_Cloth_T0_%s.fbx'%s)
    t.set_editor_property('destination_path','/Game/Characters/Shared/Clothing')
    t.set_editor_property('destination_name','SK_Cloth_T0_'+s)
    t.set_editor_property('replace_existing',True)
    t.set_editor_property('automated',True)
    t.set_editor_property('save',True)
    t.set_editor_property('options',ui)
    tasks.append(t)
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
for t in tasks: print('IMPORTED',list(t.get_editor_property('imported_object_paths')))
mat=None
for p in unreal.EditorAssetLibrary.list_assets('/Game/Characters/Shared/Clothing',recursive=False):
    if 'HeroTripo' in p: print('NEW',p)
    a=unreal.load_asset(p)
    if isinstance(a,unreal.Texture2D) and 'HeroTripo' in p:
        a.set_editor_property('max_texture_size',1024); unreal.EditorAssetLibrary.save_loaded_asset(a); print('TEX1024',p)
    if isinstance(a,unreal.MaterialInterface) and 'HeroTripo' in p: mat=a
ar=unreal.AssetRegistryHelpers.get_asset_registry()
for s in ['Head','Torso','Legs']:
    m=unreal.load_asset('/Game/Characters/Shared/Clothing/SK_Cloth_T0_'+s)
    if mat:
        ms=m.get_editor_property('materials')
        for x in ms: x.set_editor_property('material_interface',mat)
        m.set_editor_property('materials',ms)
        unreal.EditorAssetLibrary.save_loaded_asset(m)
    d=ar.get_asset_by_object_path(m.get_path_name())
    print(s,'skel',m.get_editor_property('skeleton').get_name(),'tris',d.get_tag_value('Triangles'),'mats',[x.get_editor_property('material_interface').get_name() for x in m.get_editor_property('materials')])
