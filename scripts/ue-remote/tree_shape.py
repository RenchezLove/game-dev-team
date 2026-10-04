import unreal, math
for p in ['SM_Tree_02','SM_Tree_03','SM_Tree_Birch_01','SM_Tree_Pine_01','SM_Tree_Pine_02']:
    sm=unreal.load_asset('/Game/Environment/Nature/'+p); d=sm.get_static_mesh_description(0)
    pts=[d.get_vertex_position(unreal.VertexID(i)) for i in range(d.get_vertex_count())]
    zmax=max(v.z for v in pts); bands=[0]*8
    for v in pts:
        b=min(7,int(v.z/zmax*8)); bands[b]=max(bands[b],math.hypot(v.x,v.y))
    print(p,'h',round(zmax),'radius by height band',[round(x) for x in bands])
