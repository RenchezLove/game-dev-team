import unreal
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
print('WORLD',w.get_name())
old=unreal.load_asset('/Game/Environment/Props/SM_BanditBarrel')
new=unreal.load_asset('/Game/Environment/Props/Tripo/SM_TripoBarrel')
ref=None
for a in eas.get_all_level_actors():
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        if c.static_mesh==old:
            ref=c; break
    if ref: break
if ref:
    loc=ref.get_world_location(); print('OLD_AT',ref.get_owner().get_actor_label(),loc)
else:
    loc=unreal.Vector(-3880,-4320,90); print('NO_OLD, village point')
p=unreal.Vector(loc.x+120,loc.y,loc.z+2000)
hit=unreal.SystemLibrary.line_trace_single(w,p,unreal.Vector(p.x,p.y,p.z-6000),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,[],unreal.DrawDebugTrace.NONE,True)
z=hit.to_tuple()[4].z if hit else loc.z
print('GROUND',hit.to_tuple()[4] if hit else None, hit.to_tuple()[10] if hit else None)
for x in eas.get_all_level_actors():
    if x.get_actor_label()=='TripoBarrel_Test': eas.destroy_actor(x)
act=eas.spawn_actor_from_object(new,unreal.Vector(p.x,p.y,z+42.5),unreal.Rotator(0,0,0))
act.set_actor_label('TripoBarrel_Test')
print('PLACED',act.get_actor_location())
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
print('SAVED')
