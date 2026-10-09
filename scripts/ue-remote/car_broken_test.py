import unreal
# Проверка подмены помятых деталей на временном экземпляре в мире редактора; временные экземпляры удаляются.
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
bp = unreal.load_asset('/Game/Environment/Props/AbandonedCar/BP_AbandonedCar')
for a in eas.get_all_level_actors():
    if a.get_actor_location().z < -4000 and a.get_class().get_name() == 'BP_AbandonedCar_C': eas.destroy_actor(a); print('removed leftover test car')
car = eas.spawn_actor_from_object(bp, unreal.Vector(0, 0, -5000), unreal.Rotator(0, 0, 0))
def mesh_of(n): return [c.static_mesh.get_name() for c in car.get_components_by_class(unreal.StaticMeshComponent) if c.get_name() == n][0]
print('TEST целая', mesh_of('Hood'), mesh_of('DoorFL'), mesh_of('DoorRR'))
for p in ('hood_broken', 'door_fl_broken', 'door_rr_broken'): car.set_editor_property(p, True)
print('TEST битая', mesh_of('Hood'), mesh_of('DoorFL'), mesh_of('DoorRR'))
for p in ('hood_broken', 'door_fl_broken', 'door_rr_broken'): car.set_editor_property(p, False)
print('TEST снова целая', mesh_of('Hood'), mesh_of('DoorFL'), mesh_of('DoorRR'))
eas.destroy_actor(car)
print('test cars left', len([a for a in eas.get_all_level_actors() if a.get_actor_location().z < -4000]))
print('LEVEL SAVED', unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level())
