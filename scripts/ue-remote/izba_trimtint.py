import unreal
at=unreal.AssetToolsHelpers.get_asset_tools(); eal=unreal.EditorAssetLibrary; mel=unreal.MaterialEditingLibrary
print('PIE',unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor())
SRC='E:/game-dev-team/assets/izba_slate/'; DEST='/Game/Environment/Buildings'
mi=unreal.load_asset(DEST+'/MI_IzbaSlate')
print('BEFORE wood',mel.get_material_instance_vector_parameter_value(mi,'WoodTint'),mel.get_material_instance_scalar_parameter_value(mi,'WoodBrightness'))
tt=unreal.AssetImportTask()
for k,v in [('filename',SRC+'T_IzbaSlate_WoodMask.png'),('destination_path',DEST),('destination_name','T_IzbaSlate_WoodMask'),('replace_existing',True),('automated',True),('save',False)]: tt.set_editor_property(k,v)
at.import_asset_tasks([tt])
mask=unreal.load_asset(DEST+'/T_IzbaSlate_WoodMask')
mask.set_editor_property('srgb',False); mask.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_MASKS); mask.modify()
print('MASK srgb',mask.get_editor_property('srgb'),mask.get_editor_property('compression_settings'))
tex=unreal.load_asset(DEST+'/T_IzbaSlate_D'); mat=unreal.load_asset(DEST+'/M_IzbaSlate')
mel.delete_all_material_expressions(mat)
E=lambda c,x,y: mel.create_material_expression(mat,c,x,y)
C=mel.connect_material_expressions
ts=E(unreal.MaterialExpressionTextureSample,-1500,0); ts.set_editor_property('texture',tex)
ms=E(unreal.MaterialExpressionTextureSample,-1500,700); ms.set_editor_property('texture',mask); ms.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
def tint(name,bname,y,dv):
    t=E(unreal.MaterialExpressionVectorParameter,-1500,y); t.set_editor_property('parameter_name',name); t.set_editor_property('default_value',unreal.LinearColor(1,1,1,1))
    b=E(unreal.MaterialExpressionScalarParameter,-1500,y+170); b.set_editor_property('parameter_name',bname); b.set_editor_property('default_value',1.0)
    m1=E(unreal.MaterialExpressionMultiply,-1100,y); m2=E(unreal.MaterialExpressionMultiply,-900,y+50)
    return m2,[C(ts,'RGB',m1,'A'),C(t,'',m1,'B'),C(m1,'',m2,'A'),C(b,'',m2,'B')]
w,ok1=tint('WoodTint','WoodBrightness',200,0); tr,ok2=tint('TrimTint','TrimBrightness',450,0)
l1=E(unreal.MaterialExpressionLinearInterpolate,-600,0); l2=E(unreal.MaterialExpressionLinearInterpolate,-350,0)
ok=ok1+ok2+[C(ts,'RGB',l1,'A'),C(w,'',l1,'B'),C(ms,'R',l1,'Alpha'),C(l1,'',l2,'A'),C(tr,'',l2,'B'),C(ms,'G',l2,'Alpha'),mel.connect_material_property(l2,'',unreal.MaterialProperty.MP_BASE_COLOR)]
r=E(unreal.MaterialExpressionConstant,-350,300); r.set_editor_property('r',0.9); ok.append(mel.connect_material_property(r,'',unreal.MaterialProperty.MP_ROUGHNESS))
s=E(unreal.MaterialExpressionConstant,-350,400); s.set_editor_property('r',0.2); ok.append(mel.connect_material_property(s,'',unreal.MaterialProperty.MP_SPECULAR))
print('CONN',ok)
mel.recompile_material(mat)
mel.set_material_instance_vector_parameter_value(mi,'TrimTint',unreal.LinearColor(1.0,0.72,0.45,1.0))
mel.set_material_instance_scalar_parameter_value(mi,'TrimBrightness',0.9)
mel.update_material_instance(mi)
print('PARAMS v',mel.get_vector_parameter_names(mat),'s',mel.get_scalar_parameter_names(mat))
print('AFTER wood',mel.get_material_instance_vector_parameter_value(mi,'WoodTint'),mel.get_material_instance_scalar_parameter_value(mi,'WoodBrightness'))
print('AFTER trim',mel.get_material_instance_vector_parameter_value(mi,'TrimTint'),mel.get_material_instance_scalar_parameter_value(mi,'TrimBrightness'))
for a in (mask,mat,mi): print('SAVE',a.get_name(),eal.save_loaded_asset(a,False))
