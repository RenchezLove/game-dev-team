"""Renders of the T1 Tripo set on RootAnim: rest + the melee-slash peak frame, front and
from above-side (game camera pitch 60), plus mixes with the T0 hero parts and close-ups.
Run: blender.exe -b --factory-startup --python 11_pose_check.py
"""
import bpy, sys, os, math
import numpy as np
sys.path.insert(0, 'E:/game-dev-team/assets/hero_tripo/_work')
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W
import hpose as P
import addon_utils
from mathutils import Vector

OUT = 'E:/game-dev-team/assets/armor_t1_tripo/renders/'
HERO = 'E:/game-dev-team/assets/hero_tripo/_work/hero_work.blend'
bpy.ops.wm.open_mainfile(filepath='E:/game-dev-team/assets/armor_t1_tripo/_work/t1_work.blend')
addon_utils.enable('io_scene_fbx')
rig = bpy.data.objects['RootAnim']
T1 = {s: bpy.data.objects['SK_Armor_T1_' + s] for s in ('Head', 'Torso', 'Legs')}
names = ['SK_Cloth_T0_' + s for s in ('Head', 'Torso', 'Legs')]
with bpy.data.libraries.load(HERO, link=False) as (src_d, dst_d):
    dst_d.objects = names
T0 = {}
for ob in dst_d.objects:
    bpy.context.scene.collection.objects.link(ob)
    W.rebind(ob, rig)
    T0[ob.name.split('_')[-1]] = ob
for im in bpy.data.images:
    print('IMG', im.name, im.filepath, tuple(im.size))
for m in bpy.data.materials:
    for n in (m.node_tree.nodes if m.node_tree else []):
        if n.type == 'TEX_IMAGE':
            n.interpolation = 'Linear'

sc, cam, suns = W.setup_render(res=900)
sc.render.film_transparent = False
ALL = list(T1.values()) + list(T0.values())


def show(objs):
    for o in ALL:
        o.hide_render = o not in objs


SETS = {'t1': [T1['Head'], T1['Torso'], T1['Legs']],
        'mixA': [T1['Head'], T0['Torso'], T1['Legs']],      # cap head + T1 jeans on the T0 sweater
        'mixB': [T0['Head'], T1['Torso'], T0['Legs']],      # jacket on the T0 head and legs
        't0': [T0['Head'], T0['Torso'], T0['Legs']]}
VIEWS = {'front': (0, -1, 0.10), 'top': (0.45, -0.75, 1.5), 'back': (0.2, 1, 0.25)}


def shots(pose, sets=('t1',), views=('front', 'top')):
    for sn in sets:
        show(SETS[sn])
        for vn in views:
            P.shoot(VIEWS[vn], (0, 0, 0.93), 2.25, OUT + '_%s_%s_%s.png' % (sn, pose, vn), suns)


def close(pose, sn, tag, vd, center, h):
    show(SETS[sn])
    P.shoot(vd, center, h, OUT + '_%s_%s_%s.png' % (sn, pose, tag), suns)


P.reset(rig)
shots('rest', ('t1', 'mixA', 'mixB', 't0'), ('front', 'top', 'back'))
for sn in ('t1', 'mixA', 'mixB'):
    close('rest', sn, 'neck', (0.5, -1, 0.3), (0, 0, 1.52), 0.5)
    close('rest', sn, 'neckback', (-0.5, 1, 0.4), (0, 0, 1.52), 0.5)
    close('rest', sn, 'waist', (0.5, -1, 0.25), (0, 0, 0.92), 0.6)
    close('rest', sn, 'waistback', (-0.5, 1, 0.25), (0, 0, 0.92), 0.6)

src, nm = P.load_source(P.ANIM_QC, 'Anim_MeleeSlash_Humanoid', 'MeleeSrc')
print('MELEE source rest delta vs ours = %.6f' % P.rest_delta(src, nm, rig))
reach = []
for f in range(1, 22):
    P.transfer(src, nm, rig, f)
    reach.append((rig.pose.bones['R_Hand'].head.y, f))
fpk = min(reach)[1]
print('MELEE peak reach frame', fpk)
P.transfer(src, nm, rig, fpk)
shots('melee', ('t1', 'mixA', 'mixB'), ('front', 'top', 'back'))
for sn in ('t1', 'mixA', 'mixB'):
    close('melee', sn, 'upper', (-0.55, 1, 0.75), (0, 0, 1.30), 1.25)
    close('melee', sn, 'waist', (0.5, -1, 0.25), (0, 0, 0.92), 0.6)
bpy.data.objects.remove(src, do_unlink=True)
src, nm = P.load_source(P.RUN, None, 'RunSrc')
P.transfer(src, nm, rig, 10)
shots('run', ('t1', 'mixA', 'mixB'), ('front',))
P.reset(rig)


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


sheet([['_t1_rest_front.png', '_t1_rest_top.png'], ['_t1_melee_front.png', '_t1_melee_top.png']], 'armor_t1_rest_and_melee.png')
sheet([['_t1_rest_front.png', '_t0_rest_front.png', '_mixA_rest_front.png', '_mixB_rest_front.png'],
       ['_t1_rest_back.png', '_t0_rest_back.png', '_mixA_rest_back.png', '_mixB_rest_back.png']], 'qc_mix_rest.png')
sheet([['_t1_melee_front.png', '_mixA_melee_front.png', '_mixB_melee_front.png', '_t1_run_front.png'],
       ['_t1_melee_back.png', '_mixA_melee_back.png', '_mixB_melee_back.png', '_mixB_run_front.png']], 'qc_mix_melee.png')
sheet([['_%s_rest_%s.png' % (s, t) for t in ('neck', 'neckback', 'waist', 'waistback')] for s in ('t1', 'mixA', 'mixB')], 'qc_close_rest.png')
sheet([['_%s_melee_%s.png' % (s, t) for s in ('t1', 'mixA', 'mixB')] for t in ('upper', 'waist')], 'qc_close_melee.png')
