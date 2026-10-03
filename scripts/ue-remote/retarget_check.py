import unreal
X=unreal.AnimPoseExtensions
def show(path,bones,tag,t=0.0):
    an=unreal.load_asset(path)
    o=unreal.AnimPoseEvaluationOptions()
    pose=X.get_anim_pose_at_time(an,t,o)
    names=[str(n) for n in X.get_bone_names(pose)]
    print(tag,path,'skel',an.get_editor_property('skeleton').get_name(),'len',round(an.get_play_length(),2),'bones',len(names))
    for b in bones:
        if b in names:
            tr=X.get_bone_pose(pose,b,unreal.AnimPoseSpaces.WORLD); p=tr.translation; r=tr.rotation.rotator()
            print('   ',b,[round(p.x,1),round(p.y,1),round(p.z,1)],'rot',[round(r.roll),round(r.pitch),round(r.yaw)])
show('/Game/AnimStarterPack/Idle_Pistol',['pelvis','spine_03','clavicle_l','upperarm_l','lowerarm_l','hand_l','clavicle_r','upperarm_r','lowerarm_r','hand_r','head'],'SRC')
T=['C_Root','C_Spine02','L_UpperArm','L_Shoulder','L_Arm','L_Hand','R_UpperArm','R_Arm','Pelvis_009_R_002','R_Hand','C_Head']
show('/Game/Idle_Pistol_Humanoid',T,'NEW')
show('/Game/Idle_Pistol_Humanoid',T,'NEW t=3',3.0)
show('/Game/Characters/Shared/Humanoid/Anim_AimPistol_Humanoid',T,'OLD')
