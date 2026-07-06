"""Build T2 (raider) + T3 (military) wearables from _work/master.blend.
Rinat's note applied: HARD mesh economy — geometry only for silhouette and
tier markers; wear/patches/camo are vertex-color only (face borders = edges).
Outputs: _work/wearables_t2t3.blend + QC renders in _qc2/.
Run: blender.exe -b --factory-startup --python 04_build_t2t3.py
"""
import bpy, bmesh, sys, os, math
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W
from mathutils import Vector, Matrix, Euler

QC = W.WORKDIR + '_qc2/'
os.makedirs(QC, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=W.WORKDIR + '_work/master.blend')

rig = bpy.data.objects['RootAnim']
L1T = bpy.data.objects['L1_Torso']
L1L = bpy.data.objects['L1_Legs']
BH = bpy.data.objects['BaseHead']

# palettes (art direction, approved 07-06)
SKIN = '#C89A7A'; HAIR = '#4A3826'; EYES = '#2B2823'; FITT = '#2B2823'
RUST = '#7A4A32'; STEEL = '#5A6470'
T2_SHELL = '#3C3E42'; T2_VISOR = '#17181A'; T2_SCARF = '#33342F'
T2_LEATHER = '#33302C'; T2_STRAP = '#5C4128'
T2_PANTS = '#5C5A3E'; T2_PDARK = '#4A4832'; T2_BOOTS = '#2B2823'
CAMO = ['#4F5538', '#8B7E5A', '#3E362A']
T3_RIM = '#3B4030'; T3_CHIN = '#3A3B38'; T3_VEST = '#565B44'
T3_KNEE = '#44483C'; T3_BOOTS = '#2E2A24'


# ---------- helpers (pattern from 01_build) ----------
def dup(src, name):
    ob = src.copy()
    ob.data = src.data.copy()
    ob.name = name
    ob.data.name = name
    bpy.context.collection.objects.link(ob)
    W.rebind(ob, rig)
    W.ensure_col(ob.data)
    bm = bmesh.new(); bm.from_mesh(ob.data)
    nv0 = len(bm.verts)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
    bm.to_mesh(ob.data); bm.free()
    ob.data.update()
    print('  weld %s: %d -> %d verts' % (name, nv0, len(ob.data.vertices)))
    return ob


def face_hex(me, p):
    return W.read_zone_hex(me, p.loop_indices[0])


def islands(me):
    bm = bmesh.new(); bm.from_mesh(me)
    bm.faces.ensure_lookup_table()
    seen = set(); out = []
    for f in bm.faces:
        if f.index in seen:
            continue
        stack = [f]; comp = []
        while stack:
            g = stack.pop()
            if g.index in seen:
                continue
            seen.add(g.index); comp.append(g.index)
            for e in g.edges:
                for h in e.link_faces:
                    if h.index not in seen:
                        stack.append(h)
        out.append(comp)
    bm.free()
    return out


def drop_front_boxes(ob):
    me = ob.data
    kill = []
    for comp in islands(me):
        vs = set()
        for fi in comp:
            vs.update(me.polygons[fi].vertices)
        cos = [me.vertices[i].co for i in vs]
        mn = Vector((min(c.x for c in cos), min(c.y for c in cos), min(c.z for c in cos)))
        mx = Vector((max(c.x for c in cos), max(c.y for c in cos), max(c.z for c in cos)))
        if (3 <= len(comp) <= 80 and (mx - mn).length < 0.30 and mx.y < -0.02 and
                0.95 < mn.z and mx.z < 1.45 and mn.x > -0.30 and mx.x < 0.30):
            kill.extend(comp)
    if kill:
        bm = bmesh.new(); bm.from_mesh(me)
        bm.faces.ensure_lookup_table()
        bmesh.ops.delete(bm, geom=[bm.faces[i] for i in kill], context='FACES')
        bm.to_mesh(me); bm.free(); me.update()
    print('  dropped %d vest-box faces' % len(kill))


def mode_hex(ob, flt):
    cnt = {}
    for p in ob.data.polygons:
        if flt(Vector(p.center)):
            h = face_hex(ob.data, p)
            cnt[h] = cnt.get(h, 0) + 1
    return max(cnt.items(), key=lambda kv: kv[1])[0] if cnt else None


