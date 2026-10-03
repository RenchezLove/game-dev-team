"""Build SM_IzbaSlate from TapGrade's Izba.fbx (CC-BY): source walls / casings / door / porch /
log ends are kept (rotated so the door faces -Y and scaled onto the SM_VillageHouse footprint),
the plank roof is replaced by corrugated slate sheets + ridge cap + gables + barge boards,
plus a leaning brick chimney, boards over one window and a tin patch.
Face int layers 'part' / 'grp' drive the painter (11_paint.py); grp matrices -> _grp.npz.
Run: blender.exe -b --factory-startup --python 10_build.py
"""
import bpy, bmesh, math, random, sys
import numpy as np
import addon_utils
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

SRC = 'C:/Users/pgr40/Desktop/GamdevAITeam/Izba/source/Izba.fbx'
OUT = 'E:/game-dev-team/assets/izba_slate/_work/'
NAME = 'SM_IzbaSlate'

# footprint of the old SM_VillageHouse (measured from its FBX): walls x +-2.62, y -2.12..2.10,
# roof x +-2.781, step to y -2.5, back eave y 2.22
LOG_HX, LOG_HY = 2.62, 2.11
ROOF_HX, EAVE_Y, PORCH_Y = 2.781, 2.22, -2.5
SZ = 1.6                      # door 1.21 -> 1.94 m
PITCH = math.radians(34.0)
CS, SN, TN = math.cos(PITCH), math.sin(PITCH), math.tan(PITCH)
ST, SA = 0.012, 0.045         # slate thickness / wave amplitude
(P_WALL, P_FOUND, P_GLASS, P_DOORLEAF, P_REVEAL, P_SILL, P_CASING, P_DOORFRAME, P_PORCH, P_LOGSIDE, P_LOGCAP,
 P_HIDDEN, P_SHEATH, P_GABLE, P_SLATE, P_SLATE_EDGE, P_RIDGE, P_BARGE, P_CHIM, P_PATCH, P_BOARD, P_SOFFIT) = range(1, 23)
random.seed(7)

bpy.ops.wm.read_factory_settings(use_empty=True)
addon_utils.enable('io_scene_fbx')
bpy.ops.import_scene.fbx(filepath=SRC)
src = [o for o in bpy.data.objects if o.type == 'MESH'][0]
bpy.context.view_layer.update()
bm = bmesh.new()
bm.from_mesh(src.data)
bm.transform(src.matrix_world)
while len(bm.loops.layers.uv):                # drop both source UV sets (removing in a for-loop left one behind)
    bm.loops.layers.uv.remove(bm.loops.layers.uv[0])
LP = bm.faces.layers.int.new('part')
LG = bm.faces.layers.int.new('grp')
GM = [Matrix.Identity(4)]          # grp -> local-to-world matrix
GI = [[0.0] * 6]                   # grp -> info (kind, p1..p5)


def new_grp(M, info):
    GM.append(M.copy())
    GI.append((list(info) + [0.0] * 6)[:6])
    return len(GM) - 1


# ---------- source islands ----------
bm.verts.ensure_lookup_table()
seen = set()
isl = []
for v in bm.verts:
    if v.index in seen:
        continue
    st = [v]; seen.add(v.index); vs = []
    while st:
        a = st.pop(); vs.append(a)
        for e in a.link_edges:
            b = e.other_vert(a)
            if b.index not in seen:
                seen.add(b.index); st.append(b)
    fs = set()
    for a in vs:
        fs.update(a.link_faces)
    isl.append((vs, list(fs), sum(len(f.verts) - 2 for f in fs)))
kind = {268: 'casing', 244: 'body', 234: 'roof', 96: 'doorframe', 44: 'porch', 20: 'logend'}
groups = {}
for vs, fs, t in isl:
    groups.setdefault(kind[t], []).append((vs, fs))
print('SRC islands', {k: len(v) for k, v in groups.items()})
assert len(groups['logend']) == 40 and len(groups['casing']) == 4

lv = [v.co for vs, fs in groups['logend'] for v in vs]
x0, x1 = min(c.x for c in lv), max(c.x for c in lv)
y0, y1 = min(c.y for c in lv), max(c.y for c in lv)
cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
SX, SY = LOG_HX / ((x1 - x0) / 2), LOG_HY / ((y1 - y0) / 2)
z0 = min(v.co.z for v in groups['body'][0][0])
print('SCALE sx %.4f sy %.4f sz %.4f centre (%.4f, %.4f) z0 %.4f' % (SX, SY, SZ, cx, cy, z0))

