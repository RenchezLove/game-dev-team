"""Build Anim_Death_Humanoid: the character takes a hit, buckles and falls flat
on his BACK (Rinat: humanoids die on the back, wolves on the side). One shared
animation for every humanoid (decision: applied in the master class).

Full-body authoring notes (this differs from the Build 1.1 upper-body batch):
  * The rig has THREE parentless root bones: C_Root (torso+arms+head), L_Pelvis
    and R_Pelvis (each leg) - fact from _00_master.log. Laying the body down
    means giving all three the SAME world rotation about the shared hip pivot
    plus the SAME world translation, otherwise the legs stay standing.
  * Those three bones therefore carry LOCATION keys as well as rotation keys.
    Every other keyed bone is rotation-only.
  * Arm directions are authored in the standing body frame and rotated by the
    current body pitch (bdir), so the arms stay attached to the falling torso
    instead of being re-aimed against a moving reference.

Run:  blender.exe -b E:/game-dev-team/assets/armor_wearables/_work/master.blend
          --factory-startup --python 20_build_death.py
"""
import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Vector, Matrix, Quaternion
import acommon as A
from acommon import (X, Y, Z, aim_world, rot_world, upd,
                     SPINE1, SPINE2, NECK, HEAD,
                     L_CLAV, L_UPPER, L_FORE, L_HAND,
                     R_CLAV, R_UPPER, R_FORE, R_HAND)

OUT = 'E:/game-dev-team/assets/anim_humanoid/'
WORK = OUT + '_work/'
NAME = 'Anim_Death_Humanoid'

ROOTS3 = ['C_Root', 'L_Pelvis', 'R_Pelvis']
LEGS = ['L_Thigh', 'L_Claf', 'L_Foot', 'R_Thigh', 'R_Claf', 'R_Foot']
ARMS = [L_CLAV, L_UPPER, L_FORE, L_HAND, R_CLAV, R_UPPER, R_FORE, R_HAND]
TORSO = [SPINE1, SPINE2, NECK, HEAD]
KEYED = ROOTS3 + TORSO + ARMS + LEGS          # 21 bones, full body


def fall_root(pb, pitch_deg, dy, dz, pivot):
    """World rotation about X through the shared hip pivot + world translation.
    Unlike rot_world this KEEPS the translation - that is the point."""
    upd()
    M = pb.matrix.copy()
    R = Matrix.Rotation(math.radians(pitch_deg), 4, X)
    pb.matrix = (Matrix.Translation(pivot + Vector((0.0, dy, dz)))
                 @ R @ Matrix.Translation(-pivot) @ M)
    pb.scale = (1.0, 1.0, 1.0)
    upd()


def bdir(v, pitch_deg):
    """Standing-body-frame direction -> world, following the body pitch."""
    return (Matrix.Rotation(math.radians(pitch_deg), 4, X) @ Vector(v)).normalized()


# Arm shapes in the STANDING body frame (left side; right is mirrored in x with
# a 0.85 factor on the z reach so the two arms never land perfectly symmetric).
# Columns: upper arm, forearm, hand.
ARM_SETS = {
    'neutral': ((0.32, -0.06, -0.94), (0.45, -0.20, -0.86), (0.50, -0.28, -0.80)),
    'hit':     ((0.55, -0.15, -0.80), (0.62, -0.38, -0.65), (0.66, -0.45, -0.55)),
    'flail':   ((0.72, -0.45, -0.42), (0.55, -0.72, -0.12), (0.50, -0.80, 0.05)),
    'up':      ((0.80, -0.48, -0.08), (0.62, -0.70, 0.20),  (0.55, -0.72, 0.30)),
    'wide':    ((0.90, -0.12, -0.30), (0.94, -0.05, -0.20), (0.95, 0.00, -0.15)),
    'final':   ((0.88, 0.06, 0.36),   (0.92, 0.02, 0.30),   (0.93, 0.00, 0.26)),
}

