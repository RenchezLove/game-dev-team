import unreal
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
sme=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
meshes=set()
for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.Actor):
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        sm=c.static_mesh
        if sm and sm.get_path_name().startswith('/Game/Environment') and 'AbandonedCar' not in sm.get_path_name():
            meshes.add(sm)
def res(n):
    if 'GroundPlane' in n: return 1024
    if 'House' in n or 'Shed' in n or 'Cave' in n or 'Tent' in n: return 128
    if 'Grass' in n: return 4
    if 'Bush' in n or 'Rock' in n or 'Bone' in n: return 16
    if 'Tree' in n: return 32
    return 32
for sm in sorted(meshes,key=lambda m:m.get_name()):
    ok=sme.set_generate_lightmap_uv(sm,True)
    sm.set_editor_property('light_map_coordinate_index',1)
    sm.set_editor_property('light_map_resolution',res(sm.get_name()))
    sv=unreal.EditorAssetLibrary.save_loaded_asset(sm,False)
    print('MESH',sm.get_name(),ok,'uv',sme.get_num_uv_channels(sm,0),'res',res(sm.get_name()),'saved',sv)