bmesh.ops.delete(bm, geom=groups['roof'][0][0], context='VERTS')
for v in bm.verts:                      # rotate 180 deg about Z (door +Y -> -Y) and scale
    c = v.co
    v.co = Vector((-(c.x - cx) * SX, -(c.y - cy) * SY, (c.z - z0) * SZ))
# porch: squeeze its depth so the footprint ends at PORCH_Y, sit it on the ground
pv = groups['porch'][0][0]
pin = max(v.co.y for v in pv); pout = min(v.co.y for v in pv)
for v in pv:
    v.co.y = pin + (v.co.y - pin) * (PORCH_Y - pin) / (pout - pin)
    if v.co.z < 0.03:
        v.co.z = 0.0
bm.normal_update()

body_v, body_f = groups['body'][0]
hi = [v.co for v in body_v if v.co.z > 1.0]
XN, XP = min(c.x for c in hi), max(c.x for c in hi)       # the four wall planes
YN, YP = min(c.y for c in hi), max(c.y for c in hi)
WTOP = max(v.co.z for v in body_v)
LOGTOP = max(v.co.z for vs, fs in groups['logend'] for v in vs)
print('BODY walls x %.3f..%.3f y %.3f..%.3f top %.3f logtop %.3f' % (XN, XP, YN, YP, WTOP, LOGTOP))

nglass = 0
for f in body_f:
    n = f.normal; c = f.calc_center_median()
    if n.z < -0.9 and c.z < 0.05 or n.z > 0.9 and c.z > WTOP - 0.05:
        f[LP] = P_HIDDEN
    elif c.z < 0.3 and abs(n.z) > 0.3:
        f[LP] = P_FOUND
    elif abs(n.z) > 0.9:
        f[LP] = P_SILL
    elif ((n.x > 0.9 and c.x > XP - 0.04) or (n.x < -0.9 and c.x < XN + 0.04)
          or (n.y > 0.9 and c.y > YP - 0.04) or (n.y < -0.9 and c.y < YN + 0.04)):
        f[LP] = P_WALL
    else:
        back = (abs(n.x) > 0.9 and abs(c.x) > 2.15 and n.x * c.x > 0) or (abs(n.y) > 0.9 and abs(c.x) < 2.15 and n.y * c.y > 0)
        if back:                                   # recess back face: glass / frame bar or the door leaf
            u = Vector((0, 0, 1)).cross(n).normalized()
            us = [(v.co - c).dot(u) for v in f.verts]; zs = [v.co.z - c.z for v in f.verts]
            M = Matrix.Translation(c) @ Matrix((u, n, Vector((0, 0, 1)))).transposed().to_4x4()
            door = n.y < -0.9 and c.x > 0.6
            f[LP] = P_DOORLEAF if door else P_GLASS
            f[LG] = new_grp(M, [6 if door else 5, max(us), max(zs), nglass])
            nglass += 0 if door else 1
            if door:
                print('RECESS door centre (%.2f %.2f %.2f) half (%.2f, %.2f)' % (c.x, c.y, c.z, max(us), max(zs)))
        else:
            f[LP] = P_REVEAL
for vs, fs in groups['casing']:
    for f in fs:
        f[LP] = P_CASING
for f in groups['doorframe'][0][1]:
    f[LP] = P_DOORFRAME
for f in groups['porch'][0][1]:
    f[LP] = P_PORCH
for vs, fs in groups['logend']:
    c = sum((v.co for v in vs), Vector()) / len(vs)
    g = None
    for f in fs:
        n = f.normal
        if abs(n.x) > 0.9 or abs(n.y) > 0.9:
            if g is None:
                g = new_grp(Matrix.Translation(c), [4, 0 if abs(n.x) > 0.9 else 1])
            f[LP] = P_LOGCAP; f[LG] = g
        else:
            f[LP] = P_LOGSIDE

# ---------- new geometry ----------
def add_poly(pts, part, g=0):
    f = bm.faces.new([bm.verts.new(p) for p in pts])
    f[LP] = part; f[LG] = g
    return f


