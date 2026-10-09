import unreal, math
# Проверка преграды палаток пробными лучами в мире редактора: шатёр держит, растяжки пропускают.
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
def tr(s, e):
    h = unreal.SystemLibrary.sphere_trace_single_by_profile(w, s, e, 34.0, 'Pawn', False, [], unreal.DrawDebugTrace.NONE, True)
    if not h: return None
    t = h.to_tuple(); return (t[9].get_actor_label() if t[9] else None, round(t[3]))
for a in eas.get_all_level_actors():
    if not a.get_actor_label().startswith('Большая_палатка'): continue
    T = a.get_actor_transform()
    def P(x, y, z=100): return unreal.MathLibrary.transform_location(T, unreal.Vector(x, y, z))
    print(a.get_actor_label(), 'loc', a.get_actor_location(), 'yaw', round(a.get_actor_rotation().yaw, 1))
    print('  сбоку в стену (ждём удар на ~330 от старта):', tr(P(640, 0), P(0, 0)))
    print('  вдоль борта через растяжки, мимо шатра (ждём свободно):', tr(P(330, -480), P(330, 380)))
    print('  сзади в стену (ждём удар на ~200):', tr(P(0, -640), P(0, 0)))
    print('  спереди в тамбур (ждём удар на ~200):', tr(P(0, 640), P(0, 0)))
