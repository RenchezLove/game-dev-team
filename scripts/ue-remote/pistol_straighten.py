import unreal, math
X=unreal.AnimPoseExtensions
H='/Game/Characters/Shared/Humanoid'
P=H+'/Anim_PistolIdle_Humanoid'
RAISE_CM=5.0
an=unreal.load_asset(P); idle=unreal.load_asset(H+'/Ainm_Idle_HumanoidCharacter')
n=an.get_editor_property('number_of_sampled_keys'); L=an.get_play_length()
o=unreal.AnimPoseEvaluationOptions()
W=unreal.AnimPoseSpaces.WORLD; LOC=unreal.AnimPoseSpaces.LOCAL
def q(r): return (r.x,r.y,r.z,r.w)
def v(t): return (t.x,t.y,t.z)
def qmul(a,b):
    ax,ay,az,aw=a; bx,by,bz,bw=b
    return (aw*bx+ax*bw+ay*bz-az*by, aw*by-ax*bz+ay*bw+az*bx, aw*bz+ax*by-ay*bx+az*bw, aw*bw-ax*bx-ay*by-az*bz)
def qconj(a): return (-a[0],-a[1],-a[2],a[3])
def qrot(a,p):
    r=qmul(qmul(a,(p[0],p[1],p[2],0.0)),qconj(a)); return (r[0],r[1],r[2])
def sub(a,b): return (a[0]-b[0],a[1]-b[1],a[2]-b[2])
def add(a,b): return (a[0]+b[0],a[1]+b[1],a[2]+b[2])
def mul(a,s): return (a[0]*s,a[1]*s,a[2]*s)
def dot(a,b): return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]
def cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def ln(a): return math.sqrt(dot(a,a))
def nrm(a):
    l=ln(a); return mul(a,1.0/l) if l>1e-8 else (0,0,0)
def qnorm(a):
    l=math.sqrt(sum(c*c for c in a)); return tuple(c/l for c in a)
def qbetween(a,b):
    a=nrm(a); b=nrm(b); d=dot(a,b)
    if d>0.999999: return (0,0,0,1)
    c=cross(a,b); return qnorm((c[0],c[1],c[2],1.0+d))
def qdiff(a,b): return 1.0-abs(sum(x*y for x,y in zip(a,b)))
def bp(pose,b,sp): return X.get_bone_pose(pose,b,sp)
def poses(): return [X.get_anim_pose_at_time(an,L*i/(n-1),o) for i in range(n)]
def write(keys,label):
    c=an.controller; c.open_bracket(unreal.Text(label),False)
    for b,(p,r,s) in keys.items(): print('SET',label,b,c.set_bone_track_keys(b,p,r,s,False))
    c.close_bracket(False)
def key(keys,b,pose,lq):
    t=bp(pose,b,LOC).translation
    keys.setdefault(b,([],[],[]))
    keys[b][0].append(unreal.Vector(t.x,t.y,t.z)); keys[b][1].append(unreal.Quat(lq[0],lq[1],lq[2],lq[3])); keys[b][2].append(unreal.Vector(1,1,1))
def yaw_of(qw,axis=(0,1,0)):
    f=qrot(qw,axis); return math.degrees(math.atan2(f[0],f[1]))
p0=poses()[0]
for child,parent in (('C_Spine01','C_Root'),('R_Arm','R_UpperArm'),('Pelvis_009_R_002','R_Arm'),('R_Hand','Pelvis_009_R_002'),('L_Shoulder','L_UpperArm'),('L_Arm','L_Shoulder'),('L_Hand','L_Arm')):
    d=qdiff(qmul(qconj(q(bp(p0,parent,W).rotation)),q(bp(p0,child,W).rotation)),q(bp(p0,child,LOC).rotation))
    print('HIER',child,'<-',parent,round(d,6))
    if d>1e-3: raise Exception('hierarchy '+child)
ip=X.get_anim_pose_at_time(idle,0.0,o)
Wroot_idle=q(bp(ip,'C_Root',W).rotation)
print('ROOT idle rot',bp(ip,'C_Root',W).rotation.rotator(),'pose rot',bp(p0,'C_Root',W).rotation.rotator())
off_local=qrot(qconj(q(bp(p0,'R_Hand',W).rotation)),sub(v(bp(p0,'L_Hand',W).translation),v(bp(p0,'R_Hand',W).translation)))
print('HANDS offset len',round(ln(off_local),1))
# A) upper body: make spine world orientation in game (pelvis from locomotion) equal to the authored full pose
keys={}
for pose in poses():
    key(keys,'C_Spine01',pose,qnorm(qmul(qconj(Wroot_idle),q(bp(pose,'C_Spine01',W).rotation))))