def add_hull(M, ring_a, ring_b, part, g=0, part_caps=None):
    """Closed prism between two equal rings of local points (may be concave)."""
    va = [bm.verts.new(M @ Vector(p)) for p in ring_a]
    vb = [bm.verts.new(M @ Vector(p)) for p in ring_b]
    n = len(va); out = []
    for i in range(n):
        f = bm.faces.new((va[i], va[(i + 1) % n], vb[(i + 1) % n], vb[i])); out.append(f)
    out.append(bm.faces.new(va[::-1])); out.append(bm.faces.new(vb))
    for i, f in enumerate(out):
        f[LP] = part_caps if (part_caps and i >= n) else part
        f[LG] = g
    return out


def add_box(M, mn, mx, part, g=0):
    a = [(mn[0], mn[1], mn[2]), (mx[0], mn[1], mn[2]), (mx[0], mx[1], mn[2]), (mn[0], mx[1], mn[2])]
    b = [(p[0], p[1], mx[2]) for p in a]
    return add_hull(M, a, b, part, g)


I4 = Matrix.Identity(4)
ZR = LOGTOP + 0.02 + LOG_HY * TN               # sheathing plane clears the top log ends; height at the ridge
def zs(y):
    return ZR - abs(y) * TN
print('ROOF ridge sheathing z %.3f, eave z %.3f' % (ZR, zs(EAVE_Y)))

# sheathing prism; its end triangles are the plank gables
E = EAVE_Y - 0.03
tri = [(-E, zs(E)), (0.0, ZR), (E, zs(E))]
fs = add_hull(I4, [(XN - 0.03, y, z) for y, z in tri], [(XP + 0.03, y, z) for y, z in tri], P_SHEATH)
fs[2][LP] = P_SOFFIT                            # ring edge (E)->(-E) = bottom
fs[3][LP] = P_GABLE; fs[4][LP] = P_GABLE

# slate sheets
slate_v = []
NCOL, SLATE_HX = 5, 2.762
PITCH_X = 2 * SLATE_HX / NCOL
BMAX = (EAVE_Y - (ST + SA + 0.01) * SN) / CS
ROWS = [(0.06, 1.47, 0.066), (1.27, BMAX, 0.004)]       # (b0, b1, lift): upper row laps the lower one
sheet_info = []
for s in (-1, 1):
    F = Matrix(((1, 0, 0, 0), (0, s * CS, s * SN, 0), (0, -SN, CS, ZR), (0, 0, 0, 1)))   # cols: ex, d, n, ridge
    for r, (b0, b1, h0) in enumerate(ROWS):
        ln = b1 - b0
        for c in range(NCOL):
            w = PITCH_X - 0.014
            ac = -SLATE_HX + PITCH_X * (c + 0.5)
            phi = math.radians(random.uniform(-0.9, 0.9)); db = random.uniform(-0.012, 0.012) if r == 1 else 0.0
            dh = random.uniform(0, 0.006)
            if s == -1 and r == 1 and c == 1:                 # the slipped sheet
                phi, db, dh = math.radians(4.5), 0.24, 0.012
            M = (F @ Matrix.Translation((ac, b0 + db, h0 + dh)) @ Matrix.Translation((0, ln / 2, 0))
                 @ Matrix.Rotation(phi, 4, 'Z') @ Matrix.Translation((0, -ln / 2, 0)))
            g = new_grp(M, [1, s, r, c, w, ln])
            prof = [(-w / 2 + i * w / 8, ST + (SA if i % 2 == 0 else 0.0)) for i in range(9)]
            ra = [(a, 0.0, h) for a, h in prof] + [(w / 2, 0.0, 0.0), (-w / 2, 0.0, 0.0)]
            rb = [(a, ln, h) for a, h in prof] + [(w / 2, ln, 0.0), (-w / 2, ln, 0.0)]
            fs = add_hull(M, ra, rb, P_SLATE_EDGE, g)
            for f in fs[:8]:
                f[LP] = P_SLATE
            for f in fs:
                slate_v.extend(f.verts)
            sheet_info.append((s, r, c, g))
slate_v = list(set(slate_v))
fy = EAVE_Y / max(v.co.y for v in slate_v)        # back eave exactly on the old footprint
SYM = Matrix.Diagonal((1, fy, 1, 1))
for v in slate_v:
    v.co.y *= fy
for i in range(1, len(GM)):
    if GI[i][0] == 1:
        GM[i] = SYM @ GM[i]
print('SLATE fit y factor %.4f front min y %.3f' % (fy, min(v.co.y for v in slate_v)))

