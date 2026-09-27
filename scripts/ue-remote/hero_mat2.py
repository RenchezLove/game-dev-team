import unreal
d='/Game/Characters/Shared/Clothing'
m=unreal.load_asset(d+'/M_HeroTripo')
for s2 in ['Head','Torso','Legs']:
    sk=unreal.load_asset(d+'/SK_Cloth_T0_'+s2)
    old=sk.get_editor_property('materials')
    new=[]
    for x in old:
        y=unreal.SkeletalMaterial()
        y.set_editor_property('material_interface',m)
        y.set_editor_property('material_slot_name',x.get_editor_property('material_slot_name'))
        new.append(y)
    sk.set_editor_property('materials',new)
    unreal.EditorAssetLibrary.save_loaded_asset(sk,False)
    sk=unreal.load_asset(d+'/SK_Cloth_T0_'+s2)
    print(s2,[(x.get_editor_property('material_slot_name'),x.get_editor_property('material_interface').get_name()) for x in sk.get_editor_property('materials')])
