"""Build the pistol aim pose, the pistol recoil and the wide melee slash on the
shared humanoid rig, verify them in Blender, export one armature-only FBX each.

Run:  blender.exe -b <master.blend> --factory-startup --python 10_build_anims.py
The source master.blend is never saved over; a QC blend is written next to this file.
"""
import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Vector
import acommon as A
from acommon import (X, Y, Z, aim_world, rot_world, swing_dir, rolled_up, upd,
                     SPINE1, SPINE2, NECK, HEAD,
                     L_CLAV, L_UPPER, L_FORE, L_HAND,
                     R_CLAV, R_UPPER, R_FORE, R_HAND)

OUT = 'E:/game-dev-team/assets/anim_humanoid/'
WORK = OUT + '_work/'

# world axis a bone is turned about to lift a forward-pointing muzzle
MUZZLE_UP = Vector((-1.0, 0.0, 0.0))


def clav_dir_right(alpha_deg):
    """Right collarbone: alpha > 0 drives that shoulder forward."""
    a = math.radians(alpha_deg)
    return Vector((-math.cos(a), -math.sin(a), 0.0))


def clav_dir_left(gamma_deg):
    """Left collarbone: gamma > 0 pulls that shoulder back."""
    g = math.radians(gamma_deg)
    return Vector((math.cos(g), math.sin(g), 0.0))


# ---------------------------------------------------------------- aim pose

def pose_aim(rig, recoil=0.0):
    """Pistol aim, upper body only. recoil 0 = held aim, 1 = peak of the shot."""
    A.rest_all(rig)
    P = rig.pose.bones

    rot_world(P[SPINE1], X, 6)          # small forward lean
    rot_world(P[SPINE1], Z, 14)         # bladed stance, gun shoulder leading
    rot_world(P[SPINE2], Z, 8)
    rot_world(P[SPINE2], X, -5.0 * recoil)   # chest rocks back on the shot
    rot_world(P[NECK], Z, -10)          # head keeps facing the target
    rot_world(P[HEAD], Z, -12)
    rot_world(P[HEAD], X, 8)

    # gun arm: reaching forward at chest height, hand just right of centre line
    aim_world(P[R_CLAV], clav_dir_right(25), Z)
    aim_world(P[R_UPPER], Vector((0.10, -0.97, -0.22)), Z)
    aim_world(P[R_FORE], Vector((0.14, -0.98, 0.14)), Z)
    aim_world(P[R_HAND], Vector((0.06, -0.998, 0.0)), Z)

    # support arm: bent across the chest, close to the gun without reaching it
    # (shoulder-to-shoulder span is wider than the arm, a real two-hand grip
    #  cannot close on this rig without pulling the gun back off the aim line)
    aim_world(P[L_CLAV], clav_dir_left(15), Z)
    aim_world(P[L_UPPER], Vector((-0.10, -0.62, -0.78)), Z)
    aim_world(P[L_FORE], Vector((-0.72, -0.68, 0.14)), Z)
    aim_world(P[L_HAND], Vector((-0.55, -0.83, 0.10)), Z)

    if recoil:                          # muzzle flip, adding up along the chain
        rot_world(P[R_UPPER], MUZZLE_UP, 4.0 * recoil)
        rot_world(P[R_FORE], MUZZLE_UP, 8.0 * recoil)
        rot_world(P[R_HAND], MUZZLE_UP, 20.0 * recoil)
        rot_world(P[L_FORE], MUZZLE_UP, 5.0 * recoil)
        rot_world(P[L_HAND], MUZZLE_UP, 7.0 * recoil)


# ---------------------------------------------------------------- melee slash

