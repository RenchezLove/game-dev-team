import unreal, glob
out = []
for p in ['/Game/System/BP_ContrarySurviorPlayerController']:
    if unreal.EditorAssetLibrary.does_asset_exist(p):
        c = unreal.load_object(None, p + '.' + p.split('/')[-1] + '_C'); d = unreal.get_default_object(c)
        out.append('CTRL %s radius=%s gap=%s' % (p, d.get_editor_property('PdaTouchButtonRadius'), d.get_editor_property('PdaTouchButtonGap')))
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
out.append('WORLD %s PIE %s' % (w.get_name(), unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor()))
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    if 'UAZ' in a.get_actor_label().upper() or 'УАЗ' in a.get_actor_label().upper():
        try: out.append('UAZ %s peel=%s' % (a.get_actor_label(), a.get_editor_property('PaintPeel')))
        except Exception as e: out.append('UAZ %s %s' % (a.get_actor_label(), e))
print('\n'.join(out))
