import unreal
eal=unreal.EditorAssetLibrary
D='/Game/Characters/Shared/Humanoid/Retarget'
SRC_MESH=unreal.load_asset('/Game/AnimStarterPack/Character/HeroTPP')
TGT_MESH=unreal.load_asset('/Game/Characters/Shared/Clothing/SK_Cloth_T0_Torso')
tgt=unreal.load_asset(D+'/IK_Humanoid'); rt=unreal.load_asset(D+'/RTG_AnimStarterPack_To_Humanoid')
tc=unreal.IKRigController.get_controller(tgt)
if tc.get_num_solvers()==0:
    i=tc.add_solver(unreal.IKRigFBIKSolver)
    print('SOLVER',i,tc.set_root_bone('C_Root',i))
    for g,b,ch in [('LeftHandIK','L_Hand','LeftArm'),('RightHandIK','R_Hand','RightArm')]:
        print('GOAL',tc.add_new_goal(g,b),tc.connect_goal_to_solver(g,i),tc.set_retarget_chain_goal(ch,g))
print('SAVE',eal.save_loaded_asset(tgt,False),eal.save_loaded_asset(rt,False))
if eal.does_asset_exist('/Game/Idle_Pistol_IK'): eal.delete_asset('/Game/Idle_Pistol_IK')
anims=[unreal.AssetRegistryHelpers.get_asset_registry().get_asset_by_object_path('/Game/AnimStarterPack/Idle_Pistol.Idle_Pistol')]
out=unreal.IKRetargetBatchOperation.duplicate_and_retarget(anims,SRC_MESH,TGT_MESH,rt,'','','','_IK',False)
print('OUT',[str(o.package_name) for o in out])
