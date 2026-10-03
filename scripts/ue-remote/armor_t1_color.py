import unreal
at=unreal.AssetToolsHelpers.get_asset_tools(); eal=unreal.EditorAssetLibrary; mel=unreal.MaterialEditingLibrary
pie=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor(); print('PIE',pie)
D='/Game/Characters/Shared/Armor'
mat=unreal.load_asset(D+'/M_ArmorT1Tripo'); tex=unreal.load_asset(D+'/T_ArmorT1Tripo_D')
mel.delete_all_material_expressions(mat)
E=lambda c,x,y: mel.create_material_expression(mat,c,x,y); C=mel.connect_material_expressions
ts=E(unreal.MaterialExpressionTextureSample,-1700,0); ts.set_editor_property('texture',tex)
one=E(unreal.MaterialExpressionConstant,-1700,300); one.set_editor_property('r',1.0)
gray=E(unreal.MaterialExpressionDesaturation,-1400,300)
gr=E(unreal.MaterialExpressionComponentMask,-1200,300); gr.set_editor_property('r',True); gr.set_editor_property('g',False); gr.set_editor_property('b',False); gr.set_editor_property('a',False)
thr=E(unreal.MaterialExpressionConstant,-1200,450); thr.set_editor_property('r',0.25)
sub=E(unreal.MaterialExpressionSubtract,-1000,350)
k=E(unreal.MaterialExpressionConstant,-1000,500); k.set_editor_property('r',10.0)
mul=E(unreal.MaterialExpressionMultiply,-850,350)
mask=E(unreal.MaterialExpressionSaturate,-700,350)
satp=E(unreal.MaterialExpressionScalarParameter,-1000,650); satp.set_editor_property('parameter_name','Saturation'); satp.set_editor_property('default_value',1.0)
om=E(unreal.MaterialExpressionOneMinus,-800,650)
frac=E(unreal.MaterialExpressionMultiply,-550,500)
des=E(unreal.MaterialExpressionDesaturation,-350,0)
tint=E(unreal.MaterialExpressionVectorParameter,-800,850); tint.set_editor_property('parameter_name','Tint'); tint.set_editor_property('default_value',unreal.LinearColor(1,1,1,1))
white=E(unreal.MaterialExpressionConstant3Vector,-800,1050); white.set_editor_property('constant',unreal.LinearColor(1,1,1,1))
tl=E(unreal.MaterialExpressionLinearInterpolate,-500,850)
fin=E(unreal.MaterialExpressionMultiply,-150,100)
ok=[C(ts,'RGB',gray,''),C(one,'',gray,'Fraction'),C(gray,'',gr,''),C(thr,'',sub,'A'),C(gr,'',sub,'B'),C(sub,'',mul,'A'),C(k,'',mul,'B'),C(mul,'',mask,''),
    C(satp,'',om,''),C(om,'',frac,'A'),C(mask,'',frac,'B'),C(ts,'RGB',des,''),C(frac,'',des,'Fraction'),
    C(white,'',tl,'A'),C(tint,'',tl,'B'),C(mask,'',tl,'Alpha'),C(des,'',fin,'A'),C(tl,'',fin,'B'),
    mel.connect_material_property(fin,'',unreal.MaterialProperty.MP_BASE_COLOR)]
r=E(unreal.MaterialExpressionConstant,-150,400); r.set_editor_property('r',0.9); ok.append(mel.connect_material_property(r,'',unreal.MaterialProperty.MP_ROUGHNESS))
print('CONN',ok)
mat.set_editor_property('used_with_skeletal_mesh',True)
mel.recompile_material(mat)
print('SAVE mat',eal.save_loaded_asset(mat,False))
for s,sat in [('Head',1.0),('Torso',1.4),('Legs',1.5)]:
    ip=D+'/MI_ArmorT1_'+s
    mi=unreal.load_asset(ip) if eal.does_asset_exist(ip) else at.create_asset('MI_ArmorT1_'+s,D,unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
    mel.set_material_instance_parent(mi,mat)
    mel.set_material_instance_scalar_parameter_value(mi,'Saturation',sat); mel.update_material_instance(mi)
    sk=unreal.load_asset(D+'/SK_Armor_T1_'+s); new=[]
    for x in sk.get_editor_property('materials'):
        y=unreal.SkeletalMaterial(); y.set_editor_property('material_interface',mi); y.set_editor_property('material_slot_name',x.get_editor_property('material_slot_name')); new.append(y)
    sk.set_editor_property('materials',new)
    print(s,'sat',mel.get_material_instance_scalar_parameter_value(mi,'Saturation'),'save',eal.save_loaded_asset(mi,False),eal.save_loaded_asset(sk,False),[x.get_editor_property('material_interface').get_name() for x in sk.get_editor_property('materials')])
