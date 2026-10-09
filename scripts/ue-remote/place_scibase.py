import unreal
# Замена кубов-заглушек базы учёных на готовые модели: то же место и поворот, опора на земле.
DEST = '/Game/Environment/Props/ScientistBase/'
# подпись куба -> (сетка, новая подпись, добавка к повороту)
MAP = {
    'ГБ_УАЗ_буханка': ('SM_UAZ452', 'УАЗ_буханка', 0.0),
    'ГБ_Большая_палатка': ('SM_ArmyTent', 'Большая_палатка', 0.0),
    'ГБ_Большая_палатка2': ('SM_ArmyTent', 'Большая_палатка_2', 0.0),
    'ГБ_Личный_ящик': ('SM_PersonalChest', 'Личный_ящик', 0.0),
}
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem); eal = unreal.EditorAssetLibrary
print('PIE', unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor())
n = 0
for a in eas.get_all_level_actors():
    lb = a.get_actor_label()
    if lb not in MAP: continue
    mesh, newlb, dyaw = MAP[lb]
    if not eal.does_asset_exist(DEST + mesh):
        print('WAIT', lb, '— модели', mesh, 'ещё нет'); continue
    o, e = a.get_actor_bounds(False); l = a.get_actor_location(); r = a.get_actor_rotation()
    print('CUBE', lb, 'at', round(l.x), round(l.y), 'yaw', round(r.yaw, 1), 'size', round(e.x * 2), round(e.y * 2), round(e.z * 2))
    c = a.static_mesh_component
    c.set_static_mesh(unreal.load_asset(DEST + mesh))
    for i in range(c.get_num_materials()): c.set_material(i, None)
    a.set_actor_scale3d(unreal.Vector(1, 1, 1))
    a.set_actor_location(unreal.Vector(l.x, l.y, 0), False, False)
    a.set_actor_rotation(unreal.Rotator(0, 0, r.yaw + dyaw), False)
    a.set_actor_label(newlb)
    o, e = a.get_actor_bounds(False)
    print('  NOW', newlb, c.static_mesh.get_name(), [m.get_name() for m in c.get_materials()], 'size', round(e.x * 2), round(e.y * 2), round(e.z * 2), 'zmin', round(o.z - e.z))
    n += 1
if n:
    print('SAVED', unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level())
