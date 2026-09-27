"""Skin check of the hero slots: weight report of neck/shoulder verts + close-up
renders in the real game poses: melee slash (peak reach frame and neighbours),
rest, run (RunAnimation frame 10), pistol aim.
Run: blender.exe -b --factory-startup --python 15_skin_check.py -- <tag>
Out: assets/hero_tripo/renders/skin/<tag>_<pose>_<view>.png
"""
import bpy, sys, os, math
sys.path.insert(0, 'E:/game-dev-team/assets/hero_tripo/_work')
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W
import hpose as P
import addon_utils
from mathutils import Vector

TAG = sys.argv[sys.argv.index('--') + 1] if '--' in sys.argv else 'cur'
OUT = 'E:/game-dev-team/assets/hero_tripo/renders/skin/'
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath='E:/game-dev-team/assets/hero_tripo/_work/hero_work.blend')
addon_utils.enable('io_scene_fbx')
rig = bpy.data.objects['RootAnim']
parts = [bpy.data.objects[n] for n in ('SK_Cloth_T0_Head', 'SK_Cloth_T0_Torso', 'SK_Cloth_T0_Legs')]
print('RIG world identity:', rig.matrix_world == rig.matrix_world.Identity(4))
for bn in ('C_Spine02', 'C_Neck', 'C_Head', 'L_UpperArm', 'R_UpperArm', 'L_Shoulder', 'R_Arm'):
    b = rig.data.bones[bn]
    print('BONE %-11s head=%s tail=%s' % (bn, tuple(round(a, 3) for a in b.head_local),
                                         tuple(round(a, 3) for a in b.tail_local)))

# ---- weight report: which bones hold the neck and the shoulder tops ----
ZONES = {
    'neck (z 1.46..1.60, r<0.11)': lambda c: 1.46 < c.z < 1.60 and math.hypot(c.x, c.y) < 0.11,
    'upper back (z 1.30..1.50, y>0.02, |x|<0.16)': lambda c: 1.30 < c.z < 1.50 and c.y > 0.02 and abs(c.x) < 0.16,
    'R shoulder top (x -0.10..-0.30, z>1.40)': lambda c: -0.30 < c.x < -0.10 and c.z > 1.40,
    'L shoulder top (x 0.10..0.30, z>1.40)': lambda c: 0.10 < c.x < 0.30 and c.z > 1.40,
}
for zn, pred in ZONES.items():
    agg = {}
    n = 0
    for ob in parts:
        gn = {g.index: g.name for g in ob.vertex_groups}
        for v in ob.data.vertices:
            if not pred(v.co):
                continue
            n += 1
            for g in v.groups:
                if g.weight > 0.01:
                    a = agg.setdefault(gn[g.group], [0.0, 0, 0.0])
                    a[0] += g.weight; a[1] += 1; a[2] = max(a[2], g.weight)
    print('ZONE %s: %d verts' % (zn, n))
    for k, a in sorted(agg.items(), key=lambda kv: -kv[1][0]):
        print('    %-17s share=%.2f verts=%d max=%.2f' % (k, a[0] / max(n, 1), a[1], a[2]))

sc, cam, suns = W.setup_render(res=560)
sc.render.film_transparent = False
VIEWS = {'backL': (0.55, 1, 0.75), 'backR': (-0.55, 1, 0.75), 'front': (0.25, -1, 0.35)}
UPPER = ((0, 0, 1.30), 1.25)   # neck + shoulders + upper arms


def shots(tag, views=VIEWS, frame=UPPER):
    for vn, vd in views.items():
        P.shoot(vd, frame[0], frame[1], OUT + '%s_%s_%s.png' % (TAG, tag, vn), suns)


# ---- melee: frames with the right hand furthest forward ----
# FBX reference (clean re-import of Anim_MeleeSlash_Humanoid.fbx, _dbg_anim.py):
# R_Hand head f1 (-0.530,-0.529,1.027), f15 (0.285,-0.489,1.201)
src, names = P.load_source(P.ANIM_QC, 'Anim_MeleeSlash_Humanoid', 'MeleeSrc')
print('MELEE source rest delta vs ours = %.6f' % P.rest_delta(src, names, rig))
reach = []
for f in range(1, 22):
    P.transfer(src, names, rig, f)
    h = rig.pose.bones['R_Hand'].head
    c = rig.pose.bones['R_UpperArm']
    ang = math.degrees(c.matrix.to_quaternion().rotation_difference(c.bone.matrix_local.to_quaternion()).angle)
    reach.append((h.y, f))
    print('MELEE f=%2d R_Hand=(%.3f,%.3f,%.3f) clavicle turn=%.0f deg' % (f, h.x, h.y, h.z, ang))
fpk = min(reach)[1]
MELEE = sorted({max(1, fpk - 2), fpk, min(21, fpk + 2)})
print('MELEE peak reach frame', fpk, 'shots', MELEE)
for f in MELEE:
    P.transfer(src, names, rig, f)
    shots('melee%02d' % f)
bpy.data.objects.remove(src, do_unlink=True)

# ---- rest ----
P.reset(rig)
shots('rest', {'backL': VIEWS['backL'], 'front': VIEWS['front']})

# ---- run frame 10 ----
src, names = P.load_source(P.RUN, None, 'RunSrc')
print('RUN source rest delta vs ours = %.6f' % P.rest_delta(src, names, rig))
P.transfer(src, names, rig, 10)
shots('run10', {'backL': VIEWS['backL'], 'front': VIEWS['front']})
bpy.data.objects.remove(src, do_unlink=True)

# ---- pistol aim ----
src, names = P.load_source(P.ANIM_QC, 'Anim_AimPistol_Humanoid', 'AimSrc')
P.transfer(src, names, rig, 1)
shots('aim', {'backL': VIEWS['backL'], 'front': VIEWS['front']})
P.reset(rig)
print('DONE', TAG)
