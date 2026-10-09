import unreal
# M_SciProp: добавить мягко пульсирующее свечение (параметр GlowStrength, по умолчанию 0 — у остальных предметов ничего не меняется).
# Заодно метка телепорта меню отладки на базе учёных.
mel = unreal.MaterialEditingLibrary; eal = unreal.EditorAssetLibrary
print('PIE', unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor())
mat = unreal.load_asset('/Game/Environment/Props/ScientistBase/M_SciProp')
mel.delete_all_material_expressions(mat)
E = lambda c, x, y: mel.create_material_expression(mat, c, x, y); C = mel.connect_material_expressions
tp = E(unreal.MaterialExpressionTextureSampleParameter2D, -900, 0); tp.set_editor_property('parameter_name', 'Diffuse')
tp.set_editor_property('texture', unreal.load_asset('/Game/Environment/Props/ScientistBase/T_StashChest_D'))
tint = E(unreal.MaterialExpressionVectorParameter, -900, 300); tint.set_editor_property('parameter_name', 'Tint'); tint.set_editor_property('default_value', unreal.LinearColor(1, 1, 1, 1))
br = E(unreal.MaterialExpressionScalarParameter, -900, 500); br.set_editor_property('parameter_name', 'Brightness'); br.set_editor_property('default_value', 1.0)
m1 = E(unreal.MaterialExpressionMultiply, -600, 100); m2 = E(unreal.MaterialExpressionMultiply, -400, 200)
glow = E(unreal.MaterialExpressionScalarParameter, -900, 700); glow.set_editor_property('parameter_name', 'GlowStrength'); glow.set_editor_property('default_value', 0.0)
gcol = E(unreal.MaterialExpressionVectorParameter, -900, 850); gcol.set_editor_property('parameter_name', 'GlowColor'); gcol.set_editor_property('default_value', unreal.LinearColor(1.0, 0.75, 0.4, 1))
pulse = E(unreal.MaterialExpressionCustom, -900, 1050)
pulse.set_editor_property('code', 'return 0.65 + 0.35 * sin(T * 2.5);'); pulse.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT1)
i = unreal.CustomInput(); i.set_editor_property('input_name', 'T'); pulse.set_editor_property('inputs', [i])
tm = E(unreal.MaterialExpressionTime, -1100, 1050)
g1 = E(unreal.MaterialExpressionMultiply, -600, 750); g2 = E(unreal.MaterialExpressionMultiply, -400, 800); g3 = E(unreal.MaterialExpressionMultiply, -200, 800)
ok = [C(tp, 'RGB', m1, 'A'), C(tint, '', m1, 'B'), C(m1, '', m2, 'A'), C(br, '', m2, 'B'),
      mel.connect_material_property(m2, '', unreal.MaterialProperty.MP_BASE_COLOR),
      C(tm, '', pulse, 'T'), C(glow, '', g1, 'A'), C(pulse, '', g1, 'B'), C(g1, '', g2, 'A'), C(gcol, '', g2, 'B'), C(g2, '', g3, 'A'), C(m2, '', g3, 'B'),
      mel.connect_material_property(g3, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)]
r = E(unreal.MaterialExpressionConstant, -200, 400); r.set_editor_property('r', 0.9)
s = E(unreal.MaterialExpressionConstant, -200, 500); s.set_editor_property('r', 0.2)
ok += [mel.connect_material_property(r, '', unreal.MaterialProperty.MP_ROUGHNESS), mel.connect_material_property(s, '', unreal.MaterialProperty.MP_SPECULAR)]
mel.recompile_material(mat)
st = mel.get_statistics(mat)
print('M_SciProp conn', all(ok), 'pixel instr', st.num_pixel_shader_instructions, 'SAVE', eal.save_loaded_asset(mat, False))
for n in ('MI_UAZ452', 'MI_ArmyTent', 'MI_PersonalChest', 'MI_Oscilloscope', 'MI_Radio', 'MI_StashChest'):
    mi = unreal.load_asset('/Game/Environment/Props/ScientistBase/' + n)
    t = mel.get_material_instance_texture_parameter_value(mi, 'Diffuse')
    print(' ', n, 'Diffuse ->', t.get_name() if t else None)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if not [a for a in eas.get_all_level_actors() if a.get_actor_label() == 'Метка_телепорта_учёные']:
    a = eas.spawn_actor_from_class(unreal.TargetPoint, unreal.Vector(7700, -16040, 100), unreal.Rotator(0, 0, 0))
    a.set_actor_label('Метка_телепорта_учёные'); a.set_folder_path('ScientistBase'); a.tags = ['DebugTP_Scientists']
    print('marker', a.tags, 'LEVEL SAVED', unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level())
