import unreal, math
# Личный сундук как игровой объект: чертёж BP_StashChest, на базе учёных — вместо декоративной модели, в деревне — рядом со старостой.
eal = unreal.EditorAssetLibrary; at = unreal.AssetToolsHelpers.get_asset_tools()
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
print('PIE', unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor())
p = '/Game/Environment/Props/ScientistBase/BP_StashChest'
if eal.does_asset_exist(p): bp = unreal.load_asset(p)
else:
    f = unreal.BlueprintFactory(); f.set_editor_property('parent_class', unreal.StashChest)
    bp = at.create_asset('BP_StashChest', '/Game/Environment/Props/ScientistBase', unreal.Blueprint, f)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp); print('SAVE BP', eal.save_loaded_asset(bp, False))
cls = bp.generated_class()
acts = eas.get_all_level_actors(); by = {a.get_actor_label(): a for a in acts}
print('HAVE', [l for l in by if 'ундук' in l or 'Stash' in l])
if 'Личный_сундук' in by and by['Личный_сундук'].get_class().get_name() == 'StaticMeshActor':
    old = by['Личный_сундук']; l = old.get_actor_location(); r = old.get_actor_rotation(); s = old.get_actor_scale3d()
    print('OLD base chest', l, r, s)
    a = eas.spawn_actor_from_class(cls, l, r)
    eas.destroy_actor(old)
    a.set_actor_label('Личный_сундук'); a.set_folder_path('ScientistBase')
    o, e = a.get_actor_bounds(False); print('NEW base chest', round(o.x), round(o.y), 'size', round(e.x*2), round(e.y*2), round(e.z*2), 'zmin', round(o.z-e.z))
if 'Личный_сундук_деревня' not in by:
    elder = by['BP_Elder']; el = elder.get_actor_location(); yaw = elder.get_actor_rotation().yaw
    boxes = []
    for a in acts:
        if a == elder or a.get_class().get_name() in ('Landscape', 'LandscapeStreamingProxy', 'NavMeshBoundsVolume', 'PostProcessVolume', 'LightmassImportanceVolume', 'InstancedFoliageActor', 'RecastNavMesh'): continue
        o, e = a.get_actor_bounds(True)
        if e.x <= 0 and e.y <= 0: continue
        if e.x > 3000 or e.y > 3000: continue
        if abs(o.x - el.x) < 900 + e.x and abs(o.y - el.y) < 900 + e.y:
            boxes.append((a.get_actor_label(), o.x - e.x, o.x + e.x, o.y - e.y, o.y + e.y))
    for b in boxes: print('  NEAR', b[0], [round(v) for v in b[1:]])
    best = None
    for rad in (230, 280, 330, 400):
        for dyaw in (90, -90, 120, -120, 60, -60, 150, -150, 180):
            ang = math.radians(yaw + dyaw); x = el.x + rad * math.cos(ang); y = el.y + rad * math.sin(ang)
            if all(not (x + 110 > b[1] and x - 110 < b[2] and y + 110 > b[3] and y - 110 < b[4]) for b in boxes):
                best = (x, y, dyaw, rad); break
        if best: break
    print('CHOSEN', best, 'elder', round(el.x), round(el.y), 'yaw', round(yaw))
    if best:
        face = math.degrees(math.atan2(el.y - best[1], el.x - best[0]))
        a = eas.spawn_actor_from_class(cls, unreal.Vector(best[0], best[1], el.z - 91.0), unreal.Rotator(0, 0, yaw))
        a.set_actor_label('Личный_сундук_деревня'); a.set_folder_path('Village')
        o, e = a.get_actor_bounds(False); print('NEW village chest', round(o.x), round(o.y), 'zmin', round(o.z - e.z))
print('SAVED', unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level())
