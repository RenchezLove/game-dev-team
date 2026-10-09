import unreal, os, re
# Импорт моделей базы учёных (сдача моделлера 09.10). Перезапускаемый: берёт только то, что уже лежит на диске.
ROOT = 'E:/game-dev-team/assets/scientist_base/'
DEST0 = '/Game/Environment/Props/ScientistBase'
DEST_OVERRIDE = {'SM_Shotgun_TOZ34': '/Game/Weapons/Shotgun', 'SM_ShotgunShell': '/Game/Weapons/Shotgun'}
DEST = DEST0
# имя сетки, папка, текстура цвета, разрешение карты освещения, преграда: 'box' | None | (min,max) в см
ITEMS = [
    ('SM_UAZ452', 'SM_UAZ452', 'T_UAZ452_D', 64, 'box'),
    ('SM_ArmyTent', 'SM_ArmyTent', 'T_ArmyTent_D', 128, 'later'),
    ('SM_PersonalChest', 'SM_PersonalChest', 'T_PersonalChest_D', 32, 'box'),
    ('SM_Shotgun_TOZ34', 'SM_Shotgun_TOZ34', 'T_Shotgun_TOZ34_D', 0, None),
    ('SM_ShotgunShell', 'SM_ShotgunShell', 'T_ShotgunShell_D', 0, None),
    ('SM_Oscilloscope', 'SM_Oscilloscope', 'T_Oscilloscope_D', 16, None),
    ('SM_Radio', 'SM_Radio', 'T_Radio_D', 16, None),
    ('SM_StashChest', 'SM_StashChest', 'T_StashChest_D', 32, 'box'),
]
ONLY = globals().get('ONLY')
at = unreal.AssetToolsHelpers.get_asset_tools(); eal = unreal.EditorAssetLibrary; mel = unreal.MaterialEditingLibrary
sms = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
print('PIE', unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor())

mp = DEST0 + '/M_SciProp'
if eal.does_asset_exist(mp):
    mat = unreal.load_asset(mp)
else:
    mat = at.create_asset('M_SciProp', DEST0, unreal.Material, unreal.MaterialFactoryNew())
    tp = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSampleParameter2D, -700, 0)
    tp.set_editor_property('parameter_name', 'Diffuse')
    tint = mel.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, -700, 300)
    tint.set_editor_property('parameter_name', 'Tint'); tint.set_editor_property('default_value', unreal.LinearColor(1, 1, 1, 1))
    br = mel.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -700, 500)
    br.set_editor_property('parameter_name', 'Brightness'); br.set_editor_property('default_value', 1.0)
    m1 = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -400, 100)
    m2 = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -200, 200)
    ok = [mel.connect_material_expressions(tp, 'RGB', m1, 'A'), mel.connect_material_expressions(tint, '', m1, 'B'),
          mel.connect_material_expressions(m1, '', m2, 'A'), mel.connect_material_expressions(br, '', m2, 'B'),
          mel.connect_material_property(m2, '', unreal.MaterialProperty.MP_BASE_COLOR)]
    r = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -200, 400); r.set_editor_property('r', 0.9)
    s = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -200, 500); s.set_editor_property('r', 0.2)
    ok += [mel.connect_material_property(r, '', unreal.MaterialProperty.MP_ROUGHNESS), mel.connect_material_property(s, '', unreal.MaterialProperty.MP_SPECULAR)]
    mel.recompile_material(mat); print('M_SciProp created', all(ok), eal.save_loaded_asset(mat, False))

