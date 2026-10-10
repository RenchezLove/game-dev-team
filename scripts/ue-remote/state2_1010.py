import unreal
eal = unreal.EditorAssetLibrary
ar = unreal.AssetRegistryHelpers.get_asset_registry()
for bp in ['/Game/Weapons/Pistol/BP_Pistol', '/Game/Items/BP_Ammo9mm', '/Game/Characters/Trader/BP_Trader', '/Game/Characters/Elder/BP_Elder', '/Game/Characters/ScientistGuard/BP_ScientistGuard', '/Game/Items/BP_Laptop']:
    b = unreal.load_asset(bp); cls = b.generated_class(); cdo = unreal.get_default_object(cls)
    d = ar.get_asset_by_object_path(bp + '.' + bp.rsplit('/', 1)[1])
    print('BP', bp, 'PARENT', d.get_tag_value('ParentClass'), 'NATIVE', d.get_tag_value('NativeParentClass'))
    for c in cdo.get_components_by_class(unreal.MeshComponent):
        m = c.get_editor_property('static_mesh') if isinstance(c, unreal.StaticMeshComponent) else None
        print('   comp', c.get_name(), c.get_class().get_name(), m.get_path_name() if m else '', 'rel', c.get_editor_property('relative_location'), c.get_editor_property('relative_rotation'), c.get_editor_property('relative_scale3d'))
print(eal.list_assets('/Game/Weapons', True, False))
print(eal.list_assets('/Game/Items', True, False))
print(eal.list_assets('/Game/Environment/Props/ScientistBase', False, False))
