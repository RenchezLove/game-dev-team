import unreal
ar=unreal.AssetRegistryHelpers.get_asset_registry()
tot=0
for s in ['Head','Torso','Legs']:
    d=ar.get_asset_by_object_path('/Game/Characters/Shared/Clothing/SK_Cloth_T0_%s.SK_Cloth_T0_%s'%(s,s))
    t=d.get_tag_value('Triangles'); v=d.get_tag_value('Vertices')
    print(s,'tris',t,'verts',v); tot+=int(t)
print('TOTAL',tot)
