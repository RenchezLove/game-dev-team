import unreal
X=unreal.AnimPoseExtensions
sk=unreal.load_asset('/Game/Characters/Shared/Humanoid/HeadAndSkeletonfbx_Head_Skeleton')
ref=X.get_reference_pose(sk)
names=[str(n) for n in X.get_bone_names(ref)]
print('NAMES',names)
def loc(pose,tag):
    for b in names:
        tr=X.get_bone_pose(pose,b,unreal.AnimPoseSpaces.LOCAL)
        s=tr.scale3d; p=tr.translation
        if abs(s.x-1)>0.001 or b in ('RootAnim','C_Root','C_Spine01','L_Shoulder'):
            print(tag,b,'scale',[round(s.x,4),round(s.y,4),round(s.z,4)],'loc',[round(p.x,3),round(p.y,3),round(p.z,3)])
loc(ref,'REF')
o=unreal.AnimPoseEvaluationOptions()
loc(X.get_anim_pose_at_time(unreal.load_asset('/Game/Idle_Pistol_Humanoid'),0.0,o),'NEW')
loc(X.get_anim_pose_at_time(unreal.load_asset('/Game/Characters/Shared/Humanoid/Anim_AimPistol_Humanoid'),0.0,o),'OLD')
an=unreal.load_asset('/Game/Idle_Pistol_Humanoid')
print('FRAMES',an.get_editor_property('number_of_sampled_keys'),'rate',an.get_editor_property('target_frame_rate') if hasattr(an,'target_frame_rate') else '?')
print('CTRL',[x for x in dir(an.controller) if 'bone' in x.lower() or 'key' in x.lower()])
