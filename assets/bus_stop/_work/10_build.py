"""Bus stop after the Sketchfab model 'Old Russian bus stop' by halkiridze (CC Attribution), at most 800 triangles in all.
Three separate objects on one shared texture: SM_BusStop (shelter with walls and bench), SM_BusStopSign (bus sign on a pole),
SM_BusStopUrn (litter bin).  The source (2582 tris, open side +Y, 4 m deep) is rebuilt over its own sizes and turned by 180
degrees: the open side looks -Y.  The shelter is made shallow: the roof ends 39 cm in front of the bench, so the player cannot
hide under it.  The roof is one flat slab (ribs are painted), walls are flat (the profile is painted).
Simple convex blocks UCX_SM_BusStop_01.. / UCX_SM_BusStopUrn_01 are added for collision.
Face layers: 'part', 'grp' (decal frames), 'obj', 'wx/wy/wz' = where the face has to look (used by the export check).
Run: blender.exe -b --factory-startup --python 10_build.py
"""
import bpy, bmesh, math
import numpy as np
import addon_utils
from mathutils import Vector, Matrix

SRC = 'C:/Users/pgr40/Desktop/GamdevAITeam/Автобусная остановка/old-russian-bus-stop/source/FBX.fbx'
OUT = 'E:/game-dev-team/assets/bus_stop/_work/'
NAMES = ['SM_BusStop', 'SM_BusStopSign', 'SM_BusStopUrn']
(P_ROOF, P_ROOFUNDER, P_ROOFEDGE, P_WALL, P_FENCE, P_POST, P_BEAM, P_RAFTER, P_RAIL, P_BENCH, P_BENCHLEG,
 P_SCHED, P_PLATEBACK, P_AD) = range(1, 15)
P_POLE, P_SIGNFACE, P_SIGNBACK, P_BRACKET = 20, 21, 22, 23
P_URNOUT, P_URNIN, P_URNRIM, P_URNBOTTOM = 30, 31, 32, 33

# ---- sizes (metres).  d = distance from the inner face of the back wall towards the open side; y = Y0 - d ----
RX = 2.35                        # roof half-width (source 4.70 wide)
D_BACK, D_FRONT = -0.45, 0.95    # roof edges: bench front (0.56) + 0.39 free = 0.95
Y0 = (D_BACK + D_FRONT) / 2      # the footprint is centred on the origin
Z_FRONT, SLOPE, RT = 2.70, 0.12, 0.04
XP, PW, PD = 1.98, 0.09, 0.10    # posts: centre x, half-width, half-depth (source 0.18 x 0.20)
D_BP, D_FP = -0.03, 0.78         # back / front posts
WALL_T, WALL_H = 0.06, 2.16      # back wall (source top 2.16)
BENCH_D, BENCH_Z0, BENCH_Z1 = 0.56, 0.42, 0.505
FENCE_H = 0.76
PLACE = [Vector((0, 0, 0)), Vector((-3.0, Y0 - 1.78, 0)), Vector((1.62, Y0 - 1.25, 0))]     # where sign and urn stand by the shelter
URN_R, URN_H, URN_T, URN_N, URN_FLOOR = 0.28, 0.60, 0.03, 12, 0.25
POLE_R, POLE_H, POLE_N = 0.06, 2.47, 8
def Y(d):
    return Y0 - d
def ztop(y):
    return Z_FRONT - SLOPE * (D_FRONT - (Y0 - y))

# ---- the source: decals (bus sign, timetable, two notices) keep the picture of the source texture ----
bpy.ops.wm.read_factory_settings(use_empty=True)
addon_utils.enable('io_scene_fbx')
bpy.ops.import_scene.fbx(filepath=SRC)
bpy.context.view_layer.update()
src = {o.name: o for o in bpy.data.objects if o.type == 'MESH'}
print('SOURCE objects %s' % sorted(src))
print('SOURCE triangles %d: %s' % (sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in src.values()),
      ', '.join('%s %d' % (n, sum(len(p.vertices) - 2 for p in o.data.polygons)) for n, o in sorted(src.items()))))