for mesh, folder, texname, lm, coll in ITEMS:
    if ONLY and mesh not in ONLY:
        continue
    # уже импортированное не трогаем (повторный импорт стёр бы преграду палатки); для переимпорта — вписать имя в REIMPORT
    if eal.does_asset_exist(DEST_OVERRIDE.get(mesh, DEST0) + '/' + mesh) and mesh not in (globals().get('REIMPORT') or []):
        continue
    DEST = DEST_OVERRIDE.get(mesh, DEST0)
    src = ROOT + folder + '/'
    if not os.path.isfile(src + mesh + '.fbx'):
        print('SKIP (нет файла)', mesh); continue
    if not os.path.isfile(src + texname + '.png'):
        print('FAIL нет текстуры', src + texname + '.png', os.listdir(src)); continue
    t = unreal.AssetImportTask()
    for k, v in [('filename', src + texname + '.png'), ('destination_path', DEST), ('destination_name', texname), ('replace_existing', True), ('automated', True), ('save', False)]: t.set_editor_property(k, v)
    at.import_asset_tasks([t]); tex = unreal.load_asset(DEST + '/' + texname)
    ip = DEST + '/MI_' + mesh[3:]
    mi = unreal.load_asset(ip) if eal.does_asset_exist(ip) else at.create_asset('MI_' + mesh[3:], DEST, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    mel.set_material_instance_parent(mi, mat)
    mel.set_material_instance_texture_parameter_value(mi, 'Diffuse', tex); mel.update_material_instance(mi)
    ui = unreal.FbxImportUI()
    for k, v in [('import_mesh', True), ('import_as_skeletal', False), ('import_materials', False), ('import_textures', False), ('import_animations', False), ('mesh_type_to_import', unreal.FBXImportType.FBXIT_STATIC_MESH)]: ui.set_editor_property(k, v)
    d = ui.get_editor_property('static_mesh_import_data')
    for k, v in [('combine_meshes', True), ('auto_generate_collision', False), ('generate_lightmap_u_vs', False), ('remove_degenerates', True), ('normal_import_method', unreal.FBXNormalImportMethod.FBXNIM_COMPUTE_NORMALS if mesh in (globals().get('COMPUTE_NORMALS') or []) else unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)]: d.set_editor_property(k, v)
    t = unreal.AssetImportTask()
    for k, v in [('filename', src + mesh + '.fbx'), ('destination_path', DEST), ('destination_name', mesh), ('replace_existing', True), ('automated', True), ('save', False), ('options', ui)]: t.set_editor_property(k, v)
    at.import_asset_tasks([t])
    sm = unreal.load_asset(DEST + '/' + mesh)
    if not sm:
        print('FAIL импорт', mesh); continue
    for i in range(len(sm.get_editor_property('static_materials'))): sm.set_material(i, mi)
    nuv = sms.get_num_uv_channels(sm, 0)
    if lm and nuv > 1:
        sm.set_editor_property('light_map_coordinate_index', 1); sm.set_editor_property('light_map_resolution', lm)
    ns = sm.get_editor_property('nanite_settings'); ns.enabled = False; sm.set_editor_property('nanite_settings', ns)
    sms.remove_collisions(sm)
    if coll == 'box':
        sms.add_simple_collisions(sm, unreal.ScriptCollisionShapeType.BOX)
    sm.modify()
    b = sm.get_bounding_box()
    lim = max(abs(v) for v in (b.min.x, b.min.y, b.min.z, b.max.x, b.max.y, b.max.z))
    txt = sm.get_editor_property('body_setup').get_editor_property('agg_geom').export_text()
    nums = [abs(float(v)) for v in re.findall(r'[XYZ]=(-?[0-9.]+)', txt)]
    print('NEW', mesh, 'min', [round(v) for v in (b.min.x, b.min.y, b.min.z)], 'max', [round(v) for v in (b.max.x, b.max.y, b.max.z)],
          'tris', sm.get_num_triangles(0), 'uv', nuv, 'mats', [x.material_interface.get_name() for x in sm.get_editor_property('static_materials')],
          'simple', sms.get_simple_collision_count(sm), 'convex', sms.get_convex_collision_count(sm),
          'COLL_OK' if (not nums or max(nums) <= lim * 2 + 50) else 'COLL_TOO_BIG %d' % max(nums))
    for a in (tex, mi, sm): print('  SAVE', a.get_name(), eal.save_loaded_asset(a, False))
