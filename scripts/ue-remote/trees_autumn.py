import unreal
mel=unreal.MaterialEditingLibrary; eal=unreal.EditorAssetLibrary
SRC='/Game/Materials/M_WindTrees'; DST='/Game/Materials/M_TreeAutumn'
MESHES=['/Game/Environment/Nature/SM_Tree_Birch_01','/Game/Environment/Nature/SM_Tree_02','/Game/Environment/Nature/SM_Tree_03']
print('PIE',unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor())
if eal.does_asset_exist(DST):
    src=unreal.load_asset(SRC)
    for p in MESHES:
        sm=unreal.load_asset(p)
        for i in range(len(sm.get_editor_property('static_materials'))): sm.set_material(i,src)
        eal.save_loaded_asset(sm,False)
    print('DEL old',eal.delete_asset(DST))
mat=eal.duplicate_asset(SRC,DST)
pw=mel.get_material_property_input_node(mat,unreal.MaterialProperty.MP_BASE_COLOR); print('BASE NODE',pw.get_class().get_name())
E=lambda c,x,y: mel.create_material_expression(mat,c,x,y); C=mel.connect_material_expressions
def S(name,val,pri):
    n=E(unreal.MaterialExpressionScalarParameter,-1500,900+pri*110); n.set_editor_property('parameter_name',name); n.set_editor_property('default_value',val); n.set_editor_property('group','Autumn'); n.set_editor_property('sort_priority',pri); return n
def V(name,col,pri):
    n=E(unreal.MaterialExpressionVectorParameter,-1500,1500+pri*200); n.set_editor_property('parameter_name',name); n.set_editor_property('default_value',unreal.LinearColor(*col)); n.set_editor_property('group','Autumn'); n.set_editor_property('sort_priority',pri); return n
def K(v,y):
    n=E(unreal.MaterialExpressionConstant,-1200,y); n.set_editor_property('r',v); return n
def M(ch,y):
    n=E(unreal.MaterialExpressionComponentMask,-1000,y)
    for k in 'rgba': n.set_editor_property(k,k==ch)
    return n
share=S('AutumnShare',0.5,0); redshare=S('RedShare',0.3,1); strength=S('AutumnStrength',0.8,2); bright=S('AutumnBrightness',2.0,3)
yellow=V('YellowTint',(1.0,0.72,0.12,1),4); red=V('RedTint',(0.85,0.25,0.10,1),5)
zero=K(0.0,700); one=K(1.0,760); k8=K(8.0,820); kh=K(13.37,880)
ok=[]
r_=M('r',300); g_=M('g',360); b_=M('b',420)
mx=E(unreal.MaterialExpressionMax,-800,330); sub=E(unreal.MaterialExpressionSubtract,-650,340); mk=E(unreal.MaterialExpressionMultiply,-500,340); sat=E(unreal.MaterialExpressionSaturate,-350,340)
ok+=[C(pw,'',r_,''),C(pw,'',g_,''),C(pw,'',b_,''),C(r_,'',mx,'A'),C(b_,'',mx,'B'),C(g_,'',sub,'A'),C(mx,'',sub,'B'),C(sub,'',mk,'A'),C(k8,'',mk,'B'),C(mk,'',sat,'')]
pir=E(unreal.MaterialExpressionPerInstanceRandom,-1200,1000)
def STEP(thr,val,y):
    s1=E(unreal.MaterialExpressionSubtract,-950,y); s2=E(unreal.MaterialExpressionMultiply,-850,y); s3=E(unreal.MaterialExpressionSaturate,-750,y)
    ok.extend([C(thr,'',s1,'A'),C(val,'',s1,'B'),C(s1,'',s2,'A'),C(k1000,'',s2,'B'),C(s2,'',s3,'')]); return s3
k1000=K(1000.0,940)
ifa=STEP(share,pir,1000)
mh=E(unreal.MaterialExpressionMultiply,-1000,1200); fr=E(unreal.MaterialExpressionFrac,-900,1200); ok+=[C(pir,'',mh,'A'),C(kh,'',mh,'B'),C(mh,'',fr,'')]
ifr=STEP(redshare,fr,1250)
tint=E(unreal.MaterialExpressionLinearInterpolate,-600,1500); ok+=[C(yellow,'',tint,'A'),C(red,'',tint,'B'),C(ifr,'',tint,'Alpha')]
des=E(unreal.MaterialExpressionDesaturation,-800,600); ok+=[C(pw,'',des,''),C(one,'',des,'Fraction')]
a1=E(unreal.MaterialExpressionMultiply,-450,700); a2=E(unreal.MaterialExpressionMultiply,-300,700); ok+=[C(des,'',a1,'A'),C(tint,'',a1,'B'),C(a1,'',a2,'A'),C(bright,'',a2,'B')]
al1=E(unreal.MaterialExpressionMultiply,-300,400); al2=E(unreal.MaterialExpressionMultiply,-150,400); ok+=[C(sat,'',al1,'A'),C(ifa,'',al1,'B'),C(al1,'',al2,'A'),C(strength,'',al2,'B')]
out=E(unreal.MaterialExpressionLinearInterpolate,0,300); ok+=[C(pw,'',out,'A'),C(a2,'',out,'B'),C(al2,'',out,'Alpha'),mel.connect_material_property(out,'',unreal.MaterialProperty.MP_BASE_COLOR)]
print('CONN all',all(ok),len(ok),[i for i,v in enumerate(ok) if not v])
mel.recompile_material(mat)
st=mel.get_statistics(mat); print('STATS vs',st.num_vertex_shader_instructions,'ps',st.num_pixel_shader_instructions)
so=mel.get_statistics(unreal.load_asset(SRC)); print('OLD   vs',so.num_vertex_shader_instructions,'ps',so.num_pixel_shader_instructions)
print('SAVE mat',eal.save_loaded_asset(mat,False))
for p in MESHES:
    sm=unreal.load_asset(p)
    for i in range(len(sm.get_editor_property('static_materials'))): sm.set_material(i,mat)
    sm.modify(); print('MESH',sm.get_name(),[x.material_interface.get_name() for x in sm.get_editor_property('static_materials')],'save',eal.save_loaded_asset(sm,False))
OLD='/Game/Materials/M_WindTreesAutumn'
if eal.does_asset_exist(OLD): print('REFS old',eal.find_package_referencers_for_asset(OLD,False),'DEL',eal.delete_asset(OLD))