# fr, pitch, dy, dz, s1, s2, head_x, head_yaw, thigh, calf, foot, splay, arms
# foot sign: POSITIVE = plantar flex (toes trail/relax). The foot bone is 42 cm
# (foot+toe); lying on the back an unflexed foot sticks 0.58 m straight up, so
# the final pose keeps the feet flopped forward at +65.
KEYS = [
    (1,    0,  0.00,  0.000,   2,  0,   0,   0,    0,   0,   0,  0, 'neutral'),
    (4,   -6,  0.00, -0.020,  -8, -4,  -8,   0,   -4,   6,   4,  0, 'hit'),
    (6,  -14,  0.02, -0.050,  -9, -4,  -7,   0,   -8,  18, -10,  0, 'hit'),
    (9,  -30,  0.06, -0.130, -10, -4,  -6,   0,  -18,  42, -20,  0, 'flail'),
    (14, -55,  0.15, -0.500,  -4, -2,  -4,   0,  -60,  85, -30,  0, 'up'),
    (19, -88,  0.26, -0.700,   0,  0, -12,   0,  -18,  30,  45,  3, 'wide'),
    (22, -84,  0.27, -0.670,   5,  2,  -4,   6,  -22,  34,  50,  5, 'wide'),
    (26, -90,  0.28, -0.715,   0,  0,  -6,  12,   -8,  12,  65,  7, 'final'),
    (34, -90,  0.28, -0.715,   0,  0,  -6,  12,   -8,  12,  65,  7, 'final'),
]


def pose_death(rig, k):
    (_fr, pitch, dy, dz, s1, s2, head_x, head_yaw,
     thigh, calf, foot, splay, arms) = k
    A.rest_all(rig)
    P = rig.pose.bones
    pivot = P['C_Root'].matrix.translation.copy()

    for name in ROOTS3:
        fall_root(P[name], pitch, dy, dz, pivot)

    rot_world(P[SPINE1], X, s1)
    rot_world(P[SPINE2], X, s2)
    rot_world(P[HEAD], X, head_x)
    if head_yaw:
        rot_world(P[HEAD], bdir((0, 0, 1), pitch), head_yaw)

    for sgn, th, cf, ft in (('L', 'L_Thigh', 'L_Claf', 'L_Foot'),
                            ('R', 'R_Thigh', 'R_Claf', 'R_Foot')):
        s = 1.0 if sgn == 'L' else -1.0
        rot_world(P[th], X, thigh)
        if splay:
            rot_world(P[th], Z, s * splay)
        rot_world(P[cf], X, calf)
        rot_world(P[ft], X, foot)

    U, F, H = ARM_SETS[arms]
    aim_world(P[L_CLAV], bdir((1.0, -0.08, 0.0), pitch), bdir(Z, pitch))
    aim_world(P[L_UPPER], bdir(U, pitch), bdir(Z, pitch))
    aim_world(P[L_FORE], bdir(F, pitch), bdir(Z, pitch))
    aim_world(P[L_HAND], bdir(H, pitch), bdir(Z, pitch))

    def mirror(v):
        return (-v[0], v[1], v[2] * 0.85)
    aim_world(P[R_CLAV], bdir((-1.0, -0.08, 0.0), pitch), bdir(Z, pitch))
    aim_world(P[R_UPPER], bdir(mirror(U), pitch), bdir(Z, pitch))
    aim_world(P[R_FORE], bdir(mirror(F), pitch), bdir(Z, pitch))
    aim_world(P[R_HAND], bdir(mirror(H), pitch), bdir(Z, pitch))


class DeathKeyer(A.Keyer):
    """Rotation keys on the full body + location keys on the 3 root bones."""

    def key(self, frame):
        super().key(frame)
        for name in ROOTS3:
            pb = self.rig.pose.bones[name]
            pb.keyframe_insert('location', frame=frame)


# ---------------------------------------------------------------- build

rig = A.get_rig()
bpy.ops.object.select_all(action='DESELECT')
rig.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode='POSE')
bpy.context.scene.render.fps = A.FPS
bpy.context.scene.render.fps_base = 1.0

act = A.new_action(rig, NAME)
ky = DeathKeyer(rig, KEYED)
for k in KEYS:
    pose_death(rig, k)
    ky.key(k[0])
FS, FE = KEYS[0][0], KEYS[-1][0]

bpy.ops.object.mode_set(mode='OBJECT')

# ---------------------------------------------------------------- verify