HAND_HX = mode_hex(L1T, lambda c: abs(c.x) > 0.85)
SHOE_HX = mode_hex(L1L, lambda c: c.z < 0.09)


def collar_zone(c):
    return c.z > 1.47 and (c.x * c.x + c.y * c.y) ** 0.5 < 0.14


def hair_zone(c):
    if c.z > 1.755 and c.y > -0.075:
        return True
    if c.y > 0.045 and c.z > 1.60:
        return True
    if c.y > -0.055 and c.z > 1.665 and abs(c.x) > 0.095:
        return True
    return False


def add_eyes(ob, src):
    me2 = ob.data
    n0 = len(me2.vertices)
    bm2 = bmesh.new(); bm2.from_mesh(me2)
    c2 = bm2.loops.layers.color.get('Col')
    for sx in (-0.048, 0.048):
        near = [v.co.y for v in bm2.verts
                if abs(v.co.x - sx) < 0.045 and 1.655 < v.co.z < 1.715]
        yf = (min(near) if near else -0.122) - 0.007
        vs = [bm2.verts.new((sx - 0.012, yf, 1.678)), bm2.verts.new((sx + 0.012, yf, 1.678)),
              bm2.verts.new((sx + 0.012, yf, 1.692)), bm2.verts.new((sx - 0.012, yf, 1.692))]
        f = bm2.faces.new(vs)
        f.normal_update()
        if f.normal.y > 0:
            f.normal_flip()
        ce = W.hexv(EYES)
        for lp in f.loops:
            lp[c2] = ce
    bm2.to_mesh(me2); bm2.free(); me2.update()
    W.transfer_weights(ob, [src], only_new_from=n0)


def camo_hex(c):
    """deterministic angular blotches ~16 cm, 3 tones, edges = face borders"""
    ix, iy, iz = math.floor(c.x / 0.16), math.floor(c.y / 0.16), math.floor(c.z / 0.16)
    h = (ix * 73856093) ^ (iy * 19349663) ^ (iz * 83492791)
    r = (h % 1000) / 1000.0
    if r < 0.50:
        return CAMO[0]
    if r < 0.78:
        return CAMO[1]
    return CAMO[2]


def blotch(points, radius):
    pts = [Vector(p) for p in points]
    return lambda c: any((c - p).length < radius for p in pts)


def paint_faces(bm, col, faces, hx):
    c = W.hexv(hx)
    for f in faces:
        for lp in f.loops:
            lp[col] = c


def new_faces(bm, before):
    return [f for f in bm.faces if f not in before]


def band_of(me, z, dz=0.045, xmax=0.30):
    vs = [v.co for v in me.vertices if abs(v.co.z - z) < dz and abs(v.co.x) < xmax]
    if not vs:
        return (0.16, 0.12, 0.12)
    return (max(abs(v.x) for v in vs), max(-v.y for v in vs), max(v.y for v in vs))


def leg_section(me, sgn, z0, dz=0.06):
    vs = [v.co for v in me.vertices if v.co.x * sgn > 0.02 and abs(v.co.z - z0) < dz]
    if not vs:
        return (sgn * 0.14, -0.02, 0.08)
    cx = sum(v.x for v in vs) / len(vs)
    cy = sum(v.y for v in vs) / len(vs)
    r = max(((v.x - cx) ** 2 + (v.y - cy) ** 2) ** 0.5 for v in vs)
    return (cx, cy, r)


# ============================================================
# T2 Head — full-face broken moto helmet (replaces whole head)
# ============================================================
t2h = dup(BH, 'SK_Armor_T2_Head')
# nuke the base head geometry entirely: helmet is the full slot replacement
me = t2h.data
bm = bmesh.new(); bm.from_mesh(me)
bmesh.ops.delete(bm, geom=bm.faces[:], context='FACES')
bmesh.ops.delete(bm, geom=bm.verts[:], context='VERTS')
col = bm.loops.layers.color.get('Col') or bm.loops.layers.color.new('Col')
N = 10