# tin patch on the front slope, upper row
Ff = Matrix(((1, 0, 0, 0), (0, -CS, -SN, 0), (0, -SN, CS, ZR), (0, 0, 0, 1)))
Mp = Ff @ Matrix.Translation((1.75, 0.80, 0.066 + ST + SA + 0.008)) @ Matrix.Rotation(math.radians(8), 4, 'Z')
add_box(Mp, (-0.30, -0.36, 0.0), (0.30, 0.36, 0.012), P_PATCH, new_grp(Mp, [7, 0.30, 0.36]))

# ridge cap: tin chevron, a touch crooked
HC = 0.066 + 0.006 + ST + SA + 0.006
def sl(s, b, h):
    return (s * (b * CS + h * SN), ZR - b * SN + h * CS)
chev = [sl(-1, 0.30, HC + 0.028), (0.0, ZR + (HC + 0.028) / CS), sl(1, 0.30, HC + 0.028),
        sl(1, 0.30, HC), (0.0, ZR + HC / CS), sl(-1, 0.30, HC)]
add_hull(I4, [(-ROOF_HX, y, z) for y, z in chev], [(ROOF_HX, y, z + 0.0) for y, z in chev], P_RIDGE)

# barge boards under the slate edge on both gables
for sx in (-1, 1):
    for s in (-1, 1):
        zt = ZR - 0.004 / CS
        q = [(0.0, zt), (s * E, zt - E * TN), (s * E, zt - E * TN - 0.20), (0.0, zt - 0.20)]
        xa, xb = sx * 2.715, sx * 2.752
        add_hull(I4, [(xa, y, z) for y, z in q], [(xb, y, z) for y, z in q], P_BARGE)

# leaning brick chimney on the back slope
cyh = 0.62
Mc = (Matrix.Translation((-0.75, cyh, zs(cyh) - 0.40)) @ Matrix.Rotation(math.radians(-7), 4, 'Y')
      @ Matrix.Rotation(math.radians(-4), 4, 'X'))
gc = new_grp(Mc, [2, 0.24, 1.42])
add_box(Mc, (-0.24, -0.24, 0.0), (0.24, 0.24, 1.42), P_CHIM, gc)
add_box(Mc, (-0.295, -0.295, 1.16), (0.295, 0.295, 1.30), P_CHIM, gc)

# boards nailed over the window next to the door
cas = [vs for vs, fs in groups['casing'] if max(v.co.y for v in vs) < -1.5][0]
bx0, bx1 = min(v.co.x for v in cas), max(v.co.x for v in cas)
bz0, bz1 = min(v.co.z for v in cas), max(v.co.z for v in cas)
casf = [f for vs, fs in groups['casing'] if vs is cas for f in fs if f.normal.y < -0.9]
yf = max(casf, key=lambda f: f.calc_area()).calc_center_median().y - 0.004      # front of the side posts
bcx, bw, bh = (bx0 + bx1) / 2, bx1 - bx0, bz1 - bz0
print('WINDOW boarded: casing x %.2f..%.2f z %.2f..%.2f front y %.3f (casing min y %.3f)' % (bx0, bx1, bz0, bz1, yf, min(v.co.y for v in cas)))
for dz, ang, ln, layer in ((0.36, 6.0, bw + 0.34, 0), (0.62, -5.0, bw + 0.26, 0), (0.49, 31.0, bw * 1.25, 1)):
    Mb = Matrix.Translation((bcx, yf - 0.03 * layer, bz0 + dz * bh)) @ Matrix.Rotation(math.radians(ang), 4, 'Y')
    add_box(Mb, (-ln / 2, -0.03, -0.075), (ln / 2, 0.0, 0.075), P_BOARD, new_grp(Mb, [3, ln / 2, 0.075]))

# ---------- finish mesh ----------
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
bmesh.ops.triangulate(bm, faces=bm.faces[:])
bm.normal_update()
bm.faces.ensure_lookup_table()
open_e = sum(1 for e in bm.edges if len(e.link_faces) != 2)
vol = bm.calc_volume(signed=True)

# per-face visibility (ambient occlusion with the ground) -> hidden faces + AO for the painter
LV = bm.faces.layers.float.new('vis')
bvh = BVHTree.FromBMesh(bm)
rnd = random.Random(3)
dirs = []
for i in range(24):
    u, v = (i + 0.5) / 24, (i * 0.61803) % 1.0
    r = math.sqrt(u); th = 2 * math.pi * v
    dirs.append((r * math.cos(th), r * math.sin(th), math.sqrt(1 - u)))
