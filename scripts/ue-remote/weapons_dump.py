import unreal
sms=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem); eal=unreal.EditorAssetLibrary
for p in ['/Game/Weapons/SM_Pistol','/Game/Weapons/SM_Knife','/Game/Weapons/Knife/SM_Knife']:
    sm=unreal.load_asset(p); b=sm.get_bounding_box()
    print(p,'tris',sm.get_num_triangles(0),'min',[round(v,1) for v in (b.min.x,b.min.y,b.min.z)],'max',[round(v,1) for v in (b.max.x,b.max.y,b.max.z)],'mats',[x.material_interface.get_path_name() if x.material_interface else None for x in sm.get_editor_property('static_materials')],'sockets',[str(s.socket_name) for s in sm.get_editor_property('sockets')] if hasattr(sm,'sockets') else '-','uv',sms.get_num_uv_channels(sm,0))
    print('   REFS',eal.find_package_referencers_for_asset(p,False))
