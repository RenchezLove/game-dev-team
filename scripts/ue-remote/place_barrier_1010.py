import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
print('WORLD', w.get_path_name())
cls = unreal.load_class(None, '/Script/ContrarySurvivor.QuestBarrier')
print('CLASS', cls)
old = [a for a in eas.get_all_level_actors() if a.get_actor_label() == 'ГБ_Шлагбаум']
have = [a for a in eas.get_all_level_actors() if a.get_class() == cls]
print('OLD', len(old), 'HAVE', len(have))
for a in old: eas.destroy_actor(a)
if cls and not have:
    b = eas.spawn_actor_from_class(cls, unreal.Vector(7378.0, -16040.0, 0.0), unreal.Rotator(roll=0.0, pitch=0.0, yaw=0.0))
    b.set_actor_label('Шлагбаум'); b.set_folder_path('ScientistBase')
    print('SPAWNED', b.get_actor_location(), b.get_editor_property('passage_width'))
for a in eas.get_all_level_actors():
    if a.get_actor_label() == 'Охранник':
        a.set_actor_location(unreal.Vector(7250.0, -15740.0, 91.0), False, False)
        print('GUARD', a.get_actor_location(), a.get_actor_rotation())
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
print('SAVE', les.save_current_level())
print('CHECK', [(a.get_actor_label(), a.get_class().get_name()) for a in eas.get_all_level_actors() if 'лагбаум' in a.get_actor_label()])
