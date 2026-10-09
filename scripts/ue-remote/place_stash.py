import unreal
# Личный сундук встаёт на место зелёного ящика, ящик отодвигается и остаётся обычным предметом (Ринат, 09.10).
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
print('PIE', unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor())
acts = {a.get_actor_label(): a for a in eas.get_all_level_actors()}
if 'Личный_сундук' in acts:
    print('уже стоит')
else:
    crate = acts['Личный_ящик']; l = crate.get_actor_location()
    a = eas.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(l.x, l.y, 0), unreal.Rotator(0, 0, 180.0))
    a.static_mesh_component.set_static_mesh(unreal.load_asset('/Game/Environment/Props/ScientistBase/SM_StashChest'))
    a.set_actor_label('Личный_сундук'); a.set_folder_path('ScientistBase')
    crate.set_actor_location(unreal.Vector(l.x + 115.0, l.y + 10.0, 0), False, False)
    crate.set_actor_rotation(unreal.Rotator(0, 0, 12.0), False); crate.set_actor_label('Ящик_зелёный')
    for x in (a, crate):
        o, e = x.get_actor_bounds(False); print(x.get_actor_label(), round(o.x), round(o.y), 'size', round(e.x*2), round(e.y*2), round(e.z*2), 'zmin', round(o.z-e.z))
    print('SAVED', unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level())
