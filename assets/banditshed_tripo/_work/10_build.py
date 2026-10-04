"""SM_BanditShed (bandit shed after ref.png) on the footprint of the old shed, <= 352 tris (the old shed).
Both Tripo meshes have torn walls (halves of the gable / back walls are missing) and a crumpled roof, so the
geometry is built clean here after the reference layout: plank box with gables, door recess with a half-open
door and a plank step, a red rag over the door, boards over the window, two rusty tin patches, and a gable roof
of separate flat slate sheets (some shifted, one cracked in two, one replaced by rusty tin; the waves are painted)
over dark sheathing, and a red rag thrown over the ridge (the game camera looks from above).  Everything else (planks, gaps, patches, the red paint mark) is painted by 11_paint.py.
Face int layers 'part' / 'grp' drive the painter; grp matrices -> _grp.npz.
Run: blender.exe -b --factory-startup --python 10_build.py
"""
import bpy, bmesh, math, random
import numpy as np
from mathutils import Vector, Matrix

OUT = 'E:/game-dev-team/assets/banditshed_tripo/_work/'
NAME = 'SM_BanditShed'
HX, HY = 2.55, 1.983             # old footprint: x +-2.55 (gable overhang), y +-1.983 (eaves); door on -Y, ridge along X
WX, WY = 2.42, 1.50              # walls; the front wall stands back so that the open door and the step stay inside the footprint
ZE, ZR = 2.25, 3.15              # eave / ridge height of the roof deck
TN = (ZR - ZE) / HY; PITCH = math.atan(TN); CS, SN = math.cos(PITCH), math.sin(PITCH)
WH = ZR - WY * TN + 0.03         # walls end inside the roof deck
DX, DH = 0.5, 2.0                # door opening half-width and height
(P_WALL, P_GABLE, P_RECESS, P_DOOR, P_STEP, P_RAG, P_BOARD, P_TINPATCH, P_SHEATH, P_SOFFIT,
 P_SLATE, P_TINROOF, P_RIDGE, P_BOTTOM, P_ROOFRAG) = range(1, 16)
random.seed(11)

bpy.ops.wm.read_factory_settings(use_empty=True)
bm = bmesh.new()
LP = bm.faces.layers.int.new('part'); LG = bm.faces.layers.int.new('grp')
GM = [Matrix.Identity(4)]; GI = [[0.0] * 6]
def new_grp(M, info):
    GM.append(M.copy()); GI.append((list(info) + [0.0] * 6)[:6]); return len(GM) - 1
def quad(pts, part, g=0):
    f = bm.faces.new([bm.verts.new(p) for p in pts]); f[LP] = part; f[LG] = g; return f
def box(M, mn, mx, part, g=0, skip=()):
    """Box in the frame M; skip: names of faces to leave out ('-y' = the face looking -Y of the frame ...)."""
    x0, y0, z0 = mn; x1, y1, z1 = mx
    F = {'-z': [(x0, y0, z0), (x0, y1, z0), (x1, y1, z0), (x1, y0, z0)], '+z': [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)],
         '-y': [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], '+y': [(x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x1, y1, z1)],
         '-x': [(x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1)], '+x': [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)]}
    return [quad([M @ Vector(p) for p in pts], part, g) for k, pts in F.items() if k not in skip]
I4 = Matrix.Identity(4)

