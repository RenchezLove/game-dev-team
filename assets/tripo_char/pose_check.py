"""Renders of a Tripo character on RootAnim: rest + step (run take, widest stride) + melee peak, front /
above-side (game camera pitch 60) / back, mixes with the T0 hero parts, close-ups of neck and waist.
For a coat character: counts leg vertices that come out through the coat over the whole run take.
Run: blender.exe -b --factory-startup --python pose_check.py -- <id>
"""
import bpy, bmesh, sys, os, math
import numpy as np
sys.path.insert(0, 'E:/game-dev-team/assets/tripo_char')
sys.path.insert(0, 'E:/game-dev-team/assets/hero_tripo/_work')
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W
import hpose as P
import configs
import addon_utils
from mathutils import Vector
from mathutils.bvhtree import BVHTree

C = configs.CFG[sys.argv[sys.argv.index('--') + 1]]
OUT = C['outdir'] + 'renders/'
HERO = 'E:/game-dev-team/assets/hero_tripo/_work/hero_work.blend'
bpy.ops.wm.open_mainfile(filepath=C['outdir'] + '_work/' + C['id'] + '_work.blend')
addon_utils.enable('io_scene_fbx')
rig = bpy.data.objects['RootAnim']
N = {s: bpy.data.objects[C['prefix'] + s] for s in ('Head', 'Torso', 'Legs')}
names = ['SK_Cloth_T0_' + s for s in ('Head', 'Torso', 'Legs')]
with bpy.data.libraries.load(HERO, link=False) as (src_d, dst_d):
    dst_d.objects = names
T0 = {}
for ob in dst_d.objects:
    bpy.context.scene.collection.objects.link(ob)
    W.rebind(ob, rig)
    T0[ob.name.split('_')[-1]] = ob
sc, cam, suns = W.setup_render(res=900)
sc.render.film_transparent = False
ALL = list(N.values()) + list(T0.values())
SETS = {'own': [N['Head'], N['Torso'], N['Legs']],
        'mixA': [N['Head'], T0['Torso'], N['Legs']],
        'mixB': [T0['Head'], N['Torso'], T0['Legs']],
        'legs': [N['Legs']]}
VIEWS = {'front': (0, -1, 0.10), 'top': (0.45, -0.75, 1.5), 'back': (0.2, 1, 0.25), 'side': (1, -0.15, 0.1)}


def show(objs):
    for o in ALL:
        o.hide_render = o not in objs


def shots(pose, sets, views):
    for sn in sets:
        show(SETS[sn])
        for vn in views:
            P.shoot(VIEWS[vn], (0, 0, 0.93), 2.25, OUT + '_%s_%s_%s.png' % (sn, pose, vn), suns)


def close(pose, sn, tag, vd, center, h):
    show(SETS[sn])
    P.shoot(vd, center, h, OUT + '_%s_%s_%s.png' % (sn, pose, tag), suns)


