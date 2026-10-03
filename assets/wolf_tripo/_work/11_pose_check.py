"""New Tripo wolf next to the old wolf on the same WolfRig: rest and frames of Idle / Run / Bite / Death,
side and above-side views; prints ground clearance of the paws per shot.
Run: blender.exe -b --factory-startup --python 11_pose_check.py
"""
import bpy, sys, os, math
import numpy as np
sys.path.insert(0, 'E:/game-dev-team/assets/hero_tripo/_work')
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W
import hpose as P
from mathutils import Vector, Matrix

OUT = 'E:/game-dev-team/assets/wolf_tripo/renders/'
bpy.ops.wm.open_mainfile(filepath='E:/game-dev-team/assets/wolf_tripo/_work/wolf_work.blend')
rig = bpy.data.objects['WolfRig']
new = bpy.data.objects['SK_Wolf']; old = bpy.data.objects['SK_Wolf_old']
for m in bpy.data.materials:
    for n in (m.node_tree.nodes if m.node_tree else []):
        if n.type == 'TEX_IMAGE':
            n.interpolation = 'Linear'
sc, cam, suns = W.setup_render(res=800)
sc.render.film_transparent = False
VIEWS = {'side': (1, 0.05, 0.08), 'top': (0.75, 0.45, 1.5), 'front': (0.35, 1, 0.3)}


def pose(action, frame):
    for pb in rig.pose.bones:
        pb.matrix_basis = Matrix.Identity(4)
    if action is None:
        rig.animation_data.action = None
    else:
        act = bpy.data.actions[action]
        rig.animation_data.action = act
        if hasattr(rig.animation_data, 'action_slot') and act.slots:
            rig.animation_data.action_slot = act.slots[0]
        sc.frame_set(frame)
    bpy.context.view_layer.update()


def lowest(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    e = ob.evaluated_get(dg); m = e.to_mesh()
    z = min((ob.matrix_world @ v.co).z for v in m.vertices)
    e.to_mesh_clear()
    return z


SHOTS = [('rest', None, 0), ('idle', 'Anim_Wolf_Idle', 24), ('run_a', 'Anim_Wolf_Run', 4), ('run_b', 'Anim_Wolf_Run', 12),
         ('bite', 'Anim_Wolf_Bite', 0), ('death_mid', 'Anim_Wolf_Death', 14), ('death_end', 'Anim_Wolf_Death', 32)]
# bite: the frame where the head reaches furthest forward
act = bpy.data.actions['Anim_Wolf_Bite']
best = None
for f in range(int(act.frame_range[0]), int(act.frame_range[1]) + 1):
    pose('Anim_Wolf_Bite', f)
    y = rig.pose.bones['head'].tail.y
    if best is None or y > best[0]:
        best = (y, f)
SHOTS[4] = ('bite', 'Anim_Wolf_Bite', best[1])
print('BITE furthest head reach at frame %d' % best[1])
for a in ('Anim_Wolf_Idle', 'Anim_Wolf_Run', 'Anim_Wolf_Bite', 'Anim_Wolf_Death'):
    lo = []
    r = bpy.data.actions[a].frame_range
    for f in range(int(r[0]), int(r[1]) + 1):
        pose(a, f)
        lo.append((lowest(new), lowest(old)))
    print('GROUND %s frames %d..%d: lowest point of the new wolf %.3f..%.3f, of the old wolf %.3f..%.3f' % (
        a, r[0], r[1], min(l[0] for l in lo), max(l[0] for l in lo), min(l[1] for l in lo), max(l[1] for l in lo)))
for tag, a, f in SHOTS:
    pose(a, f)
    for vn, vd in VIEWS.items():
        for nm, ob, other in (('new', new, old), ('old', old, new)):
            ob.hide_render = False; other.hide_render = True
            P.shoot(vd, (0, 0, 0.5), 2.3, OUT + '_%s_%s_%s.png' % (tag, vn, nm), suns)
pose(None, 0)


def load(p):
    im = bpy.data.images.load(p)
    w, h = im.size
    a = np.array(im.pixels[:], dtype=np.float32).reshape(h, w, 4)
    bpy.data.images.remove(im)
    a[:, :2, :3] = 1.0; a[:2, :, :3] = 1.0
    return a


def sheet(rows, out):
    sh = np.concatenate([np.concatenate([load(OUT + n) for n in r], axis=1) for r in reversed(rows)], axis=0)
    h, w, _ = sh.shape
    im = bpy.data.images.new('sheet', w, h, alpha=False)
    im.pixels = sh.ravel()
    im.filepath_raw = OUT + out; im.file_format = 'PNG'; im.save()
    print('SHEET', OUT + out, w, h)


# columns: rest, run, bite, death end; rows: new side, old side, new above-side, old above-side
cols = ('rest', 'run_a', 'bite', 'death_end')
sheet([['_%s_side_new.png' % c for c in cols], ['_%s_side_old.png' % c for c in cols],
       ['_%s_top_new.png' % c for c in cols], ['_%s_top_old.png' % c for c in cols]], 'wolf_new_vs_old.png')
cols2 = ('idle', 'run_b', 'death_mid', 'rest')
sheet([['_%s_side_new.png' % c for c in cols2], ['_%s_front_new.png' % c for c in ('rest', 'run_a', 'bite', 'death_end')],
       ['_%s_front_old.png' % c for c in ('rest', 'run_a', 'bite', 'death_end')]], 'qc_more_frames.png')
for f in os.listdir(OUT):
    if f.startswith('_'):
        os.remove(OUT + f)
