import unreal
dst='/Game/Environment/Props/Tripo/CarRaw2'
t=unreal.AssetImportTask()
t.set_editor_property('filename','E:/ContrarySurvior/ContrarySurvivor/Saved/Tripo/car2/car2.glb')
t.set_editor_property('destination_path',dst)
t.set_editor_property('destination_name','SM_TripoCar2_Raw')
t.set_editor_property('automated',True)
t.set_editor_property('replace_existing',True)
t.set_editor_property('save',True)
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
print('IMPORTED',list(t.get_editor_property('imported_object_paths')))
m=None
for p in unreal.EditorAssetLibrary.list_assets(dst,recursive=True):
    a=unreal.load_asset(p)
    print('ASSET',p,type(a).__name__)
    if isinstance(a,unreal.StaticMesh): m=a
b=m.get_bounding_box(); print('size',b.max-b.min,'tris',m.get_num_triangles(0))
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for x in eas.get_all_level_actors():
    if x.get_actor_label()=='TripoCar2_Raw': eas.destroy_actor(x)
a=eas.spawn_actor_from_object(m,unreal.Vector(7870,9550,0.0018-b.min.z),unreal.Rotator(0,0,0))
a.set_actor_label('TripoCar2_Raw')
print('PLACED',a.get_actor_location())
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
print('SAVED')
