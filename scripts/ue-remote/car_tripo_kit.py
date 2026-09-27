import unreal
D='/Game/Environment/Props/AbandonedCar'
SRC='E:/game-dev-team/assets/abandoned_car_tripo/'
at=unreal.AssetToolsHelpers.get_asset_tools(); mel=unreal.MaterialEditingLibrary; eal=unreal.EditorAssetLibrary
def imp(f,name):
    t=unreal.AssetImportTask()
    for k,v in [('filename',SRC+f),('destination_path',D),('destination_name',name),('replace_existing',True),('automated',True),('save',True)]: t.set_editor_property(k,v)
    at.import_asset_tasks([t]); return list(t.get_editor_property('imported_object_paths'))
print('TEX',imp('T_AbandonedCarTripo_D.png','T_AbandonedCarTripo_D'))
tex=unreal.load_asset(D+'/T_AbandonedCarTripo_D')
mp=D+'/M_CarTripo'
if eal.does_asset_exist(mp): eal.delete_asset(mp)
m=at.create_asset('M_CarTripo',D,unreal.Material,unreal.MaterialFactoryNew())
ts=mel.create_material_expression(m,unreal.MaterialExpressionTextureSampleParameter2D,-700,0); ts.set_editor_property('parameter_name','Diffuse'); ts.set_editor_property('texture',tex)
pc=mel.create_material_expression(m,unreal.MaterialExpressionVectorParameter,-700,300); pc.set_editor_property('parameter_name','BodyColor'); pc.set_editor_property('default_value',unreal.LinearColor(0.212,0.296,0.456,1))
one=mel.create_material_expression(m,unreal.MaterialExpressionConstant3Vector,-450,300); one.set_editor_property('constant',unreal.LinearColor(1,1,1,1))
lp=mel.create_material_expression(m,unreal.MaterialExpressionLinearInterpolate,-300,200)
mel.connect_material_expressions(one,'',lp,'A'); mel.connect_material_expressions(pc,'',lp,'B'); mel.connect_material_expressions(ts,'A',lp,'Alpha')
mu=mel.create_material_expression(m,unreal.MaterialExpressionMultiply,-150,0)
mel.connect_material_expressions(ts,'RGB',mu,'A'); mel.connect_material_expressions(lp,'',mu,'B')
mel.connect_material_property(mu,'',unreal.MaterialProperty.MP_BASE_COLOR)
r=mel.create_material_expression(m,unreal.MaterialExpressionConstant,-150,250); r.set_editor_property('r',0.8)
mel.connect_material_property(r,'',unreal.MaterialProperty.MP_ROUGHNESS)
mel.recompile_material(m); eal.save_loaded_asset(m)
glass=unreal.load_asset(D+'/M_CarGlass')
parts=['Body','Glass','Door_FL','Door_FR','Door_RL','Door_RR','Hood','Trunk','Wheel']
for p in parts:
    print('IMP',p,imp('SM_AbandonedCar_%s.fbx'%p,'SM_AbandonedCar_'+p))
    sm=unreal.load_asset(D+'/SM_AbandonedCar_'+p)
    for i in range(len(sm.get_editor_property('static_materials'))): sm.set_material(i,glass if p=='Glass' else m)
    if p=='Body':
        ag=sm.get_editor_property('body_setup').get_editor_property('agg_geom')
        if len(ag.get_editor_property('convex_elems'))+len(ag.get_editor_property('box_elems'))==0:
            unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem).add_simple_collisions(sm,unreal.ScriptCollisionShapeType.BOX)
        ag=sm.get_editor_property('body_setup').get_editor_property('agg_geom')
        print('  BODY collision convex',len(ag.get_editor_property('convex_elems')),'box',len(ag.get_editor_property('box_elems')))
    sm.modify(); eal.save_loaded_asset(sm,False)
    b=sm.get_bounding_box(); print('  tris',sm.get_num_triangles(0),'size',[round(x,1) for x in (b.max-b.min).to_tuple()],'slots',len(sm.get_editor_property('static_materials')))
for x in eal.list_assets('/Game/Environment/Props/AbandonedCar',recursive=False):
    if 'M_CarTripo' in x and 'Glass' in x: print('EXTRA',x)
