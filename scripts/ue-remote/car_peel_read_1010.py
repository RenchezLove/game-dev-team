import unreal
# ТОЛЬКО ЧТЕНИЕ: поля облезлости и материалы всех слотов у машин (мир редактора и, если идёт игра, игровой мир).
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
cls = unreal.load_class(None, '/Script/ContrarySurvivor.AbandonedCar')


def mat_info(m):
    if not m:
        return 'None'
    out = '%s[%s]' % (m.get_name(), type(m).__name__)
    if isinstance(m, unreal.MaterialInstance):
        p = m.get_editor_property('parent')
        out += ' parent=%s' % (p.get_name() if p else None)
        out += ' S=%s' % [(str(x.parameter_info.name), round(x.parameter_value, 3)) for x in m.get_editor_property('scalar_parameter_values')]
        out += ' V=%s' % [str(x.parameter_info.name) for x in m.get_editor_property('vector_parameter_values')]
    if isinstance(m, unreal.MaterialInstanceDynamic):
        out += ' outer=%s' % m.get_outer().get_name()
        try:
            out += ' peel_now=%s' % round(m.k2_get_scalar_parameter_value('PaintPeel'), 3)
        except Exception as e:
            out += ' peel_now=ERR'
    return out


def dump(world, tag):
    if not world:
        print(tag, 'нет мира')
        return
    for a in unreal.GameplayStatics.get_all_actors_of_class(world, cls):
        label = a.get_actor_label()
        print('%s ACTOR %s class=%s peel=%s peel_param=%s color_param=%s override_color=%s' % (
            tag, label, a.get_class().get_name(), a.get_editor_property('paint_peel'),
            a.get_editor_property('paint_peel_param_name'), a.get_editor_property('paint_color_param_name'),
            a.get_editor_property('override_body_color')))
        if 'УАЗ' not in label and 'UAZ' not in a.get_class().get_name():
            continue
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            sm = c.static_mesh
            n = c.get_num_materials()
            print('  %s COMP %s mesh=%s vis=%s slots=%d override=%s' % (tag, c.get_name(), sm.get_name() if sm else None, c.is_visible(), n,
                  [m.get_name() if m else None for m in c.get_editor_property('override_materials')]))
            for i in range(n):
                print('    slot %d: %s' % (i, mat_info(c.get_material(i))))


dump(ues.get_editor_world(), 'EDITOR')
if unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor():
    dump(ues.get_game_world(), 'GAME')
else:
    print('GAME игра в редакторе не идёт')
cdo = unreal.get_default_object(unreal.load_class(None, '/Game/Environment/Props/UAZ452/BP_UAZ452.BP_UAZ452_C')) if unreal.EditorAssetLibrary.does_asset_exist('/Game/Environment/Props/UAZ452/BP_UAZ452') else None
if cdo:
    print('CDO BP_UAZ452 peel=%s peel_param=%s color_param=%s' % (cdo.get_editor_property('paint_peel'), cdo.get_editor_property('paint_peel_param_name'), cdo.get_editor_property('paint_color_param_name')))
mel = unreal.MaterialEditingLibrary
for p in ['/Game/Environment/Props/UAZ452/M_UAZ452Body', '/Game/Environment/Props/AbandonedCar/M_CarTripo']:
    if unreal.EditorAssetLibrary.does_asset_exist(p):
        m = unreal.load_asset(p)
        print('MAT', p, 'scalars', [str(x) for x in mel.get_scalar_parameter_names(m)], 'vectors', [str(x) for x in mel.get_vector_parameter_names(m)], 'tex', [str(x) for x in mel.get_texture_parameter_names(m)])
mi = unreal.load_asset('/Game/Environment/Props/UAZ452/MI_UAZ452Kit')
if mi:
    print('MI', mat_info(mi), 'PeelMask', mel.get_material_instance_texture_parameter_value(mi, 'PeelMask'))