# frame, right arm (phi/pitch per joint), hand roll, collarbone, torso twist,
# left arm (phi/pitch). phi: 0 = forward, positive = towards the character's left.
# Pitch is held in a narrow band on purpose: the blade has to stay in one roughly
# horizontal plane at belly/chest height, otherwise the move reads as an overhead
# chop instead of the wide horizontal swing that was asked for.
SLASH_KEYS = [
    # fr   u_phi u_pit  f_phi f_pit  h_phi h_pit  roll alpha  tau   lu_phi lu_pit lf_phi lf_pit
    (  1,   -38,   34,   -16,   26,    -6,   24,     5,    6,   -6,     44,    46,    -4,    26),
    (  5,   -80,   10,  -128,   10,  -142,   12,    35,  -10,  -28,     36,    40,   -16,    18),
    (  7,   -83,    8,  -132,    8,  -146,   10,    42,  -12,  -31,     34,    38,   -20,    16),
    ( 10,   -52,   10,   -56,   12,   -54,   14,    68,   -2,  -13,     50,    42,     0,    26),
    ( 12,     0,   12,     8,   14,    14,   16,    84,   14,    8,     68,    46,    18,    30),
    ( 14,    40,   12,    62,   14,    72,   16,    84,   32,   28,     88,    48,    40,    32),
    ( 16,    46,   12,    92,   14,   104,   16,    66,   40,   38,    102,    46,    56,    30),
    ( 18,    22,   24,    44,   24,    54,   24,    28,   24,   18,     70,    46,    22,    28),
    ( 21,   -38,   34,   -16,   26,    -6,   24,     5,    6,   -6,     44,    46,    -4,    26),
]


def pose_slash(rig, k):
    (_fr, u_phi, u_pit, f_phi, f_pit, h_phi, h_pit, roll, alpha, tau,
     lu_phi, lu_pit, lf_phi, lf_pit) = k
    A.rest_all(rig)
    P = rig.pose.bones

    rot_world(P[SPINE1], X, 10)         # leaning into the strike
    rot_world(P[SPINE1], Z, tau * 0.6)
    rot_world(P[SPINE2], Z, tau * 0.4)
    rot_world(P[NECK], Z, -tau * 0.35)  # eyes stay on the target through the swing
    rot_world(P[HEAD], Z, -tau * 0.25)
    rot_world(P[HEAD], X, 10)

    aim_world(P[R_CLAV], clav_dir_right(alpha), Z)
    aim_world(P[R_UPPER], swing_dir(u_phi, u_pit), Z)
    aim_world(P[R_FORE], swing_dir(f_phi, f_pit), Z)
    hd = swing_dir(h_phi, h_pit)
    # rolling the wrist lays the weapon flat through the middle of the arc, which
    # is what makes a horizontal slash read from a top-down camera
    aim_world(P[R_HAND], hd, rolled_up(hd, roll))

    aim_world(P[L_CLAV], clav_dir_left(tau * 0.5), Z)
    aim_world(P[L_UPPER], swing_dir(lu_phi, lu_pit), Z)
    aim_world(P[L_FORE], swing_dir(lf_phi, lf_pit), Z)
    aim_world(P[L_HAND], swing_dir(lf_phi - 14, lf_pit + 4), Z)


# ---------------------------------------------------------------- build

RECOIL_KEYS = [(1, 0.0), (2, 0.85), (3, 1.0), (5, 0.45), (7, 0.15), (9, 0.0)]

rig = A.get_rig()
bpy.ops.object.select_all(action='DESELECT')
rig.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode='POSE')
bpy.context.scene.render.fps = A.FPS
bpy.context.scene.render.fps_base = 1.0

built = []

# 1) held aim, two identical frames so it can be sampled as a pose or looped
act = A.new_action(rig, 'Anim_AimPistol_Humanoid')
ky = A.Keyer(rig, A.UPPER_BODY)
for fr in (1, 2):
    pose_aim(rig, 0.0)
    ky.key(fr)
built.append(('Anim_AimPistol_Humanoid', act, 1, 2))

# 2) single shot recoil on top of that same aim
act = A.new_action(rig, 'Anim_FirePistol_Humanoid')
ky = A.Keyer(rig, A.UPPER_BODY)
for fr, t in RECOIL_KEYS:
    pose_aim(rig, t)
    ky.key(fr)
built.append(('Anim_FirePistol_Humanoid', act, 1, 9))

# 3) wide horizontal melee swing, weapon-shape agnostic
act = A.new_action(rig, 'Anim_MeleeSlash_Humanoid')
ky = A.Keyer(rig, A.UPPER_BODY)
for k in SLASH_KEYS:
    pose_slash(rig, k)
    ky.key(k[0])
built.append(('Anim_MeleeSlash_Humanoid', act, 1, 21))

