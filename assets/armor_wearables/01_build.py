"""Build T0 (recolor) + T1 (sculpt) wearables from _work/master.blend.
Outputs: _work/wearables_work.blend + QC renders in _qc/.
Deterministic: always starts from master.blend.
Run: blender.exe -b --factory-startup --python 01_build.py
"""
import bpy, bmesh, sys, os, math
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W
from mathutils import Vector, Matrix, Euler

QC = W.WORKDIR + '_qc/'
os.makedirs(QC, exist_ok=True)

bpy.ops.wm.open_mainfile(filepath=W.WORKDIR + '_work/master.blend')
addon = __import__('addon_utils')
addon.enable('io_scene_fbx')

rig = bpy.data.objects['RootAnim']
L1T = bpy.data.objects['L1_Torso']
L1L = bpy.data.objects['L1_Legs']
BH = bpy.data.objects['BaseHead']

# palette (art direction, approved 07-06)
SKIN = '#C89A7A'; HAIR = '#4A3826'; EYES = '#2B2823'
T0_TEE = '#7C776A'; T0_NECK = '#635E52'; T0_PANTS = '#4A4843'; T0_SHOE = '#33302C'; T0_BELT = '#3B362F'
T1_LEATHER = '#6F4A2B'; T1_DARK = '#56381F'; T1_SHIRT = '#A89B7E'; T1_FITT = '#2B2823'
T1_PANTS = '#4E5258'; T1_DIRT = '#5C5348'; T1_CAP = '#4A443C'; T1_VISOR = '#3B362F'; T1_BELT = '#3B362F'


def dup(src, name):
    ob = src.copy()
    ob.data = src.data.copy()
    ob.name = name
    ob.data.name = name
    bpy.context.collection.objects.link(ob)
    W.rebind(ob, rig)          # explicit identity basis/parent_inverse
    W.ensure_col(ob.data)
    # weld: UE export fully vertex-split the meshes; weld so that island
    # detection and clean topology work (flat shade + FACE export re-splits)
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


def island_info(ob):
    me = ob.data
    res = []
    for comp in islands(me):
        vs = set()
        for fi in comp:
            vs.update(me.polygons[fi].vertices)
        cos = [me.vertices[i].co for i in vs]
        mn = Vector((min(c.x for c in cos), min(c.y for c in cos), min(c.z for c in cos)))
        mx = Vector((max(c.x for c in cos), max(c.y for c in cos), max(c.z for c in cos)))
        res.append((comp, mn, mx))
    return res


def delete_faces(ob, face_indices):
    me = ob.data
    bm = bmesh.new(); bm.from_mesh(me)
    bm.faces.ensure_lookup_table()
    doomed = [bm.faces[i] for i in face_indices]
    bmesh.ops.delete(bm, geom=doomed, context='FACES')
    bm.to_mesh(me); bm.free()
    me.update()


def drop_front_boxes(ob):
    """Remove the 4 vest pocket boxes (small islands on chest front)."""
    kill = []
    for comp, mn, mx in island_info(ob):
        size = mx - mn
        if (3 <= len(comp) <= 80 and size.length < 0.30 and mx.y < -0.02 and
                0.95 < mn.z and mx.z < 1.45 and mn.x > -0.30 and mx.x < 0.30):
            kill.extend(comp)
            print('  drop island faces=%d bbox=(%.2f,%.2f,%.2f)-(%.2f,%.2f,%.2f)' % (
                len(comp), mn.x, mn.y, mn.z, mx.x, mx.y, mx.z))
    if kill:
        delete_faces(ob, kill)
    return len(kill)


# ---------- zone hex sampling on L1 torso ----------
def mode_hex(ob, flt):
    me = ob.data
    cnt = {}
    for p in me.polygons:
        c = Vector(p.center)
        if flt(c):
            h = face_hex(me, p)
            cnt[h] = cnt.get(h, 0) + 1
    return max(cnt.items(), key=lambda kv: kv[1])[0] if cnt else None


SLEEVE_HX = mode_hex(L1T, lambda c: 0.40 < abs(c.x) < 0.70)
HAND_HX = mode_hex(L1T, lambda c: abs(c.x) > 0.85)
PANTS_HX = mode_hex(L1L, lambda c: 0.3 < c.z < 0.8)
SHOE_HX = mode_hex(L1L, lambda c: c.z < 0.09)
print('SAMPLED sleeves=%s hands=%s pants=%s shoes=%s' % (
    SLEEVE_HX, HAND_HX, PANTS_HX, SHOE_HX))


