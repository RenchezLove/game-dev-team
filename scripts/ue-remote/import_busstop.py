import unreal
SRC='E:/game-dev-team/assets/bus_stop/'; DEST='/Game/Environment/Props/BusStop'; TEX='T_BusStop_D'; MASK='T_BusStop_Mask'; MAT='M_BusStop'; MI='MI_BusStop'
MESHES=[('SM_BusStop',128),('SM_BusStopSign',32),('SM_BusStopUrn',32)]
ZONES=[('Roof','R',(0.50,0.56,0.60)),('Urn','G',(0.62,0.58,0.50)),('Wall','B',(0.22,0.42,0.62)),('Wood','A',(1,1,1))]
at=unreal.AssetToolsHelpers.get_asset_tools(); eal=unreal.EditorAssetLibrary; mel=unreal.MaterialEditingLibrary
sms=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
print('PIE',unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor())
tasks=[]
for n in (TEX,MASK):
    t=unreal.AssetImportTask()
    for k,v in [('filename',SRC+n+'.png'),('destination_path',DEST),('destination_name',n),('replace_existing',True),('automated',True),('save',False)]: t.set_editor_property(k,v)
    tasks.append(t)
at.import_asset_tasks(tasks)
tex=unreal.load_asset(DEST+'/'+TEX); mask=unreal.load_asset(DEST+'/'+MASK)
mask.set_editor_property('srgb',False); mask.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_MASKS); mask.modify()
mp=DEST+'/'+MAT
mat=unreal.load_asset(mp) if eal.does_asset_exist(mp) else at.create_asset(MAT,DEST,unreal.Material,unreal.MaterialFactoryNew())
mel.delete_all_material_expressions(mat)
E=lambda c,x,y: mel.create_material_expression(mat,c,x,y); C=mel.connect_material_expressions
ts=E(unreal.MaterialExpressionTextureSample,-2200,0); ts.set_editor_property('texture',tex)
ms=E(unreal.MaterialExpressionTextureSample,-2200,1700); ms.set_editor_property('texture',mask); ms.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
ok=[]; prev=(ts,'RGB'); y=300; i=0
for zone,ch,col in ZONES:
    sat=E(unreal.MaterialExpressionScalarParameter,-2200,y); sat.set_editor_property('parameter_name',zone+'Saturation'); sat.set_editor_property('default_value',1.0); sat.set_editor_property('group',zone); sat.set_editor_property('sort_priority',1)
    tint=E(unreal.MaterialExpressionVectorParameter,-2200,y+110); tint.set_editor_property('parameter_name',zone+'Tint'); tint.set_editor_property('default_value',unreal.LinearColor(col[0],col[1],col[2],1)); tint.set_editor_property('group',zone); tint.set_editor_property('sort_priority',0)
    br=E(unreal.MaterialExpressionScalarParameter,-2200,y+290); br.set_editor_property('parameter_name',zone+'Brightness'); br.set_editor_property('default_value',1.0); br.set_editor_property('group',zone); br.set_editor_property('sort_priority',2)
    om=E(unreal.MaterialExpressionOneMinus,-1950,y); des=E(unreal.MaterialExpressionDesaturation,-1750,y)
    m1=E(unreal.MaterialExpressionMultiply,-1550,y+60); m2=E(unreal.MaterialExpressionMultiply,-1350,y+120)
    lp=E(unreal.MaterialExpressionLinearInterpolate,-1100+i*220,0)
    ok+=[C(sat,'',om,''),C(ts,'RGB',des,''),C(om,'',des,'Fraction'),C(des,'',m1,'A'),C(tint,'',m1,'B'),C(m1,'',m2,'A'),C(br,'',m2,'B'),C(prev[0],prev[1],lp,'A'),C(m2,'',lp,'B'),C(ms,ch,lp,'Alpha')]
    prev=(lp,''); y+=380; i+=1
ok.append(mel.connect_material_property(prev[0],'',unreal.MaterialProperty.MP_BASE_COLOR))
r=E(unreal.MaterialExpressionConstant,-300,300); r.set_editor_property('r',0.9); ok.append(mel.connect_material_property(r,'',unreal.MaterialProperty.MP_ROUGHNESS))
s=E(unreal.MaterialExpressionConstant,-300,400); s.set_editor_property('r',0.2); ok.append(mel.connect_material_property(s,'',unreal.MaterialProperty.MP_SPECULAR))
print('CONN all',all(ok),len(ok))
mel.recompile_material(mat)
ip=DEST+'/'+MI
mi=unreal.load_asset(ip) if eal.does_asset_exist(ip) else at.create_asset(MI,DEST,unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
mel.set_material_instance_parent(mi,mat); mel.update_material_instance(mi)
saves=[tex,mask,mat,mi]
for mesh,lm in MESHES:
    ui=unreal.FbxImportUI()
    for k,v in [('import_mesh',True),('import_as_skeletal',False),('import_materials',False),('import_textures',False),('import_animations',False),('mesh_type_to_import',unreal.FBXImportType.FBXIT_STATIC_MESH)]: ui.set_editor_property(k,v)
    d=ui.get_editor_property('static_mesh_import_data')
    for k,v in [('combine_meshes',True),('auto_generate_collision',False),('generate_lightmap_u_vs',False),('remove_degenerates',True),('normal_import_method',unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)]: d.set_editor_property(k,v)
    t=unreal.AssetImportTask()
    for k,v in [('filename',SRC+mesh+'.fbx'),('destination_path',DEST),('destination_name',mesh),('replace_existing',True),('automated',True),('save',False),('options',ui)]: t.set_editor_property(k,v)
    at.import_asset_tasks([t]); print('IMP',list(t.get_editor_property('imported_object_paths')))
    sm=unreal.load_asset(DEST+'/'+mesh)
    for i in range(len(sm.get_editor_property('static_materials'))): sm.set_material(i,mi)
    sm.set_editor_property('light_map_coordinate_index',1); sm.set_editor_property('light_map_resolution',lm)
    ns=sm.get_editor_property('nanite_settings'); ns.enabled=False; sm.set_editor_property('nanite_settings',ns); sm.modify()
    b=sm.get_bounding_box()
    print('NEW',mesh,'min',[round(v) for v in (b.min.x,b.min.y,b.min.z)],'max',[round(v) for v in (b.max.x,b.max.y,b.max.z)],'tris',sm.get_num_triangles(0),'uv',sms.get_num_uv_channels(sm,0),'mats',[x.material_interface.get_name() for x in sm.get_editor_property('static_materials')],'simple collision',sms.get_simple_collision_count(sm),'convex',sms.get_convex_collision_count(sm))
    saves.append(sm)
for a in saves: print('SAVE',a.get_name(),eal.save_loaded_asset(a,False))
