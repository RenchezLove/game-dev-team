import unreal
eal=unreal.EditorAssetLibrary
H='/Game/Characters/Shared/Humanoid'
tgt=unreal.load_asset(H+'/Retarget/IK_Humanoid')
tc=unreal.IKRigController.get_controller(tgt)
for ch in ('LeftArm','RightArm'): tc.set_retarget_chain_goal(ch,'')
for g in ('LeftHandIK','RightHandIK'): print('RMGOAL',tc.remove_goal(g))
while tc.get_num_solvers()>0: print('RMSOLVER',tc.remove_solver(0))
print('SAVE',eal.save_loaded_asset(tgt,False))
if eal.does_asset_exist('/Game/Idle_Pistol_IK'): print('DELIK',eal.delete_asset('/Game/Idle_Pistol_IK'))
NEWP=H+'/Anim_PistolIdle_Humanoid'; OLDP=H+'/Anim_AimPistol_Humanoid'; BAK=H+'/Anim_AimPistol_Humanoid_Old'
if eal.does_asset_exist('/Game/Idle_Pistol_Humanoid'): print('MOVE',eal.rename_asset('/Game/Idle_Pistol_Humanoid',NEWP))
ar=unreal.AssetRegistryHelpers.get_asset_registry()
print('OLD REFS',[str(r) for r in ar.get_referencers(OLDP,unreal.AssetRegistryDependencyOptions())])
if not eal.does_asset_exist(BAK): print('BAK',eal.duplicate_asset(OLDP,BAK) is not None)
new=unreal.load_asset(NEWP); old=unreal.load_asset(OLDP)
print('CONSOLIDATE',eal.consolidate_assets(new,[old]))
abp=unreal.load_asset(H+'/ABP_HumanoidCharacter')
unreal.BlueprintEditorLibrary.compile_blueprint(abp)
print('ABP SAVE',eal.save_asset(H+'/ABP_HumanoidCharacter',only_if_is_dirty=False))
print('ALL',unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True))
print('NEW REFS',[str(r) for r in ar.get_referencers(NEWP,unreal.AssetRegistryDependencyOptions())])
print('OLD EXISTS',eal.does_asset_exist(OLDP),'BAK',eal.does_asset_exist(BAK))
