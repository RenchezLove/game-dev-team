import unreal
eal = unreal.EditorAssetLibrary
print('DEL old', eal.delete_asset('/Game/Environment/Props/UAZ452/M_UAZ452Paint') if eal.does_asset_exist('/Game/Environment/Props/UAZ452/M_UAZ452Paint') else 'нет')
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in eas.get_all_level_actors():
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        sm = c.get_editor_property('static_mesh')
        if sm and ('Shed' in sm.get_name() or 'Sarai' in sm.get_name() or 'Barn' in sm.get_name()):
            l = a.get_actor_location()
            print('SHED', a.get_actor_label(), '|', str(a.get_folder_path()), '|', sm.get_path_name(), round(l.x), round(l.y), 'scale', a.get_actor_scale3d().x,
                  'mats', [m.get_path_name() if m else None for m in c.get_materials()], 'override', [m.get_name() if m else None for m in c.get_editor_property('override_materials')],
                  'asset mats', [x.material_interface.get_name() if x.material_interface else None for x in sm.get_editor_property('static_materials')], 'lm', sm.get_editor_property('light_map_resolution'), 'uv', unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem).get_num_uv_channels(sm, 0))
