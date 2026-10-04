import unreal
D='/Game/Environment/Props/BusStop'; N='BP_BusStop'
at=unreal.AssetToolsHelpers.get_asset_tools(); eal=unreal.EditorAssetLibrary
cls=unreal.load_class(None,'/Script/ContrarySurvivor.BusStop'); print('CLASS',cls)
if eal.does_asset_exist(D+'/'+N): bp=unreal.load_asset(D+'/'+N)
else:
    f=unreal.BlueprintFactory(); f.set_editor_property('parent_class',cls); bp=at.create_asset(N,D,unreal.Blueprint,f)
gc=unreal.load_object(None,D+'/'+N+'.'+N+'_C'); cdo=unreal.get_default_object(gc)
for k,v in [('RoofColor',unreal.LinearColor(0.50,0.56,0.60,1)),('WallColor',unreal.LinearColor(0.22,0.42,0.62,1)),('UrnColor',unreal.LinearColor(0.62,0.58,0.50,1)),('SignLocation',unreal.Vector(-300,153,0)),('UrnLocation',unreal.Vector(162,100,0))]:
    cdo.set_editor_property(k,v); print(k,cdo.get_editor_property(k))
unreal.BlueprintEditorLibrary.compile_blueprint(bp); print('SAVE',eal.save_loaded_asset(bp,False))
for k in ['SignTiltDeg','SignTiltDirectionDeg','bHasLoot','MoneyRange','bHasCampfire','bCampfireIsSavePoint','CampfireOffset','CampfireClass']:
    try: print(k,cdo.get_editor_property(k))
    except Exception as e: print(k,'ERR',str(e)[:70])
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
a=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_class(gc,unreal.Vector(0,0,-50000))
for c in a.get_components_by_class(unreal.StaticMeshComponent):
    sm=c.static_mesh; print('COMP',c.get_name(),sm.get_name() if sm else None,'mat',c.get_material(0).get_name() if sm and c.get_material(0) else None,'loc',[round(v) for v in (c.relative_location.x,c.relative_location.y,c.relative_location.z)],'rot',[round(v,1) for v in (c.relative_rotation.pitch,c.relative_rotation.yaw,c.relative_rotation.roll)],'coll',c.get_collision_enabled(),'mob',c.mobility)
unreal.get_editor_subsystem(unreal.EditorActorSubsystem).destroy_actor(a)