def decal(name, img, min_area, ymin=-1e9):
    """Front (+Y) face of a source plate: its rectangle (x0 x1 z0 z1) and the affine map (x, z) -> uv of the source texture."""
    o = src[name]; me = o.data; mw = o.matrix_world; n3 = mw.to_3x3(); uvl = me.uv_layers[0].data
    fs = [p for p in me.polygons if (n3 @ p.normal).normalized().y > 0.9 and p.area > min_area and (mw @ p.center).y > ymin]
    A, U = [], []
    for p in fs:
        for li in p.loop_indices:
            w = mw @ me.vertices[me.loops[li].vertex_index].co
            A.append([w.x, w.z, 1.0]); U.append(list(uvl[li].uv))
    A, U = np.array(A), np.array(U)
    X, res, _, _ = np.linalg.lstsq(A, U, rcond=None)
    err = np.abs(A @ X - U).max()
    x0, x1, z0, z1 = A[:, 0].min(), A[:, 0].max(), A[:, 1].min(), A[:, 1].max()
    uv = lambda x, z: list(np.array([x, z, 1.0]) @ X)
    print('SOURCE decal %-8s faces %3d rect x %.3f..%.3f z %.3f..%.3f (%.3f x %.3f m), worst fit error %.4f uv, uv corners %s %s %s' % (
        name, len(fs), x0, x1, z0, z1, x1 - x0, z1 - z0, err, np.round(uv(x0, z0), 3), np.round(uv(x1, z0), 3), np.round(uv(x0, z1), 3)))
    return dict(rect=(x0, x1, z0, z1), row=[img] + uv(x0, z0) + uv(x1, z0) + uv(x0, z1))
def notice(name, img, w, h, uv00, uv10, uv01):
    """A curled sheet of paper in the source: laid flat here, w x h around the middle of its bounds, with its own uv rectangle."""
    o = src[name]; c = np.array([o.matrix_world @ v.co for v in o.data.vertices]); cx, cz = (c[:, 0].min() + c[:, 0].max()) / 2, (c[:, 2].min() + c[:, 2].max()) / 2
    print('SOURCE notice %-8s middle x %.3f z %.3f, laid flat %.2f x %.2f m' % (name, cx, cz, w, h))
    return dict(rect=(cx - w / 2, cx + w / 2, cz - h / 2, cz + h / 2), row=[img] + list(uv00) + list(uv10) + list(uv01))
D_SIGN = decal('znak4', 1, 0.0005, ymin=1.063)               # the plate only: the pole faces lie at y < 1.06
D_SCHED = decal('gvozd', 0, 0.05)
D_AD1 = notice('obv.002', 0, 0.32, 0.40, (0.307, 0.651), (0.005, 0.651), (0.307, 0.953))     # 'flat to let' with tear-off phone numbers
D_AD2 = notice('obv.003', 0, 0.32, 0.30, (0.622, 0.664), (0.313, 0.664), (0.622, 0.953))     # 'potatoes, cheap'
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o)

bm = bmesh.new()
LP = bm.faces.layers.int.new('part'); LG = bm.faces.layers.int.new('grp'); LO = bm.faces.layers.int.new('obj')
LW = [bm.faces.layers.float.new(n) for n in ('wx', 'wy', 'wz')]
GM = [Matrix.Identity(4)]; GI = [[0.0] * 4]; DEC = [[0.0] * 7]
OBJ = 0
def quad(pts, part, want, g=0):
    """One-sided face turned to look along 'want' (a new bmesh face has a zero normal until normal_update())."""
    off = PLACE[OBJ]
    f = bm.faces.new([bm.verts.new(Vector(p) + off) for p in pts]); f[LP] = part; f[LG] = g; f[LO] = OBJ
    want = Vector(want).normalized()
    for i in range(3):
        f[LW[i]] = want[i]
    f.normal_update()
    if f.normal.dot(want) < 0:
        f.normal_flip()
    return f
FACES = {'-x': ((0, 0, 0), (0, 1, 0), (0, 1, 1), (0, 0, 1)), '+x': ((1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)),
         '-y': ((0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)), '+y': ((0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)),
         '-z': ((0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)), '+z': ((0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1))}
def hexa(c, part, faces, parts=None):
    """Block from 8 corners c[(i, j, k)] (low / high x, y, z); only the named faces; each looks away from the middle of the block."""
    mid = sum((Vector(v) for v in c.values()), Vector()) / 8
    for name in faces:
        pts = [Vector(c[k]) for k in FACES[name]]
        quad(pts, (parts or {}).get(name, part), sum(pts, Vector()) / 4 - mid)
