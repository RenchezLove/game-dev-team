import unreal
mel=unreal.MaterialEditingLibrary; eal=unreal.EditorAssetLibrary; at=unreal.AssetToolsHelpers.get_asset_tools()
SRC='/Game/Materials/M_WindTrees'; D='/Game/Materials'; MAT='M_TreesAutumn'; MI='MI_TreesAutumn'; OLD='/Game/Materials/M_TreeAutumn'
MESHES=['/Game/Environment/Nature/SM_Tree_Birch_01','/Game/Environment/Nature/SM_Tree_03']
print('PIE',unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor())
if eal.does_asset_exist(D+'/'+MAT): raise Exception('EXISTS')
mat=eal.duplicate_asset(SRC,D+'/'+MAT)
pw=mel.get_material_property_input_node(mat,unreal.MaterialProperty.MP_BASE_COLOR); vc=mel.get_inputs_for_material_expression(mat,pw)[0]
print('BASE',pw.get_class().get_name(),'<-',vc.get_class().get_name())
E=lambda c,x,y: mel.create_material_expression(mat,c,x,y); ok=[]
def C(a,o,b,i): ok.append(mel.connect_material_expressions(a,o,b,i))
def S(name,val,grp,pri):
    n=E(unreal.MaterialExpressionScalarParameter,-1700,800+pri*100); n.set_editor_property('parameter_name',name); n.set_editor_property('default_value',val); n.set_editor_property('group',grp); n.set_editor_property('sort_priority',pri); return n
def V(name,col,grp,pri):
    n=E(unreal.MaterialExpressionVectorParameter,-1700,1700+pri*200); n.set_editor_property('parameter_name',name); n.set_editor_property('default_value',unreal.LinearColor(col[0],col[1],col[2],1)); n.set_editor_property('group',grp); n.set_editor_property('sort_priority',pri); return n
def K(v,y):
    n=E(unreal.MaterialExpressionConstant,-1400,y); n.set_editor_property('r',v); return n
def M(ch,y):
    n=E(unreal.MaterialExpressionComponentMask,-1250,y)
    for k in 'rgba': n.set_editor_property(k,k==ch)
    return n
def OP(cls,a,b,x,y):
    n=E(cls,x,y); C(a,'',n,'A'); C(b,'',n,'B'); return n
def SAT(a,x,y):
    n=E(unreal.MaterialExpressionSaturate,x,y); C(a,'',n,''); return n
def LERP(a,b,al,x,y):
    n=E(unreal.MaterialExpressionLinearInterpolate,x,y); C(a,'',n,'A'); C(b,'',n,'B'); C(al,'',n,'Alpha'); return n
Mul=unreal.MaterialExpressionMultiply; Sub=unreal.MaterialExpressionSubtract; Add=unreal.MaterialExpressionAdd
G='Autumn trees'
yshare=S('YellowShare',0.3,G,0); rshare=S('RedShare',0.2,G,1)
ycol=V('YellowColor',(0.55,0.36,0.03),G,2); ybr=S('YellowBrightness',1.0,G,3)
rcol=V('RedColor',(0.45,0.08,0.03),G,4); rbr=S('RedBrightness',1.0,G,5)
gcol=V('GreenTint',(1,1,1),G,6); gbr=S('GreenBrightness',1.0,G,7)
eps=K(0.001,300); thr=K(1.5,360); k4=K(4.0,420); k1000=K(1000.0,480)
r_=M('r',-400); g_=M('g',-340); b_=M('b',-280)
for m in (r_,g_,b_): C(vc,'',m,'')
mx=OP(unreal.MaterialExpressionMax,r_,b_,-1100,-380); den=OP(Add,mx,eps,-980,-380); ratio=OP(unreal.MaterialExpressionDivide,g_,den,-860,-360)
crown=SAT(OP(Mul,OP(Sub,ratio,thr,-740,-360),k4,-620,-360),-500,-360)
pir=E(unreal.MaterialExpressionPerInstanceRandom,-1400,900)
isY=SAT(OP(Mul,OP(Sub,yshare,pir,-1150,900),k1000,-1030,900),-910,900)
isA=SAT(OP(Mul,OP(Sub,OP(Add,yshare,rshare,-1270,1050),pir,-1150,1050),k1000,-1030,1050),-910,1050)
isR=OP(Sub,isA,isY,-790,1000)
green=OP(Mul,OP(Mul,pw,gcol,-900,200),gbr,-780,200)
yel=OP(Mul,ycol,ybr,-900,1700); red=OP(Mul,rcol,rbr,-900,2100)
c1=LERP(green,yel,isY,-550,400); c2=LERP(c1,red,isR,-400,400); out=LERP(pw,c2,crown,-200,200)
ok.append(mel.connect_material_property(out,'',unreal.MaterialProperty.MP_BASE_COLOR))
print('CONN all',all(ok),len(ok),[i for i,v in enumerate(ok) if not v])
mel.recompile_material(mat); st=mel.get_statistics(mat); print('STATS ps',st.num_pixel_shader_instructions,'save',eal.save_loaded_asset(mat,False))
mi=at.create_asset(MI,D,unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew()); mel.set_material_instance_parent(mi,mat); mel.update_material_instance(mi); print('MI save',eal.save_loaded_asset(mi,False))
for p in MESHES:
    sm=unreal.load_asset(p); sm.set_material(0,mi); sm.modify(); print('MESH',sm.get_name(),sm.get_material(0).get_name(),'save',eal.save_loaded_asset(sm,False))
print('OLD refs',eal.find_package_referencers_for_asset(OLD,False),'DEL',eal.delete_asset(OLD))