def hring(z, rx, ry, cy=0.0):
    return [bm.verts.new((rx * math.cos(2 * math.pi * i / N),
                          cy + ry * math.sin(2 * math.pi * i / N), z)) for i in range(N)]


def hloft(a, b, out):
    for i in range(N):
        j = (i + 1) % N
        out.append(bm.faces.new([a[i], a[j], b[j], b[i]]))


shell, visor, scarf = [], [], []
r0 = hring(1.565, 0.118, 0.130, cy=-0.020)   # jaw bottom (chin guard fwd)
r1 = hring(1.615, 0.143, 0.155, cy=-0.014)   # dome ~+10% of head halfwidth 0.133 (spec)
r2 = hring(1.660, 0.147, 0.160, cy=-0.004)
r3 = hring(1.730, 0.147, 0.157)
r4 = hring(1.795, 0.121, 0.129)
hloft(r0, r1, shell)
hloft(r1, r2, shell)
vband = []
hloft(r2, r3, vband)                          # eye-level band: front = visor
apexf = []
hloft(r3, r4, shell)
apex = bm.verts.new((0.0, 0.0, 1.852))
for i in range(N):
    j = (i + 1) % N
    shell.append(bm.faces.new([r4[i], r4[j], apex]))
# visor = front faces of the eye band (centers with y < -0.10)
for f in vband:
    (visor if f.calc_center_median().y < -0.10 else shell).append(f)
# scarf tube below the helmet
s0 = hring(1.497, 0.092, 0.104)
hloft(s0, [bm.verts.new((v.co.x * 1.22, v.co.y * 1.20, 1.565)) for v in s0], scarf)
paint_faces(bm, col, shell, T2_SHELL)
paint_faces(bm, col, visor, T2_VISOR)
paint_faces(bm, col, scarf, T2_SCARF)
# rust chips: 3 angular blotches on the dome (color only)
chips = blotch([(0.09, -0.09, 1.79), (-0.12, 0.05, 1.75), (0.03, 0.14, 1.70)], 0.055)
for f in shell:
    if chips(f.calc_center_median()):
        paint_faces(bm, col, [f], RUST)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
bm.to_mesh(me); bm.free(); me.update()
W.transfer_weights(t2h, [BH], only_new_from=0)

# ============================================================
# T2 Torso — raider leather jacket: repaint + shoulder plates,
# chest strap cross, forearm straps
# ============================================================
t2t = dup(L1T, 'SK_Armor_T2_Torso')
drop_front_boxes(t2t)
patches = blotch([(0.10, 0.14, 1.13), (-0.55, 0.03, 1.34)], 0.075)


def rule_t2_body(c, p, me):
    h = face_hex(me, p)
    if collar_zone(c):
        return T2_LEATHER
    if h == HAND_HX or abs(c.x) > 0.83:
        return SKIN if abs(c.x) > 0.945 else FITT   # fingerless gloves
    if patches(c):
        return RUST                                 # patches (color only, art: #7A4A32)
    return T2_LEATHER


W.paint_by_rule(t2t, rule_t2_body)
me = t2t.data
N0 = len(me.vertices)
bm = bmesh.new(); bm.from_mesh(me)
col = bm.loops.layers.color.get('Col')
straps, metal = [], []
# chest strap cross (front only, flat ribbons on the body)
for sgn in (1, -1):
    rows = []
    for t in (0.0, 0.25, 0.5, 0.75, 1.0):
        z = 1.42 - t * (1.42 - 0.96)
        x = sgn * (-0.17 + t * 0.30)
        a, fb, bb = band_of(me, z)
        p = Vector((x, -(fb + 0.008), z))
        w = Vector((0.016, 0.0, 0.010))
        rows.append((bm.verts.new(p - w), bm.verts.new(p + w)))
    for (a1, a2), (b1, b2) in zip(rows, rows[1:]):
        straps.append(bm.faces.new([a1, a2, b2, b1]))
# buckle at the cross
a, fb, bb = band_of(me, 1.19)
before = set(bm.faces)
bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((0, -(fb + 0.012), 1.19)) @
                      Matrix.Diagonal((0.055, 0.022, 0.055, 1)))
