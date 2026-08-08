import unreal
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/L_World_C')
sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in sub.get_all_level_actors():
    lbl = a.get_actor_label()
    if 'POI' in lbl.upper():
        print('POIDUMP|%s|%s|%s' % (lbl, a.get_class().get_name(), a.get_folder_path()))
print('POIDUMP|DONE')
