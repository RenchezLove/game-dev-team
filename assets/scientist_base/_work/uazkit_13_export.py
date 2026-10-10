"""Export the eight FBX of the UAZ kit (origin of each part on its mounting point) and check the written files by importing them back:
triangles, origin, where every face looks, UV; then put the kit together by the mounting points and compare it with the one-piece SM_UAZ452.fbx.
Run: blender -b uazkit_work.blend --factory-startup --python uazkit_13_export.py"""
import bpy, math, sys, os
import numpy as np
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
sys.path.insert(0, 'E:/game-dev-team/assets/scientist_base/_work')
import sb, uazkit_common as U
OUT = sb.ROOT + 'SM_UAZ452_kit/'
parts = U.split()
REF = {}
for n, o in parts.items():
    o.location = (0, 0, 0); bpy.context.view_layer.update()
    REF[n] = sb.ref_of(o)
    for a in ('wx', 'wy', 'wz'):
        o.data.attributes.remove(o.data.attributes[a])
    sb.export_fbx([o], OUT + o.name + '.fbx')
tex = OUT + 'T_UAZ452Kit_D.png'
ok_all = True; RES = {}
for n in U.PARTS:
    name = 'SM_UAZ452_' + n
    ok, res = sb.roundtrip(OUT + name + '.fbx', name, REF[n], 1293, [tex], 1024, uv_expect=('UVMap',), origin_ground=False, centred=False)
    ok_all &= ok; RES[n] = res
ti = bpy.data.images.load(tex)
A = np.array(ti.pixels[:], dtype=np.float32).reshape(ti.size[1], ti.size[0], ti.channels)
print('TEXTURE %dx%d channels %d; paint mask (alpha) set on %.1f%% of the picture, values other than 0 and 1: %d' % (ti.size[0], ti.size[1], ti.channels, 100 * (A[..., 3] > 0.5).mean() if ti.channels == 4 else -1,
      int(((A[..., 3] > 0.02) & (A[..., 3] < 0.98)).sum()) if ti.channels == 4 else -1))
ok_all &= ti.channels == 4
# ---- assembly by the mounting points against the one-piece model
sb.empty()
def load(path):
    before = set(bpy.data.objects); bpy.ops.import_scene.fbx(filepath=path)
    return [o for o in bpy.data.objects if o not in before and o.type == 'MESH'][0]
V = []; F = []; tris = 0
def add(o, loc, rz=0.0):
    global tris
    M = Matrix.Translation(Vector(loc)) @ Matrix.Rotation(rz, 4, 'Z') @ o.matrix_world
    off = len(V); V.extend([M @ v.co for v in o.data.vertices]); F.extend([[i + off for i in p.vertices] for p in o.data.polygons]); tris += len(o.data.polygons)
print('MOUNTING POINTS (Unreal, cm, from the body origin; X to the right side, nose -Y):')
for n in U.PARTS:
    o = load(OUT + 'SM_UAZ452_%s.fbx' % n)
    if n == 'Wheel':
        for nm, c in zip(('front left', 'front right', 'rear left', 'rear right'), U.META['wheels']):
            add(o, c, 0.0 if c[0] < 0 else math.pi); print('  Wheel %-11s %s' % (nm, U.ue(c)))
    else:
        p = U.pivot(n); add(o, p); print('  %-17s %s' % (n, U.ue(p)))
print('WHEEL radius %.1f cm, width %.1f cm' % (U.META['wheel_r'] * 100, U.META['wheel_hw'] * 200))
K = np.array([v[:] for v in V])
mono = load(sb.ROOT + 'SM_UAZ452/SM_UAZ452.fbx')
Mv = [mono.matrix_world @ v.co for v in mono.data.vertices]; Mn = np.array([v[:] for v in Mv])
tm = BVHTree.FromPolygons(Mv, [list(p.vertices) for p in mono.data.polygons]); tk = BVHTree.FromPolygons(V, F)
d1 = np.array([tm.find_nearest(v)[3] for v in V]); d2 = np.array([tk.find_nearest(v)[3] for v in Mv])
print('ASSEMBLED kit: triangles %d (limit 1293); min %s max %s' % (tris, K.min(0).round(3), K.max(0).round(3)))
print('ONE-PIECE SM_UAZ452: triangles %d; min %s max %s' % (len(mono.data.polygons), Mn.min(0).round(3), Mn.max(0).round(3)))
inner = d1 > 0.05
print('DISTANCE kit points -> one-piece surface: median %.4f m, 95%% %.4f m, max %.4f m (points further than 5 cm: %d - plugs, cabin floor and inner wheel sides the one-piece model does not have)' % (
    np.median(d1), np.percentile(d1, 95), d1.max(), int(inner.sum())))
print('DISTANCE one-piece points -> kit surface: median %.4f m, 95%% %.4f m, max %.4f m' % (np.median(d2), np.percentile(d2, 95), d2.max()))
same_box = np.abs(K.min(0) - Mn.min(0)).max() < 0.01 and np.abs(K.max(0) - Mn.max(0)).max() < 0.01
ok_all &= tris <= 1293 and same_box and np.percentile(d2, 95) < 0.03
print('KIT ROUNDTRIP', 'PASS' if ok_all else 'FAIL', '| outer size equal to the one-piece model within 1 cm:', same_box)