# ---- walls (outward normals), closed bottom, no top (it is inside the roof deck) ----
quad([(-WX, -WY, 0), (-DX, -WY, 0), (-DX, -WY, WH), (-WX, -WY, WH)], P_WALL)            # front, left of the door
quad([(DX, -WY, 0), (WX, -WY, 0), (WX, -WY, WH), (DX, -WY, WH)], P_WALL)                # front, right of the door
quad([(-DX, -WY, DH), (DX, -WY, DH), (DX, -WY, WH), (-DX, -WY, WH)], P_WALL)            # front, above the door
quad([(WX, WY, 0), (-WX, WY, 0), (-WX, WY, WH), (WX, WY, WH)], P_WALL)                  # back
quad([(-WX, WY, 0), (-WX, -WY, 0), (-WX, -WY, WH), (-WX, WY, WH)], P_WALL)              # left side
quad([(WX, -WY, 0), (WX, WY, 0), (WX, WY, WH), (WX, -WY, WH)], P_WALL)                  # right side
quad([(-WX, WY, 0), (WX, WY, 0), (WX, -WY, 0), (-WX, -WY, 0)], P_BOTTOM)
# door recess (dark inside), its floor is level with the step
RD, FZ = 0.75, 0.12
quad([(DX, -WY + RD, FZ), (-DX, -WY + RD, FZ), (-DX, -WY + RD, DH), (DX, -WY + RD, DH)], P_RECESS)       # back
quad([(-DX, -WY, FZ), (-DX, -WY + RD, FZ), (-DX, -WY + RD, DH), (-DX, -WY, DH)], P_RECESS)             # left cheek (looks +X)
quad([(DX, -WY + RD, FZ), (DX, -WY, FZ), (DX, -WY, DH), (DX, -WY + RD, DH)], P_RECESS)                 # right cheek
quad([(-DX, -WY, DH), (-DX, -WY + RD, DH), (DX, -WY + RD, DH), (DX, -WY, DH)], P_RECESS)               # ceiling (looks down)
quad([(-DX, -WY + RD, FZ), (-DX, -WY, FZ), (DX, -WY, FZ), (DX, -WY + RD, FZ)], P_RECESS)               # floor
# plank step and the half-open door (hinged on the left jamb, swung outwards)
box(I4, (-0.78, -HY + 0.05, 0.0), (0.78, -WY + 0.01, FZ), P_STEP, 0, skip=('-z',))
ANG = math.radians(-27)
Md = Matrix.Translation((-DX, -WY - 0.005, 0)) @ Matrix.Rotation(ANG, 4, 'Z')
box(Md, (0.0, -0.05, FZ + 0.04), (0.95, 0.0, DH - 0.02), P_DOOR, new_grp(Md, [1, 0.95]))
# red rag draped over the door: a sagging band and two hanging ends (seen from the front)
ry = -WY - 0.045
top = [(-0.58, 2.20), (-0.2, 2.10), (0.2, 2.10), (0.58, 2.20)]; bot = [(-0.58, 2.05), (-0.2, 1.90), (0.2, 1.90), (0.58, 2.05)]
for i in range(3):
    yy = (ry, ry - 0.03, ry - 0.03, ry)
    quad([(bot[i][0], yy[i], bot[i][1]), (bot[i + 1][0], yy[i + 1], bot[i + 1][1]), (top[i + 1][0], yy[i + 1], top[i + 1][1]), (top[i][0], yy[i], top[i][1])], P_RAG)
quad([(-0.70, ry, 1.58), (-0.56, ry, 1.68), (-0.56, ry, 2.22), (-0.70, ry, 2.22)], P_RAG)
quad([(0.56, ry, 1.74), (0.70, ry, 1.52), (0.70, ry, 2.22), (0.56, ry, 2.22)], P_RAG)
# boards nailed over the window (front wall, right of the door) - front faces only, the camera never sees their edges
WINDOW = (1.28, 2.06, 0.98, 1.76)                 # x0 x1 z0 z1, painted dark on the wall
wcx, wcz = (WINDOW[0] + WINDOW[1]) / 2, (WINDOW[2] + WINDOW[3]) / 2
for dz, ang, ln, lay in ((0.24, 4.0, 1.02, 0), (-0.22, -5.0, 0.98, 0), (0.0, 30.0, 1.05, 1)):
    Mb = Matrix.Translation((wcx, -WY - 0.035 * lay, wcz + dz)) @ Matrix.Rotation(math.radians(ang), 4, 'Y')
    box(Mb, (-ln / 2, -0.035, -0.07), (ln / 2, 0.0, 0.07), P_BOARD, new_grp(Mb, [2, ln / 2, 0.07]), skip=('+y', '-z', '+z', '-x', '+x'))
# rusty tin patches: on the left gable wall and low on the front wall (front faces only)
Mt1 = Matrix.Translation((-WX, -0.5, 0.95)) @ Matrix.Rotation(math.radians(90), 4, 'Z') @ Matrix.Rotation(math.radians(3), 4, 'Y')
box(Mt1, (-0.45, 0.0, -0.65), (0.45, 0.025, 0.65), P_TINPATCH, new_grp(Mt1, [3, 0.45, 0.65]), skip=('-y', '-z', '+z', '-x', '+x'))
Mt2 = Matrix.Translation((2.08, -WY, 0.42)) @ Matrix.Rotation(math.radians(180), 4, 'Z') @ Matrix.Rotation(math.radians(-4), 4, 'Y')
box(Mt2, (-0.22, 0.0, -0.32), (0.22, 0.025, 0.32), P_TINPATCH, new_grp(Mt2, [3, 0.22, 0.32]), skip=('-y', '-z', '+z', '-x', '+x'))

