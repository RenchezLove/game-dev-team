import unreal
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.InstancedFoliageActor):
    for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        n=c.static_mesh.get_name()
        if 'Tree' in n:
            print(n,'used',c.get_material(0).get_path_name(),'overrides',[m.get_name() if m else None for m in c.get_editor_property('override_materials')],'mesh mat',c.static_mesh.get_material(0).get_name())
for p in ['SM_Tree_Birch_01','SM_Tree_02','SM_Tree_03']:
    sm=unreal.load_asset('/Game/Environment/Nature/'+p)
    d=sm.get_static_mesh_description(0); cols={}
    for vi in range(d.get_vertex_instance_count()):
        try: c=d.get_vertex_instance_color(unreal.VertexInstanceID(vi))
        except Exception as e: print('ERR',e); break
        k=(round(c.x,2),round(c.y,2),round(c.z,2)); cols[k]=cols.get(k,0)+1
    print(p,sorted(cols.items(),key=lambda x:-x[1])[:6])
m=unreal.load_asset('/Game/Materials/M_TreeAutumn'); mel=unreal.MaterialEditingLibrary
print({str(n):mel.get_material_default_scalar_parameter_value(m,n) for n in mel.get_scalar_parameter_names(m)})