metal += new_faces(bm, before)
# shoulder plates: draped over the REAL top surface of each shoulder
# (cylinder around slice-center ballooned — the x-slice includes the whole
# jacket side, not just the arm; drape rows on max-z instead)
for sgn in (1, -1):
    rows = []
    for xm in (0.260, 0.315, 0.368):
        band = [v.co for v in me.vertices
                if abs(v.co.x * sgn - xm) < 0.075 and v.co.z > 1.30]
        if not band:                       # welded mesh is sparse — widen
            band = [v.co for v in me.vertices
                    if abs(v.co.x * sgn - xm) < 0.12 and v.co.z > 1.30]
        cyv = sum(v.y for v in band) / len(band)
        zt = max(v.z for v in band)
        pts = []
        for dy in (-0.078, -0.028, 0.028, 0.078):
            sag = 0.030 * (abs(dy) / 0.078) ** 2
            pts.append(bm.verts.new((sgn * xm, cyv + dy, zt + 0.012 - sag)))
        rows.append(pts)
    for ra, rb in zip(rows, rows[1:]):
        for i in range(3):
            metal.append(bm.faces.new([ra[i], ra[i + 1], rb[i + 1], rb[i]]))
# forearm strap rings
for sgn in (1, -1):
    vs = [v.co for v in me.vertices if 0.62 < v.co.x * sgn < 0.78]
    cyv = sum(v.y for v in vs) / len(vs)
    czv = sum(v.z for v in vs) / len(vs)
    rr = max(((v.y - cyv) ** 2 + (v.z - czv) ** 2) ** 0.5 for v in vs) + 0.007
    before = set(bm.faces)
    bmesh.ops.create_cone(bm, cap_ends=False, segments=8, radius1=rr, radius2=rr,
                          depth=0.045, matrix=Matrix.Translation((sgn * 0.70, cyv, czv)) @
                          Euler((0, math.pi / 2, 0)).to_matrix().to_4x4())
    straps += new_faces(bm, before)
paint_faces(bm, col, straps, T2_STRAP)
paint_faces(bm, col, metal, STEEL)
# rusty edge on one plate face per side (marker of самопал; skip buckle = metal[0..5])
for f in metal[7:8] + metal[-2:-1]:
    paint_faces(bm, col, [f], RUST)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
bm.to_mesh(me); bm.free(); me.update()
W.transfer_weights(t2t, [L1T], only_new_from=N0)

# ============================================================
# T2 Legs — olive cargo + metal knee pads + heavy boots
# ============================================================
t2l = dup(L1L, 'SK_Armor_T2_Legs')


def rule_t2_legs(c, p, me):
    h = face_hex(me, p)
    if h == SHOE_HX:
        return T2_BOOTS
    if c.z > 0.873:
        return T2_PDARK
    return T2_PANTS


W.paint_by_rule(t2l, rule_t2_legs)
me = t2l.data
N0 = len(me.vertices)
bm = bmesh.new(); bm.from_mesh(me)
col = bm.loops.layers.color.get('Col')
dark, metal, strapsf, soles = [], [], [], []
shoe_l = [Vector(p.center) for p in L1L.data.polygons if face_hex(L1L.data, p) == SHOE_HX and p.center[0] > 0]
shoe_r = [Vector(p.center) for p in L1L.data.polygons if face_hex(L1L.data, p) == SHOE_HX and p.center[0] < 0]
for cluster in (shoe_l, shoe_r):
    xs = [c.x for c in cluster]; ys = [c.y for c in cluster]
    cx = (min(xs) + max(xs)) / 2; cyv = (min(ys) + max(ys)) / 2
    hx_ = (max(xs) - min(xs)) / 2 + 0.018
    hy_ = (max(ys) - min(ys)) / 2 + 0.020
    before = set(bm.faces)
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((cx, cyv, 0.018)) @
                          Matrix.Diagonal((hx_ * 2, hy_ * 2, 0.036, 1)))
    soles += new_faces(bm, before)
