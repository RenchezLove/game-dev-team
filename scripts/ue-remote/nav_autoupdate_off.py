import unreal
s=unreal.load_object(None,'/Script/UnrealEd.Default__LevelEditorMiscSettings')
for n in ['bNavigationAutoUpdate','b_navigation_auto_update','NavigationAutoUpdate']:
    try:
        print(n,'WAS',s.get_editor_property(n)); s.set_editor_property(n,False); print(n,'NOW',s.get_editor_property(n)); break
    except Exception as e: print(n,'ERR',str(e)[:80])
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.RecastNavMesh):
    print('NAVMESH',a.get_name(),'runtime_generation',a.get_editor_property('runtime_generation'))