# ---- roof deck: a solid wedge from eave to eave (dark sheathing, plank gables, dark soffit) ----
quad([(-HX, -HY, ZE), (HX, -HY, ZE), (HX, 0, ZR), (-HX, 0, ZR)], P_SHEATH)
quad([(HX, HY, ZE), (-HX, HY, ZE), (-HX, 0, ZR), (HX, 0, ZR)], P_SHEATH)
quad([(-HX, HY, ZE), (HX, HY, ZE), (HX, -HY, ZE), (-HX, -HY, ZE)], P_SOFFIT)
f = bm.faces.new([bm.verts.new(p) for p in ((-HX, HY, ZE), (-HX, -HY, ZE), (-HX, 0, ZR))]); f[LP] = P_GABLE
f = bm.faces.new([bm.verts.new(p) for p in ((HX, -HY, ZE), (HX, HY, ZE), (HX, 0, ZR))]); f[LP] = P_GABLE

# ---- slate: 4 columns x 2 rows per slope, one flat quad per sheet (waves are painted), the deck shows in the gaps ----
NCOL, SA = 4, 0.04
PX = 2 * HX / NCOL
LB = (HY - (0.07 + SA) * SN) / CS - 0.002
ROWS = [(0.05, 1.18, 0.06), (1.02, LB, 0.015)]
def sheet(F, ac, b0, b1, h0, w, phi, part, kind, s, r, c):
    ln = b1 - b0
    M = (F @ Matrix.Translation((ac, b0, h0 + SA / 2)) @ Matrix.Translation((0, ln / 2, 0)) @ Matrix.Rotation(phi, 4, 'Z') @ Matrix.Translation((0, -ln / 2, 0)))
    g = new_grp(M, [kind, s, r, c, w, ln])
    f = quad([M @ Vector(p) for p in ((-w / 2, 0, 0), (w / 2, 0, 0), (w / 2, ln, 0), (-w / 2, ln, 0))], part, g)
    if f.normal.dot(F.col[2].to_3d()) < 0:
        f.normal_flip()
for s in (-1, 1):
    F = Matrix(((1, 0, 0, 0), (0, s * CS, s * SN, 0), (0, -SN, CS, ZR), (0, 0, 0, 1)))
    for r, (b0, b1, h0) in enumerate(ROWS):
        for c in range(NCOL):
            w = PX - 0.018
            ac = -HX + PX * (c + 0.5)
            phi = math.radians(random.uniform(-0.5, 0.5)); db = 0.0
            if (s, r, c) == (-1, 1, 1):                      # slipped: turned and pushed up under the upper row
                phi, db = math.radians(5.0), -0.14
            if (s, r, c) == (1, 1, 2):
                phi, db = math.radians(-4.0), -0.10
            if (s, r, c) == (-1, 0, 1):                      # cracked in two: halves pulled apart, one turned
                sheet(F, ac - w / 4 - 0.03, b0, b1, h0, w / 2 - 0.02, math.radians(2.5), P_SLATE, 4, s, r, c)
                sheet(F, ac + w / 4 + 0.03, b0 + 0.05, b1, h0 + 0.01, w / 2 - 0.02, math.radians(-3.0), P_SLATE, 4, s, r, c)
                continue
            tin = (s, r, c) == (-1, 0, 3)                    # one sheet replaced by rusty tin (front slope, upper right, as on the reference)
            sheet(F, ac, b0 + db, b1 + db, h0 + random.uniform(0, 0.006), w, phi, P_TINROOF if tin else P_SLATE, 5 if tin else 4, s, r, c)
# ridge: two boards as a shallow cap over the top edges of the sheets
for s in (-1, 1):
    h = 0.06 + SA + 0.012
    def sl(b):
        return (s * (b * CS + h * SN), ZR - b * SN + h * CS)
    y1, z1 = sl(0.20); z0 = ZR + h / CS
    f = quad([(-HX, 0, z0), (HX, 0, z0), (HX, y1, z1), (-HX, y1, z1)], P_RIDGE)
    if f.normal.z < 0:
        f.normal_flip()
# red rag thrown over the ridge: a short end on the back slope, a long one with a torn lower edge on the front slope
def on_slope(s, a, b, h):
    return (a, s * (b * CS + h * SN), ZR - b * SN + h * CS)
RA = (0.14, 0.50, 0.84, 1.18)                                # along the ridge (third column of sheets, clear of the cracked and the tin ones)
rows = [[on_slope(1, a + 0.05, b, 0.125) for a, b in zip(RA, (0.44, 0.52, 0.38, 0.47))],
        [(a + 0.02, 0.0, ZR + (0.06 + SA + 0.012) / CS + 0.03 + dz) for a, dz in zip(RA, (0, 0.012, 0, 0.008))],
        [on_slope(-1, a - 0.03, 0.58, h) for a, h in zip(RA, (0.125, 0.15, 0.125, 0.145))],
        [on_slope(-1, a - 0.09 + da, b, 0.09) for a, b, da in zip(RA, (1.30, 1.08, 1.38, 1.17), (0.03, 0.0, -0.02, 0.04))]]
