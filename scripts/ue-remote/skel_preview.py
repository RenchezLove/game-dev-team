import unreal
sk=unreal.load_asset('/Game/Characters/Shared/Humanoid/HeadAndSkeletonfbx_Head_Skeleton')
for p in ('sockets','preview_attached_asset_container','additional_preview_skeletal_meshes'):
    try:
        v=sk.get_editor_property(p); print('SKEL',p,v)
        if p=='sockets':
            for s in v: print('   SOCKET',s.get_editor_property('socket_name'),s.get_editor_property('bone_name'),s.get_editor_property('relative_location'),s.get_editor_property('relative_rotation'),s.get_editor_property('relative_scale'))
    except Exception as e: print('SKEL',p,'ERR',e)
ar=unreal.AssetRegistryHelpers.get_asset_registry()
for a in ar.get_assets_by_path('/Game/Characters',recursive=True):
    if str(a.asset_class_path.asset_name)=='SkeletalMesh':
        m=unreal.load_asset(str(a.package_name))
        for p in ('preview_attached_asset_container',):
            try:
                v=m.get_editor_property(p)
                if v: print('MESH',a.package_name,p,v)
            except Exception as e: pass
        try:
            n=m.num_sockets()
            for i in range(n):
                s=m.get_socket_by_index(i); print('MSOCK',a.package_name,s.get_editor_property('socket_name'),s.get_editor_property('bone_name'),s.get_editor_property('relative_scale'))
        except Exception as e: pass
an=unreal.load_asset('/Game/Characters/Shared/Humanoid/Anim_PistolIdle_Humanoid')
for p in ('preview_skeletal_mesh','preview_pose_asset'):
    try: print('ANIM',p,an.get_editor_property(p))
    except Exception as e: print('ANIM',p,'ERR',e)
