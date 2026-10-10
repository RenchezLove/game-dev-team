import unreal
# Материал кузова «буханки» (отдельный: общий M_CarTripo не трогаем — удаление его узлов из скрипта роняет редактор): параметр PaintPeel (0 — краска целая, 1 — облезлость как нарисована) по отдельной маске PeelMask.
# При маске по умолчанию (чёрная) и PaintPeel=1 вид прежний: цвет = текстура * lerp(белый, BodyColor, альфа).
mel = unreal.MaterialEditingLibrary; eal = unreal.EditorAssetLibrary
print('PIE', unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor())
at = unreal.AssetToolsHelpers.get_asset_tools()
MP = '/Game/Environment/Props/UAZ452/M_UAZ452Body'
m = unreal.load_asset(MP) if eal.does_asset_exist(MP) else at.create_asset('M_UAZ452Body', '/Game/Environment/Props/UAZ452', unreal.Material, unreal.MaterialFactoryNew())
if 'PaintPeel' in [str(x) for x in mel.get_scalar_parameter_names(m)]:
    print('уже есть')
else:
    old_tex = unreal.load_asset('/Game/Environment/Props/AbandonedCar/T_AbandonedCarTripo_D')
    E = lambda cls, x, y: mel.create_material_expression(m, cls, x, y)
    tex = E(unreal.MaterialExpressionTextureSampleParameter2D, -1300, 0); tex.set_editor_property('parameter_name', 'Diffuse'); tex.set_editor_property('texture', old_tex)
    body = E(unreal.MaterialExpressionVectorParameter, -1300, 300); body.set_editor_property('parameter_name', 'BodyColor'); body.set_editor_property('default_value', unreal.LinearColor(0.212, 0.296, 0.456, 1.0))
    white = E(unreal.MaterialExpressionConstant3Vector, -1300, 500); white.set_editor_property('constant', unreal.LinearColor(1, 1, 1, 1))
    l0 = E(unreal.MaterialExpressionLinearInterpolate, -1000, 300)
    cur = E(unreal.MaterialExpressionMultiply, -800, 100)
    base = E(unreal.MaterialExpressionScalarParameter, -1300, 700); base.set_editor_property('parameter_name', 'PaintBase'); base.set_editor_property('default_value', 0.68)
    clean = E(unreal.MaterialExpressionMultiply, -1000, 600)
    peel = E(unreal.MaterialExpressionScalarParameter, -1000, 850); peel.set_editor_property('parameter_name', 'PaintPeel'); peel.set_editor_property('default_value', 1.0)
    l1 = E(unreal.MaterialExpressionLinearInterpolate, -600, 500)
    mask = E(unreal.MaterialExpressionTextureSampleParameter2D, -800, 950); mask.set_editor_property('parameter_name', 'PeelMask')
    mask.set_editor_property('texture', unreal.load_asset('/Engine/EngineResources/Black')); mask.set_editor_property('sampler_type', unreal.MaterialSamplerType.SAMPLERTYPE_COLOR)
    l2 = E(unreal.MaterialExpressionLinearInterpolate, -350, 200)
    rough = E(unreal.MaterialExpressionConstant, -350, 500); rough.set_editor_property('r', 0.8)
    C = mel.connect_material_expressions
    ok = [C(white, '', l0, 'A'), C(body, '', l0, 'B'), C(tex, 'A', l0, 'Alpha'), C(tex, 'RGB', cur, 'A'), C(l0, '', cur, 'B'),
          C(body, '', clean, 'A'), C(base, '', clean, 'B'), C(clean, '', l1, 'A'), C(cur, '', l1, 'B'), C(peel, '', l1, 'Alpha'),
          C(cur, '', l2, 'A'), C(l1, '', l2, 'B'), C(mask, 'R', l2, 'Alpha'),
          mel.connect_material_property(l2, '', unreal.MaterialProperty.MP_BASE_COLOR), mel.connect_material_property(rough, '', unreal.MaterialProperty.MP_ROUGHNESS)]
    mel.recompile_material(m)
    print('CONN', ok, 'SAVE', eal.save_loaded_asset(m, False))
print('scalars', mel.get_scalar_parameter_names(m), 'tex', mel.get_texture_parameter_names(m), 'black sampler', unreal.load_asset('/Engine/EngineResources/Black').get_editor_property('srgb'), unreal.load_asset('/Engine/EngineResources/Black').get_editor_property('compression_settings'))

mi = unreal.load_asset('/Game/Environment/Props/UAZ452/MI_UAZ452Kit')
mel.set_material_instance_parent(mi, m); mel.update_material_instance(mi)
print('MI parent', mi.get_editor_property('parent').get_name(), 'tex', mel.get_material_instance_texture_parameter_value(mi, 'Diffuse').get_name(), 'color', mel.get_material_instance_vector_parameter_value(mi, 'BodyColor'), 'SAVE', eal.save_loaded_asset(mi, False))