for j in range(3):
    for i in range(3):
        f = quad([rows[j][i], rows[j][i + 1], rows[j + 1][i + 1], rows[j + 1][i]], P_ROOFRAG)
        if f.normal.z < 0:
            f.normal_flip()

for v in bm.verts:                                           # everything stays inside the old footprint
    v.co.x = max(-HX, min(HX, v.co.x)); v.co.y = max(-HY, min(HY, v.co.y))
bm.normal_update()
bmesh.ops.triangulate(bm, faces=bm.faces[:])
me = bpy.data.meshes.new(NAME)
bm.to_mesh(me); bm.free()
for p in me.polygons:
    p.use_smooth = False
print('STEP mesh', len(me.polygons), flush=True)
ob = bpy.data.objects.new(NAME, me)
bpy.context.scene.collection.objects.link(ob)
part = np.zeros(len(me.polygons), np.int32); me.attributes['part'].data.foreach_get('value', part)
assert part.min() > 0


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


UVK = {P_SHEATH: 0.3, P_SOFFIT: 0.3, P_BOTTOM: 0.12, P_SLATE: 1.25, P_TINROOF: 1.25, P_ROOFRAG: 1.25}     # texel density per part (the roof is what the camera sees)
bpy.context.scene.tool_settings.use_uv_select_sync = True
def unwrap(layer, margin, weighted):
    print('STEP unwrap', layer, flush=True)
    me.uv_layers.active = me.uv_layers[layer]
    for ang in (66, 50, 35):
        bpy.ops.object.select_all(action='DESELECT')
        ob.select_set(True); bpy.context.view_layer.objects.active = ob
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=math.radians(ang), island_margin=0.0, correct_aspect=True, scale_to_bounds=False)
        print('STEP projected', ang, flush=True)
        bpy.ops.object.mode_set(mode='OBJECT')
        if weighted:
            d = me.uv_layers[layer].data
            for p in me.polygons:
                k = UVK.get(int(part[p.index]), 1.0)
                if k != 1.0:
                    for li in p.loop_indices:
                        d[li].uv = d[li].uv * k
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        import os
        V = os.environ.get('PACKV', 'e')      # 'a' (concave shapes + exact margin) never returns on this mesh; boxes pack fine
        if V == 'a':
            bpy.ops.uv.pack_islands(rotate=True, margin_method='FRACTION', margin=margin)
        elif V == 'b':
            bpy.ops.uv.pack_islands(rotate=False, margin_method='FRACTION', margin=margin)
        elif V == 'c':
            bpy.ops.uv.pack_islands(rotate=True, margin_method='SCALED', margin=margin * 4)
        elif V == 'd':
            bpy.ops.uv.pack_islands(rotate=True, margin_method='ADD', margin=margin)
        elif V == 'e':
            bpy.ops.uv.pack_islands(rotate=True, margin_method='FRACTION', margin=margin, shape_method='AABB')
        bpy.ops.object.mode_set(mode='OBJECT')
        print('STEP packed', flush=True)
        n = overlaps(layer)
        print('UNWRAP %s angle %d: overlapping texels %d' % (layer, ang, n))
        if n == 0:
            break
me.uv_layers.new(name='UVMap'); me.uv_layers.new(name='LightmapUV')
unwrap('UVMap', 0.004, True)
unwrap('LightmapUV', 0.01, False)
me.uv_layers.active = me.uv_layers['UVMap']; me.uv_layers['UVMap'].active_render = True
mat = bpy.data.materials.new('M_BanditShedTripo'); mat.use_nodes = True
me.materials.append(mat)
np.savez(OUT + '_grp.npz', M=np.array([[list(r) for r in m] for m in GM], np.float64), I=np.array(GI, np.float64),
         consts=np.array([WX, WY, WH, ZE, ZR, TN, HX, HY, DX, DH] + list(WINDOW)))
co = np.array([v.co[:] for v in me.vertices])
cnt = {}
for p in part:
    cnt[int(p)] = cnt.get(int(p), 0) + 1
print('BUILD tris %d verts %d min %s max %s size %s parts %s' % (len(me.polygons), len(me.vertices), co.min(0).round(3), co.max(0).round(3), (co.max(0) - co.min(0)).round(3), sorted(cnt.items())))
bpy.ops.wm.save_as_mainfile(filepath=OUT + 'banditshed_work.blend')
