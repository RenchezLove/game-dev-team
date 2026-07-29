"""Pose/animation helpers for the shared 21-bone humanoid rig (RootAnim).

Bones are driven by WORLD-SPACE directions, never by euler angles per bone name.
Reason: the right arm chain is name-shifted by one joint (R_Arm is the upper arm,
Pelvis_009_R_002 is the forearm) and bone rolls are unknown, so any name-mirrored
or euler-based authoring lands one joint off. World aiming is immune to both.

Rig facts, measured from assets/armor_wearables/_work/master.blend (log _00_master.log):
  forward = -Y (foot tails at y=-0.423), up = +Z, character-left = +X
  rest is a clean T-pose, armature object transform is identity
"""
import bpy, math, os
from mathutils import Vector, Matrix, Quaternion

X = Vector((1.0, 0.0, 0.0))
Y = Vector((0.0, 1.0, 0.0))
Z = Vector((0.0, 0.0, 1.0))
FWD = Vector((0.0, -1.0, 0.0))

SPINE1, SPINE2, NECK, HEAD = 'C_Spine01', 'C_Spine02', 'C_Neck', 'C_Head'
L_CLAV, L_UPPER, L_FORE, L_HAND = 'L_UpperArm', 'L_Shoulder', 'L_Arm', 'L_Hand'
R_CLAV, R_UPPER, R_FORE, R_HAND = 'R_UpperArm', 'R_Arm', 'Pelvis_009_R_002', 'R_Hand'

UPPER_BODY = [SPINE1, SPINE2, NECK, HEAD,
              L_CLAV, L_UPPER, L_FORE, L_HAND,
              R_CLAV, R_UPPER, R_FORE, R_HAND]
LOWER_BODY = ['C_Root', 'L_Pelvis', 'L_Thigh', 'L_Claf', 'L_Foot',
              'R_Pelvis', 'R_Thigh', 'R_Claf', 'R_Foot']
ALL_21 = UPPER_BODY + LOWER_BODY

FPS = 30


# ---------------------------------------------------------------- rig access

def get_rig():
    rigs = [o for o in bpy.data.objects if o.type == 'ARMATURE']
    assert len(rigs) == 1, 'expected exactly one armature, got %s' % [o.name for o in rigs]
    rig = rigs[0]
    assert rig.name == 'RootAnim', 'armature object must stay named RootAnim (UE root bone)'
    names = [b.name for b in rig.data.bones]
    missing = [n for n in ALL_21 if n not in names]
    assert not missing, 'rig is missing bones %s' % missing
    assert len(names) == 21, 'expected 21 bones, got %d' % len(names)
    return rig


def upd():
    bpy.context.view_layer.update()


def rest_all(rig):
    """Back to bind pose: clears every channel on every bone."""
    for pb in rig.pose.bones:
        pb.rotation_mode = 'QUATERNION'
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.location = (0, 0, 0)
        pb.scale = (1, 1, 1)
    upd()


# ---------------------------------------------------------------- posing ops

def _finish(pb):
    # the matrix setter can only introduce translation if the head we fed it was
    # stale; keep the rig rotation-only so nothing can slide off the skeleton
    if pb.location.length > 1e-5:
        print('WARN  translation %.6f introduced on %s (zeroed)' % (pb.location.length, pb.name))
    pb.location = (0, 0, 0)
    pb.scale = (1, 1, 1)
    upd()


def rot_world(pb, axis, deg):
    """Rotate a bone about a world axis passing through its own head.
    Children of the bone follow along, as in a real joint."""
    upd()
    M = pb.matrix.copy()
    head = M.translation.copy()
    R = Matrix.Rotation(math.radians(deg), 4, Vector(axis).normalized())
    pb.matrix = Matrix.Translation(head) @ R @ Matrix.Translation(-head) @ M
    _finish(pb)


def aim_world(pb, ydir, zhint=None):
    """Point the bone along a world direction. A bone's local +Y runs head->tail,
    so ydir is where the bone points; zhint picks the roll around that axis."""
    upd()
    head = pb.matrix.translation.copy()
    y = Vector(ydir).normalized()
    zh = Vector(zhint) if zhint is not None else Z.copy()
    z = zh - y * zh.dot(y)
    if z.length < 1e-5:                      # zhint parallel to the bone, pick any
        z = Z - y * y.z
        if z.length < 1e-5:
            z = Y - y * y.y
    z.normalize()
    x = y.cross(z)                           # right-handed: x cross y = z
    pb.matrix = Matrix(((x.x, y.x, z.x, head.x),
                        (x.y, y.y, z.y, head.y),
                        (x.z, y.z, z.z, head.z),
                        (0.0, 0.0, 0.0, 1.0)))
    _finish(pb)


