import unreal
X=unreal.AnimPoseExtensions
def bones(mesh_path,tag):
    m=unreal.load_asset(mesh_path).get_editor_property("skeleton")
    pose=X.get_reference_pose(m)
    for n in X.get_bone_names(pose):
        t=X.get_bone_pose(pose,n,unreal.AnimPoseSpaces.WORLD).translation
        par=None
        try: par=X.get_bone_parent_name(pose,n)
        except Exception as e: par='?'
        print('BONE',tag,n,'<-',par,[round(t.x,1),round(t.y,1),round(t.z,1)])
bones('/Game/AnimStarterPack/Character/HeroTPP','SRC')
bones('/Game/Characters/Shared/Clothing/SK_Cloth_T0_Torso','TGT')
print('IKAPI',[x for x in dir(unreal.IKRigController) if not x.startswith('_')])
print('RTAPI',[x for x in dir(unreal.IKRetargeterController) if not x.startswith('_')])
print('BATCH',[x for x in dir(unreal.IKRetargetBatchOperation) if not x.startswith('_')])