def box(lo, hi, part, faces, parts=None):
    c = {(i, j, k): ((hi if i else lo)[0], (hi if j else lo)[1], (hi if k else lo)[2]) for i in (0, 1) for j in (0, 1) for k in (0, 1)}
    hexa(c, part, faces, parts)
def sloped(x0, x1, y0, y1, drop, height, part, faces, parts=None):
    """Block under the roof slope: its top lies 'drop' under the top of the roof."""
    c = {(i, j, k): ((x1 if i else x0), (y1 if j else y0), ztop(y1 if j else y0) - drop - (0 if k else height)) for i in (0, 1) for j in (0, 1) for k in (0, 1)}
    hexa(c, part, faces, parts)
def add_decal(d, origin, part):
    """Quad with the picture of a source plate; the source is turned by 180 degrees: source +x runs along -X here."""
    x0, x1, z0, z1 = d['rect']; w, h = x1 - x0, z1 - z0
    M = Matrix(((-1, 0, 0), (0, 0, 1), (0, -1, 0))).transposed().to_4x4(); M.translation = Vector(origin) + PLACE[OBJ]
    GM.append(M); GI.append([w, h, 0, 0]); DEC.append(d['row'])
    o = Vector(origin)
    quad([o, o + Vector((-w, 0, 0)), o + Vector((-w, 0, h)), o + Vector((0, 0, h))], part, (0, -1, 0), len(GM) - 1)
    return w, h

# ================= SM_BusStop =================
OBJ = 0
yb, yf = Y(D_BACK), Y(D_FRONT)
quad([(-RX, yf, ztop(yf)), (RX, yf, ztop(yf)), (RX, yb, ztop(yb)), (-RX, yb, ztop(yb))], P_ROOF, (0, 0, 1))
quad([(-RX, yf, ztop(yf) - RT), (RX, yf, ztop(yf) - RT), (RX, yb, ztop(yb) - RT), (-RX, yb, ztop(yb) - RT)], P_ROOFUNDER, (0, 0, -1))   # seen from below at the edge of the game view
sloped(-RX, RX, yf, yb, 0.0, RT, P_ROOFEDGE, ('-x', '+x', '-y', '+y'))
for sx in (-1, 1):
    x0, x1 = sorted((sx * (XP - PW), sx * (XP + PW)))
    for dc in (D_BP, D_FP):                                   # posts stand under the rafters
        y0, y1 = Y(dc + PD), Y(dc - PD)
        box((x0, y0, 0), (x1, y1, ztop((y0 + y1) / 2) - RT - 0.10), P_POST, ('-x', '+x', '-y', '+y'))
    sloped(sx * XP - 0.06, sx * XP + 0.06, Y(D_FRONT - 0.02), Y(D_BACK + 0.05), RT, 0.14, P_RAFTER, ('-x', '+x', '-y', '+y', '-z'))
    # low side wall of profile on the outer faces of the posts, with a wooden rail on top
    f0, f1 = sorted((sx * 2.06, sx * 2.11))
    box((f0, Y(D_FP + PD), 0), (f1, Y(D_BP - PD), FENCE_H), P_FENCE, ('-x', '+x', '-y', '+y'))
    r0, r1 = sorted((sx * 2.04, sx * 2.16))
    box((r0, Y(D_FP + PD) - 0.02, FENCE_H - 0.04), (r1, Y(D_BP - PD) + 0.02, FENCE_H + 0.08), P_RAIL, ('-x', '+x', '-y', '+y', '+z'))
for dc in (D_BP, D_FP):                                       # beams between the posts, right under the roof
    yc = Y(dc)
    box((-(XP - PW), yc - 0.08, ztop(yc) - RT - 0.17), (XP - PW, yc + 0.08, ztop(yc) - RT - 0.01), P_BEAM, ('-y', '+y', '-z'))
