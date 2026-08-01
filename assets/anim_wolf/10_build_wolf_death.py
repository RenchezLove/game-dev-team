"""Build Anim_Wolf_Death: the wolf staggers, its legs buckle and it topples
over onto its RIGHT side (Rinat: humanoids die on the back, wolves on the
side). Final pose: lying still on the side, legs slightly curled, head down.

Authoring facts (inspected from wolf.blend, not from memory):
  * WolfRig: 22 bones, ONE parentless bone 'root' (head z=0.058) - everything
    hangs off it, so the whole-body roll+drop is keyed on 'root' alone
    (rotation AND location); every other keyed bone is rotation-only.
  * Wolf forward = +Y, up = +Z, spine runs along Y at z~0.66-0.77.
    Rolling +90 deg about world Y puts the LEFT flank up -> lies on the RIGHT
    side. Pose bones use XYZ euler (wolf batch convention, kept).
  * Scene fps in wolf.blend is 24 (old batch); this take is authored at 30
    (my Build 1.1 standard) - UE reads take time in seconds, mixing is fine.

Run:  blender.exe -b "E:/ForGameLead(Materials)/phase3-assets/_build/wolf.blend"
          --factory-startup --python 10_build_wolf_death.py
"""
import bpy, os, math
from mathutils import Vector, Matrix

OUT = 'E:/game-dev-team/assets/anim_wolf/'
WORK = OUT + '_work/'
NAME = 'Anim_Wolf_Death'
FPS = 30
PIVOT = Vector((0.0, 0.0, 0.66))     # spine centre at rest

arm = bpy.data.objects['WolfRig']
mesh_obj = bpy.data.objects['SK_Wolf']
sc = bpy.context.scene
sc.render.fps = FPS
sc.render.fps_base = 1.0


def upd():
    bpy.context.view_layer.update()


def rest_all():
    for pb in arm.pose.bones:
        pb.rotation_mode = 'XYZ'
        pb.rotation_euler = (0, 0, 0)
        pb.location = (0, 0, 0)
        pb.scale = (1, 1, 1)
    upd()


def root_fall(roll_deg, dx, dz):
    """Whole-body roll about world +Y through the spine pivot + translation.
    Keyed on 'root' (the single hierarchy root), keeps translation."""
    pb = arm.pose.bones['root']
    upd()
    M = pb.matrix.copy()
    R = Matrix.Rotation(math.radians(roll_deg), 4, Vector((0, 1, 0)))
    pb.matrix = (Matrix.Translation(PIVOT + Vector((dx, 0.0, dz)))
                 @ R @ Matrix.Translation(-PIVOT) @ M)
    pb.scale = (1, 1, 1)
    upd()


def d(v):
    return tuple(math.radians(x) for x in v)