def swing_dir(phi_deg, pitch_deg=0.0):
    """Horizontal aim direction. phi is measured from forward (-Y), positive towards
    the character's own left (+X); pitch tilts the result downwards."""
    p, r = math.radians(phi_deg), math.radians(pitch_deg)
    cr = math.cos(r)
    return Vector((math.sin(p) * cr, -math.cos(p) * cr, -math.sin(r)))


def rolled_up(direction, roll_deg):
    """World 'up' for a bone, rolled around its own aim axis. Used to lay a held
    weapon over during a swing (roll 90 = weapon flat, best read from top-down)."""
    d = Vector(direction).normalized()
    up = Z - d * Z.dot(d)
    if up.length < 1e-5:
        up = Y - d * Y.dot(d)
    up.normalize()
    return (Matrix.Rotation(math.radians(roll_deg), 4, d) @ up)


# ---------------------------------------------------------------- keyframing

class Keyer:
    """Inserts rotation-only keys and keeps quaternions sign-continuous.

    Rebuilding every key from the bind pose can hand back q and -q on neighbouring
    frames (same orientation, opposite sign); interpolating across that sign flip
    spins the bone the long way round. Flipping to match the previous key kills it.
    """

    def __init__(self, rig, bones):
        self.rig = rig
        self.bones = list(bones)
        self.prev = {}

    def key(self, frame):
        for name in self.bones:
            pb = self.rig.pose.bones[name]
            q = pb.rotation_quaternion.copy()
            p = self.prev.get(name)
            if p is not None and q.dot(p) < 0.0:
                q = Quaternion((-q.w, -q.x, -q.y, -q.z))
                pb.rotation_quaternion = q
            self.prev[name] = q
            pb.keyframe_insert('rotation_quaternion', frame=frame)


def new_action(rig, name):
    ad = rig.animation_data or rig.animation_data_create()
    for tr in list(ad.nla_tracks):
        ad.nla_tracks.remove(tr)
    act = bpy.data.actions.get(name)
    if act:
        bpy.data.actions.remove(act)
    act = bpy.data.actions.new(name)
    act.use_fake_user = True
    ad.action = act
    return act


def action_fcurves(act):
    """Blender 5.x slotted actions: fcurves live in a channelbag, not on the action."""
    out = []
    for layer in act.layers:
        for strip in layer.strips:
            for slot in act.slots:
                cb = strip.channelbag(slot)
                if cb:
                    out.extend(cb.fcurves)
    return out


# ---------------------------------------------------------------- export

def export_anim(rig, act, frame_start, frame_end, path):
    """Armature-only FBX with one baked take, matching the shape of the project's
    existing Anim_Run_Humanoid.fbx (that file holds an armature and no mesh).

    The 5.x exporter skips a loose action, so the action is pushed onto a temporary
    NLA strip and baked from there (lesson from the wolf animation batch)."""
    ad = rig.animation_data
    ad.action = None
    for tr in list(ad.nla_tracks):
        ad.nla_tracks.remove(tr)
    tr = ad.nla_tracks.new()
    strip = tr.strips.new(act.name, int(frame_start), act)
    strip.action_frame_start = frame_start
    strip.action_frame_end = frame_end
    strip.frame_start = frame_start
    strip.frame_end = frame_end
    try:
        if act.slots:
            strip.action_slot = act.slots[0]
    except Exception as e:
        print('NOTE could not bind strip slot:', e)

    sc = bpy.context.scene
    sc.render.fps = FPS
    sc.render.fps_base = 1.0
    sc.frame_start, sc.frame_end = int(frame_start), int(frame_end)

    bpy.ops.object.select_all(action='DESELECT')
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.export_scene.fbx(
        filepath=path, use_selection=True, object_types={'ARMATURE'},
        add_leaf_bones=False,            # 21 bones + RootAnim root = the 22 UE holds
        bake_anim=True, bake_anim_use_all_actions=False,
        bake_anim_use_nla_strips=True, bake_anim_step=1.0,
        bake_anim_simplify_factor=0.0,   # keep every baked frame, no decimation
        path_mode='AUTO')

    for t in list(ad.nla_tracks):
        ad.nla_tracks.remove(t)
    ad.action = act
    ok = os.path.exists(path)
    print('EXPORT %-40s exists=%s bytes=%s' % (os.path.basename(path), ok,
                                               os.path.getsize(path) if ok else '-'))
    return ok
