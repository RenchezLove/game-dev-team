import unreal
# Ринат 09.10: приглушить и притемнить землю примерно на четверть (в сторону бурой осенней травы),
# забор — из почти белого в серый с ржавчиной.
mel = unreal.MaterialEditingLibrary; eal = unreal.EditorAssetLibrary
at = unreal.AssetToolsHelpers.get_asset_tools()
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
print('PIE', unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor())

# --- земля: настройки поверх M_GroundAutumn (сам материал не меняется, откат = вернуть его на землю) ---
base = unreal.load_asset('/Game/Materials/M_GroundAutumn')
ip = '/Game/Materials/MI_GroundAutumn'
mi = unreal.load_asset(ip) if eal.does_asset_exist(ip) else at.create_asset('MI_GroundAutumn', '/Game/Materials', unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
mel.set_material_instance_parent(mi, base)
print('GrassTint', mel.set_material_instance_vector_parameter_value(mi, 'GrassTint', unreal.LinearColor(0.74, 0.82, 0.55, 1.0)))
print('GrassMacroLight', mel.set_material_instance_vector_parameter_value(mi, 'GrassMacroLight', unreal.LinearColor(1.08, 1.0, 0.85, 1.0)))
mel.update_material_instance(mi)
print('SAVE MI', eal.save_loaded_asset(mi, False))
for a in eas.get_all_level_actors():
    if a.get_actor_label() == 'GroundPlane':
        c = a.static_mesh_component
        print('ground before', [m.get_name() for m in c.get_materials()])
        for i in range(c.get_num_materials()):
            if c.get_material(i) and c.get_material(i).get_base_material() == base:
                c.set_material(i, mi)
        print('ground after', [m.get_name() for m in c.get_materials()])

# --- забор: новые цвета по умолчанию ---
H = 340.0
mat = unreal.load_asset('/Game/Environment/Buildings/M_ChainLinkFence')
mel.delete_all_material_expressions(mat)
wp = mel.create_material_expression(mat, unreal.MaterialExpressionWorldPosition, -900, 0)
hp = mel.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -900, 200)
hp.set_editor_property('parameter_name', 'FenceHeight'); hp.set_editor_property('default_value', H)
def custom(code, y):
    c = mel.create_material_expression(mat, unreal.MaterialExpressionCustom, -600, y)
    c.set_editor_property('code', code)
    c.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    i = unreal.CustomInput(); i.set_editor_property('input_name', 'WP')
    j = unreal.CustomInput(); j.set_editor_property('input_name', 'H')
    c.set_editor_property('inputs', [i, j])
    mel.connect_material_expressions(wp, '', c, 'WP'); mel.connect_material_expressions(hp, '', c, 'H')
    return c
solid = custom('float u=WP.x+WP.y; float d=(0.5-abs(frac(u/300.0)-0.5))*300.0; float post=step(d,7.0); float rail=step(H-8.0,WP.z); return max(post,rail);', 200)
mask = custom('float u=(WP.x+WP.y)/12.0; float v=WP.z/12.0; float a=abs(frac(u+v)-0.5); float b=abs(frac(u-v)-0.5); float wire=max(step(0.41,a),step(0.41,b)); float uu=WP.x+WP.y; float d=(0.5-abs(frac(uu/300.0)-0.5))*300.0; return max(wire,max(step(d,7.0),step(H-8.0,WP.z)));', 0)
wire = mel.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, -600, -400)
wire.set_editor_property('parameter_name', 'WireColor'); wire.set_editor_property('default_value', unreal.LinearColor(0.085, 0.060, 0.042, 1))
post = mel.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, -600, -200)
post.set_editor_property('parameter_name', 'PostColor'); post.set_editor_property('default_value', unreal.LinearColor(0.17, 0.16, 0.145, 1))
lerp = mel.create_material_expression(mat, unreal.MaterialExpressionLinearInterpolate, -300, -200)
ok = [mel.connect_material_expressions(wire, '', lerp, 'A'), mel.connect_material_expressions(post, '', lerp, 'B'), mel.connect_material_expressions(solid, '', lerp, 'Alpha'),
      mel.connect_material_property(lerp, '', unreal.MaterialProperty.MP_BASE_COLOR), mel.connect_material_property(mask, '', unreal.MaterialProperty.MP_OPACITY_MASK)]
rough = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -300, 100); rough.set_editor_property('r', 0.9)
spec = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -300, 200); spec.set_editor_property('r', 0.1)
ok += [mel.connect_material_property(rough, '', unreal.MaterialProperty.MP_ROUGHNESS), mel.connect_material_property(spec, '', unreal.MaterialProperty.MP_SPECULAR)]
mel.recompile_material(mat)
st = mel.get_statistics(mat)
print('FENCE conn', all(ok), 'pixel instr', st.num_pixel_shader_instructions, 'SAVE', eal.save_loaded_asset(mat, False))
print('LEVEL SAVED', unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level())
