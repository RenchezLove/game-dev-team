import unreal
D='/Game/Environment/Props/Tripo'
at=unreal.AssetToolsHelpers.get_asset_tools()
def imp(src,name):
    t=unreal.AssetImportTask()
    t.set_editor_property('filename',src); t.set_editor_property('destination_path',D)
    t.set_editor_property('destination_name',name); t.set_editor_property('replace_existing',True)
    t.set_editor_property('automated',True); t.set_editor_property('save',True)
    at.import_asset_tasks([t]); print('IMPORTED',list(t.get_editor_property('imported_object_paths')))
imp('E:/game-dev-team/assets/barrel_tripo/T_TripoBarrel_D.png','T_TripoBarrel_D')
imp('E:/game-dev-team/assets/barrel_tripo/SM_TripoBarrel.fbx','SM_TripoBarrel')
tex=unreal.load_asset(D+'/T_TripoBarrel_D')
mel=unreal.MaterialEditingLibrary
mp=D+'/M_TripoBarrelPaint'
if unreal.EditorAssetLibrary.does_asset_exist(mp): unreal.EditorAssetLibrary.delete_asset(mp)
m=at.create_asset('M_TripoBarrelPaint',D,unreal.Material,unreal.MaterialFactoryNew())
ts=mel.create_material_expression(m,unreal.MaterialExpressionTextureSampleParameter2D,-700,0)
ts.set_editor_property('parameter_name','Diffuse'); ts.set_editor_property('texture',tex)
pc=mel.create_material_expression(m,unreal.MaterialExpressionVectorParameter,-700,300)
pc.set_editor_property('parameter_name','PaintColor'); pc.set_editor_property('default_value',unreal.LinearColor(1,1,1,1))
one=mel.create_material_expression(m,unreal.MaterialExpressionConstant3Vector,-450,300)
one.set_editor_property('constant',unreal.LinearColor(1,1,1,1))
lp=mel.create_material_expression(m,unreal.MaterialExpressionLinearInterpolate,-300,200)
mel.connect_material_expressions(one,'',lp,'A'); mel.connect_material_expressions(pc,'',lp,'B'); mel.connect_material_expressions(ts,'A',lp,'Alpha')
mu=mel.create_material_expression(m,unreal.MaterialExpressionMultiply,-150,0)
mel.connect_material_expressions(ts,'RGB',mu,'A'); mel.connect_material_expressions(lp,'',mu,'B')
mel.connect_material_property(mu,'',unreal.MaterialProperty.MP_BASE_COLOR)
r=mel.create_material_expression(m,unreal.MaterialExpressionConstant,-150,250); r.set_editor_property('r',0.85)
mel.connect_material_property(r,'',unreal.MaterialProperty.MP_ROUGHNESS)
mel.recompile_material(m); unreal.EditorAssetLibrary.save_loaded_asset(m)
COL={'Grey':(0.25,0.30,0.36),'Blue':(0.20,0.36,0.66),'Green':(0.07,0.13,0.04),'Red':(0.45,0.04,0.03),'Yellow':(0.80,0.42,0.03)}
mis={}
for k,c in COL.items():
    p=D+'/MI_TripoBarrel_'+k
    mi=unreal.load_asset(p) if unreal.EditorAssetLibrary.does_asset_exist(p) else at.create_asset('MI_TripoBarrel_'+k,D,unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
    mel.set_material_instance_parent(mi,m)
    mel.set_material_instance_vector_parameter_value(mi,'PaintColor',unreal.LinearColor(c[0],c[1],c[2],1))
    unreal.EditorAssetLibrary.save_loaded_asset(mi); mis[k]=mi
sm=unreal.load_asset(D+'/SM_TripoBarrel')
sm.set_material(0,mis['Grey']); unreal.EditorAssetLibrary.save_loaded_asset(sm)
b=sm.get_bounding_box(); print('SM tris',sm.get_num_triangles(0),'size',b.max-b.min,'min',b.min,'slots',len(sm.get_editor_property('static_materials')))
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
base=None
for x in eas.get_all_level_actors():
    l=x.get_actor_label()
    if l.startswith('TripoBarrel_'): eas.destroy_actor(x); continue
    if isinstance(x,unreal.StaticMeshActor) and x.static_mesh_component.static_mesh==sm and base is None: base=x
print('BASE',base.get_actor_label() if base else None, base.get_actor_location() if base else None)
if base:
    L=base.get_actor_location(); i=0
    for k in ['Blue','Green','Red','Yellow']:
        i+=1
        a=eas.spawn_actor_from_object(sm,unreal.Vector(L.x-90*i,L.y,L.z),unreal.Rotator(0,0,0))
        a.set_actor_label('TripoBarrel_'+k); a.static_mesh_component.set_material(0,mis[k])
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level(); print('SAVED')
