import unreal
at=unreal.AssetToolsHelpers.get_asset_tools(); eal=unreal.EditorAssetLibrary; mel=unreal.MaterialEditingLibrary
print('PIE',unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor())
SRC='E:/game-dev-team/assets/izba_slate/'; DEST='/Game/Environment/Buildings'
tt=unreal.AssetImportTask()
for k,v in [('filename',SRC+'T_IzbaSlate_WoodMask.png'),('destination_path',DEST),('destination_name','T_IzbaSlate_WoodMask'),('replace_existing',True),('automated',True),('save',False)]: tt.set_editor_property(k,v)
at.import_asset_tasks([tt])
mask=unreal.load_asset(DEST+'/T_IzbaSlate_WoodMask')
mask.set_editor_property('srgb',False); mask.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_MASKS)
mask.modify()
tex=unreal.load_asset(DEST+'/T_IzbaSlate_D')
mat=unreal.load_asset(DEST+'/M_IzbaSlate')
mel.delete_all_material_expressions(mat)
E=lambda c,x,y: mel.create_material_expression(mat,c,x,y)
ts=E(unreal.MaterialExpressionTextureSample,-1100,0); ts.set_editor_property('texture',tex)
ms=E(unreal.MaterialExpressionTextureSample,-1100,500); ms.set_editor_property('texture',mask); ms.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
wt=E(unreal.MaterialExpressionVectorParameter,-1100,250); wt.set_editor_property('parameter_name','WoodTint'); wt.set_editor_property('default_value',unreal.LinearColor(1,1,1,1))
wb=E(unreal.MaterialExpressionScalarParameter,-1100,420); wb.set_editor_property('parameter_name','WoodBrightness'); wb.set_editor_property('default_value',1.0)
m1=E(unreal.MaterialExpressionMultiply,-750,150); m2=E(unreal.MaterialExpressionMultiply,-550,200)
lp=E(unreal.MaterialExpressionLinearInterpolate,-300,0)
ok=[mel.connect_material_expressions(ts,'RGB',m1,'A'),mel.connect_material_expressions(wt,'',m1,'B'),
    mel.connect_material_expressions(m1,'',m2,'A'),mel.connect_material_expressions(wb,'',m2,'B'),
    mel.connect_material_expressions(ts,'RGB',lp,'A'),mel.connect_material_expressions(m2,'',lp,'B'),mel.connect_material_expressions(ms,'R',lp,'Alpha'),
    mel.connect_material_property(lp,'',unreal.MaterialProperty.MP_BASE_COLOR)]
r=E(unreal.MaterialExpressionConstant,-300,300); r.set_editor_property('r',0.9); ok.append(mel.connect_material_property(r,'',unreal.MaterialProperty.MP_ROUGHNESS))
s=E(unreal.MaterialExpressionConstant,-300,400); s.set_editor_property('r',0.2); ok.append(mel.connect_material_property(s,'',unreal.MaterialProperty.MP_SPECULAR))
print('CONN',ok)
mel.recompile_material(mat)
ip=DEST+'/MI_IzbaSlate'
mi=unreal.load_asset(ip) if eal.does_asset_exist(ip) else at.create_asset('MI_IzbaSlate',DEST,unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
mel.set_material_instance_parent(mi,mat)
print('SETV',mel.set_material_instance_vector_parameter_value(mi,'WoodTint',unreal.LinearColor(1.0,0.78,0.55,1.0)))
print('SETS',mel.set_material_instance_scalar_parameter_value(mi,'WoodBrightness',1.2))
mel.update_material_instance(mi)
sm=unreal.load_asset(DEST+'/SM_VillageHouse')
for i in range(len(sm.get_editor_property('static_materials'))): sm.set_material(i,mi)
sm.modify()
print('MATS',[m.material_interface.get_path_name() for m in sm.get_editor_property('static_materials')])
print('PARAMS v',mel.get_vector_parameter_names(mat),'s',mel.get_scalar_parameter_names(mat))
print('MI v',mel.get_material_instance_vector_parameter_value(mi,'WoodTint'),'s',mel.get_material_instance_scalar_parameter_value(mi,'WoodBrightness'))
for a in (mask,mat,mi,sm): print('SAVE',a.get_name(),eal.save_loaded_asset(a,False))