# fr -> (roll, dx, dz, {bone: local euler deg})
KEYS = [
    (1, 0, 0.00, 0.000, {
        'chest': (2, 0, 0), 'head': (2, 0, 0), 'tail_01': (0, 0, 4)}),
    (4, 6, 0.00, -0.020, {
        'head': (-8, 0, 6), 'neck': (-4, 0, 0), 'frontlower_L': (-10, 0, 0),
        'frontlower_R': (-10, 0, 0), 'shin_L': (15, 0, 0), 'shin_R': (15, 0, 0),
        'tail_01': (8, 0, 6)}),
    (8, 22, 0.01, -0.100, {
        'neck': (-5, 0, 0), 'head': (-4, 0, 4),
        'frontupper_L': (15, 0, 0), 'frontlower_L': (-35, 0, 0), 'frontpaw_L': (15, 0, 0),
        'frontupper_R': (15, 0, 0), 'frontlower_R': (-35, 0, 0), 'frontpaw_R': (15, 0, 0),
        'thigh_L': (20, 0, 0), 'shin_L': (30, 0, 0), 'rearpaw_L': (-15, 0, 0),
        'thigh_R': (20, 0, 0), 'shin_R': (30, 0, 0), 'rearpaw_R': (-15, 0, 0),
        'tail_01': (12, 0, -6)}),
    (13, 62, 0.03, -0.300, {
        'neck': (5, 0, 5), 'head': (8, 0, 5),
        'frontupper_L': (28, 0, 0), 'frontlower_L': (-55, 0, 0), 'frontpaw_L': (22, 0, 0),
        'frontupper_R': (28, 0, 0), 'frontlower_R': (-55, 0, 0), 'frontpaw_R': (22, 0, 0),
        'thigh_L': (32, 0, 0), 'shin_L': (45, 0, 0), 'rearpaw_L': (-25, 0, 0),
        'thigh_R': (32, 0, 0), 'shin_R': (45, 0, 0), 'rearpaw_R': (-25, 0, 0),
        'tail_01': (10, 0, 8), 'tail_02': (8, 0, 4)}),
    (17, 90, 0.05, -0.440, {
        'neck': (8, 0, 8), 'head': (10, 0, 12),
        'frontupper_L': (22, 0, 0), 'frontlower_L': (-45, 0, 0), 'frontpaw_L': (18, 0, 0),
        'frontupper_R': (22, 0, 0), 'frontlower_R': (-45, 0, 0), 'frontpaw_R': (18, 0, 0),
        'thigh_L': (26, 0, 0), 'shin_L': (38, 0, 0), 'rearpaw_L': (-20, 0, 0),
        'thigh_R': (26, 0, 0), 'shin_R': (38, 0, 0), 'rearpaw_R': (-20, 0, 0),
        'tail_01': (8, 0, 6), 'tail_02': (6, 0, 4)}),
    (20, 86, 0.05, -0.420, {
        'neck': (9, 0, 9), 'head': (11, 0, 14),
        'frontupper_L': (24, 0, 0), 'frontlower_L': (-50, 0, 0), 'frontpaw_L': (20, 0, 0),
        'frontupper_R': (24, 0, 0), 'frontlower_R': (-50, 0, 0), 'frontpaw_R': (20, 0, 0),
        'thigh_L': (28, 0, 0), 'shin_L': (40, 0, 0), 'rearpaw_L': (-22, 0, 0),
        'thigh_R': (28, 0, 0), 'shin_R': (40, 0, 0), 'rearpaw_R': (-22, 0, 0),
        'tail_01': (7, 0, 5), 'tail_02': (5, 0, 4)}),
    (24, 93, 0.06, -0.450, {
        'neck': (10, 0, 12), 'head': (12, 0, 18),
        'frontupper_L': (18, 0, 0), 'frontlower_L': (-40, 0, 0), 'frontpaw_L': (15, 0, 0),
        'frontupper_R': (18, 0, 0), 'frontlower_R': (-40, 0, 0), 'frontpaw_R': (15, 0, 0),
        'thigh_L': (22, 0, 0), 'shin_L': (32, 0, 0), 'rearpaw_L': (-16, 0, 0),
        'thigh_R': (22, 0, 0), 'shin_R': (32, 0, 0), 'rearpaw_R': (-16, 0, 0),
        'tail_01': (6, 0, 4), 'tail_02': (4, 0, 6)}),
    (32, 93, 0.06, -0.450, {
        'neck': (10, 0, 12), 'head': (12, 0, 18),
        'frontupper_L': (18, 0, 0), 'frontlower_L': (-40, 0, 0), 'frontpaw_L': (15, 0, 0),
        'frontupper_R': (18, 0, 0), 'frontlower_R': (-40, 0, 0), 'frontpaw_R': (15, 0, 0),
        'thigh_L': (22, 0, 0), 'shin_L': (32, 0, 0), 'rearpaw_L': (-16, 0, 0),
        'thigh_R': (22, 0, 0), 'shin_R': (32, 0, 0), 'rearpaw_R': (-16, 0, 0),
        'tail_01': (6, 0, 4), 'tail_02': (4, 0, 6)}),
]
FS, FE = KEYS[0][0], KEYS[-1][0]

# ---------------------------------------------------------------- build

ad = arm.animation_data or arm.animation_data_create()
ad.action = None
for tr in list(ad.nla_tracks):
    ad.nla_tracks.remove(tr)
old = bpy.data.actions.get(NAME)
if old:
    bpy.data.actions.remove(old)
act = bpy.data.actions.new(NAME)
act.use_fake_user = True
ad.action = act

for fr, roll, dx, dz, locals_ in KEYS:
    rest_all()
    for bone, rot in locals_.items():
        arm.pose.bones[bone].rotation_euler = d(rot)
    upd()
    root_fall(roll, dx, dz)
    for bone in locals_:
        arm.pose.bones[bone].keyframe_insert('rotation_euler', frame=fr)
    rpb = arm.pose.bones['root']
    rpb.keyframe_insert('rotation_euler', frame=fr)
    rpb.keyframe_insert('location', frame=fr)

# ---------------------------------------------------------------- verify

print('==== CHANNEL CHECK (honest: what is actually keyed) ====')


def action_fcurves(a):
    out = []
    try:
        for layer in a.layers:
            for strip in layer.strips:
                for slot in a.slots:
                    cb = strip.channelbag(slot)
                    if cb:
                        out.extend(cb.fcurves)
    except AttributeError:
        out = list(a.fcurves)
    return out


rot_bones, loc_bones = set(), set()
for fc in action_fcurves(act):
    if '"' not in fc.data_path:
        continue
    bone = fc.data_path.split('"')[1]
    ch = fc.data_path.rsplit('.', 1)[-1]
    if ch == 'rotation_euler':
        rot_bones.add(bone)
    elif ch == 'location':
        loc_bones.add(bone)
