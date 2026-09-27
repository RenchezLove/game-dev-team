import unreal
at=unreal.AssetToolsHelpers.get_asset_tools()
d='/Game/Characters/Shared/Clothing'
t=unreal.AssetImportTask()
t.set_editor_property('filename','E:/game-dev-team/assets/hero_tripo/T_HeroTripo_D.png')
t.set_editor_property('destination_path',d)
t.set_editor_property('destination_name','T_HeroTripo_D')
t.set_editor_property('replace_existing',True)
t.set_editor_property('automated',True)
t.set_editor_property('save',True)
at.import_asset_tasks([t])
tex=unreal.load_asset(d+'/T_HeroTripo_D')
tex.set_editor_property('max_texture_size',1024)
unreal.EditorAssetLibrary.save_loaded_asset(tex)
mp=d+'/M_HeroTripo'
if unreal.EditorAssetLibrary.does_asset_exist(mp):
    m=unreal.load_asset(mp)
else:
    m=at.create_asset('M_HeroTripo',d,unreal.Material,unreal.MaterialFactoryNew())
mel=unreal.MaterialEditingLibrary
mel.delete_all_material_expressions(m)
s=mel.create_material_expression(m,unreal.MaterialExpressionTextureSample,-400,0)
s.set_editor_property('texture',tex)
mel.connect_material_property(s,'RGB',unreal.MaterialProperty.MP_BASE_COLOR)
r=mel.create_material_expression(m,unreal.MaterialExpressionConstant,-400,250)
r.set_editor_property('r',0.9)
mel.connect_material_property(r,'',unreal.MaterialProperty.MP_ROUGHNESS)
m.set_editor_property('used_with_skeletal_mesh',True)
mel.recompile_material(m)
unreal.EditorAssetLibrary.save_loaded_asset(m)
for s2 in ['Head','Torso','Legs']:
    sk=unreal.load_asset(d+'/SK_Cloth_T0_'+s2)
    ms=sk.get_editor_property('materials')
    for x in ms: x.set_editor_property('material_interface',m)
    sk.set_editor_property('materials',ms)
    unreal.EditorAssetLibrary.save_loaded_asset(sk)
    print(s2,[x.get_editor_property('material_interface').get_name() for x in sk.get_editor_property('materials')])
print('TEX',tex.blueprint_get_size_x(),tex.get_editor_property('max_texture_size'))