def collar_zone(c):
    return c.z > 1.47 and (c.x * c.x + c.y * c.y) ** 0.5 < 0.14

# ============================================================
# T0_Torso — tee look: corpus tee, arms+hands skin, collar cant
# ============================================================
t0t = dup(L1T, 'SK_Cloth_T0_Torso')
n = drop_front_boxes(t0t)
print('T0_Torso dropped box faces:', n)


def rule_t0_torso(c, p, me):
    h = face_hex(me, p)
    if collar_zone(c):
        return T0_NECK
    if abs(c.x) > 0.315 or h == HAND_HX:
        return SKIN
    return T0_TEE


W.paint_by_rule(t0t, rule_t0_torso)

# ============================================================
# T0_Legs — plain grey pants + dark shoes + belt band
# ============================================================
t0l = dup(L1L, 'SK_Cloth_T0_Legs')


def rule_t0_legs(c, p, me):
    h = face_hex(me, p)
    if h == SHOE_HX:
        return T0_SHOE
    if c.z > 0.873:
        return T0_BELT
    return T0_PANTS


W.paint_by_rule(t0l, rule_t0_legs)

# ============================================================
# T0_Head — base head painted: skin + hair + eyes
# ============================================================
t0h = dup(BH, 'SK_Cloth_T0_Head')


def hair_zone(c):
    if c.z > 1.755 and c.y > -0.075:
        return True                      # crown (not over the forehead)
    if c.y > 0.045 and c.z > 1.60:
        return True                      # back of skull
    if c.y > -0.055 and c.z > 1.665 and abs(c.x) > 0.095:
        return True                      # sides above ears
    return False


def rule_head_plain(c, p, me):
    if hair_zone(c):
        return HAIR
    return SKIN


def add_eyes(ob):
    """Base head facets are too coarse for painted eyes ('мелко' per spec) —
    add two tiny quads floating 4 mm off the face instead."""
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
        col_e = W.hexv(EYES)
        for lp in f.loops:
            lp[c2] = col_e
    bm2.to_mesh(me2); bm2.free(); me2.update()
    W.transfer_weights(ob, [BH], only_new_from=n0)


W.paint_by_rule(t0h, rule_head_plain)
add_eyes(t0h)

# ============================================================
# T1_Head — painted head + cap dome + visor + hair strands
# ============================================================
t1h = dup(BH, 'SK_Armor_T1_Head')
W.paint_by_rule(t1h, rule_head_plain)
add_eyes(t1h)

me = t1h.data
N0 = len(me.vertices)
bm = bmesh.new(); bm.from_mesh(me)
col = bm.loops.layers.color.get('Col') or bm.loops.layers.color.new('Col')
CX, CY = 0.0, -0.006


def ring(z, rx, ry, n=12):
    return [bm.verts.new((CX + rx * math.cos(2 * math.pi * i / n),
                          CY + ry * math.sin(2 * math.pi * i / n), z)) for i in range(n)]


def loft(a, b, hx, faces):
    for i in range(len(a)):
        j = (i + 1) % len(a)
        f = bm.faces.new([a[i], a[j], b[j], b[i]])
        faces.append((f, hx))


capf = []
r0 = ring(1.712, 0.150, 0.163)
r1 = ring(1.768, 0.143, 0.155)
r2 = ring(1.822, 0.098, 0.106)
loft(r0, r1, T1_CAP, capf)
loft(r1, r2, T1_CAP, capf)
apex = bm.verts.new((CX, CY, 1.845))
for i in range(12):
    j = (i + 1) % 12
    f = bm.faces.new([r2[i], r2[j], apex])
    capf.append((f, T1_CAP))
# visor (forward = -Y), slight side curl up
zt, zb = 1.732, 1.720
top_pts = [(-0.080, -0.150, zt), (0.080, -0.150, zt),
           (0.072, -0.240, zt - 0.003), (0.042, -0.292, zt - 0.008),
           (-0.042, -0.292, zt - 0.008), (-0.072, -0.240, zt - 0.003)]
vt = [bm.verts.new(p) for p in top_pts]
vb = [bm.verts.new((p[0], p[1], p[2] - (zt - zb))) for p in top_pts]
f = bm.faces.new(vt); capf.append((f, T1_VISOR))
f = bm.faces.new(list(reversed(vb))); capf.append((f, T1_VISOR))
for i in range(6):
    j = (i + 1) % 6
    f = bm.faces.new([vt[i], vt[j], vb[j], vb[i]])
    capf.append((f, T1_VISOR))