def deformed(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    e = ob.evaluated_get(dg)
    m = e.to_mesh()
    co = [ob.matrix_world @ v.co for v in m.vertices]
    fs = [tuple(p.vertices) for p in m.polygons]
    e.to_mesh_clear()
    return co, fs


def pierce(tag):
    """Leg-slot vertices that are under the coat at rest and lie outside the coat surface in this pose."""
    co, fs = deformed(N['Torso'])
    tree = BVHTree.FromPolygons(co, fs)
    lco, _ = deformed(N['Legs'])
    bad = 0; worst = 0.0; zr = []
    pb = rig.pose.bones['C_Root']
    a = pb.head.copy(); s = (pb.tail - pb.head).normalized()
    for i in UNDER:
        p = lco[i]
        r = (p - a) - s * (p - a).dot(s)            # outwards from the spine axis of this pose
        if r.length < 1e-4 or REST_Z[i] < HEM + 0.02:
            continue
        if tree.ray_cast(p, r.normalized(), 1.0)[0] is None:   # no coat wall beyond the vertex -> it is outside
            bad += 1; zr.append(REST_Z[i]); worst = max(worst, (tree.find_nearest(p)[0] - p).length)
    return bad, worst, (min(zr), max(zr)) if zr else (0, 0)


P.reset(rig)
if C.get('coat'):
    co, fs = deformed(N['Torso'])
    tree = BVHTree.FromPolygons(co, fs)
    lco, _ = deformed(N['Legs'])
    REST_Z = [p.z for p in lco]; HEM = min(c.z for c in co); REST = [p.copy() for p in lco]
    UNDER = [i for i, p in enumerate(lco) if all(tree.ray_cast(p, Vector((math.cos(math.pi * k / 4), math.sin(math.pi * k / 4), 0)), 2.0)[0] is not None for k in range(8))]
    print('COAT rest: %d of %d leg-slot vertices are enclosed by the coat; %d of them are 2 cm or more above the hem (z %.3f) and are tested' % (len(UNDER), len(lco), sum(1 for i in UNDER if REST_Z[i] >= HEM + 0.02), HEM))

shots('rest', ('own', 'mixA', 'mixB'), ('front', 'top', 'back'))
shots('rest', ('legs',), ('front', 'back'))
for sn in ('own', 'mixA', 'mixB'):
    close('rest', sn, 'neck', (0.5, -1, 0.3), (0, 0, 1.52), 0.5)
    close('rest', sn, 'neckback', (-0.5, 1, 0.4), (0, 0, 1.52), 0.5)
    close('rest', sn, 'waist', (0.5, -1, 0.25), (0, 0, 0.92), 0.6)
    close('rest', sn, 'waistback', (-0.5, 1, 0.25), (0, 0, 0.92), 0.6)

src, nm = P.load_source(P.RUN, None, 'RunSrc')
print('RUN source rest delta vs ours = %.6f' % P.rest_delta(src, nm, rig))
act = src.animation_data.action
f0, f1 = [int(v) for v in act.frame_range]
best = None
for f in range(f0, f1 + 1):
    P.transfer(src, nm, rig, f)
    d = abs(rig.pose.bones['L_Foot'].head.y - rig.pose.bones['R_Foot'].head.y)
    if best is None or d > best[0]:
        best = (d, f)
    if C.get('coat'):
        b, wst, zr = pierce(f)
        print('COAT run frame %2d: stride %.3f, leg vertices outside the coat %d (deepest %.3f m, their rest heights %.3f..%.3f)' % (f, d, b, wst, zr[0], zr[1]))
print('RUN take frames %d..%d, widest stride %.3f m at frame %d' % (f0, f1, best[0], best[1]))
P.transfer(src, nm, rig, best[1])
shots('step', ('own', 'mixA', 'mixB'), ('front', 'top', 'back', 'side'))
close('step', 'own', 'waist', (0.5, -1, 0.25), (0, 0, 0.80), 0.9)
close('step', 'own', 'waistside', (1, -0.1, 0.1), (0, 0, 0.80), 0.9)
close('step', 'own', 'waistback', (-0.5, 1, 0.25), (0, 0, 0.80), 0.9)
bpy.data.objects.remove(src, do_unlink=True)

src, nm = P.load_source(P.ANIM_QC, 'Anim_MeleeSlash_Humanoid', 'MeleeSrc')
reach = []
for f in range(1, 22):
    P.transfer(src, nm, rig, f)
    reach.append((rig.pose.bones['R_Hand'].head.y, f))
fpk = min(reach)[1]
print('MELEE peak reach frame', fpk)
P.transfer(src, nm, rig, fpk)
shots('melee', ('own',), ('front', 'back'))
close('melee', 'own', 'upper', (-0.55, 1, 0.75), (0, 0, 1.30), 1.25)
bpy.data.objects.remove(src, do_unlink=True)
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


I = C['id']
sheet([['_own_rest_front.png', '_own_rest_top.png'], ['_own_step_front.png', '_own_step_top.png']], I + '_rest_and_step.png')
sheet([['_own_rest_front.png', '_own_rest_back.png', '_mixA_rest_front.png', '_mixB_rest_front.png', '_legs_rest_front.png'],
       ['_own_step_side.png', '_own_step_back.png', '_mixA_step_front.png', '_mixB_step_front.png', '_legs_rest_back.png']], 'qc_mix.png')
sheet([['_%s_rest_%s.png' % (s, t) for t in ('neck', 'neckback', 'waist', 'waistback')] for s in ('own', 'mixA', 'mixB')], 'qc_close_rest.png')
sheet([['_own_step_waist.png', '_own_step_waistside.png', '_own_step_waistback.png'],
       ['_own_melee_front.png', '_own_melee_back.png', '_own_melee_upper.png']], 'qc_step_melee.png')
for f in os.listdir(OUT):
    if f.startswith('_'):
        os.remove(OUT + f)
