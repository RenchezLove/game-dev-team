import unreal
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
print([x for x in dir(unreal.LightmapType)])
for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.InstancedFoliageActor):
    for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        if 'Grass' in c.static_mesh.get_name():
            c.set_editor_property('lightmap_type',unreal.LightmapType.FORCE_VOLUMETRIC)
            print('GRASS',c.static_mesh.get_name(),c.get_editor_property('lightmap_type'))
print('LVL',unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level())
