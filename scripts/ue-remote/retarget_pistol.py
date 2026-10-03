import unreal
at=unreal.AssetToolsHelpers.get_asset_tools(); eal=unreal.EditorAssetLibrary
D='/Game/Characters/Shared/Humanoid/Retarget'
SRC_MESH=unreal.load_asset('/Game/AnimStarterPack/Character/HeroTPP')
TGT_MESH=unreal.load_asset('/Game/Characters/Shared/Clothing/SK_Cloth_T0_Torso')
def mk(name,cls,fac):
    p=D+'/'+name
    if eal.does_asset_exist(p): eal.delete_asset(p)
    return at.create_asset(name,D,cls,fac)
src=mk('IK_AnimStarterPack',unreal.IKRigDefinition,unreal.IKRigDefinitionFactory())
sc=unreal.IKRigController.get_controller(src)
print('SRC mesh',sc.set_skeletal_mesh(SRC_MESH))
print('SRC auto',sc.apply_auto_generated_retarget_definition())
print('SRC root',sc.get_retarget_root(),'chains',[(str(c.get_editor_property('chain_name')),str(sc.get_retarget_chain_start_bone(c.get_editor_property('chain_name'))),str(sc.get_retarget_chain_end_bone(c.get_editor_property('chain_name')))) for c in sc.get_retarget_chains()])
tgt=mk('IK_Humanoid',unreal.IKRigDefinition,unreal.IKRigDefinitionFactory())
tc=unreal.IKRigController.get_controller(tgt)
print('TGT mesh',tc.set_skeletal_mesh(TGT_MESH))
print('TGT root',tc.set_retarget_root('C_Root'))
for n,a,b in [('Spine','C_Spine01','C_Spine02'),('Neck','C_Neck','C_Neck'),('Head','C_Head','C_Head'),('LeftClavicle','L_UpperArm','L_UpperArm'),('LeftArm','L_Shoulder','L_Hand'),('RightClavicle','R_UpperArm','R_UpperArm'),('RightArm','R_Arm','R_Hand'),('LeftLeg','L_Thigh','L_Foot'),('RightLeg','R_Thigh','R_Foot')]:
    print('TGT chain',n,tc.add_retarget_chain(n,a,b,''))
print('TGT chains',[(str(c.get_editor_property('chain_name')),str(tc.get_retarget_chain_start_bone(c.get_editor_property('chain_name'))),str(tc.get_retarget_chain_end_bone(c.get_editor_property('chain_name')))) for c in tc.get_retarget_chains()])
rt=mk('RTG_AnimStarterPack_To_Humanoid',unreal.IKRetargeter,unreal.IKRetargetFactory())
rc=unreal.IKRetargeterController.get_controller(rt)
S=unreal.RetargetSourceOrTarget
rc.set_ik_rig(S.SOURCE,src); rc.set_ik_rig(S.TARGET,tgt)
rc.set_preview_mesh(S.SOURCE,SRC_MESH); rc.set_preview_mesh(S.TARGET,TGT_MESH)
rc.auto_map_chains(unreal.AutoMapChainType.FUZZY,True)
for c in tc.get_retarget_chains():
    print('MAP',c.get_editor_property('chain_name'),'<-',rc.get_source_chain(c.get_editor_property('chain_name')))
try: rc.auto_align_all_bones(S.TARGET)
except Exception as e:
    print('ALIGN1',e); rc.auto_align_all_bones(S.TARGET,unreal.RetargetAutoAlignMethod.CHAIN_TO_CHAIN)
for p in (src,tgt,rt): print('SAVE',eal.save_loaded_asset(p,False))
anims=[unreal.AssetRegistryHelpers.get_asset_registry().get_asset_by_object_path('/Game/AnimStarterPack/Idle_Pistol.Idle_Pistol')]
out=unreal.IKRetargetBatchOperation.duplicate_and_retarget(anims,SRC_MESH,TGT_MESH,rt,'','','','_Humanoid',False)
print('OUT',[str(o.package_name) for o in out])