nhid = 0
for f in bm.faces:
    n = f.normal
    t = n.orthogonal().normalized(); b = n.cross(t)
    c = f.calc_center_median()
    pts = [c] + [c * 0.55 + v.co * 0.45 for v in f.verts]
    free = 0; tot = 0
    for p in pts:
        o = p + n * 0.003
        for d in dirs:
            w = t * d[0] + b * d[1] + n * d[2]
            tot += 1
            if w.z < -1e-4 and -o.z / w.z < 8.0:
                continue                                    # ground
            if bvh.ray_cast(o, w, 8.0)[0] is None:
                free += 1
    f[LV] = free / tot
    if f[LV] < 0.02 or (n.z < -0.5 and c.z < 0.02):
        f[LP] = P_HIDDEN; nhid += 1

me = bpy.data.meshes.new(NAME)
bm.to_mesh(me)
bm.free()
for p in me.polygons:
    p.use_smooth = False
bpy.data.objects.remove(src)
ob = bpy.data.objects.new(NAME, me)
bpy.context.scene.collection.objects.link(ob)
bpy.ops.object.select_all(action='DESELECT')
ob.select_set(True); bpy.context.view_layer.objects.active = ob
part = np.zeros(len(me.polygons), np.int32); me.attributes['part'].data.foreach_get('value', part)
assert part.min() > 0, 'unclassified faces'

# ---------- UV0 (texture) and UV1 (lightmap) ----------
bpy.context.scene.tool_settings.use_uv_select_sync = True
UVK = {P_HIDDEN: 0.2, P_SHEATH: 0.3, P_SOFFIT: 0.3, P_SLATE: 1.5, P_RIDGE: 1.3}     # texel density per part (roof is what the camera sees)
def unwrap(layer, margin, shrink_hidden):
    me.uv_layers.active = me.uv_layers[layer]
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.0, correct_aspect=True, scale_to_bounds=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    if shrink_hidden:
        d = me.uv_layers[layer].data
        for p in me.polygons:
            k = UVK.get(int(part[p.index]), 1.0)
            if k != 1.0:
                for li in p.loop_indices:
                    d[li].uv = d[li].uv * k
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    try:
        bpy.ops.uv.pack_islands(rotate=True, margin_method='FRACTION', margin=margin)
    except TypeError:
        bpy.ops.uv.pack_islands(rotate=True, margin=margin)
    bpy.ops.object.mode_set(mode='OBJECT')
    uv = np.zeros(len(me.loops) * 2, np.float32); me.uv_layers[layer].data.foreach_get('uv', uv)
    uv = uv.reshape(-1, 3, 2)
    area = 0.5 * np.abs(np.cross(uv[:, 1] - uv[:, 0], uv[:, 2] - uv[:, 0])).sum()
    print('UV %s range [%.4f..%.4f] covered %.3f' % (layer, uv.min(), uv.max(), area))

me.uv_layers.new(name='UVMap')
me.uv_layers.new(name='LightmapUV')
unwrap('UVMap', 0.003, True)
unwrap('LightmapUV', 0.008, False)
me.uv_layers.active = me.uv_layers['UVMap']
me.uv_layers['UVMap'].active_render = True

mat = bpy.data.materials.new('M_IzbaSlate')
mat.use_nodes = True
me.materials.append(mat)

np.savez(OUT + '_grp.npz', M=np.array([[list(r) for r in m] for m in GM], np.float64), I=np.array(GI, np.float64),
         consts=np.array([XN, XP, YN, YP, WTOP, ZR, EAVE_Y, LOGTOP, SZ, TN]))
cs = np.array([v.co[:] for v in me.vertices])
tris = len(me.polygons)
cnt = {}
for p in part:
    cnt[int(p)] = cnt.get(int(p), 0) + 1
print('BUILD tris %d verts %d min %s max %s size %s' % (tris, len(me.vertices), cs.min(0).round(4), cs.max(0).round(4), (cs.max(0) - cs.min(0)).round(4)))
print('BUILD open_edges %d signed_volume %.3f hidden_faces %d groups %d parts %s' % (open_e, vol, nhid, len(GM), sorted(cnt.items())))
bpy.ops.wm.save_as_mainfile(filepath=OUT + 'izba_work.blend')