# hair strands: angular slabs at back + sides under cap rim
strand_defs = [
    (0.000, 0.132, 1.652, 0.052, 0.014, 0.062, 8),
    (0.075, 0.108, 1.645, 0.034, 0.013, 0.055, 22),
    (-0.075, 0.108, 1.645, 0.034, 0.013, 0.055, -22),
    (0.118, 0.028, 1.660, 0.013, 0.036, 0.048, 6),
    (-0.118, 0.028, 1.660, 0.013, 0.036, 0.048, -6),
]
for (sx, sy, sz, hx_, hy_, hz_, rz) in strand_defs:
    R = Euler((0, 0, math.radians(rz)), 'XYZ').to_matrix().to_4x4()
    M = Matrix.Translation((sx, sy, sz)) @ R @ Matrix.Diagonal((hx_ * 2, hy_ * 2, hz_ * 2, 1))
    before = set(bm.faces)
    bmesh.ops.create_cube(bm, size=1.0, matrix=M)
    for f in set(bm.faces) - before:
        capf.append((f, HAIR))

for f, hx in capf:
    c = W.hexv(hx)
    for lp in f.loops:
        lp[col] = c
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
bm.to_mesh(me); bm.free(); me.update()
W.transfer_weights(t1h, [BH], only_new_from=N0)

# ============================================================
# T1_Torso — leather jacket: repaint body + open-front shell,
# collar, chest pockets, cuffs
# ============================================================
t1t = dup(L1T, 'SK_Armor_T1_Torso')
drop_front_boxes(t1t)


def open_w(z):
    """front opening half-width of the jacket shell (V: wide up, narrow down)"""
    pts = [(0.850, 0.028), (0.950, 0.034), (1.060, 0.042), (1.180, 0.052),
           (1.300, 0.062), (1.400, 0.068), (1.462, 0.058), (1.505, 0.050),
           (1.552, 0.040)]
    for (z0, w0), (z1, w1) in zip(pts, pts[1:]):
        if z <= z1:
            t = max(0.0, (z - z0) / (z1 - z0))
            return w0 + (w1 - w0) * t
    return pts[-1][1]


def vwidth(z):
    """shirt V half-width on the underbody front (a bit wider than opening)"""
    return open_w(min(z, 1.44)) + 0.015


def rule_t1_body(c, p, me):
    h = face_hex(me, p)
    if collar_zone(c):
        return T1_DARK
    if h == HAND_HX or abs(c.x) > 0.83:
        return SKIN
    if abs(c.x) > 0.75:
        return T1_DARK                    # cuff band on sleeve near wrist
    if abs(c.x) > 0.315:
        return T1_LEATHER                 # sleeves
    if c.y < -0.02 and abs(c.x) < vwidth(c.z) and c.z > 0.94:
        return T1_SHIRT                   # shirt in the V
    if 0.24 < abs(c.x) and c.z > 1.38:
        return T1_DARK                    # shoulder seam band
    return T1_LEATHER


W.paint_by_rule(t1t, rule_t1_body)

# trunk cross-sections for the shell
me = t1t.data
N0 = len(me.vertices)


def band(z, dz=0.045, xmax=0.30):
    vs = [v.co for v in me.vertices if abs(v.co.z - z) < dz and abs(v.co.x) < xmax]
    if not vs:
        return (0.16, 0.12, 0.12)
    return (max(abs(v.x) for v in vs), max(-v.y for v in vs), max(v.y for v in vs))


OFF = 0.028
RINGS = []  # (z, a, fb, bb, gap_rad)
spec = [(0.850, 0.955, 0.034), (0.950, 0.955, 0.030), (1.060, 1.060, 0.028),
        (1.180, 1.180, 0.028), (1.300, 1.300, 0.028), (1.400, 1.400, 0.028, 0.27),
        (1.462, 1.462, 0.028, 0.22), (1.505, 1.505, 0.030, 0.17),
        (1.552, 1.552, 0.030, 0.16)]
for s in spec:
    z, mz, off = s[0], s[1], s[2]
    xmax = s[3] if len(s) > 3 else 0.30
    a, fb, bb = band(mz, xmax=xmax)
    a, fb, bb = a + off, fb + off, bb + off
    gap = math.asin(min(0.9, open_w(z) / a))
    RINGS.append((z, a, fb, bb, gap))
    print('  ring z=%.3f a=%.3f fb=%.3f bb=%.3f gap=%.1fdeg' % (
        z, a, fb, bb, math.degrees(gap)))

