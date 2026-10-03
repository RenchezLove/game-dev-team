import unreal, math
X=unreal.AnimPoseExtensions
P='/Game/Characters/Shared/Humanoid/Anim_PistolIdle_Humanoid'
OFF_WORLD=(8.8,3.6,-2.9)
an=unreal.load_asset(P)
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
    if d<-0.999999:
        ax=nrm(cross(a,(1,0,0))) if abs(a[0])<0.9 else nrm(cross(a,(0,1,0))); return (ax[0],ax[1],ax[2],0.0)
    c=cross(a,b); return qnorm((c[0],c[1],c[2],1.0+d))
def qdiff(a,b): return 1.0-abs(sum(x*y for x,y in zip(a,b)))
def bp(pose,b,sp): return X.get_bone_pose(pose,b,sp)
pose0=X.get_anim_pose_at_time(an,0.0,o)
for child,parent in (('L_Shoulder','L_UpperArm'),('L_Arm','L_Shoulder'),('L_Hand','L_Arm')):
    calc=qmul(qconj(q(bp(pose0,parent,W).rotation)),q(bp(pose0,child,W).rotation))
    d=qdiff(calc,q(bp(pose0,child,LOC).rotation))
    print('HIERARCHY',child,'<-',parent,'err',round(d,6))
    if d>1e-3: raise Exception('hierarchy assumption wrong for '+child)
r0=bp(pose0,'R_Hand',W)
off_local=qrot(qconj(q(r0.rotation)),OFF_WORLD)
keys={b:([],[],[]) for b in ('L_Shoulder','L_Arm','L_Hand')}
before=[];after=[];clamped=0
for i in range(n):
    pose=X.get_anim_pose_at_time(an,L*i/(n-1),o)
    S=v(bp(pose,'L_Shoulder',W).translation); E=v(bp(pose,'L_Arm',W).translation); H=v(bp(pose,'L_Hand',W).translation)
    rh=bp(pose,'R_Hand',W); T=add(v(rh.translation),qrot(q(rh.rotation),off_local))
    l1=ln(sub(E,S)); l2=ln(sub(H,E))
    d=sub(T,S); dist=ln(d)
    mx=(l1+l2)*0.995
    if dist>mx: T=add(S,mul(nrm(d),mx)); d=sub(T,S); dist=mx; clamped+=1
    dn=nrm(d)
    a=(l1*l1-l2*l2+dist*dist)/(2*dist)
    h=math.sqrt(max(l1*l1-a*a,0.0))
    pole=sub(E,S); pole=sub(pole,mul(dn,dot(pole,dn))); pole=nrm(pole)
    E2=add(add(S,mul(dn,a)),mul(pole,h))
    qS=q(bp(pose,'L_Shoulder',W).rotation); qE=q(bp(pose,'L_Arm',W).rotation); qH=q(bp(pose,'L_Hand',W).rotation); qP=q(bp(pose,'L_UpperArm',W).rotation)
    d1=qbetween(sub(E,S),sub(E2,S))
    qS2=qnorm(qmul(d1,qS))
    lower_dir=qrot(d1,sub(H,E))
    d2=qbetween(lower_dir,sub(T,E2))
    qE2=qnorm(qmul(d2,qmul(d1,qE)))
    locS=qnorm(qmul(qconj(qP),qS2)); locE=qnorm(qmul(qconj(qS2),qE2)); locH=qnorm(qmul(qconj(qE2),qH))
    for b,lq in (('L_Shoulder',locS),('L_Arm',locE),('L_Hand',locH)):
        t=bp(pose,b,LOC).translation
        keys[b][0].append(unreal.Vector(t.x,t.y,t.z)); keys[b][1].append(unreal.Quat(lq[0],lq[1],lq[2],lq[3])); keys[b][2].append(unreal.Vector(1,1,1))
    before.append(ln(sub(H,v(rh.translation)))); after.append(ln(sub(T,v(rh.translation))))
ctrl=an.controller
ctrl.open_bracket(unreal.Text('left hand to grip'),False)
for b,(p,r,s) in keys.items(): print('SET',b,ctrl.set_bone_track_keys(b,p,r,s,False))
ctrl.close_bracket(False)
print('SAVE',unreal.EditorAssetLibrary.save_asset(P,only_if_is_dirty=False))
print('HANDS DIST before',round(min(before),1),round(max(before),1),'target',round(min(after),1),round(max(after),1),'clamped frames',clamped)
for t in (0.0,3.0,6.0):
    pose=X.get_anim_pose_at_time(unreal.load_asset(P),t,o)
    a=v(bp(pose,'L_Hand',W).translation); b=v(bp(pose,'R_Hand',W).translation); e=v(bp(pose,'L_Arm',W).translation); s=v(bp(pose,'L_Shoulder',W).translation)
    print('CHECK t',t,'L_Hand',[round(c,1) for c in a],'R_Hand',[round(c,1) for c in b],'dist',round(ln(sub(a,b)),1),'elbow',[round(c,1) for c in e],'upper',round(ln(sub(e,s)),1),'lower',round(ln(sub(a,e)),1))