box((-(XP - PW), Y(0.0), 0), (XP - PW, Y(-WALL_T), WALL_H), P_WALL, ('-y', '+y', '+z'))
box((-(XP - PW), Y(BENCH_D), BENCH_Z0), (XP - PW, Y(0.0), BENCH_Z1), P_BENCH, ('-y', '+z'))
box((-0.05, Y(0.43), 0), (0.05, Y(0.33), BENCH_Z0), P_BENCHLEG, ('-x', '+x', '-y', '+y'))
# timetable plate on the front face of the right front post (source: left post), two notices on the back wall
x0, x1, z0, z1 = D_SCHED['rect']; yp = Y(D_FP + PD)
add_decal(D_SCHED, (-x0, yp - 0.016, z0), P_SCHED)
box((-x1, yp - 0.016, z0), (-x0, yp, z1), P_PLATEBACK, ('-x', '+x', '+y', '-z', '+z'))
for d in (D_AD1, D_AD2):
    x0, x1, z0, z1 = d['rect']
    add_decal(d, (-x0, Y(0.0) - 0.008, z0), P_AD)

# ================= SM_BusStopSign (origin = foot of the pole, the plate looks -Y) =================
OBJ = 1
ring = [(POLE_R * math.cos(2 * math.pi * (i + 0.5) / POLE_N), POLE_R * math.sin(2 * math.pi * (i + 0.5) / POLE_N)) for i in range(POLE_N)]
for i in range(POLE_N):
    (ax, ay), (bx, by) = ring[i], ring[(i + 1) % POLE_N]
    quad([(ax, ay, 0), (bx, by, 0), (bx, by, POLE_H), (ax, ay, POLE_H)], P_POLE, ((ax + bx) / 2, (ay + by) / 2, 0))
quad([(x, y, POLE_H) for x, y in ring], P_POLE, (0, 0, 1))
x0, x1, z0, z1 = D_SIGN['rect']; xc = (x0 + x1) / 2
yq = -POLE_R - 0.005
w, h = add_decal(D_SIGN, (w_ := (x1 - x0) / 2, yq - 0.02, z0), P_SIGNFACE)
box((-w / 2, yq - 0.02, z0), (w / 2, yq, z1), P_SIGNBACK, ('-x', '+x', '+y', '-z', '+z'))
for zc in (z0 + 0.16, z1 - 0.09):                             # two clamps that hold the plate on the pole (source: 1.73-1.81, 2.29-2.37)
    box((-0.24, yq, zc - 0.04), (0.24, POLE_R, zc + 0.04), P_BRACKET, ('-x', '+x', '+y', '-z', '+z'))

# ================= SM_BusStopUrn (origin = middle of the bottom) =================
OBJ = 2
def ringp(r, z):
    return [(r * math.cos(2 * math.pi * i / URN_N), r * math.sin(2 * math.pi * i / URN_N), z) for i in range(URN_N)]
o0, o1 = ringp(URN_R, 0), ringp(URN_R, URN_H)
i1, i0 = ringp(URN_R - URN_T, URN_H), ringp(URN_R - URN_T, URN_FLOOR)
for i in range(URN_N):
    j = (i + 1) % URN_N
    mid = Vector(((o0[i][0] + o0[j][0]) / 2, (o0[i][1] + o0[j][1]) / 2, 0))
    quad([o0[i], o0[j], o1[j], o1[i]], P_URNOUT, mid)
    quad([o1[i], o1[j], i1[j], i1[i]], P_URNRIM, (0, 0, 1))
    quad([i1[i], i1[j], i0[j], i0[i]], P_URNIN, -mid)
quad(i0, P_URNBOTTOM, (0, 0, 1))

OBJ = 0
bm.normal_update()
bmesh.ops.triangulate(bm, faces=bm.faces[:])
me = bpy.data.meshes.new('all')
bm.to_mesh(me); bm.free()
for p in me.polygons:
    p.use_smooth = False
ob = bpy.data.objects.new('all', me)
bpy.context.scene.collection.objects.link(ob)
def fattr(m, name, dt=np.int32):
    a = np.zeros(len(m.polygons), dt); m.attributes[name].data.foreach_get('value', a); return a
part = fattr(me, 'part')
assert part.min() > 0