# thigh cargo boxes (bigger than T1, but NOT the whole thigh depth)
th = [v.co for v in me.vertices if 0.58 < v.co.z < 0.72]
mx = max(abs(c.x) for c in th)
ymid = sum(c.y for c in th) / len(th)
for sx in (-(mx + 0.010), mx + 0.010):
    before = set(bm.faces)
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((sx, ymid - 0.02, 0.63)) @
                          Matrix.Diagonal((0.045, 0.125, 0.165, 1)))
    dark += new_faces(bm, before)
# knee pads: FRONT plates (radius from front surface, not slice max —
# slice max made a fat ring around the whole leg) + strap ring below
for sgn in (1, -1):
    vs = [v.co for v in me.vertices if v.co.x * sgn > 0.02 and 0.40 < v.co.z < 0.55]
    cx = sum(v.x for v in vs) / len(vs)
    cyv = sum(v.y for v in vs) / len(vs)
    r = (cyv - min(v.y for v in vs)) + 0.014
    arcs = []
    for z, rr in ((0.415, r), (0.470, r + 0.004), (0.522, r - 0.010)):
        arcs.append([Vector((cx + rr * math.sin(ph), cyv - rr * math.cos(ph), z))
                     for ph in (a2 * math.pi / 180 for a2 in (-40, -14, 14, 40))])
    for aA, aB in zip(arcs, arcs[1:]):
        va = [bm.verts.new(p) for p in aA]
        vb = [bm.verts.new(p) for p in aB]
        for i in range(3):
            metal.append(bm.faces.new([va[i], va[i + 1], vb[i + 1], vb[i]]))
    cx2, cy2, r2_ = leg_section(me, sgn, 0.36, dz=0.05)
    before = set(bm.faces)
    bmesh.ops.create_cone(bm, cap_ends=False, segments=8, radius1=r2_ + 0.006,
                          radius2=r2_ + 0.006, depth=0.030,
                          matrix=Matrix.Translation((cx2, cy2, 0.36)))
    strapsf += new_faces(bm, before)
paint_faces(bm, col, dark, T2_PDARK)
paint_faces(bm, col, metal, STEEL)
paint_faces(bm, col, strapsf, T2_STRAP)
paint_faces(bm, col, soles, T2_BOOTS)
for f in metal[2:3] + metal[8:9]:
    paint_faces(bm, col, [f], RUST)      # rusty rim, small
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
bm.to_mesh(me); bm.free(); me.update()
W.transfer_weights(t2l, [L1L], only_new_from=N0)

# ============================================================
# T3 Head — open face + wide flat olive dome + chin strap
# ============================================================
t3h = dup(BH, 'SK_Armor_T3_Head')


def rule_head_plain(c, p, me):
    return HAIR if hair_zone(c) else SKIN


W.paint_by_rule(t3h, rule_head_plain)
add_eyes(t3h, BH)
me = t3h.data
N0 = len(me.vertices)
bm = bmesh.new(); bm.from_mesh(me)
col = bm.loops.layers.color.get('Col')
dome, rim, chin = [], [], []
N = 10


def dring(z, rx, ry, lift=0.0):
    """helmet ring; lift raises the FRONT (-Y) so the face/eyes stay open
    (eyes sit at z 1.678..1.692) while sides/back dip over ears (ref 2.png)."""
    out = []
    for i in range(N):
        th = 2 * math.pi * i / N
        s = math.sin(th)
        out.append(bm.verts.new((rx * math.cos(th), -0.004 + ry * s,
                                 z + lift * max(0.0, -s))))
    return out


d0 = dring(1.664, 0.148, 0.156, lift=0.044)   # rim bottom: front 1.708 (brow), sides over ears
d1 = dring(1.702, 0.150, 0.158, lift=0.026)
d2 = dring(1.775, 0.136, 0.144)
d3 = dring(1.833, 0.086, 0.092)
for a2, b2, out in ((d0, d1, rim), (d1, d2, dome), (d2, d3, dome)):
    for i in range(N):
        j = (i + 1) % N
        out.append(bm.faces.new([a2[i], a2[j], b2[j], b2[i]]))
