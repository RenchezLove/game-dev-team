import unreal
L=unreal.MaterialEditingLibrary; EA=unreal.EditorAssetLibrary
dst='/Game/Materials/M_GroundAutumn'
if not EA.does_asset_exist(dst): EA.duplicate_asset('/Game/Materials/M_GroundBlend_WIP',dst)
mat=unreal.load_asset(dst)
lp=L.get_material_property_input_node(mat,unreal.MaterialProperty.MP_BASE_COLOR)
ins=L.get_inputs_for_material_expression(mat,lp)
g,d=ins[0],ins[1]
g.set_editor_property('texture',unreal.load_asset('/Game/Materials/Textures/Autumn/T_GroundGrassAutumn'))
d.set_editor_property('texture',unreal.load_asset('/Game/Materials/Textures/Autumn/T_GroundDirtAutumn'))
X=lp.get_editor_property('material_expression_editor_x'); Y=lp.get_editor_property('material_expression_editor_y')
def ex(cls,x,y): return L.create_material_expression(mat,cls,X+x,Y+y)
def vp(name,val,x,y):
    e=ex(unreal.MaterialExpressionVectorParameter,x,y); e.set_editor_property('parameter_name',name); e.set_editor_property('default_value',val); return e
def sp(name,val,x,y):
    e=ex(unreal.MaterialExpressionScalarParameter,x,y); e.set_editor_property('parameter_name',name); e.set_editor_property('default_value',val); return e
wp=ex(unreal.MaterialExpressionWorldPosition,-1400,-600)
mk=ex(unreal.MaterialExpressionComponentMask,-1200,-600); mk.set_editor_property('r',True); mk.set_editor_property('g',True); mk.set_editor_property('b',False); mk.set_editor_property('a',False)
L.connect_material_expressions(wp,'',mk,'')
ms=sp('MacroTiling',0.0003,-1200,-500)
mm=ex(unreal.MaterialExpressionMultiply,-1000,-600); L.connect_material_expressions(mk,'',mm,'A'); L.connect_material_expressions(ms,'',mm,'B')
mt=ex(unreal.MaterialExpressionTextureSample,-800,-600); mt.set_editor_property('texture',unreal.load_asset('/Game/Materials/Textures/Autumn/T_GroundMacroMask')); mt.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_GRAYSCALE)
L.connect_material_expressions(mm,'',mt,'UVs')
dk=vp('GrassMacroDark',unreal.LinearColor(0.8,0.85,0.75,1),-800,-400)
lt=vp('GrassMacroLight',unreal.LinearColor(1.2,1.1,0.9,1),-800,-300)
ml=ex(unreal.MaterialExpressionLinearInterpolate,-550,-500); L.connect_material_expressions(dk,'',ml,'A'); L.connect_material_expressions(lt,'',ml,'B'); L.connect_material_expressions(mt,'R',ml,'Alpha')
gt=vp('GrassTint',unreal.LinearColor(1,1,1,1),-550,-350)
g1=ex(unreal.MaterialExpressionMultiply,-350,-450); L.connect_material_expressions(g,'RGB',g1,'A'); L.connect_material_expressions(ml,'',g1,'B')
g2=ex(unreal.MaterialExpressionMultiply,-200,-400); L.connect_material_expressions(g1,'',g2,'A'); L.connect_material_expressions(gt,'',g2,'B')
L.connect_material_expressions(g2,'',lp,'A')
dt=vp('DirtTint',unreal.LinearColor(1,1,1,1),-550,200)
d1=ex(unreal.MaterialExpressionMultiply,-200,150); L.connect_material_expressions(d,'RGB',d1,'A'); L.connect_material_expressions(dt,'',d1,'B')
L.connect_material_expressions(d1,'',lp,'B')
rg=sp('Roughness',0.95,-200,400); L.connect_material_property(rg,'',unreal.MaterialProperty.MP_ROUGHNESS)
L.recompile_material(mat)
print('SAVED',EA.save_asset(dst,only_if_is_dirty=False))
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for x in eas.get_all_level_actors():
    if x.get_actor_label()=='GroundPlane':
        x.static_mesh_component.set_material(0,mat); print('GROUND',x.static_mesh_component.get_material(0).get_path_name())
print('LVL',unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level())
