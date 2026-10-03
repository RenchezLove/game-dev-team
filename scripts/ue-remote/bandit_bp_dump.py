import unreal
cls=unreal.load_asset('/Game/Characters/Bandit/BP_EnemyBandit').generated_class(); cdo=unreal.get_default_object(cls)
for c in cdo.get_components_by_class(unreal.SkeletalMeshComponent):
    sk=c.get_skeletal_mesh_asset()
    print('CDO comp',c.get_name(),'mesh',sk.get_path_name() if sk else None,'override',[m.get_name() if m else None for m in c.get_editor_property('override_materials')])
for p in ['head_mesh','torso_mesh','legs_mesh','head_mesh_asset','torso_mesh_asset','legs_mesh_asset','merged_material','body_material']:
    try: print('PROP',p,cdo.get_editor_property(p))
    except Exception as e: pass
print('REFS M_Bandit_VColor',unreal.EditorAssetLibrary.find_package_referencers_for_asset('/Game/Characters/Bandit/M_Bandit_VColor',False))
for s in ['Head','Torso','Legs']:
    print('REFS',s,unreal.EditorAssetLibrary.find_package_referencers_for_asset('/Game/Characters/Bandit/SK_Bandit_'+s,False))