write(keys,'spine straight')
def ik(chain,parent,target_fn,label):
    S_,E_,H_=chain; keys={}; cl=0
    for pose in poses():
        S=v(bp(pose,S_,W).translation); E=v(bp(pose,E_,W).translation); Hh=v(bp(pose,H_,W).translation)
        T=target_fn(pose)
        l1=ln(sub(E,S)); l2=ln(sub(Hh,E)); d=sub(T,S); dist=ln(d); mx=(l1+l2)*0.995
        if dist>mx: T=add(S,mul(nrm(d),mx)); d=sub(T,S); dist=mx; cl+=1
        dn=nrm(d); a=(l1*l1-l2*l2+dist*dist)/(2*dist); h=math.sqrt(max(l1*l1-a*a,0.0))
        pole=sub(E,S); pole=nrm(sub(pole,mul(dn,dot(pole,dn))))
        E2=add(add(S,mul(dn,a)),mul(pole,h))
        qS=q(bp(pose,S_,W).rotation); qE=q(bp(pose,E_,W).rotation); qH=q(bp(pose,H_,W).rotation); qP=q(bp(pose,parent,W).rotation)
        d1=qbetween(sub(E,S),sub(E2,S)); qS2=qnorm(qmul(d1,qS))
        d2=qbetween(qrot(d1,sub(Hh,E)),sub(T,E2)); qE2=qnorm(qmul(d2,qmul(d1,qE)))
        key(keys,S_,pose,qnorm(qmul(qconj(qP),qS2))); key(keys,E_,pose,qnorm(qmul(qconj(qS2),qE2))); key(keys,H_,pose,qnorm(qmul(qconj(qE2),qH)))
    write(keys,label); print('IK',label,'clamped',cl)
# B) raise right hand (up in game frame)
def right_target(pose):
    up=qrot(qmul(q(bp(pose,'C_Root',W).rotation),qconj(Wroot_idle)),(0,0,1))
    return add(v(bp(pose,'R_Hand',W).translation),mul(up,RAISE_CM))
ik(('R_Arm','Pelvis_009_R_002','R_Hand'),'R_UpperArm',right_target,'right hand up')
# C) left hand back to the grip
def left_target(pose):
    rh=bp(pose,'R_Hand',W); return add(v(rh.translation),qrot(q(rh.rotation),off_local))
ik(('L_Shoulder','L_Arm','L_Hand'),'L_UpperArm',left_target,'left hand grip')
# report in GAME frame (pelvis as in idle)
for t in (0.0,3.0):
    pose=X.get_anim_pose_at_time(an,t,o)
    G=qmul(Wroot_idle,qconj(q(bp(pose,'C_Root',W).rotation)))
    root=v(bp(pose,'C_Root',W).translation)
    def g(b): return qrot(G,sub(v(bp(pose,b,W).translation),root))
    r=g('R_Hand'); l=g('L_Hand'); hd=g('C_Head'); sp=g('C_Spine02')
    rq=qmul(G,q(bp(pose,'R_Hand',W).rotation)); hq=qmul(G,q(bp(pose,'C_Head',W).rotation))
    rr=unreal.Quat(rq[0],rq[1],rq[2],rq[3]).rotator(); hr=unreal.Quat(hq[0],hq[1],hq[2],hq[3]).rotator()
    print('GAME t',t,'R_Hand rel pelvis',[round(c,1) for c in r],'L_Hand',[round(c,1) for c in l],'hands dist',round(ln(sub(r,l)),1),'chest',[round(c,1) for c in sp],'head',[round(c,1) for c in hd])
    print('     R_Hand rot (roll,pitch,yaw)',[round(rr.roll),round(rr.pitch),round(rr.yaw)],'head rot',[round(hr.roll),round(hr.pitch),round(hr.yaw)])
op=X.get_anim_pose_at_time(unreal.load_asset(H+'/Anim_AimPistol_Humanoid_Old'),0.0,o)
print('OLD AIM R_Hand rot',op and bp(op,'R_Hand',W).rotation.rotator(),'head',bp(op,'C_Head',W).rotation.rotator(),'R_Hand rel pelvis',[round(c,1) for c in sub(v(bp(op,'R_Hand',W).translation),v(bp(op,'C_Root',W).translation))])
print('PIE',unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor())
print('SAVE',unreal.EditorAssetLibrary.save_asset(P,only_if_is_dirty=False))
