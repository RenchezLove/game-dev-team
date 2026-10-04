import unreal
sms=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
for p in ['/Game/Environment/Props/BusStop/SM_BusStop','/Game/Environment/Nature/SM_Tree_Birch_01','/Game/Environment/Props/SM_BanditCrate']:
    sm=unreal.load_asset(p); ag=sm.get_editor_property('body_setup').get_editor_property('agg_geom')
    print(p,'simple',sms.get_simple_collision_count(sm),'convex',sms.get_convex_collision_count(sm))
    for n in ['convex_elems','box_elems','sphere_elems','sphyl_elems']:
        try: print('   ',n,len(ag.get_editor_property(n)))
        except Exception as e: print('   ',n,'ERR',str(e)[:60])
aid=unreal.load_asset('/Game/Environment/Props/BusStop/SM_BusStop').get_editor_property('asset_import_data'); print(aid.get_class().get_name())