print('  rotation keys on %d bones: %s' % (len(rot_bones), sorted(rot_bones)))
print('  location keys on %d bones: %s' % (len(loc_bones), sorted(loc_bones)))
bad = 0
if sorted(loc_bones) != ['root']:
    bad += 1
    print('  FAIL location keys must sit on root only')

print('==== MOTION CHECK (world space, per frame) ====')
sc.frame_start, sc.frame_end = FS, FE
minz_all = []
for fr in range(FS, FE + 1):
    sc.frame_set(fr)
    upd()
    pts = []
    for pb in arm.pose.bones:
        pts.append(((arm.matrix_world @ pb.head).z, pb.name + '.head'))
        pts.append(((arm.matrix_world @ pb.tail).z, pb.name + '.tail'))
    (minz, lown), (maxz, topn) = min(pts), max(pts)
    minz_all.append((minz, fr))
    print('  f%-3d min_z=%+.3f (%s) max_z=%.3f (%s)' % (fr, minz, lown, maxz, topn))
worst = min(minz_all)
print('  lowest point in the take: %.3f m at f%d (limit -0.03)' % worst)
if worst[0] < -0.03:
    bad += 1
    print('  FAIL body part under the floor')

sc.frame_set(FE)
upd()
final_max = max((arm.matrix_world @ pb.tail).z for pb in arm.pose.bones)
print('  final frame highest bone point: %.3f m (on the side => must be < 0.45)' % final_max)
if final_max > 0.45:
    bad += 1
    print('  FAIL final pose is not flat on the side')

sc.frame_set(24)
upd()
snap = {pb.name: (arm.matrix_world @ pb.tail).copy() for pb in arm.pose.bones}
drift = 0.0
for fr in range(25, FE + 1):
    sc.frame_set(fr)
    upd()
    for pb in arm.pose.bones:
        drift = max(drift, ((arm.matrix_world @ pb.tail) - snap[pb.name]).length)
print('  hold drift f24..f%d: %.6f m (must be ~0)' % (FE, drift))
if drift > 1e-4:
    bad += 1
    print('  FAIL corpse still moving during the hold')

dur = (FE - FS) / float(FPS)
print('  duration: %d frames = %.3f s (asked 0.8-1.2)' % (FE - FS + 1, dur))
if not (0.8 <= dur <= 1.2):
    bad += 1
    print('  FAIL duration out of band')

# mesh deform sanity (same metric as the old wolf batch: edge stretch)
rest_all()
sc.frame_set(1)
me = mesh_obj.data
rest_co = [v.co.copy() for v in me.vertices]
rest_edge = [(e.vertices[0], e.vertices[1],
              (rest_co[e.vertices[0]] - rest_co[e.vertices[1]]).length)
             for e in me.edges]
max_stretch = 0.0
for fr in range(FS, FE + 1):
    sc.frame_set(fr)
    dg = bpy.context.evaluated_depsgraph_get()
    ob_eval = mesh_obj.evaluated_get(dg)
    me_eval = ob_eval.to_mesh()
    co = [v.co.copy() for v in me_eval.vertices]
    for (i, j, l0) in rest_edge:
        if l0 > 1e-6:
            max_stretch = max(max_stretch, (co[i] - co[j]).length / l0)
    ob_eval.to_mesh_clear()
print('  max mesh edge stretch vs rest: %.3f (smearing guard, limit 2.5)' % max_stretch)
if max_stretch > 2.5:
    bad += 1
    print('  FAIL mesh smears during playback')

# ---------------------------------------------------------------- export

# wolf batch contract: MESH+ARMATURE in the file, action via temp NLA strip
ad.action = None
for tr in list(ad.nla_tracks):
    ad.nla_tracks.remove(tr)
tr = ad.nla_tracks.new()
strip = tr.strips.new(NAME, FS, act)
try:
    if act.slots:
        strip.action_slot = act.slots[0]
except Exception as e:
    print('NOTE could not bind strip slot:', e)
sc.frame_start, sc.frame_end = FS, FE
bpy.ops.object.select_all(action='DESELECT')
mesh_obj.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
path = OUT + NAME + '.fbx'
bpy.ops.export_scene.fbx(
    filepath=path, use_selection=True, object_types={'MESH', 'ARMATURE'},
    mesh_smooth_type='FACE', add_leaf_bones=False,
    bake_anim=True, bake_anim_use_all_actions=False,
    bake_anim_use_nla_strips=True, bake_anim_step=1.0,
    bake_anim_simplify_factor=0.0, use_mesh_modifiers=True, path_mode='AUTO')
for tr in list(ad.nla_tracks):
    ad.nla_tracks.remove(tr)
ad.action = act
print('EXPORT %s exists=%s bytes=%s' % (path, os.path.exists(path),
                                        os.path.getsize(path) if os.path.exists(path) else '-'))

sc.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=WORK + '_qc_wolf_death.blend')
print('BUILD_DONE failures=%d' % bad)
