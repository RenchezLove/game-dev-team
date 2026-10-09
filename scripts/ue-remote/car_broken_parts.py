import unreal
# Помятые двери и капот брошенной машины (Ринат, 09.10): импорт и подключение к галочкам «битая» в BP_AbandonedCar.
SRC = 'E:/game-dev-team/assets/abandoned_car_tripo/broken/'; DEST = '/Game/Environment/Props/AbandonedCar'
at = unreal.AssetToolsHelpers.get_asset_tools(); eal = unreal.EditorAssetLibrary
print('PIE', unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor())
mat = unreal.load_asset(DEST + '/M_CarTripo')
PARTS = {'Door_FL': 'door_fl_broken_mesh', 'Door_FR': 'door_fr_broken_mesh', 'Door_RL': 'door_rl_broken_mesh', 'Door_RR': 'door_rr_broken_mesh', 'Hood': 'hood_broken_mesh'}
saves = []; got = {}
for part, prop in PARTS.items():
    name = 'SM_AbandonedCar_' + part + '_Broken'
    ui = unreal.FbxImportUI()
    for k, v in [('import_mesh', True), ('import_as_skeletal', False), ('import_materials', False), ('import_textures', False), ('import_animations', False), ('mesh_type_to_import', unreal.FBXImportType.FBXIT_STATIC_MESH)]: ui.set_editor_property(k, v)
    d = ui.get_editor_property('static_mesh_import_data')
    for k, v in [('combine_meshes', True), ('auto_generate_collision', False), ('generate_lightmap_u_vs', False), ('remove_degenerates', True), ('normal_import_method', unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)]: d.set_editor_property(k, v)
    t = unreal.AssetImportTask()
    for k, v in [('filename', SRC + name + '.fbx'), ('destination_path', DEST), ('destination_name', name), ('replace_existing', True), ('automated', True), ('save', False), ('options', ui)]: t.set_editor_property(k, v)
    at.import_asset_tasks([t]); sm = unreal.load_asset(DEST + '/' + name)
    whole = unreal.load_asset(DEST + '/SM_AbandonedCar_' + part)
    for i in range(len(sm.get_editor_property('static_materials'))): sm.set_material(i, mat)
    ns = sm.get_editor_property('nanite_settings'); ns.enabled = False; sm.set_editor_property('nanite_settings', ns)
    sm.set_editor_property('light_map_resolution', whole.get_editor_property('light_map_resolution')); sm.set_editor_property('light_map_coordinate_index', whole.get_editor_property('light_map_coordinate_index'))
    unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem).remove_collisions(sm); sm.modify()
    verts, tris, normals, uvs, tangents = unreal.ProceduralMeshLibrary.get_section_from_static_mesh(sm, 0, 0)
    bad = sum(1 for i in range(0, len(tris), 3) if (verts[tris[i + 1]] - verts[tris[i]]).cross(verts[tris[i + 2]] - verts[tris[i]]).dot(normals[tris[i]] + normals[tris[i + 1]] + normals[tris[i + 2]]) > 0)
    b = sm.get_bounding_box(); w = whole.get_bounding_box()
    print(name, 'tris', sm.get_num_triangles(0), 'bbox', [round(x) for x in (b.min.x, b.min.y, b.min.z, b.max.x, b.max.y, b.max.z)], 'целая', [round(x) for x in (w.min.x, w.min.y, w.min.z, w.max.x, w.max.y, w.max.z)], 'NORMALS_OK' if bad == 0 else 'NORMALS_INVERTED %d' % bad)
    got[prop] = sm; saves.append(sm)
bp = unreal.load_asset(DEST + '/BP_AbandonedCar')
cdo = unreal.get_default_object(bp.generated_class())
for prop, sm in got.items(): cdo.set_editor_property(prop, sm)
bp.modify(); unreal.BlueprintEditorLibrary.compile_blueprint(bp)
cdo = unreal.get_default_object(bp.generated_class())
print('BP', {p: (cdo.get_editor_property(p).get_name() if cdo.get_editor_property(p) else None) for p in list(PARTS.values()) + ['trunk_broken_mesh']})
saves.append(bp)
for a in saves: print('SAVE', a.get_name(), eal.save_loaded_asset(a, False))
# проверка подмены на живом экземпляре в мире редактора (без сохранения уровня): ставим галочку, смотрим сетку, снимаем
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
car = eas.spawn_actor_from_object(bp, unreal.Vector(0, 0, -5000), unreal.Rotator(0, 0, 0))
def mesh_of(n): return [c.static_mesh.get_name() for c in car.get_components_by_class(unreal.StaticMeshComponent) if c.get_name() == n][0]
print('TEST целая', mesh_of('Hood'), mesh_of('DoorFL'))
car.set_editor_property('hood_broken', True); car.set_editor_property('door_fl_broken', True); car.rerun_construction_scripts()
print('TEST битая', mesh_of('Hood'), mesh_of('DoorFL'))
car.set_editor_property('hood_broken', False); car.set_editor_property('door_fl_broken', False); car.rerun_construction_scripts()
print('TEST снова целая', mesh_of('Hood'), mesh_of('DoorFL'))
eas.destroy_actor(car)
print('DIRTY maps', [p.get_name() for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()])
