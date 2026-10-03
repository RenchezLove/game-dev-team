"""Leg / head close-ups of the new wolf: rest, run, bite.  Run: blender.exe -b --factory-startup --python 12_closeup.py"""
import bpy, sys, os
import numpy as np
sys.path.insert(0, 'E:/game-dev-team/assets/hero_tripo/_work'); sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W, hpose as P
from mathutils import Matrix
OUT = 'E:/game-dev-team/assets/wolf_tripo/renders/'
bpy.ops.wm.open_mainfile(filepath='E:/game-dev-team/assets/wolf_tripo/_work/wolf_work.blend')
rig = bpy.data.objects['WolfRig']; bpy.data.objects['SK_Wolf_old'].hide_render = True
sc, cam, suns = W.setup_render(res=800); sc.render.film_transparent = False
def pose(a, f):
    for pb in rig.pose.bones: pb.matrix_basis = Matrix.Identity(4)
    if a is None: rig.animation_data.action = None
    else:
        act = bpy.data.actions[a]; rig.animation_data.action = act
        if hasattr(rig.animation_data, 'action_slot') and act.slots: rig.animation_data.action_slot = act.slots[0]
        sc.frame_set(f)
    bpy.context.view_layer.update()
tiles = []
for tag, a, f in (('rest', None, 0), ('run4', 'Anim_Wolf_Run', 4), ('run12', 'Anim_Wolf_Run', 12), ('bite18', 'Anim_Wolf_Bite', 18)):
    pose(a, f)
    for vn, vd, c, h in (('legs', (1, 0.25, 0.1), (0, -0.05, 0.35), 1.0), ('legsfront', (0.5, 1, 0.2), (0, 0.1, 0.35), 1.0), ('head', (1, 0.6, 0.2), (0, 0.55, 0.8), 0.9)):
        p = OUT + '_c_%s_%s.png' % (tag, vn); P.shoot(vd, c, h, p, suns); tiles.append(p)
def load(p):
    im = bpy.data.images.load(p); w, h = im.size
    a = np.array(im.pixels[:], dtype=np.float32).reshape(h, w, 4); bpy.data.images.remove(im)
    a[:, :2, :3] = 1.0; a[:2, :, :3] = 1.0; return a
rows = [np.concatenate([load(t) for t in tiles[i:i + 3]], axis=1) for i in range(0, 12, 3)]
sh = np.concatenate(list(reversed(rows)), axis=0)
im = bpy.data.images.new('s', sh.shape[1], sh.shape[0], alpha=False); im.pixels = sh.ravel()
im.filepath_raw = OUT + 'qc_closeups.png'; im.file_format = 'PNG'; im.save()
for t in tiles: os.remove(t)
print('SHEET', OUT + 'qc_closeups.png')