print('==== CHANNEL CHECK (honest: what is actually keyed) ====')
rot_bones, loc_bones, chans = set(), set(), set()
for fc in A.action_fcurves(act):
    if '"' not in fc.data_path:
        chans.add(fc.data_path)
        continue
    bone = fc.data_path.split('"')[1]
    ch = fc.data_path.rsplit('.', 1)[-1]
    chans.add(ch)
    if ch == 'rotation_quaternion':
        rot_bones.add(bone)
    elif ch == 'location':
        loc_bones.add(bone)
print('  rotation keys on %d bones: %s' % (len(rot_bones), sorted(rot_bones)))
print('  location keys on %d bones: %s' % (len(loc_bones), sorted(loc_bones)))
print('  channel kinds: %s' % sorted(chans))
bad = 0
if sorted(loc_bones) != sorted(ROOTS3):
    bad += 1
    print('  FAIL location keys must sit exactly on the 3 root bones')
if len(rot_bones) != 21:
    bad += 1
    print('  FAIL expected rotation keys on all 21 bones, got %d' % len(rot_bones))

print('==== MOTION CHECK (world space, per frame) ====')
ad = rig.animation_data
ad.action = act
if act.slots and ad.action_slot is None:
    ad.action_slot = act.slots[0]
sc = bpy.context.scene
sc.frame_start, sc.frame_end = FS, FE
minz_all = []
flex_worst = (0.0, '?', 0)
heights = []
for fr in range(FS, FE + 1):
    sc.frame_set(fr)
    upd()
    pts = []
    for pb in rig.pose.bones:
        pts.append(((rig.matrix_world @ pb.head).z, pb.name + '.head'))
        pts.append(((rig.matrix_world @ pb.tail).z, pb.name + '.tail'))
    (minz, lowname), (maxz, _) = min(pts), max(pts)
    minz_all.append((minz, fr))
    heights.append((fr, maxz))
    for side, (cl, up_) in (('R', (R_CLAV, R_UPPER)), ('L', (L_CLAV, L_UPPER))):
        a = (rig.pose.bones[cl].tail - rig.pose.bones[cl].head).normalized()
        b = (rig.pose.bones[up_].tail - rig.pose.bones[up_].head).normalized()
        ang = math.degrees(a.angle(b))
        if ang > flex_worst[0]:
            flex_worst = (ang, side, fr)
    print('  f%-3d min_z=%+.3f (%s) max_z=%.3f' % (fr, minz, lowname, maxz))
worst_minz = min(minz_all)
print('  lowest point in the whole take: %.3f m at f%d (limit -0.03)' % worst_minz)
if worst_minz[0] < -0.03:
    bad += 1
    print('  FAIL body part passes through the floor')
print('  max shoulder flex: %.1f deg (%s arm, f%d)   limit 110' % flex_worst)
if flex_worst[0] > 110.0:
    bad += 1
    print('  FAIL shoulder flex past the deltoid smear point')

sc.frame_set(FE)
upd()
final_max = max((rig.matrix_world @ pb.tail).z for pb in rig.pose.bones)
print('  final frame highest point: %.3f m (lying flat => must be < 0.45)' % final_max)
if final_max > 0.45:
    bad += 1
    print('  FAIL final pose is not flat on the ground')

# stillness of the hold: nothing may move between the two identical last keys
sc.frame_set(26)
upd()
snap = {pb.name: (rig.matrix_world @ pb.tail).copy() for pb in rig.pose.bones}
drift = 0.0
for fr in range(27, FE + 1):
    sc.frame_set(fr)
    upd()
    for pb in rig.pose.bones:
        drift = max(drift, ((rig.matrix_world @ pb.tail) - snap[pb.name]).length)
print('  hold drift f26..f%d: %.6f m (must be ~0)' % (FE, drift))
if drift > 1e-4:
    bad += 1
    print('  FAIL corpse still moving during the hold')

dur = (FE - FS) / float(A.FPS)
print('  duration: %d frames = %.3f s (asked 1.0-1.5)' % (FE - FS + 1, dur))
if not (1.0 <= dur <= 1.5):
    bad += 1
    print('  FAIL duration out of the asked band')

# ---------------------------------------------------------------- export

print('==== EXPORT ====')
A.export_anim(rig, act, FS, FE, OUT + NAME + '.fbx')

ad.action = act
bpy.context.scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=WORK + '_qc_death.blend')
print('BUILD_DONE failures=%d' % bad)
