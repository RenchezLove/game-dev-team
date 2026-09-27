"""Pose sources + close-up shots for the hero skin checks (15_skin_check.py).
Poses come from the SOURCE rigs the game FBX were exported from (anim_humanoid
_qc_anim.blend, RunAnimation.blend). Their rest must equal our RootAnim rest
(checked, max delta printed); then matrix_basis is copied bone by bone, which is
exact incl. twist. (FBX re-import is useless here: its rest = the take's first
frame, not our T-pose.)"""
import bpy, math
from mathutils import Vector, Matrix

ANIM_QC = 'E:/game-dev-team/assets/anim_humanoid/_work/_qc_anim.blend'
RUN = ('E:/ForGameLead(Materials)/Порядок (PipeLine) создания мешей,анимаций '
       'AMasterHumanoidCharacter импорт и экспорт/RunAnimation.blend')


def reset(rig):
    for pb in rig.pose.bones:
        pb.matrix_basis = Matrix.Identity(4)
    bpy.context.view_layer.update()


def load_source(path, action_name=None, tag='Src'):
    """Append RootAnim from path (+ the named action), check rest vs ours."""
    with bpy.data.libraries.load(path, link=False) as (src_d, dst_d):
        dst_d.objects = ['RootAnim']
        if action_name:
            dst_d.actions = [action_name]
    src = dst_d.objects[0]
    src.name = tag
    bpy.context.scene.collection.objects.link(src)
    src.hide_render = True
    if action_name:
        act = dst_d.actions[0]
        src.animation_data.action = act
        if hasattr(src.animation_data, 'action_slot') and act.slots:
            src.animation_data.action_slot = act.slots[0]
    names = {pb.name.replace('.', '_'): pb.name for pb in src.pose.bones}
    return src, names


def rest_delta(src, names, rig):
    return max(max(abs(a - b) for ra, rb in zip(src.data.bones[names[b.name]].matrix_local,
                                                   b.matrix_local) for a, b in zip(ra, rb))
               for b in rig.data.bones)


def transfer(src, names, rig, frame):
    bpy.context.scene.frame_set(frame)
    bpy.context.view_layer.update()
    for pb in rig.pose.bones:
        pb.matrix_basis = src.pose.bones[names[pb.name]].matrix_basis.copy()
    bpy.context.view_layer.update()


def shoot(view_dir, center, height, out_path, suns):
    """Ortho close-up: camera along view_dir onto center, frame height in metres."""
    sc = bpy.context.scene
    cam = sc.camera
    vd = Vector(view_dir).normalized()
    cam.location = Vector(center) + vd * 8
    fwd = -vd
    cam.rotation_euler = fwd.to_track_quat('-Z', 'Y').to_euler()
    cam.data.ortho_scale = height
    cam.data.clip_start = 0.01
    cam.data.clip_end = 30
    zup = Vector((0, 0, 1))
    right = fwd.cross(zup)
    right = right.normalized() if right.length > 1e-5 else Vector((1, 0, 0))
    up = right.cross(fwd).normalized()
    for s, t in zip(suns, (fwd + 0.55 * right - 0.55 * up, fwd - 0.5 * right + 0.35 * up,
                           fwd - 0.9 * up + 0.1 * right)):
        s.rotation_euler = t.normalized().to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = out_path
    bpy.ops.render.render(write_still=True)
    print('RENDER', out_path)
