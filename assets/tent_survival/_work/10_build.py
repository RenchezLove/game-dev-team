"""SM_Tent (survival shelter after the Sketchfab model 'Low Poly Survival Tent' by simonaskLDE, CC Attribution) with fewer triangles.
The source (172 tris: two slab tarps of 36, five hexagonal poles of 20) is rebuilt over its own measurements: every pole becomes a
square prism on the axis and mean radius of the source pole (legs: no bottom cap, it stands on the ground), every tarp becomes one
quad on the outer surface of the source slab plus one quad for its underside (Unreal does not draw the back of a face, and the
underside shows through the open ends at the edges of the game view).  Scaled and placed on the footprint of the old SM_Tent:
origin (0,0,0), bottom at Z 0, ridge and both open ends along Y, width = the narrowest old half-width (0.76 m) on both sides.
Face int layers 'part' / 'grp' drive the painter; grp matrices and pole axes -> _grp.npz.
Run: blender.exe -b --factory-startup --python 10_build.py
"""
import bpy, bmesh, math, os
import numpy as np
import addon_utils
from mathutils import Vector, Matrix

SRC = 'C:/Users/pgr40/Desktop/GamdevAITeam/Палатка/low-poly-survival-tent/source/tent.fbx'
OUT = 'E:/game-dev-team/assets/tent_survival/_work/'
NAME = 'SM_Tent'
WIDTH = 1.52                     # old SM_Tent spans x -0.76 .. 0.80: the new one is centred, so it takes 2 x 0.76
OLD_MIN, OLD_MAX = (-0.76, -1.434), (0.80, 1.434)
P_TARP, P_TARPIN, P_POLE, P_POLECAP = 1, 2, 3, 4
SQ = 1.0                         # half-side of the square pole in mean radii of the hexagonal source pole (a little thicker: read from 30 m)
INNER = 0.006                    # the underside of the tarp lies this far (m) under the outer face

bpy.ops.wm.read_factory_settings(use_empty=True)
addon_utils.enable('io_scene_fbx')
bpy.ops.import_scene.fbx(filepath=SRC)
bpy.context.view_layer.update()
src = {o.name: o for o in bpy.data.objects if o.type == 'MESH'}
print('SOURCE objects %s, triangles %d' % (sorted(src), sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in src.values())))
POLES = []                                                   # (name, bottom centre, top centre, mean radius) in source units
for n in ('F.L', 'F.R', 'B.L', 'B.R', 'T'):
    o = src[n]; w = [o.matrix_world @ v.co for v in o.data.vertices]
    a = sum((w[i] for i in range(0, 12, 2)), Vector()) / 6; b = sum((w[i] for i in range(1, 12, 2)), Vector()) / 6
    if n != 'T' and a.z > b.z:
        a, b = b, a
    ax = (b - a).normalized()
    r = sum(((p - a) - ax * (p - a).dot(ax)).length for p in w) / 12
    POLES.append((n, a, b, r))
    print('SOURCE pole %-3s axis (%.3f %.3f %.3f) -> (%.3f %.3f %.3f) mean radius %.3f' % (n, *a, *b, r))
TARPS = []                                                   # (name, top front, top back, bottom front, bottom back): outer side of the slab
for n in ('T.L', 'T.R'):
    o = src[n]; w = [o.matrix_world @ v.co for v in o.data.vertices]
    c = [w[1], w[3], w[0], w[2]]
    if c[0].y > c[1].y:
        c = [c[1], c[0], c[3], c[2]]
    TARPS.append((n, *c))
    print('SOURCE tarp %s outer corners: top (%.3f %.3f %.3f) (%.3f %.3f %.3f) bottom (%.3f %.3f %.3f) (%.3f %.3f %.3f)' % (n, *c[0], *c[1], *c[2], *c[3]))
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o)