apex = bm.verts.new((0.0, -0.004, 1.856))
for i in range(N):
    j = (i + 1) % N
    dome.append(bm.faces.new([d3[i], d3[j], apex]))
# chin strap: flat ribbon around the jaw
path = [Vector(p) for p in ((0.128, -0.015, 1.652), (0.095, -0.088, 1.600),
                            (0.0, -0.128, 1.572), (-0.095, -0.088, 1.600),
                            (-0.128, -0.015, 1.652))]
rows = [(bm.verts.new(p + Vector((0, 0, 0.010))), bm.verts.new(p - Vector((0, 0, 0.010))))
        for p in path]
for (a1, a2), (b1, b2) in zip(rows, rows[1:]):
    chin.append(bm.faces.new([a1, a2, b2, b1]))
paint_faces(bm, col, dome, CAMO[0])
paint_faces(bm, col, rim, T3_RIM)
paint_faces(bm, col, chin, T3_CHIN)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
bm.to_mesh(me); bm.free(); me.update()
W.transfer_weights(t3h, [BH], only_new_from=N0)

# ============================================================
# T3 Torso — camo jacket + solid-color chest rig (6 pouches)
# ============================================================
t3t = dup(L1T, 'SK_Armor_T3_Torso')
drop_front_boxes(t3t)


def rule_t3_body(c, p, me):
    h = face_hex(me, p)
    if collar_zone(c):
        return CAMO[0]
    if h == HAND_HX or abs(c.x) > 0.83:
        return SKIN if abs(c.x) > 0.945 else FITT   # fingerless gloves
    if c.y < -0.04 and abs(c.x) < 0.20 and 1.06 < c.z < 1.40:
        return T3_VEST                              # chest rig panel (solid)
    return camo_hex(c)


W.paint_by_rule(t3t, rule_t3_body)
me = t3t.data
N0 = len(me.vertices)
bm = bmesh.new(); bm.from_mesh(me)
col = bm.loops.layers.color.get('Col')
pouches = []
a, fb, bb = band_of(me, 1.20)
py = -(fb + 0.020)
for cz in (1.145, 1.265):
    for sx in (-0.115, 0.0, 0.115):
        before = set(bm.faces)
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((sx, py, cz)) @
                              Matrix.Diagonal((0.066, 0.034, 0.082, 1)))
        pouches += new_faces(bm, before)
paint_faces(bm, col, pouches, T3_VEST)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
bm.to_mesh(me); bm.free(); me.update()
W.transfer_weights(t3t, [L1T], only_new_from=N0)

# ============================================================
# T3 Legs — camo pants tucked into high boots + fabric knee pads
# ============================================================
t3l = dup(L1L, 'SK_Armor_T3_Legs')


def rule_t3_legs(c, p, me):
    h = face_hex(me, p)
    if h == SHOE_HX or c.z < 0.27:
        return T3_BOOTS                 # high boots (tucked-in look)
    if c.z > 0.873:
        return CAMO[2]                  # belt = dark camo tone
    return camo_hex(c)


W.paint_by_rule(t3l, rule_t3_legs)
me = t3l.data
N0 = len(me.vertices)
bm = bmesh.new(); bm.from_mesh(me)
col = bm.loops.layers.color.get('Col')
boots, knees, dark = [], [], []
# boot shafts: tapered tubes (pant tucks INTO the shaft = tier marker)
# section taken at calf z=0.31 — the z=0.20 slice caught the FOOT (toe box)
# and blew the radius up to a bell-bottom
for sgn in (1, -1):
    cx, cyv, r = leg_section(me, sgn, 0.31, dz=0.04)
    before = set(bm.faces)
    bmesh.ops.create_cone(bm, cap_ends=False, segments=8, radius1=r + 0.005,
                          radius2=r + 0.011, depth=0.20,
                          matrix=Matrix.Translation((cx, cyv, 0.19)))
    boots += new_faces(bm, before)