bpy.ops.object.mode_set(mode='OBJECT')

# ---------------------------------------------------------------- verify

print('==== CHANNEL CHECK (rotation only, upper body only) ====')
bad = 0
for name, act, fs, fe in built:
    chans, bones = set(), set()
    for fc in A.action_fcurves(act):
        if '"' not in fc.data_path:
            chans.add(fc.data_path)
            continue
        bones.add(fc.data_path.split('"')[1])
        chans.add(fc.data_path.rsplit('.', 1)[-1])
    leg = sorted(bones & set(A.LOWER_BODY))
    extra = sorted(chans - {'rotation_quaternion'})
    print('  %-32s bones=%2d channels=%s lower_body_keys=%s' % (name, len(bones), sorted(chans), leg))
    if leg or extra:
        bad += 1
        print('     FAIL lower body or non-rotation channels present')

print('==== MOTION CHECK (world space, per frame) ====')
ad = rig.animation_data
sc = bpy.context.scene
for name, act, fs, fe in built:
    ad.action = act
    if act.slots and ad.action_slot is None:
        ad.action_slot = act.slots[0]
    sc.frame_start, sc.frame_end = fs, fe
    prev, travel, samples, flex = {}, {}, [], []
    for fr in range(fs, fe + 1):
        sc.frame_set(fr)
        upd()
        # angle between collarbone and upper arm. The rig has no twist or helper
        # bones, so past roughly 110 deg the deltoid weights smear into a flat
        # sheet across the chest - caught on the f16 close-up at 127 deg.
        for side, (cl, up_) in (('R', (R_CLAV, R_UPPER)), ('L', (L_CLAV, L_UPPER))):
            a = (rig.pose.bones[cl].tail - rig.pose.bones[cl].head).normalized()
            b = (rig.pose.bones[up_].tail - rig.pose.bones[up_].head).normalized()
            flex.append((math.degrees(a.angle(b)), side, fr))
        for pb in rig.pose.bones:
            w = (rig.matrix_world @ pb.tail).copy()
            if pb.name in prev:
                travel[pb.name] = travel.get(pb.name, 0.0) + (w - prev[pb.name]).length
            prev[pb.name] = w
        hb = rig.pose.bones[R_HAND]
        head = (rig.matrix_world @ hb.head).copy()
        tail = (rig.matrix_world @ hb.tail).copy()
        d = (tail - head).normalized()
        phi = math.degrees(math.atan2(d.x, -d.y))
        samples.append((fr, phi, tail.copy()))
    low = max((travel.get(b, 0.0) for b in A.LOWER_BODY))
    hand = travel.get(R_HAND, 0.0)
    dur = (fe - fs) / float(A.FPS)
    print('  %-32s frames=%2d dur=%.3fs  R_Hand_travel=%.3fm  max_lower_body_travel=%.6fm' % (
        name, fe - fs + 1, dur, hand, low))
    if low > 1e-9:
        bad += 1
        print('     FAIL legs/root move')
    phis = [s[1] for s in samples]
    zs = [s[2].z for s in samples]
    print('     hand aim angle: min=%+.1f max=%+.1f sweep=%.1f deg  (0=forward, +=to char left)' % (
        min(phis), max(phis), max(phis) - min(phis)))
    print('     hand height band: min=%.3f max=%.3f spread=%.3f m' % (min(zs), max(zs), max(zs) - min(zs)))
    worst = max(flex)
    print('     max shoulder flex: %.1f deg (%s arm, f%d)   limit 110' % (worst[0], worst[1], worst[2]))
    if worst[0] > 110.0:
        bad += 1
        print('     FAIL shoulder flex past the point where the deltoid smears')
    for fr, phi, t in samples:
        print('       f%-3d phi=%+7.1f  hand_tail=(%+.3f,%+.3f,%+.3f)' % (fr, phi, t.x, t.y, t.z))

# ---------------------------------------------------------------- export

print('==== EXPORT ====')
for name, act, fs, fe in built:
    A.export_anim(rig, act, fs, fe, OUT + name + '.fbx')

ad.action = None
bpy.context.scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=WORK + '_qc_anim.blend')
print('BUILD_DONE failures=%d' % bad)
