import unreal
ar = unreal.AssetRegistryHelpers.get_asset_registry()
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in eas.get_all_level_actors():
    lab = a.get_actor_label(); l = a.get_actor_location()
    if 'чён' in lab or 'ченый' in lab or 'Учен' in lab or a.get_class().get_name() in ('BP_Elder_C', 'BP_Trader_C', 'BP_ScientistGuard_C') or 'Pickup' in a.get_class().get_name() or 'Навес' in lab:
        print('ACT', lab, '|', a.get_class().get_name(), '|', round(l.x), round(l.y), round(l.z), 'yaw', round(a.get_actor_rotation().yaw), 'scale', [round(v, 2) for v in (a.get_actor_scale3d().x, a.get_actor_scale3d().y, a.get_actor_scale3d().z)])
        for c in a.get_components_by_class(unreal.SkeletalMeshComponent):
            sk = c.get_skeletal_mesh_asset()
            print('     ', c.get_name(), sk.get_name() if sk else None, 'anim', c.get_editor_property('anim_class').get_name() if c.get_editor_property('anim_class') else None, 'mode', c.get_editor_property('animation_mode'), 'leader', c.get_editor_property('leader_pose_component') if hasattr(c, 'leader_pose_component') else '-')
f = unreal.ARFilter(class_paths=[unreal.TopLevelAssetPath('/Script/Engine', 'Blueprint')], package_paths=['/Game'], recursive_paths=True)
for d in ar.get_assets(f):
    np = str(d.get_tag_value('NativeParentClass'))
    if 'Pickup' in np or 'NPC' in np or 'Trader' in np: print('BP', d.package_name, np)
for n in ['ScientistGuardNPC', 'ScientistQuestNPC', 'ScientistHelmetNPC', 'ScientistTrader', 'QuestItemSpawner']: print('CLASS', n, hasattr(unreal, n))
cdo = unreal.get_default_object(unreal.load_asset('/Game/Characters/Elder/BP_Elder').generated_class())
for k in ['head_mesh_asset', 'torso_mesh_asset', 'legs_mesh_asset', 'head_mesh', 'body_parts']:
    try: print('ELDER', k, cdo.get_editor_property(k))
    except Exception as e: pass
