import unreal
eal = unreal.EditorAssetLibrary
# двусторонность: снять временную
for p in ['/Game/Weapons/Shotgun/MI_Shotgun_TOZ34', '/Game/Environment/Props/ScientistBase/MI_Oscilloscope', '/Game/Environment/Props/ScientistBase/MI_Radio', '/Game/Environment/Props/ScientistBase/MI_StashChest']:
    mi = unreal.load_asset(p)
    o = mi.get_editor_property('base_property_overrides')
    print('TWOSIDED', p.rsplit('/',1)[1], o.get_editor_property('override_two_sided'), o.get_editor_property('two_sided'))
for bp in ['/Game/Characters/Trader/BP_Trader', '/Game/Characters/Elder/BP_Elder', '/Game/Characters/ScientistGuard/BP_ScientistGuard']:
    cls = unreal.load_asset(bp).generated_class(); cdo = unreal.get_default_object(cls)
    print('BP', bp, 'parent', unreal.SystemLibrary.get_class_display_name(cls), type(cdo).__mro__[1].__name__ if True else '')
    for c in cdo.get_components_by_class(unreal.SkeletalMeshComponent):
        sk = c.get_skeletal_mesh_asset()
        print('  comp', c.get_name(), 'mesh', sk.get_path_name() if sk else None, 'anim', c.get_editor_property('anim_class'))
sub = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
for bp in ['/Game/Characters/Trader/BP_Trader', '/Game/Characters/ScientistGuard/BP_ScientistGuard']:
    b = unreal.load_asset(bp)
    for h in sub.k2_gather_subobject_data_for_blueprint(b):
        d = unreal.SubobjectDataBlueprintFunctionLibrary.get_data(h)
        o = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(d)
        if o:
            extra = ''
            if isinstance(o, unreal.SkeletalMeshComponent):
                sk = o.get_skeletal_mesh_asset(); extra = (sk.get_name() if sk else 'None') + ' anim=' + str(o.get_editor_property('anim_class')) + ' leader?'
            print('  SUB', bp.rsplit('/',1)[1], o.get_name(), o.get_class().get_name(), extra)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in eas.get_all_level_actors():
    f = str(a.get_folder_path()); n = a.get_class().get_name(); l = a.get_actor_location()
    if 'Scientist' in f or 'Den' in n or 'EnemyBase' in n or 'Base' in n or 'Trader' in n or 'Elder' in n or 'Stash' in n or 'Campfire' in n:
        print('ACT', a.get_actor_label(), '|', n, '|', f, '|', round(l.x), round(l.y), round(l.z), 'yaw', round(a.get_actor_rotation().yaw))
dt = unreal.load_asset('/Game/Data/DT_Items') if eal.does_asset_exist('/Game/Data/DT_Items') else None
print('DT', dt)
if not dt:
    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    for d in ar.get_assets_by_class(unreal.TopLevelAssetPath('/Script/Engine', 'DataTable')): print('  TABLE', d.package_name)
else:
    print('ROWS', [str(x) for x in unreal.DataTableFunctionLibrary.get_data_table_row_names(dt)])
    print(dt.export_to_csv_string() if hasattr(dt,'export_to_csv_string') else unreal.DataTableFunctionLibrary.export_data_table_to_csv_string(dt))