bm = bmesh.new(); bm.from_mesh(me)
col = bm.loops.layers.color.get('Col')
NP = 14
shellf = []
ring_pts = []
for (z, a, fb, bb, gap) in RINGS:
    g = gap
    pts = []
    for i in range(NP):
        th = g + (2 * math.pi - 2 * g) * i / (NP - 1)
        x = a * math.sin(th)
        cy = math.cos(th)
        y = -fb * cy if cy > 0 else -bb * cy
        pts.append(bm.verts.new((x, y, z)))
    ring_pts.append(pts)
for k in range(len(ring_pts) - 1):
    A, B = ring_pts[k], ring_pts[k + 1]
    hx = T1_DARK if RINGS[k][0] >= 1.46 else T1_LEATHER
    for i in range(NP - 1):
        f = bm.faces.new([A[i], A[i + 1], B[i + 1], B[i]])
        shellf.append((f, hx))
# inner lips along the front opening (zipper edge)
for side in (0, NP - 1):
    prev = None
    for k, pts in enumerate(ring_pts):
        p = pts[side]
        q = bm.verts.new((p.co.x * 0.82, p.co.y * 0.82, p.co.z))
        if prev is not None:
            f = bm.faces.new([prev[0], p, q, prev[1]])
            shellf.append((f, T1_FITT))
        prev = (p, q)
# chest pockets on the shell
zp = 1.22
a, fb, bb = band(1.22)
py = -(fb + OFF + 0.012)
for sx in (-0.138, 0.138):
    for (cz, hz, hx) in ((1.205, 0.034, T1_LEATHER), (1.247, 0.012, T1_DARK)):
        M = Matrix.Translation((sx, py, cz)) @ Matrix.Diagonal((0.088, 0.024, hz * 2, 1))
        before = set(bm.faces)
        bmesh.ops.create_cube(bm, size=1.0, matrix=M)
        for f in set(bm.faces) - before:
            shellf.append((f, hx))
# sleeve cuff ridges near wrists
for sx in (-0.79, 0.79):
    vs = [v.co for v in me.vertices if abs(abs(v.co.x) - abs(sx)) < 0.05 and abs(v.co.x) > 0.6]
    if vs:
        cyv = sum(v.y for v in vs) / len(vs); czv = sum(v.z for v in vs) / len(vs)
        rr = max(((v.y - cyv) ** 2 + (v.z - czv) ** 2) ** 0.5 for v in vs) + 0.008
    else:
        cyv, czv, rr = -0.001, 1.336, 0.045
    before = set(bm.faces)
    bmesh.ops.create_cone(bm, cap_ends=False, segments=8, radius1=rr, radius2=rr,
                          depth=0.05, matrix=Matrix.Translation((sx, cyv, czv)) @
                          Euler((0, math.pi / 2, 0)).to_matrix().to_4x4())
    for f in set(bm.faces) - before:
        shellf.append((f, T1_DARK))
for f, hx in shellf:
    c = W.hexv(hx)
    for lp in f.loops:
        lp[col] = c
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
bm.to_mesh(me); bm.free(); me.update()
W.transfer_weights(t1t, [L1T], only_new_from=N0)

# ============================================================
# T1_Legs — work pants: repaint + thigh pockets + soles + ankle cuffs
# ============================================================
t1l = dup(L1L, 'SK_Armor_T1_Legs')


def rule_t1_legs(c, p, me):
    h = face_hex(me, p)
    if h == SHOE_HX:
        return T1_LEATHER                  # boots
    if c.z > 0.873:
        return T1_BELT
    if c.z < 0.15:
        return T1_DIRT                     # low hem wear
    return T1_PANTS


W.paint_by_rule(t1l, rule_t1_legs)

me = t1l.data
N0 = len(me.vertices)
# shoe clusters (by original color) for soles/cuffs placement
shoe_l = [v.co for p in L1L.data.polygons if face_hex(L1L.data, p) == SHOE_HX and p.center[0] > 0
          for v in [L1L.data.vertices[i] for i in p.vertices]]
shoe_r = [v.co for p in L1L.data.polygons if face_hex(L1L.data, p) == SHOE_HX and p.center[0] < 0
          for v in [L1L.data.vertices[i] for i in p.vertices]]
