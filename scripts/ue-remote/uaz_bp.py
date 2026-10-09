import unreal, re
# «Буханка» как мастер-машина (Ринат, 09.10): набор деталей моделлера -> чертёж BP_UAZ452 на классе брошенной машины.
SRC = 'E:/game-dev-team/assets/scientist_base/SM_UAZ452_kit/'
DEST = '/Game/Environment/Props/UAZ452'
V = unreal.Vector
at = unreal.AssetToolsHelpers.get_asset_tools(); eal = unreal.EditorAssetLibrary; mel = unreal.MaterialEditingLibrary
sms = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
print('PIE', unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor())

# 1) текстура (цвет + маска краски в альфа-канале) и настройки материала поверх M_CarTripo
t = unreal.AssetImportTask()
for k, v in [('filename', SRC + 'T_UAZ452Kit_D.png'), ('destination_path', DEST), ('destination_name', 'T_UAZ452Kit_D'), ('replace_existing', True), ('automated', True), ('save', False)]: t.set_editor_property(k, v)
at.import_asset_tasks([t]); tex = unreal.load_asset(DEST + '/T_UAZ452Kit_D')
print('TEX', tex.blueprint_get_size_x(), tex.get_editor_property('compression_settings'), 'srgb', tex.get_editor_property('srgb'))
ip = DEST + '/MI_UAZ452Kit'
mi = unreal.load_asset(ip) if eal.does_asset_exist(ip) else at.create_asset('MI_UAZ452Kit', DEST, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
mel.set_material_instance_parent(mi, unreal.load_asset('/Game/Environment/Props/AbandonedCar/M_CarTripo'))
mel.set_material_instance_texture_parameter_value(mi, 'Diffuse', tex)
lin = lambda c: ((c + 0.055) / 1.055) ** 2.4
GREEN = unreal.LinearColor(lin(0.225), lin(0.265), lin(0.196), 1.0)
mel.set_material_instance_vector_parameter_value(mi, 'BodyColor', GREEN)
mel.update_material_instance(mi)
glass_mat = unreal.load_asset('/Game/Environment/Props/AbandonedCar/M_CarGlass')

# 2) сетки
MESHES = ['Body', 'Door_FL', 'Door_FR', 'Door_Side', 'RearDoor_L', 'RearDoor_R', 'Glass', 'Wheel']
saves = [tex, mi]; total = 0
for part in MESHES:
    name = 'SM_UAZ452_' + part
    ui = unreal.FbxImportUI()
    for k, v in [('import_mesh', True), ('import_as_skeletal', False), ('import_materials', False), ('import_textures', False), ('import_animations', False), ('mesh_type_to_import', unreal.FBXImportType.FBXIT_STATIC_MESH)]: ui.set_editor_property(k, v)
    d = ui.get_editor_property('static_mesh_import_data')
    for k, v in [('combine_meshes', True), ('auto_generate_collision', False), ('generate_lightmap_u_vs', False), ('remove_degenerates', True), ('normal_import_method', unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)]: d.set_editor_property(k, v)
    t = unreal.AssetImportTask()
    for k, v in [('filename', SRC + name + '.fbx'), ('destination_path', DEST), ('destination_name', name), ('replace_existing', True), ('automated', True), ('save', False), ('options', ui)]: t.set_editor_property(k, v)
    at.import_asset_tasks([t]); sm = unreal.load_asset(DEST + '/' + name)
    for i in range(len(sm.get_editor_property('static_materials'))): sm.set_material(i, glass_mat if part == 'Glass' else mi)
    ns = sm.get_editor_property('nanite_settings'); ns.enabled = False; sm.set_editor_property('nanite_settings', ns)
    sm.set_editor_property('light_map_resolution', 4); sm.set_editor_property('light_map_coordinate_index', 0)
    sms.remove_collisions(sm)
    if part == 'Body': sms.add_simple_collisions(sm, unreal.ScriptCollisionShapeType.BOX)
    sm.modify()
    # замер: нормали согласованы с обходом граней так же, как у заведомо правильных сеток (обход и нормаль «не согласны»)
    verts, tris, normals, uvs, tangents = unreal.ProceduralMeshLibrary.get_section_from_static_mesh(sm, 0, 0)
    bad = 0
    for i in range(0, len(tris), 3):
        a, b, c = tris[i], tris[i + 1], tris[i + 2]
        if (verts[b] - verts[a]).cross(verts[c] - verts[a]).dot(normals[a] + normals[b] + normals[c]) > 0: bad += 1
    bb = sm.get_bounding_box(); n = sm.get_num_triangles(0); total += n * (4 if part == 'Wheel' else 1)
    lim = max(abs(x) for x in (bb.min.x, bb.min.y, bb.min.z, bb.max.x, bb.max.y, bb.max.z))
    nums = [abs(float(x)) for x in re.findall(r'[XYZ]=(-?[0-9.]+)', sm.get_editor_property('body_setup').get_editor_property('agg_geom').export_text())]
    print('NEW', name, 'tris', n, 'min', [round(x) for x in (bb.min.x, bb.min.y, bb.min.z)], 'max', [round(x) for x in (bb.max.x, bb.max.y, bb.max.z)],
          'mat', [x.material_interface.get_name() for x in sm.get_editor_property('static_materials')], 'simple', sms.get_simple_collision_count(sm),
          'NORMALS_OK' if bad == 0 else 'NORMALS_INVERTED %d' % bad, 'COLL_OK' if (not nums or max(nums) <= lim * 2 + 50) else 'COLL_TOO_BIG')
    saves.append(sm)
print('TOTAL tris in assembly', total)

# 3) чертёж: копия BP_AbandonedCar со своими сетками и числами
bpp = DEST + '/BP_UAZ452'
if not eal.does_asset_exist(bpp):
    eal.duplicate_asset('/Game/Environment/Props/AbandonedCar/BP_AbandonedCar', bpp)
bp = unreal.load_asset(bpp)
M = lambda p: unreal.load_asset(DEST + '/SM_UAZ452_' + p)
COMP = {  # компонент -> (сетка, место, рыскание)
    'Body': (M('Body'), None, None), 'Glass': (M('Glass'), None, None),
    'DoorFL': (M('Door_FL'), None, None), 'DoorFR': (M('Door_FR'), None, None),
    'DoorRR': (M('Door_Side'), None, None), 'DoorRL': (M('RearDoor_L'), None, None), 'Trunk': (M('RearDoor_R'), None, None),
    'Hood': (None, None, None), 'Scratches': (None, None, None),
    'WheelFL': (M('Wheel'), V(-80.8, -118.7, 35.8), 0.0), 'WheelFR': (M('Wheel'), V(80.3, -118.8, 35.8), 180.0),
    'WheelRL': (M('Wheel'), V(-80.8, 120.2, 35.8), 0.0), 'WheelRR': (M('Wheel'), V(80.3, 120.2, 35.8), 180.0),
    'Block': ('keep', V(80.0, -118.8, 0.0), None),
}
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
for h in sds.k2_gather_subobject_data_for_blueprint(bp):
    o = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(unreal.SubobjectDataBlueprintFunctionLibrary.get_data(h))
    if isinstance(o, unreal.StaticMeshComponent) and o.get_name() in COMP:
        mesh, loc, yaw = COMP[o.get_name()]
        o.modify()
        if mesh != 'keep': o.set_editor_property('static_mesh', mesh)
        if loc is not None: o.set_editor_property('relative_location', loc)
        if yaw is not None: o.set_editor_property('relative_rotation', unreal.Rotator(0, 0, yaw))
        print('TPL', o.get_name(), o.static_mesh.get_name() if o.static_mesh else None, o.get_editor_property('relative_location').to_tuple(), o.get_editor_property('relative_rotation').yaw)
cdo = unreal.get_default_object(bp.generated_class())
Z = V(0, 0, 0)
PROPS = {'car_scale': 1.5, 'hood': False, 'scratches': False, 'block': False, 'trunk_hinge_vertical': True,
         'door_fl_mount': V(-88.8, -186.0, 58.0), 'door_fr_mount': V(88.8, -186.0, 58.0),
         'door_rr_mount': V(95.9, -36.0, 82.0), 'door_rl_mount': V(-70.0, 211.9, 80.0), 'trunk_mount': V(70.0, 211.9, 80.0),
         'door_fl_hinge': Z, 'door_fr_hinge': Z, 'door_rl_hinge': Z, 'door_rr_hinge': Z, 'trunk_hinge': Z,
         'body_color': GREEN}
for k, v in PROPS.items(): cdo.set_editor_property(k, v)
bp.modify(); unreal.BlueprintEditorLibrary.compile_blueprint(bp)
cdo = unreal.get_default_object(bp.generated_class())
print('CDO', {k: (cdo.get_editor_property(k).to_tuple() if hasattr(cdo.get_editor_property(k), 'to_tuple') else cdo.get_editor_property(k)) for k in ('car_scale', 'hood', 'trunk_hinge_vertical', 'door_rr_mount', 'trunk_mount')})
saves.append(bp)
for a in saves: print('SAVE', a.get_name(), eal.save_loaded_asset(a, False))

# 4) уровень: цельную модель на базе заменить чертежом на том же месте
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in eas.get_all_level_actors():
    if a.get_actor_label() == 'УАЗ_буханка' and isinstance(a, unreal.StaticMeshActor):
        l = a.get_actor_location(); r = a.get_actor_rotation()
        car = eas.spawn_actor_from_object(bp, V(l.x, l.y, 0), unreal.Rotator(0, 0, r.yaw))
        car.set_actor_label('УАЗ_буханка'); car.set_folder_path('ScientistBase')
        eas.destroy_actor(a)
        o, e = car.get_actor_bounds(False)
        print('PLACED', car.get_class().get_name(), round(l.x), round(l.y), 'yaw', round(r.yaw, 1), 'size', round(e.x * 2), round(e.y * 2), round(e.z * 2), 'scale', car.get_editor_property('car_scale'))
        for c in car.get_components_by_class(unreal.StaticMeshComponent):
            if c.get_name() in ('Body', 'DoorFL', 'Trunk', 'WheelFR', 'Hood'):
                rl = c.get_editor_property('relative_location'); print('   ', c.get_name(), c.static_mesh.get_name() if c.static_mesh else None, 'vis', c.is_visible(), (round(rl.x, 1), round(rl.y, 1), round(rl.z, 1)))
        print('LEVEL SAVED', unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level())