# soles
for cluster in (shoe_l, shoe_r):
    xs = [c.x for c in cluster]; ys = [c.y for c in cluster]
    cx = (min(xs) + max(xs)) / 2; cyv = (min(ys) + max(ys)) / 2
    hx_ = (max(xs) - min(xs)) / 2 + 0.014
    hy_ = (max(ys) - min(ys)) / 2 + 0.016
    before = set(bm.faces)
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((cx, cyv, 0.016)) @
                          Matrix.Diagonal((hx_ * 2, hy_ * 2, 0.032, 1)))
    boots += new_faces(bm, before)
# fabric knee plates (solid dark, NOT metal) — front-surface radius, narrow arc
for sgn in (1, -1):
    vs = [v.co for v in me.vertices if v.co.x * sgn > 0.02 and 0.40 < v.co.z < 0.55]
    cx = sum(v.x for v in vs) / len(vs)
    cyv = sum(v.y for v in vs) / len(vs)
    r = (cyv - min(v.y for v in vs)) + 0.012
    arcs = []
    for z, rr in ((0.412, r), (0.468, r + 0.003), (0.518, r - 0.010)):
        arcs.append([Vector((cx + rr * math.sin(ph), cyv - rr * math.cos(ph), z))
                     for ph in (a2 * math.pi / 180 for a2 in (-38, -13, 13, 38))])
    for aA, aB in zip(arcs, arcs[1:]):
        va = [bm.verts.new(p) for p in aA]
        vb = [bm.verts.new(p) for p in aB]
        for i in range(3):
            knees.append(bm.faces.new([va[i], va[i + 1], vb[i + 1], vb[i]]))
# cargo boxes (solid dark tone)
th = [v.co for v in me.vertices if 0.58 < v.co.z < 0.72]
mx = max(abs(c.x) for c in th)
ymid = sum(c.y for c in th) / len(th)
for sx in (-(mx + 0.008), mx + 0.008):
    before = set(bm.faces)
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((sx, ymid - 0.02, 0.64)) @
                          Matrix.Diagonal((0.040, 0.115, 0.155, 1)))
    dark += new_faces(bm, before)
paint_faces(bm, col, boots, T3_BOOTS)
paint_faces(bm, col, knees, T3_KNEE)
paint_faces(bm, col, dark, CAMO[2])
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
bm.to_mesh(me); bm.free(); me.update()
W.transfer_weights(t3l, [L1L], only_new_from=N0)

# ============================================================
# finalize + QC
# ============================================================
OUTS = [t2h, t2t, t2l, t3h, t3t, t3l]
for ob in OUTS:
    while ob.data.uv_layers:
        ob.data.uv_layers.remove(ob.data.uv_layers[0])
    W.finalize_mesh(ob)          # unwraps too (uv_layers just wiped)
    unw = sum(1 for v in ob.data.vertices if not v.groups)
    print('BUILT %-22s tris=%4d verts=%4d unweighted=%d' % (
        ob.name, W.tri_count(ob), len(ob.data.vertices), unw))
for ob in OUTS + [rig]:
    W.assert_identity(ob)
for ob in (L1T, L1L, bpy.data.objects['L1_Head'], BH):
    ob.hide_render = True
    ob.hide_viewport = True
bpy.ops.wm.save_mainfile(filepath=W.WORKDIR + '_work/wearables_t2t3.blend')
print('SAVED', W.WORKDIR + '_work/wearables_t2t3.blend')

sc, cam, suns = W.setup_render()


def show_only(objs):
    for o in bpy.data.objects:
        if o.type == 'MESH':
            o.hide_render = o not in objs


VIEWS = {'front': (0, -1, 0.12), 'tq': (0.7, -1, 0.55), 'side': (1, 0, 0.12),
         'top': (0, -0.001, 1), 'back': (0, 1, 0.12)}
for ob in OUTS:
    show_only([ob])
    for vn, vd in VIEWS.items():
        W.frame_and_shoot([ob], vd, QC + '%s_%s.png' % (ob.name, vn), suns=suns)
for label, trio in (('T2_set', [t2h, t2t, t2l]), ('T3_set', [t3h, t3t, t3l])):
    show_only(trio)
    for vn, vd in VIEWS.items():
        W.frame_and_shoot(trio, vd, QC + '%s_%s.png' % (label, vn), suns=suns)
print('QC DONE')
