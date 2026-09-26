import unreal
L=unreal.MaterialEditingLibrary; EA=unreal.EditorAssetLibrary
path='/Game/Materials/M_GroundAutumn'
mat=unreal.load_asset(path)
lp=L.get_material_property_input_node(mat,unreal.MaterialProperty.MP_BASE_COLOR)
old=L.get_inputs_for_material_expression(mat,lp)[:2]
dead=set()
def collect(x):
    if not x or x.get_name() in dead: return
    dead.add(x.get_name())
    for i in L.get_inputs_for_material_expression(mat,x): collect(i)
    todel.append(x)
todel=[]
for o in old: collect(o)
for x in todel: L.delete_material_expression(mat,x)
print('DELETED',len(todel))
X=lp.get_editor_property('material_expression_editor_x'); Y=lp.get_editor_property('material_expression_editor_y')
def ex(cls,x,y): return L.create_material_expression(mat,cls,X+x,Y+y)
def sp(n,v,x,y):
    e=ex(unreal.MaterialExpressionScalarParameter,x,y); e.set_editor_property('parameter_name',n); e.set_editor_property('default_value',v); return e
def vp(n,v,x,y):
    e=ex(unreal.MaterialExpressionVectorParameter,x,y); e.set_editor_property('parameter_name',n); e.set_editor_property('default_value',v); return e
def mul(a,b,x,y,ao='',bo=''):
    m=ex(unreal.MaterialExpressionMultiply,x,y); L.connect_material_expressions(a,ao,m,'A'); L.connect_material_expressions(b,bo,m,'B'); return m
def lerp(a,b,al,x,y,alo=''):
    m=ex(unreal.MaterialExpressionLinearInterpolate,x,y); L.connect_material_expressions(a,'',m,'A'); L.connect_material_expressions(b,'',m,'B'); L.connect_material_expressions(al,alo,m,'Alpha'); return m
def tex(t,uv,x,y,gray=False):
    s=ex(unreal.MaterialExpressionTextureSample,x,y); s.set_editor_property('texture',unreal.load_asset(t))
    if gray: s.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_GRAYSCALE)
    L.connect_material_expressions(uv,'',s,'UVs'); return s
wp=ex(unreal.MaterialExpressionWorldPosition,-2200,0)
mr=ex(unreal.MaterialExpressionComponentMask,-2000,-60); [mr.set_editor_property(k,v) for k,v in [('r',True),('g',False),('b',False),('a',False)]]
mg=ex(unreal.MaterialExpressionComponentMask,-2000,60); [mg.set_editor_property(k,v) for k,v in [('r',False),('g',True),('b',False),('a',False)]]
L.connect_material_expressions(wp,'',mr,''); L.connect_material_expressions(wp,'',mg,'')
xy=ex(unreal.MaterialExpressionAppendVector,-1850,-100); L.connect_material_expressions(mr,'',xy,'A'); L.connect_material_expressions(mg,'',xy,'B')
yx=ex(unreal.MaterialExpressionAppendVector,-1850,100); L.connect_material_expressions(mg,'',yx,'A'); L.connect_material_expressions(mr,'',yx,'B')
t1=sp('GrassTiling',0.0025,-1850,-250); t2=sp('GrassTiling2',0.00071,-1850,250)
uv1=mul(xy,t1,-1650,-150); uv2=mul(yx,t2,-1650,150)
mt=sp('MacroTiling',0.0003,-1850,450); mt2=sp('MacroTiling2',0.00011,-1850,600)
uvm=mul(xy,mt,-1650,450); uvm2=mul(yx,mt2,-1650,600)
M=tex('/Game/Materials/Textures/Autumn/T_GroundMacroMask',uvm,-1450,450,True)
M2=tex('/Game/Materials/Textures/Autumn/T_GroundMacroMask',uvm2,-1450,650,True)
bs=sp('TileBlendSharpness',3.0,-1450,850)
c05=ex(unreal.MaterialExpressionConstant,-1300,900); c05.set_editor_property('r',0.5)
sub=ex(unreal.MaterialExpressionSubtract,-1250,500); L.connect_material_expressions(M,'R',sub,'A'); L.connect_material_expressions(c05,'',sub,'B')
sh=mul(sub,bs,-1100,500)
add=ex(unreal.MaterialExpressionAdd,-950,500); L.connect_material_expressions(sh,'',add,'A'); L.connect_material_expressions(c05,'',add,'B')
al=ex(unreal.MaterialExpressionSaturate,-800,500); L.connect_material_expressions(add,'',al,'')
GA=tex('/Game/Materials/Textures/Autumn/T_GroundGrassAutumn',uv1,-1450,-500); GB=tex('/Game/Materials/Textures/Autumn/T_GroundGrassAutumn',uv2,-1450,-250)
DA=tex('/Game/Materials/Textures/Autumn/T_GroundDirtAutumn',uv1,-1450,-50); DB=tex('/Game/Materials/Textures/Autumn/T_GroundDirtAutumn',uv2,-1450,200)
gm=lerp(GA,GB,al,-650,-400); dm=lerp(DA,DB,al,-650,100)
dk=vp('GrassMacroDark',unreal.LinearColor(0.8,0.85,0.75,1),-650,650); lt=vp('GrassMacroLight',unreal.LinearColor(1.2,1.1,0.9,1),-650,800)
mc=lerp(dk,lt,M2,-450,650,'R')
gt=vp('GrassTint',unreal.LinearColor(0.75,1.2,0.55,1),-450,-250)
g1=mul(gm,mc,-300,-400); g2=mul(g1,gt,-150,-350)
dt=vp('DirtTint',unreal.LinearColor(1,1,1,1),-450,250)
d1=mul(dm,dt,-150,100)
L.connect_material_expressions(g2,'',lp,'A'); L.connect_material_expressions(d1,'',lp,'B')
L.recompile_material(mat)
print('SAVED',EA.save_asset(path,only_if_is_dirty=False),'N',L.get_num_material_expressions(mat))
