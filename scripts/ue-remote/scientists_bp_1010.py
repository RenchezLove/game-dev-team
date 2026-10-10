import unreal, math
# Персонажи базы учёных: чертежи трёх учёных, охранник переводится на класс собеседника с заданием, расстановка вместо кубов, место рации у южного логова.
eal = unreal.EditorAssetLibrary; at = unreal.AssetToolsHelpers.get_asset_tools(); bel = unreal.BlueprintEditorLibrary
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
print('PIE', unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor())
D = '/Game/Characters/Scientist'
ABP = unreal.load_asset('/Game/Characters/Shared/Humanoid/ABP_HumanoidCharacter').generated_class()
HEAD = unreal.load_asset(D + '/SK_Scientist_Head'); TORSO = unreal.load_asset(D + '/SK_Scientist_Torso'); LEGS = unreal.load_asset(D + '/SK_Scientist_Legs')
CAP = unreal.load_asset('/Game/Characters/Shared/Armor/SK_Armor_T1_Head'); BLOND = unreal.load_asset(D + '/MI_Scientist_Blond')
print('ASSETS', HEAD, TORSO, LEGS, CAP, BLOND)
def make(name, parent, head, head_mat):
    p = D + '/' + name
    if eal.does_asset_exist(p): bp = unreal.load_asset(p)
    else:
        f = unreal.BlueprintFactory(); f.set_editor_property('parent_class', parent)
        bp = at.create_asset(name, D, unreal.Blueprint, f)
    cdo = unreal.get_default_object(bp.generated_class())
    for c in cdo.get_components_by_class(unreal.SkeletalMeshComponent):
        m = {'CharacterMesh0': head, 'TorsoMesh': TORSO, 'LegsMesh': LEGS}.get(c.get_name())
        if not m: continue
        c.set_skeletal_mesh_asset(m); c.set_editor_property('anim_class', ABP)
        if c.get_name() == 'CharacterMesh0' and head_mat: c.set_material(0, head_mat)
    bel.compile_blueprint(bp); ok = eal.save_loaded_asset(bp, False)
    cdo = unreal.get_default_object(bp.generated_class())
    print('BP', name, 'save', ok, [(c.get_name(), c.get_skeletal_mesh_asset().get_name() if c.get_skeletal_mesh_asset() else None, round(c.get_editor_property('relative_location').z), round(c.get_editor_property('relative_rotation').yaw)) for c in cdo.get_components_by_class(unreal.SkeletalMeshComponent)])
    return bp
bq = make('BP_ScientistQuest', unreal.ScientistQuestNPC, HEAD, None)
bt = make('BP_ScientistTrader', unreal.ScientistTrader, HEAD, BLOND)
bh = make('BP_ScientistHelmet', unreal.ScientistHelmetNPC, CAP, None)
g = unreal.load_asset('/Game/Characters/ScientistGuard/BP_ScientistGuard')
bel.reparent_blueprint(g, unreal.ScientistGuardNPC); bel.compile_blueprint(g)
gc = unreal.get_default_object(g.generated_class())
print('GUARD parent ok', isinstance(gc, unreal.ScientistGuardNPC), 'save', eal.save_loaded_asset(g, False), [(c.get_name(), c.get_skeletal_mesh_asset().get_name() if c.get_skeletal_mesh_asset() else None, round(c.get_editor_property('relative_location').z), round(c.get_editor_property('relative_rotation').yaw)) for c in gc.get_components_by_class(unreal.SkeletalMeshComponent)])
acts = eas.get_all_level_actors(); by = {a.get_actor_label(): a for a in acts}
CENTER = (8700.0, -16000.0)
for cube, bp, lab in [('Квестовы ученый. Главный научный сотрудник.', bq, 'Учёный_квестовый'), ('Ученый-торговец', bt, 'Учёный_торговец'), ('Ученый, который выдает квест на VR шлем - просмотр рекламы', bh, 'Учёный_со_шлемом')]:
    if lab in by or cube not in by: print('skip', lab); continue
    c = by[cube]; l = c.get_actor_location()
    yaw = math.degrees(math.atan2(CENTER[1] - l.y, CENTER[0] - l.x))
    a = eas.spawn_actor_from_class(bp.generated_class(), unreal.Vector(l.x, l.y, 91.0), unreal.Rotator(0, 0, yaw))
    a.set_actor_label(lab); a.set_folder_path('ScientistBase'); eas.destroy_actor(c)
    print('PLACED', lab, round(l.x), round(l.y), 'yaw', round(yaw), 'tags', [str(t) for t in a.tags])
if 'Место_рации' not in by:
    den = by['BP_WolfDen2'].get_actor_location(); best = None
    for dx, dy in [(800, 500), (900, 0), (700, -600), (0, 900), (-800, 500), (1100, 700)]:
        x, y = den.x + dx, den.y + dy; free = True
        for a in acts:
            if a.get_class().get_name() in ('Landscape', 'InstancedFoliageActor', 'NavMeshBoundsVolume', 'PostProcessVolume', 'LightmassImportanceVolume', 'RecastNavMesh', 'BP_WolfDen_C'): continue
            o, e = a.get_actor_bounds(True)
            if 0 < e.x < 3000 and e.z < 3000 and abs(o.x - x) < e.x + 80 and abs(o.y - y) < e.y + 80 and o.z + e.z > 20: free = False; print('  blocked by', a.get_actor_label()); break
        if free: best = (x, y); break
    print('RADIO SPOT', best, 'den', round(den.x), round(den.y))
    if best:
        s = eas.spawn_actor_from_class(unreal.QuestItemSpawner, unreal.Vector(best[0], best[1], den.z), unreal.Rotator(0, 0, 35))
        s.set_actor_label('Место_рации'); s.set_folder_path('WolfDen')
        s.set_editor_property('pickup_class', unreal.load_asset('/Game/System/BP_Pickup').generated_class())
        for k in ['quest_id', 'item_row', 'count', 'b_only_when_quest_active', 'pickup_class']:
            try: print('   ', k, s.get_editor_property(k))
            except Exception as ex: print('   ', k, 'ERR')
gl = by['Охранник']
print('GUARD on level', gl.get_class().get_name(), round(gl.get_actor_location().z), [(c.get_name(), round(c.get_editor_property('relative_location').z)) for c in gl.get_components_by_class(unreal.SkeletalMeshComponent)])
print('SAVED', unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level())