def build(T, s):
    bm = bmesh.new()
    LP = bm.faces.layers.int.new('part'); LG = bm.faces.layers.int.new('grp')
    GM = [Matrix.Identity(4)]; GI = [[0.0] * 6]; AX = [[0.0] * 6]
    def quad(pts, part, g, want):
        """One-sided face turned to look along 'want' (a new bmesh face has a zero normal until normal_update())."""
        f = bm.faces.new([bm.verts.new(p) for p in pts]); f[LP] = part; f[LG] = g
        f.normal_update()
        if f.normal.dot(want) < 0:
            f.normal_flip()
    for n, a, b, r in POLES:
        a, b = T @ a, T @ b; h = r * s * SQ; ln = (b - a).length
        z = (b - a).normalized(); ref = Vector((0, 1, 0)) if abs(z.y) < 0.9 else Vector((1, 0, 0))
        x = (ref - z * ref.dot(z)).normalized(); y = z.cross(x)
        M = Matrix((x, y, z)).transposed().to_4x4(); M.translation = a
        GM.append(M); GI.append([2, ln, h, 0, 0, 0]); AX.append(list(a) + list(b)); g = len(GM) - 1
        c = [(-h, -h), (h, -h), (h, h), (-h, h)]
        for i in range(4):
            (x0, y0), (x1, y1) = c[i], c[(i + 1) % 4]
            quad([M @ Vector(p) for p in ((x0, y0, 0), (x1, y1, 0), (x1, y1, ln), (x0, y0, ln))], P_POLE, g, M.to_3x3() @ Vector(((x0 + x1) / 2, (y0 + y1) / 2, 0)))
        quad([M @ Vector((px, py, ln)) for px, py in c], P_POLECAP, g, z)
        if n == 'T':                                         # the ridge pole hangs in the forks: both ends are seen
            quad([M @ Vector((px, py, 0)) for px, py in c], P_POLECAP, g, -z)
    for i, (n, tf, tb, bf, bb) in enumerate(TARPS):
        tf, tb, bf, bb = T @ tf, T @ tb, T @ bf, T @ bb
        x = (tb - tf).normalized(); y = (bf - tf); y = (y - x * y.dot(x)).normalized(); z = x.cross(y)
        if z.z < 0:
            z = -z
        M = Matrix((x, y, z)).transposed().to_4x4(); M.translation = tf
        for inner in (0, 1):
            GM.append(M); GI.append([1, (tb - tf).length, (bf - tf).length, inner, i, 0]); AX.append([0.0] * 6)
            d = -z * INNER * inner
            quad([tf + d, tb + d, bb + d, bf + d], P_TARPIN if inner else P_TARP, len(GM) - 1, -z if inner else z)
    return bm, GM, GI, AX


bm, _, _, _ = build(Matrix.Identity(4), 1.0)
lo = Vector([min(v.co[i] for v in bm.verts) for i in range(3)]); hi = Vector([max(v.co[i] for v in bm.verts) for i in range(3)])
bm.free()
s = WIDTH / (hi.x - lo.x)
T = Matrix.Diagonal((s, s, s, 1)) @ Matrix.Translation(-Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z)))
print('PLACE scale %.5f (source %.3f x %.3f x %.3f units)' % (s, *(hi - lo)))
bm, GM, GI, AX = build(T, s)
bm.normal_update()
bmesh.ops.triangulate(bm, faces=bm.faces[:])
me = bpy.data.meshes.new(NAME)
bm.to_mesh(me); bm.free()
for p in me.polygons:
    p.use_smooth = False
ob = bpy.data.objects.new(NAME, me)
bpy.context.scene.collection.objects.link(ob)
part = np.zeros(len(me.polygons), np.int32); me.attributes['part'].data.foreach_get('value', part)
assert part.min() > 0
co = np.array([v.co[:] for v in me.vertices])
assert abs(co[:, 2].min()) < 1e-6 and co[:, 0].min() >= OLD_MIN[0] - 1e-4 and co[:, 0].max() <= OLD_MAX[0] + 1e-4 and co[:, 1].min() >= OLD_MIN[1] and co[:, 1].max() <= OLD_MAX[1]


