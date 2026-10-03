import unreal
at=unreal.AssetToolsHelpers.get_asset_tools(); eal=unreal.EditorAssetLibrary; mel=unreal.MaterialEditingLibrary
print('PIE',unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor())
SRC='E:/game-dev-team/assets/wolf_tripo/'; D='/Game/Characters/Wolf'
ar=unreal.AssetRegistryHelpers.get_asset_registry()
old=unreal.load_asset(D+'/SK_Wolf'); ob=old.get_bounds()
print('OLD tris',ar.get_asset_by_object_path(D+'/SK_Wolf.SK_Wolf').get_tag_value('Triangles'),'skel',old.get_editor_property('skeleton').get_path_name(),'mats',[x.get_editor_property('material_interface').get_path_name() for x in old.get_editor_property('materials')],'ext',[round(v) for v in (ob.box_extent.x,ob.box_extent.y,ob.box_extent.z)],'phys',old.get_editor_property('physics_asset').get_name() if old.get_editor_property('physics_asset') else None)
skel=old.get_editor_property('skeleton')
tt=unreal.AssetImportTask()
for k,v in [('filename',SRC+'T_WolfTripo_D.png'),('destination_path',D),('destination_name','T_WolfTripo_D'),('replace_existing',True),('automated',True),('save',False)]: tt.set_editor_property(k,v)
at.import_asset_tasks([tt])
tex=unreal.load_asset(D+'/T_WolfTripo_D'); tex.set_editor_property('max_texture_size',1024)
mp=D+'/M_WolfTripo'
mat=unreal.load_asset(mp) if eal.does_asset_exist(mp) else at.create_asset('M_WolfTripo',D,unreal.Material,unreal.MaterialFactoryNew())
mel.delete_all_material_expressions(mat)
ts=mel.create_material_expression(mat,unreal.MaterialExpressionTextureSample,-400,0); ts.set_editor_property('texture',tex)
r=mel.create_material_expression(mat,unreal.MaterialExpressionConstant,-400,250); r.set_editor_property('r',0.9)
print('CONN',mel.connect_material_property(ts,'RGB',unreal.MaterialProperty.MP_BASE_COLOR),mel.connect_material_property(r,'',unreal.MaterialProperty.MP_ROUGHNESS))
mat.set_editor_property('used_with_skeletal_mesh',True); mel.recompile_material(mat)
ui=unreal.FbxImportUI()
for k,v in [('import_mesh',True),('import_as_skeletal',True),('mesh_type_to_import',unreal.FBXImportType.FBXIT_SKELETAL_MESH),('skeleton',skel),('import_materials',False),('import_textures',False),('import_animations',False),('create_physics_asset',False),('automated_import_should_detect_type',False)]: ui.set_editor_property(k,v)
t=unreal.AssetImportTask()
for k,v in [('filename',SRC+'SK_Wolf.fbx'),('destination_path',D),('destination_name','SK_Wolf'),('replace_existing',True),('automated',True),('save',False),('options',ui)]: t.set_editor_property(k,v)
at.import_asset_tasks([t]); print('IMPORTED',list(t.get_editor_property('imported_object_paths')))
sk=unreal.load_asset(D+'/SK_Wolf'); new=[]
for x in sk.get_editor_property('materials'):
    y=unreal.SkeletalMaterial(); y.set_editor_property('material_interface',mat); y.set_editor_property('material_slot_name',x.get_editor_property('material_slot_name')); new.append(y)
sk.set_editor_property('materials',new)
print('SAVE',eal.save_loaded_asset(tex,False),eal.save_loaded_asset(mat,False),eal.save_loaded_asset(sk,False))
b=sk.get_bounds()
print('NEW tris',ar.get_asset_by_object_path(D+'/SK_Wolf.SK_Wolf').get_tag_value('Triangles'),'skel',sk.get_editor_property('skeleton').get_name(),'mats',[x.get_editor_property('material_interface').get_name() for x in sk.get_editor_property('materials')],'ext',[round(v) for v in (b.box_extent.x,b.box_extent.y,b.box_extent.z)])
bp=unreal.load_asset(D+'/BP_Wolf'); cdo=unreal.get_default_object(bp.generated_class()); ch=False
for c in cdo.get_components_by_class(unreal.SkeletalMeshComponent):
    ov=c.get_editor_property('override_materials'); m=c.get_skeletal_mesh_asset()
    print('BP comp',c.get_name(),'mesh',m.get_name() if m else None,'override',[x.get_name() if x else None for x in ov])
    if len(ov): c.modify(); c.set_editor_property('override_materials',[]); ch=True
if ch:
    bp.modify(); unreal.BlueprintEditorLibrary.compile_blueprint(bp); print('BP SAVE',eal.save_loaded_asset(bp,False))
    cdo=unreal.get_default_object(unreal.load_asset(D+'/BP_Wolf').generated_class())
    for c in cdo.get_components_by_class(unreal.SkeletalMeshComponent): print('BP after',c.get_name(),[x.get_name() if x else None for x in c.get_materials()])
