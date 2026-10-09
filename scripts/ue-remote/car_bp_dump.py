import unreal
mel = unreal.MaterialEditingLibrary
bp = unreal.load_asset('/Game/Environment/Props/AbandonedCar/BP_AbandonedCar')
print('parent', bp.get_editor_property('parent_class').get_name() if hasattr(bp, 'parent_class') else '', 'gen', bp.generated_class().get_name())
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
for h in sds.k2_gather_subobject_data_for_blueprint(bp):
    o = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(unreal.SubobjectDataBlueprintFunctionLibrary.get_data(h))
    if isinstance(o, unreal.StaticMeshComponent):
        l = o.get_editor_property('relative_location'); r = o.get_editor_property('relative_rotation'); s = o.get_editor_property('relative_scale3d')
        print('C', o.get_name(), o.static_mesh.get_name() if o.static_mesh else None, 'loc', (round(l.x,1), round(l.y,1), round(l.z,1)), 'rot', (round(r.roll,1), round(r.pitch,1), round(r.yaw,1)), 'scale', (s.x, s.y, s.z), 'mats', [m.get_name() if m else None for m in o.get_editor_property('override_materials')], 'mob', o.mobility)
cdo = unreal.get_default_object(bp.generated_class())
for p in ['car_scale','door_fl_mount','door_fr_mount','door_rl_mount','door_rr_mount','hood_mount','trunk_mount','door_fl_hinge','trunk_hinge','door_fl_open_angle_deg','door_fr_open_angle_deg','trunk_open_angle_deg','trunk_hinge_vertical','override_body_color','body_color','paint_movable_parts','paint_color_param_name','glass','glass_broken','hood','trunk','scratches','block','has_loot','door_fl_broken_mesh']:
    try: print('P', p, cdo.get_editor_property(p))
    except Exception as e: print('P', p, 'ERR', str(e)[:80])
m = unreal.load_asset('/Game/Environment/Props/AbandonedCar/M_CarTripo')
print('M_CarTripo tex params', [str(x) for x in mel.get_texture_parameter_names(m)], 'used', [t.get_path_name() for t in mel.get_used_textures(m)], 'two_sided', m.get_editor_property('two_sided'), 'default BodyColor', mel.get_material_default_vector_parameter_value(m, 'BodyColor'))
g = unreal.load_asset('/Game/Environment/Props/AbandonedCar/M_CarGlass'); print('glass blend', g.get_editor_property('blend_mode'))
b = unreal.load_asset('/Game/Environment/Props/AbandonedCar/SM_AbandonedCar_Body')
sms = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
print('body coll simple', sms.get_simple_collision_count(b), 'convex', sms.get_convex_collision_count(b), sms.get_collision_complexity(b), 'lm', b.get_editor_property('light_map_resolution'), b.get_editor_property('light_map_coordinate_index'), 'uv', sms.get_num_uv_channels(b, 0))
