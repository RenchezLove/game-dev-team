import unreal
D='/Game/Environment/Props/Tripo/MI_TripoBarrel_'
t=unreal.AssetImportTask()
t.set_editor_property('filename','E:/game-dev-team/assets/barrel_tripo/SM_TripoBarrel.fbx')
t.set_editor_property('destination_path','/Game/Environment/Props')
t.set_editor_property('destination_name','SM_BanditBarrel')
t.set_editor_property('replace_existing',True); t.set_editor_property('automated',True); t.set_editor_property('save',True)
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
print('IMPORTED',list(t.get_editor_property('imported_object_paths')))
sm=unreal.load_asset('/Game/Environment/Props/SM_BanditBarrel')
ses=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
ag=sm.get_editor_property('body_setup').get_editor_property('agg_geom')
nc=len(ag.get_editor_property('convex_elems'))+len(ag.get_editor_property('box_elems'))+len(ag.get_editor_property('sphyl_elems'))
if nc==0:
    ses.add_simple_collisions(sm,unreal.ScriptCollisionShapeType.NDOP10_Z)
sm.set_material(0,unreal.load_asset(D+'Grey'))
unreal.EditorAssetLibrary.save_loaded_asset(sm,False)
ag=sm.get_editor_property('body_setup').get_editor_property('agg_geom')
b=sm.get_bounding_box()
print('SM tris',sm.get_num_triangles(0),'size',[round(x) for x in (b.max-b.min).to_tuple()],'minz',round(b.min.z,2),'convex',len(ag.get_editor_property('convex_elems')),'mat',sm.get_material(0).get_name())
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
cyc=['Blue','Green','Red','Yellow','Grey']; i=0
for x in eas.get_all_level_actors():
    l=x.get_actor_label()
    if l=='TripoBarrel_Test' or l.startswith('TripoBarrel_'):
        eas.destroy_actor(x); print('DEL',l); continue
    if isinstance(x,unreal.StaticMeshActor) and x.static_mesh_component.static_mesh==sm:
        k=cyc[i%5]; i+=1
        x.static_mesh_component.set_material(0,unreal.load_asset(D+k)); print('COLOR',l,k,x.get_actor_location())
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level(); print('SAVED')
print('TRIPO_REFS',[str(r) for r in unreal.EditorAssetLibrary.find_package_referencers_for_asset('/Game/Environment/Props/Tripo/SM_TripoBarrel',False)])