bm = bmesh.new(); bm.from_mesh(me)
col = bm.loops.layers.color.get('Col')
newf = []
for cluster in (shoe_l, shoe_r):
    if not cluster:
        continue
    xs = [c.x for c in cluster]; ys = [c.y for c in cluster]; zs = [c.z for c in cluster]
    cx = (min(xs) + max(xs)) / 2; cyv = (min(ys) + max(ys)) / 2
    hx_ = (max(xs) - min(xs)) / 2 + 0.014
    hy_ = (max(ys) - min(ys)) / 2 + 0.016
    # sole slab
    M = Matrix.Translation((cx, cyv, 0.016)) @ Matrix.Diagonal((hx_ * 2, hy_ * 2, 0.032, 1))
    before = set(bm.faces)
    bmesh.ops.create_cube(bm, size=1.0, matrix=M)
    for f in set(bm.faces) - before:
        newf.append((f, T1_FITT))
    # ankle cuff (pant hem over boot)
    ank = [v.co for v in me.vertices if abs(v.co.x - cx) < 0.08 and 0.13 < v.co.z < 0.22]
    if ank:
        ay = sum(c.y for c in ank) / len(ank)
        ar = max(((c.x - cx) ** 2 + (c.y - ay) ** 2) ** 0.5 for c in ank) + 0.010
    else:
        ay, ar = cyv, 0.062
    before = set(bm.faces)
    bmesh.ops.create_cone(bm, cap_ends=False, segments=8, radius1=ar + 0.008, radius2=ar,
                          depth=0.075, matrix=Matrix.Translation((cx, ay, 0.155)))
    for f in set(bm.faces) - before:
        newf.append((f, T1_DIRT))
# thigh cargo pockets (sides)
th = [v.co for v in me.vertices if 0.58 < v.co.z < 0.72]
mx = max(abs(c.x) for c in th) if th else 0.16
ymid = (sum(c.y for c in th) / len(th)) if th else -0.02
for sx in (-(mx + 0.008), mx + 0.008):
    M = Matrix.Translation((sx, ymid, 0.645)) @ Matrix.Diagonal((0.024, 0.095, 0.105, 1))
    before = set(bm.faces)
    bmesh.ops.create_cube(bm, size=1.0, matrix=M)
    for f in set(bm.faces) - before:
        newf.append((f, T1_PANTS))
    M = Matrix.Translation((sx, ymid, 0.706)) @ Matrix.Diagonal((0.028, 0.100, 0.022, 1))
    before = set(bm.faces)
    bmesh.ops.create_cube(bm, size=1.0, matrix=M)
    for f in set(bm.faces) - before:
        newf.append((f, T1_DIRT))
for f, hx in newf:
    c = W.hexv(hx)
    for lp in f.loops:
        lp[col] = c
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
bm.to_mesh(me); bm.free(); me.update()
W.transfer_weights(t1l, [L1L], only_new_from=N0)

# ============================================================
# finalize all six: triangulate/flat/mat/UV, report tris
# ============================================================
OUTS = [t0h, t0t, t0l, t1h, t1t, t1l]
for ob in OUTS:
    if ob.data.uv_layers:
        while ob.data.uv_layers:
            ob.data.uv_layers.remove(ob.data.uv_layers[0])
    W.finalize_mesh(ob)
    W.smart_uv(ob)
    unw = sum(1 for v in ob.data.vertices if not v.groups)
    print('BUILT %-22s tris=%4d verts=%4d unweighted=%d' % (
        ob.name, W.tri_count(ob), len(ob.data.vertices), unw))

for ob in OUTS + [rig]:
    W.assert_identity(ob)

# hide sources
for ob in (L1T, L1L, bpy.data.objects['L1_Head'], BH):
    ob.hide_render = True
    ob.hide_viewport = True

bpy.ops.wm.save_mainfile(filepath=W.WORKDIR + '_work/wearables_work.blend')
print('SAVED', W.WORKDIR + '_work/wearables_work.blend')

# ============================================================
# QC renders
# ============================================================
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
for label, trio in (('T0_set', [t0h, t0t, t0l]), ('T1_set', [t1h, t1t, t1l])):
    show_only(trio)
    for vn, vd in VIEWS.items():
        W.frame_and_shoot(trio, vd, QC + '%s_%s.png' % (label, vn), suns=suns)
print('QC DONE')
