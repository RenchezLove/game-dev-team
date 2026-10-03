import unreal
at=unreal.AssetToolsHelpers.get_asset_tools(); eal=unreal.EditorAssetLibrary; mel=unreal.MaterialEditingLibrary
print('PIE',unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor())
D='/Game/Characters/Bandit'
tt=unreal.AssetImportTask()
for k,v in [('filename','E:/game-dev-team/assets/bandit_tripo/T_BanditTripo_Mask.png'),('destination_path',D),('destination_name','T_BanditTripo_Mask'),('replace_existing',True),('automated',True),('save',False)]: tt.set_editor_property(k,v)
at.import_asset_tasks([tt])
mask=unreal.load_asset(D+'/T_BanditTripo_Mask'); mask.set_editor_property('srgb',False); mask.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_MASKS); mask.modify()
print('MASK',mask.blueprint_get_size_x(),mask.get_editor_property('srgb'),mask.get_editor_property('compression_settings'))
tex=unreal.load_asset(D+'/T_BanditTripo_D'); mat=unreal.load_asset(D+'/M_BanditTripo')
mel.delete_all_material_expressions(mat)
E=lambda c,x,y: mel.create_material_expression(mat,c,x,y); C=mel.connect_material_expressions
ts=E(unreal.MaterialExpressionTextureSample,-2200,0); ts.set_editor_property('texture',tex)
ms=E(unreal.MaterialExpressionTextureSample,-2200,1700); ms.set_editor_property('texture',mask); ms.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
ok=[]; prev=(ts,'RGB'); y=300; i=0
for zone,ch in [('Jacket','R'),('Shirt','G'),('Pants','B'),('Stripe','A')]:
    sat=E(unreal.MaterialExpressionScalarParameter,-2200,y); sat.set_editor_property('parameter_name',zone+'Saturation'); sat.set_editor_property('default_value',1.0); sat.set_editor_property('group',zone); sat.set_editor_property('sort_priority',1)
    tint=E(unreal.MaterialExpressionVectorParameter,-2200,y+110); tint.set_editor_property('parameter_name',zone+'Tint'); tint.set_editor_property('default_value',unreal.LinearColor(1,1,1,1)); tint.set_editor_property('group',zone); tint.set_editor_property('sort_priority',0)
    br=E(unreal.MaterialExpressionScalarParameter,-2200,y+290); br.set_editor_property('parameter_name',zone+'Brightness'); br.set_editor_property('default_value',1.0); br.set_editor_property('group',zone); br.set_editor_property('sort_priority',2)
    om=E(unreal.MaterialExpressionOneMinus,-1950,y); des=E(unreal.MaterialExpressionDesaturation,-1750,y)
    m1=E(unreal.MaterialExpressionMultiply,-1550,y+60); m2=E(unreal.MaterialExpressionMultiply,-1350,y+120)
    lp=E(unreal.MaterialExpressionLinearInterpolate,-1100+i*220,0)
    ok+=[C(sat,'',om,''),C(ts,'RGB',des,''),C(om,'',des,'Fraction'),C(des,'',m1,'A'),C(tint,'',m1,'B'),C(m1,'',m2,'A'),C(br,'',m2,'B'),
         C(prev[0],prev[1],lp,'A'),C(m2,'',lp,'B'),C(ms,ch,lp,'Alpha')]
    prev=(lp,''); y+=380; i+=1
ok.append(mel.connect_material_property(prev[0],'',unreal.MaterialProperty.MP_BASE_COLOR))
r=E(unreal.MaterialExpressionConstant,-300,300); r.set_editor_property('r',0.9); ok.append(mel.connect_material_property(r,'',unreal.MaterialProperty.MP_ROUGHNESS))
print('CONN all',all(ok),len(ok),[i for i,v in enumerate(ok) if not v])
mat.set_editor_property('used_with_skeletal_mesh',True); mel.recompile_material(mat)
ip=D+'/MI_Bandit'
mi=unreal.load_asset(ip) if eal.does_asset_exist(ip) else at.create_asset('MI_Bandit',D,unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
mel.set_material_instance_parent(mi,mat); mel.update_material_instance(mi)
print('SAVE',eal.save_loaded_asset(mask,False),eal.save_loaded_asset(mat,False),eal.save_loaded_asset(mi,False))
for s in ['Head','Torso','Legs']:
    sk=unreal.load_asset(D+'/SK_Bandit_'+s); new=[]
    for x in sk.get_editor_property('materials'):
        y2=unreal.SkeletalMaterial(); y2.set_editor_property('material_interface',mi); y2.set_editor_property('material_slot_name',x.get_editor_property('material_slot_name')); new.append(y2)
    sk.set_editor_property('materials',new); print(s,eal.save_loaded_asset(sk,False),[x.get_editor_property('material_interface').get_name() for x in sk.get_editor_property('materials')])
print('PARAMS',[str(x) for x in mel.get_scalar_parameter_names(mat)],[str(x) for x in mel.get_vector_parameter_names(mat)])
cdo=unreal.get_default_object(unreal.load_asset(D+'/BP_EnemyBandit').generated_class())
for c in cdo.get_components_by_class(unreal.SkeletalMeshComponent): print('BP',c.get_name(),[x.get_name() if x else None for x in c.get_materials()])