def overlaps(meshes, layer, res=1024):
    inner = np.zeros((res, res), np.int16)
    for m in meshes:
        T_ = len(m.polygons)
        a = np.zeros(len(m.loops) * 2); m.uv_layers[layer].data.foreach_get('uv', a)
        uv = a.reshape(T_, 3, 2)
        for t in range(T_):
            p = uv[t] * res
            d = (p[1, 0] - p[0, 0]) * (p[2, 1] - p[0, 1]) - (p[1, 1] - p[0, 1]) * (p[2, 0] - p[0, 0])
            if abs(d) < 1e-9:
                continue
            x0 = max(int(math.floor(p[:, 0].min())), 0); x1 = min(int(math.ceil(p[:, 0].max())) + 1, res)
            y0 = max(int(math.floor(p[:, 1].min())), 0); y1 = min(int(math.ceil(p[:, 1].max())) + 1, res)
            X, Yg = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
            w1 = ((X - p[0, 0]) * (p[2, 1] - p[0, 1]) - (Yg - p[0, 1]) * (p[2, 0] - p[0, 0])) / d
            w2 = ((p[1, 0] - p[0, 0]) * (Yg - p[0, 1]) - (p[1, 1] - p[0, 1]) * (X - p[0, 0])) / d
            w0 = 1 - w1 - w2
            el = [np.linalg.norm(p[2] - p[1]), np.linalg.norm(p[0] - p[2]), np.linalg.norm(p[1] - p[0])]
            dist = np.minimum(np.minimum(w0 * abs(d) / el[0], w1 * abs(d) / el[1]), w2 * abs(d) / el[2])
            inner[y0:y1, x0:x1] += (dist > 0.6)
    return int((inner > 1).sum())


# texel density per part: what the camera above sees and the pictures get more, undersides and backs less
UVK = {P_ROOF: 1.25, P_ROOFUNDER: 0.4, P_ROOFEDGE: 1.0, P_WALL: 0.75, P_FENCE: 0.8, P_POST: 0.8, P_BEAM: 0.6, P_RAFTER: 0.7, P_RAIL: 0.9, P_BENCH: 0.8, P_BENCHLEG: 0.6,
       P_SCHED: 2.2, P_PLATEBACK: 0.7, P_AD: 2.2, P_POLE: 1.0, P_SIGNFACE: 2.0, P_SIGNBACK: 0.8, P_BRACKET: 0.8, P_URNOUT: 1.2, P_URNIN: 0.9, P_URNRIM: 1.2, P_URNBOTTOM: 0.9}
bpy.context.scene.tool_settings.use_uv_select_sync = True
def unwrap(o, layer, margin, weighted):
    m = o.data; prt = fattr(m, 'part')
    m.uv_layers.active = m.uv_layers[layer]
    for ang in (66, 50, 35):
        bpy.ops.object.select_all(action='DESELECT')
        o.select_set(True); bpy.context.view_layer.objects.active = o
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=math.radians(ang), island_margin=0.0, correct_aspect=True, scale_to_bounds=False)
        bpy.ops.object.mode_set(mode='OBJECT')
        if weighted:
            d = m.uv_layers[layer].data
            for p in m.polygons:
                k = UVK.get(int(prt[p.index]), 1.0)
                for li in p.loop_indices:
                    d[li].uv = d[li].uv * k
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.pack_islands(rotate=True, margin_method='FRACTION', margin=margin, shape_method='AABB')     # the default shape method can hang forever
        bpy.ops.object.mode_set(mode='OBJECT')
        n = overlaps([m], layer)
        print('UNWRAP %s %s angle %d: overlapping texels %d' % (o.name, layer, ang, n), flush=True)
        if n == 0:
            break
me.uv_layers.new(name='UVMap'); me.uv_layers.new(name='LightmapUV')
unwrap(ob, 'UVMap', 0.004, True)                              # one shared texture: the three objects are unwrapped together

# ---- split into the three objects; each keeps its place by the shelter as the object location ----
mat = bpy.data.materials.new('M_BusStop'); mat.use_nodes = True
objs = []
for k, name in enumerate(NAMES):
    b2 = bmesh.new(); b2.from_mesh(me)
    lo = b2.faces.layers.int['obj']
    bmesh.ops.delete(b2, geom=[f for f in b2.faces if f[lo] != k], context='FACES')
    bmesh.ops.delete(b2, geom=[v for v in b2.verts if not v.link_faces], context='VERTS')
    bmesh.ops.translate(b2, verts=b2.verts[:], vec=-PLACE[k])
    m = bpy.data.meshes.new(name); b2.to_mesh(m); b2.free()
    for p in m.polygons:
        p.use_smooth = False
    m.materials.append(mat)
    o = bpy.data.objects.new(name, m); o.location = PLACE[k]
    bpy.context.scene.collection.objects.link(o); objs.append(o)
