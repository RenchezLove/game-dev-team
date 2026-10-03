import unreal
X=unreal.AnimPoseExtensions
P='/Game/Idle_Pistol_Humanoid'
an=unreal.load_asset(P)
n=an.get_editor_property('number_of_sampled_keys'); L=an.get_play_length()
o=unreal.AnimPoseEvaluationOptions()
keys={'RootAnim':([],[],[]),'C_Root':([],[],[])}
for i in range(n):
    pose=X.get_anim_pose_at_time(an,L*i/(n-1),o)
    r=X.get_bone_pose(pose,'RootAnim',unreal.AnimPoseSpaces.LOCAL)
    c=X.get_bone_pose(pose,'C_Root',unreal.AnimPoseSpaces.LOCAL)
    keys['RootAnim'][0].append(unreal.Vector(0,0,0)); keys['RootAnim'][1].append(r.rotation); keys['RootAnim'][2].append(unreal.Vector(100,100,100))
    t=c.translation
    keys['C_Root'][0].append(unreal.Vector(t.x/100.0,t.y/100.0,t.z/100.0)); keys['C_Root'][1].append(c.rotation); keys['C_Root'][2].append(unreal.Vector(1,1,1))
ctrl=an.controller
ctrl.open_bracket(unreal.Text('fix root scale'),False)
for b,(p,r,s) in keys.items():
    print('SET',b,ctrl.set_bone_track_keys(b,p,r,s,False))
ctrl.close_bracket(False)
print('SAVE',unreal.EditorAssetLibrary.save_asset(P,only_if_is_dirty=False))
