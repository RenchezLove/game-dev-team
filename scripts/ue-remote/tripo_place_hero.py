import unreal
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
new=unreal.load_asset('/Game/Environment/Props/Tripo/SM_TripoHero_Raw')
b=new.get_bounding_box()
for x in eas.get_all_level_actors():
    if x.get_actor_label()=='TripoHero_Raw': eas.destroy_actor(x)
a=eas.spawn_actor_from_object(new,unreal.Vector(7870,8620,0.0018-b.min.z),unreal.Rotator(0,0,0))
a.set_actor_label('TripoHero_Raw')
print('PLACED',a.get_actor_location(),'size',b.max-b.min)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
print('SAVED')
