import unreal
# Стол с приборами у входа в большую палатку (как на картинке-образце): стол + осциллограф + радиоприёмник.
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
P = '/Game/Environment/Props/'
print('PIE', unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor())
have = {a.get_actor_label() for a in eas.get_all_level_actors()}
tent = [a for a in eas.get_all_level_actors() if a.get_actor_label() == 'Большая_палатка'][0]
T = tent.get_actor_transform()
def W(x, y, z): return unreal.MathLibrary.transform_location(T, unreal.Vector(x, y, z))
yaw = tent.get_actor_rotation().yaw
ITEMS = [('Стол_с_приборами', P + 'LowPolyMarket/SM_Table_01', (-260.0, 520.0, 0.0), 0.0),
         ('Осциллограф', P + 'ScientistBase/SM_Oscilloscope', (-320.0, 520.0, 80.2), 0.0),
         ('Радиоприёмник', P + 'ScientistBase/SM_Radio', (-200.0, 530.0, 80.2), -15.0)]
n = 0
for label, path, loc, dyaw in ITEMS:
    if label in have:
        print('уже стоит', label); continue
    m = unreal.load_asset(path)
    if not m:
        print('нет модели', path); continue
    a = eas.spawn_actor_from_class(unreal.StaticMeshActor, W(*loc), unreal.Rotator(0, 0, yaw + dyaw))
    a.static_mesh_component.set_static_mesh(m)
    a.set_actor_label(label); a.set_folder_path('ScientistBase')
    o, e = a.get_actor_bounds(False)
    print('PLACED', label, round(o.x), round(o.y), 'z', round(o.z - e.z), round(o.z + e.z), 'size', round(e.x * 2), round(e.y * 2), round(e.z * 2))
    n += 1
if n: print('SAVED', unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level())