def overlaps(layer, res=1024):
    T_ = len(me.polygons)
    a = np.zeros(len(me.loops) * 2); me.uv_layers[layer].data.foreach_get('uv', a)
    uv = a.reshape(T_, 3, 2)
    inner = np.zeros((res, res), np.int16)
    for t in range(T_):
        p = uv[t] * res
        d = (p[1, 0] - p[0, 0]) * (p[2, 1] - p[0, 1]) - (p[1, 1] - p[0, 1]) * (p[2, 0] - p[0, 0])
        if abs(d) < 1e-9:
            continue
        x0 = max(int(math.floor(p[:, 0].min())), 0); x1 = min(int(math.ceil(p[:, 0].max())) + 1, res)
        y0 = max(int(math.floor(p[:, 1].min())), 0); y1 = min(int(math.ceil(p[:, 1].max())) + 1, res)
        X, Y = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
        w1 = ((X - p[0, 0]) * (p[2, 1] - p[0, 1]) - (Y - p[0, 1]) * (p[2, 0] - p[0, 0])) / d
        w2 = ((p[1, 0] - p[0, 0]) * (Y - p[0, 1]) - (p[1, 1] - p[0, 1]) * (X - p[0, 0])) / d
        w0 = 1 - w1 - w2
        el = [np.linalg.norm(p[2] - p[1]), np.linalg.norm(p[0] - p[2]), np.linalg.norm(p[1] - p[0])]
        dist = np.minimum(np.minimum(w0 * abs(d) / el[0], w1 * abs(d) / el[1]), w2 * abs(d) / el[2])
        inner[y0:y1, x0:x1] += (dist > 0.6)
    return int((inner > 1).sum())


UVK = {P_TARP: 1.0, P_TARPIN: 0.45, P_POLE: 0.8, P_POLECAP: 1.0}     # texel density per part (the underside of the tarp is hardly seen)
bpy.context.scene.tool_settings.use_uv_select_sync = True
def unwrap(layer, margin, weighted):
    me.uv_layers.active = me.uv_layers[layer]
    for ang in (66, 50, 35):
        bpy.ops.object.select_all(action='DESELECT')
        ob.select_set(True); bpy.context.view_layer.objects.active = ob
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=math.radians(ang), island_margin=0.0, correct_aspect=True, scale_to_bounds=False)
        bpy.ops.object.mode_set(mode='OBJECT')
        if weighted:
            d = me.uv_layers[layer].data
            for p in me.polygons:
                k = UVK.get(int(part[p.index]), 1.0)
                for li in p.loop_indices:
                    d[li].uv = d[li].uv * k
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.pack_islands(rotate=True, margin_method='FRACTION', margin=margin, shape_method='AABB')     # the default shape method can hang forever
        bpy.ops.object.mode_set(mode='OBJECT')
        n = overlaps(layer)
        print('UNWRAP %s angle %d: overlapping texels %d' % (layer, ang, n), flush=True)
        if n == 0:
            break
me.uv_layers.new(name='UVMap'); me.uv_layers.new(name='LightmapUV')
unwrap('UVMap', 0.008, True)
unwrap('LightmapUV', 0.02, False)
me.uv_layers.active = me.uv_layers['UVMap']; me.uv_layers['UVMap'].active_render = True
mat = bpy.data.materials.new('M_TentSurvival'); mat.use_nodes = True
me.materials.append(mat)
np.savez(OUT + '_grp.npz', M=np.array([[list(r) for r in m] for m in GM], np.float64), I=np.array(GI, np.float64), AX=np.array(AX, np.float64))
cnt = {}
for p in part:
    cnt[int(p)] = cnt.get(int(p), 0) + 1
print('BUILD tris %d verts %d min %s max %s size %s parts %s' % (len(me.polygons), len(me.vertices), co.min(0).round(3), co.max(0).round(3), (co.max(0) - co.min(0)).round(3), sorted(cnt.items())))
bpy.ops.wm.save_as_mainfile(filepath=OUT + 'tent_work.blend')
