import unreal
mel = unreal.MaterialEditingLibrary
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
print('PIE', unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor())
for a in eas.get_all_level_actors():
    if a.get_actor_label() == 'GroundPlane':
        for m in a.static_mesh_component.get_materials():
            print('GROUND MAT', m.get_path_name(), m.get_class().get_name())
            base = m.get_base_material()
            print(' base', base.get_path_name())
            for n in mel.get_vector_parameter_names(base):
                v = mel.get_material_instance_vector_parameter_value(m, n) if isinstance(m, unreal.MaterialInstanceConstant) else mel.get_material_default_vector_parameter_value(base, n)
                print('  VEC', n, [round(x, 3) for x in (v.r, v.g, v.b, v.a)], 'default', [round(x, 3) for x in mel.get_material_default_vector_parameter_value(base, n).to_tuple()])
            for n in mel.get_scalar_parameter_names(base):
                v = mel.get_material_instance_scalar_parameter_value(m, n) if isinstance(m, unreal.MaterialInstanceConstant) else mel.get_material_default_scalar_parameter_value(base, n)
                print('  SCAL', n, round(v, 3), 'default', round(mel.get_material_default_scalar_parameter_value(base, n), 3))
            for n in mel.get_texture_parameter_names(base):
                print('  TEX', n)
            print('  used textures', [t.get_name() for t in mel.get_used_textures(base)])
