"""Pose check of the Tripo hero slots on RootAnim + review sheets.
Poses: rest (T), run (bone directions copied from the real Anim_Run_Humanoid
FBX at the widest-stride frame), arms down (clavicle 12 deg + shoulder 76 deg).
Views: front + side. Output: assets/hero_tripo/renders/*.png + sheets.
Run: blender.exe -b --factory-startup --python 11_pose_check.py
"""
import bpy, sys, os, math
import numpy as np
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W
import addon_utils
from mathutils import Vector, Matrix, Quaternion

OUT = 'E:/game-dev-team/assets/hero_tripo/renders/'
os.makedirs(OUT, exist_ok=True)
RUN = ('E:/ForGameLead(Materials)/Порядок (PipeLine) создания мешей,анимаций '
       'AMasterHumanoidCharacter импорт и экспорт/RunAnimation.blend')   # 20-frame run take, read-only
bpy.ops.wm.open_mainfile(filepath='E:/game-dev-team/assets/hero_tripo/_work/hero_work.blend')
addon_utils.enable('io_scene_fbx')
rig = bpy.data.objects['RootAnim']
parts = [bpy.data.objects[n] for n in ('SK_Cloth_T0_Head', 'SK_Cloth_T0_Torso', 'SK_Cloth_T0_Legs')]

# weight report
for ob in parts:
    gn = {g.index: g.name for g in ob.vertex_groups}
    st = {}
    for v in ob.data.vertices:
        for g in v.groups:
            s = st.setdefault(gn[g.group], [0.0, 0])
            s[0] = max(s[0], g.weight)
            s[1] += g.weight > 0.05
    print('WEIGHTS %s: %s' % (ob.name, ', '.join('%s max=%.2f n>0.05=%d' % (k, v[0], v[1])
                                                 for k, v in sorted(st.items()))))

sc, cam, suns = W.setup_render(res=700)
sc.render.film_transparent = False
VIEWS = {'front': (0, -1, 0.12), 'side': (1, 0, 0.12)}

order = []
def walk(b):
    order.append(b.name)
    for c in b.children:
        walk(c)
for b in rig.data.bones:
    if b.parent is None:
        walk(b)


def reset():
    for pb in rig.pose.bones:
        pb.matrix_basis = Matrix.Identity(4)
    bpy.context.view_layer.update()


def turn(pb, q):
    """World rotation q about the bone head (rig is identity in world)."""
    h = pb.head.copy()
    pb.matrix = Matrix.Translation(h) @ q.to_matrix().to_4x4() @ Matrix.Translation(-h) @ pb.matrix
    bpy.context.view_layer.update()


def shoot(tag):
    for vn, vd in VIEWS.items():
        W.frame_and_shoot(parts, vd, OUT + 'hero_%s_%s.png' % (tag, vn), margin=1.08, suns=suns)


# ---- rest ----
reset()
shoot('rest')

# ---- run: copy bone directions from the real run take ----
with bpy.data.libraries.load(RUN, link=False) as (src_d, dst_d):
    dst_d.objects = ["RootAnim"]
src = dst_d.objects[0]
sc.collection.objects.link(src)
src.hide_render = True
act = src.animation_data.action
f0, f1 = [int(v) for v in act.frame_range]
best = None
for f in range(f0, f1 + 1):
    sc.frame_set(f)
    a = src.matrix_world @ src.pose.bones['L_Foot'].head
    b = src.matrix_world @ src.pose.bones['R_Foot'].head
    d = abs(a.y - b.y)
    if best is None or d > best[0]:
        best = (d, f)
sc.frame_set(best[1])
print('RUN take frames %d..%d, widest stride %.3f m at frame %d' % (f0, f1, best[0], best[1]))
sp = {pb.name.replace('.', '_'): pb for pb in src.pose.bones}
reset()
for bn in order:
    s = sp[bn]
    d = ((src.matrix_world @ s.tail) - (src.matrix_world @ s.head)).normalized()
    pb = rig.pose.bones[bn]
    c = (pb.tail - pb.head).normalized()
    turn(pb, c.rotation_difference(d))
src.hide_render = True
bpy.context.view_layer.update()
shoot('run')

# ---- arms down ----
reset()
for side, sgn, cl, sh in (('L', 1, 'L_UpperArm', 'L_Shoulder'), ('R', -1, 'R_UpperArm', 'R_Arm')):
    turn(rig.pose.bones[cl], Quaternion((0, 1, 0), math.radians(12) * sgn))
    turn(rig.pose.bones[sh], Quaternion((0, 1, 0), math.radians(76) * sgn))
shoot('armsdown')
reset()

# ---- sheets ----


def load(p):
    im = bpy.data.images.load(p)
    w, h = im.size
    a = np.array(im.pixels[:], dtype=np.float32).reshape(h, w, 4)
    bpy.data.images.remove(im)
    return a


def sheet(names, out):
    row = np.concatenate([load(OUT + n) for n in names], axis=1)
    h, w, _ = row.shape
    im = bpy.data.images.new('sheet', w, h, alpha=True)
    im.pixels = row.ravel()
    im.filepath_raw = out
    im.file_format = 'PNG'
    im.save()
    print('SHEET', out, w, h)


sheet(['hero_run_front.png', 'hero_run_side.png', 'hero_armsdown_front.png',
       'hero_armsdown_side.png'], OUT + 'hero_pose_sheet.png')
sheet(['hero_rest_front.png', 'hero_rest_side.png'], OUT + 'hero_rest_sheet.png')
