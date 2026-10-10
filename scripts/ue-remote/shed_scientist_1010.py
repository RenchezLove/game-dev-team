import unreal
# Сарай базы учёных: вместо некрашеной заготовки — текстурная модель сарая (та же, что у бандитов), своя копия с преградой
# и свой материал, где красные бандитские метки приглушены до цвета дерева.
eal = unreal.EditorAssetLibrary; at = unreal.AssetToolsHelpers.get_asset_tools(); mel = unreal.MaterialEditingLibrary
sms = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
print('PIE', unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor())
D = '/Game/Environment/Props/ScientistBase'
sp = D + '/SM_ScientistShed'
sm = unreal.load_asset(sp) if eal.does_asset_exist(sp) else eal.duplicate_asset('/Game/Environment/Props/SM_BanditShed', sp)
ip = D + '/MI_ScientistShed'
mi = unreal.load_asset(ip) if eal.does_asset_exist(ip) else at.create_asset('MI_ScientistShed', D, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
mel.set_material_instance_parent(mi, unreal.load_asset('/Game/Environment/Props/M_BanditShedTripo'))
mel.set_material_instance_scalar_parameter_value(mi, 'RedMarksSaturation', 0.0)
mel.set_material_instance_vector_parameter_value(mi, 'RedMarksTint', unreal.LinearColor(0.55, 0.45, 0.36, 1.0))
mel.update_material_instance(mi)
for i in range(len(sm.get_editor_property('static_materials'))): sm.set_material(i, mi)
sms.remove_collisions(sm); sms.add_simple_collisions(sm, unreal.ScriptCollisionShapeType.BOX); sm.modify()
print('COLL', sm.get_editor_property('body_setup').get_editor_property('agg_geom').export_text()[:200])
print('SAVE', eal.save_loaded_asset(mi, False), eal.save_loaded_asset(sm, False))
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in eas.get_all_level_actors():
    if a.get_actor_label() == 'Сарай_склад':
        c = a.static_mesh_component; c.set_static_mesh(sm)
        o, e = a.get_actor_bounds(False)
        print('SWAPPED', c.get_editor_property('static_mesh').get_name(), [m.get_name() for m in c.get_materials()], 'center', round(o.x), round(o.y), 'size', round(e.x*2), round(e.y*2), round(e.z*2), 'zmin', round(o.z-e.z), 'yaw', a.get_actor_rotation().yaw)
print('SAVED', unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level())
