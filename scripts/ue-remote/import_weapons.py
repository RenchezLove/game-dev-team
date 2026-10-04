import unreal
SRC='E:/game-dev-team/assets/weapons_tripo/'; DEST='/Game/Weapons'; MAT='M_WeaponTripo'
ITEMS=[('SM_Pistol','T_PistolPM_D','MI_PistolPM'),('SM_Knife','T_KnifeTripo_D','MI_KnifeTripo')]
at=unreal.AssetToolsHelpers.get_asset_tools(); eal=unreal.EditorAssetLibrary; mel=unreal.MaterialEditingLibrary
sms=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
print('PIE',unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor())
def box(sm):
    b=sm.get_bounding_box(); return [round(v,1) for v in (b.min.x,b.min.y,b.min.z,b.max.x,b.max.y,b.max.z)]
mp=DEST+'/'+MAT
mat=unreal.load_asset(mp) if eal.does_asset_exist(mp) else at.create_asset(MAT,DEST,unreal.Material,unreal.MaterialFactoryNew())
mel.delete_all_material_expressions(mat)
E=lambda c,x,y: mel.create_material_expression(mat,c,x,y); C=mel.connect_material_expressions
ts=E(unreal.MaterialExpressionTextureSampleParameter2D,-900,0); ts.set_editor_property('parameter_name','Diffuse')
tint=E(unreal.MaterialExpressionVectorParameter,-900,300); tint.set_editor_property('parameter_name','Tint'); tint.set_editor_property('default_value',unreal.LinearColor(1,1,1,1))
br=E(unreal.MaterialExpressionScalarParameter,-900,500); br.set_editor_property('parameter_name','Brightness'); br.set_editor_property('default_value',1.0)
ro=E(unreal.MaterialExpressionScalarParameter,-900,600); ro.set_editor_property('parameter_name','Roughness'); ro.set_editor_property('default_value',0.6)
m1=E(unreal.MaterialExpressionMultiply,-600,100); m2=E(unreal.MaterialExpressionMultiply,-400,200)
ok=[C(ts,'RGB',m1,'A'),C(tint,'',m1,'B'),C(m1,'',m2,'A'),C(br,'',m2,'B'),mel.connect_material_property(m2,'',unreal.MaterialProperty.MP_BASE_COLOR),mel.connect_material_property(ro,'',unreal.MaterialProperty.MP_ROUGHNESS)]
saves=[mat]
for mesh,texn,min_ in ITEMS:
    old=unreal.load_asset(DEST+'/'+mesh); trace=old.get_editor_property('body_setup').get_editor_property('collision_trace_flag')
    print('OLD',mesh,box(old),'tris',old.get_num_triangles(0),'trace',trace)
    t=unreal.AssetImportTask()
    for k,v in [('filename',SRC+texn+'.png'),('destination_path',DEST),('destination_name',texn),('replace_existing',True),('automated',True),('save',False)]: t.set_editor_property(k,v)
    at.import_asset_tasks([t]); tex=unreal.load_asset(DEST+'/'+texn)
    if mesh=='SM_Pistol': ts.set_editor_property('texture',tex); mel.recompile_material(mat)
    ip=DEST+'/'+min_
    mi=unreal.load_asset(ip) if eal.does_asset_exist(ip) else at.create_asset(min_,DEST,unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
    mel.set_material_instance_parent(mi,mat); print('TEXSET',mel.set_material_instance_texture_parameter_value(mi,'Diffuse',tex)); mel.update_material_instance(mi)
    ui=unreal.FbxImportUI()
    for k,v in [('import_mesh',True),('import_as_skeletal',False),('import_materials',False),('import_textures',False),('import_animations',False),('mesh_type_to_import',unreal.FBXImportType.FBXIT_STATIC_MESH)]: ui.set_editor_property(k,v)
    d=ui.get_editor_property('static_mesh_import_data')
    for k,v in [('combine_meshes',True),('auto_generate_collision',False),('generate_lightmap_u_vs',False),('remove_degenerates',True),('normal_import_method',unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)]: d.set_editor_property(k,v)
    t=unreal.AssetImportTask()
    for k,v in [('filename',SRC+mesh+'.fbx'),('destination_path',DEST),('destination_name',mesh),('replace_existing',True),('automated',True),('save',False),('options',ui)]: t.set_editor_property(k,v)
    at.import_asset_tasks([t]); print('IMP',list(t.get_editor_property('imported_object_paths')))
    sm=unreal.load_asset(DEST+'/'+mesh)
    for i in range(len(sm.get_editor_property('static_materials'))): sm.set_material(i,mi)
    sm.get_editor_property('body_setup').set_editor_property('collision_trace_flag',trace)
    ns=sm.get_editor_property('nanite_settings'); ns.enabled=False; sm.set_editor_property('nanite_settings',ns); sm.modify()
    print('NEW',mesh,box(sm),'tris',sm.get_num_triangles(0),'uv',sms.get_num_uv_channels(sm,0),'mats',[x.material_interface.get_name() for x in sm.get_editor_property('static_materials')])
    saves+=[tex,mi,sm]
print('CONN all',all(ok),len(ok))
for a in saves: print('SAVE',a.get_name(),eal.save_loaded_asset(a,False))