bpy.data.objects.remove(ob)
for o in objs:
    unwrap(o, 'LightmapUV', 0.02, False)                      # the light map is per object
    o.data.uv_layers.active = o.data.uv_layers['UVMap']; o.data.uv_layers['UVMap'].active_render = True
print('UNWRAP shared UVMap of the three objects together: overlapping texels %d' % overlaps([o.data for o in objs], 'UVMap'))


# ---- collision: simple convex blocks.  A hero capsule of radius 0.40 stops with its centre at the roof edge ----
def ucx(name, lo, hi, parent, ngon=0):
    b = bmesh.new()
    if ngon:
        r, h = hi
        bmesh.ops.create_cone(b, cap_ends=True, segments=ngon, radius1=r / math.cos(math.pi / ngon), radius2=r / math.cos(math.pi / ngon), depth=h)
        bmesh.ops.translate(b, verts=b.verts[:], vec=(0, 0, h / 2))
    else:
        bmesh.ops.create_cube(b, size=1.0)
        for v in b.verts:
            v.co = Vector(((lo[i] + hi[i]) / 2 + v.co[i] * (hi[i] - lo[i]) for i in range(3)))
    bmesh.ops.recalc_face_normals(b, faces=b.faces[:])
    vol = b.calc_volume(signed=True)
    m = bpy.data.meshes.new(name); b.to_mesh(m); b.free()
    o = bpy.data.objects.new(name, m); o.location = parent.location
    bpy.context.scene.collection.objects.link(o); o.hide_render = True
    c = np.array([v.co[:] for v in m.vertices])
    print('COLLISION %s min %s max %s volume %+.3f' % (name, c.min(0).round(3), c.max(0).round(3), vol))
# 01: back wall + bench up to the front of the bench, full height: nobody walks or jumps onto the bench
ucx('UCX_SM_BusStop_01', (-2.16, Y(BENCH_D), 0), (2.16, Y(D_BP - PD), WALL_H + 0.2), objs[0])
# 02, 03: front post with the rest of the side wall
ucx('UCX_SM_BusStop_02', (-2.16, Y(D_FP + PD), 0), (-(XP - PW), Y(BENCH_D), 2.55), objs[0])
ucx('UCX_SM_BusStop_03', (XP - PW, Y(D_FP + PD), 0), (2.16, Y(BENCH_D), 2.55), objs[0])
ucx('UCX_SM_BusStopUrn_01', None, (URN_R, URN_H), objs[2], ngon=8)

np.savez(OUT + '_grp.npz', M=np.array([[list(r) for r in m] for m in GM], np.float64), I=np.array(GI, np.float64), DEC=np.array(DEC, np.float64),
         PLACE=np.array([list(p) for p in PLACE]), consts=np.array([RX, Y0, D_BACK, D_FRONT, D_BP, D_FP, WALL_H, FENCE_H, BENCH_D, URN_R, URN_H, URN_T, URN_FLOOR, POLE_R, POLE_H, XP]))
tot = 0
for o in objs:
    m = o.data; co = np.array([v.co[:] for v in m.vertices]); prt = fattr(m, 'part'); cnt = {}
    for p in prt:
        cnt[int(p)] = cnt.get(int(p), 0) + 1
    tot += len(m.polygons)
    print('BUILD %-15s tris %3d verts %3d place %s min %s max %s size %s parts %s' % (o.name, len(m.polygons), len(m.vertices), tuple(round(a, 3) for a in o.location),
          co.min(0).round(3), co.max(0).round(3), (co.max(0) - co.min(0)).round(3), sorted(cnt.items())))
print('BUILD total triangles of the three objects %d (limit 800); free depth under the roof in front of the bench %.2f m' % (tot, D_FRONT - BENCH_D))
bpy.ops.wm.save_as_mainfile(filepath=OUT + 'busstop_work.blend')
