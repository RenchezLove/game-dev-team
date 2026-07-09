"""Build the village-elder NPC (kit "B": knit hat + vest, ref ElderRefecrence/1.png)
as 3 modular skinned meshes on the shared 21-bone RootAnim rig, from
armor_wearables/_work/master.blend. Same pipeline as the T0-T3 wearables:
duplicate the base body, repaint zones by vertex color, add silhouette geometry
via bmesh, transfer weights from the base body (KDTree), finalize + QC render.
Rinat's economy rule (T2/T3): geometry only for silhouette; the rest is vcol.

Outputs: _work/elder_work.blend + QC renders in _qc_elder/.
Run: blender.exe -b --factory-startup --python 10_build_elder.py
"""
import bpy, bmesh, sys, os, math
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W
from mathutils import Vector, Matrix

HERE = 'E:/game-dev-team/assets/npc_elder/'
QC = HERE + '_qc_elder/'
os.makedirs(QC, exist_ok=True)
os.makedirs(HERE + '_work', exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=W.WORKDIR + '_work/master.blend')
__import__('addon_utils').enable('io_scene_fbx')

rig = bpy.data.objects['RootAnim']
BH = bpy.data.objects['BaseHead']
L1T = bpy.data.objects['L1_Torso']
L1L = bpy.data.objects['L1_Legs']

# --- palette (ref 1.png + approved cs-palette table, npc-elder-trader-prompts.md) ---
SKIN = '#C89A7A'          # face + bare forearms/hands (approved skin)
GREY = '#ADA492'          # hair + beard (warm silver-grey per ref 1.png; the
#                           palette #9AA08C read cold/mint under QC light —
#                           modeler lays exact hex, ref sets warm silver beard)
EYES = '#2B2823'
HAT = '#6E4A2C'           # knit beanie (warm brown, darker than vest)
VEST = '#8A5A32'          # sleeveless vest (Timber, доминант верха)
SHIRT = '#B4A57F'         # beige shirt (body + collar + upper-arm sleeve)
SHIRT_FOLD = '#9E9070'    # rolled-cuff fold (a touch darker beige)
BELT = '#3A2A1D'          # dark leather belt
BUCKLE = '#3A3632'        # belt buckle / buttons (dark)
PANTS = '#48453F'         # dark warm-grey work trousers
BOOTS = '#5A3E28'         # brown boots
SOLE = '#33291E'          # boot sole (darkest brown)

MAT = 'M_Elder_Flat'


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


def mode_hex(ob, flt):
    cnt = {}
    for p in ob.data.polygons:
        if flt(Vector(p.center)):
            h = face_hex(ob.data, p)
            cnt[h] = cnt.get(h, 0) + 1
    return max(cnt.items(), key=lambda kv: kv[1])[0] if cnt else None


def band_of(me, z, dz=0.05, xmax=0.30):
    vs = [v.co for v in me.vertices if abs(v.co.z - z) < dz and abs(v.co.x) < xmax]
    if not vs:
        return (0.20, 0.19, 0.18)
    return (max(abs(v.x) for v in vs), max(-v.y for v in vs), max(v.y for v in vs))


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
    """Remove the 4 chest pocket boxes baked into the base L1_Torso (small front
    islands) — same cleanup the T1/T2/T3 builders do before adding their shell."""
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
    print('  dropped %d pocket-box faces' % len(kill))


SHOE_HX = mode_hex(L1L, lambda c: c.z < 0.06)
print('SHOE_HX =', SHOE_HX)


def collar_zone(c):
    return c.z > 1.47 and (c.x * c.x + c.y * c.y) ** 0.5 < 0.14


def hair_zone(c):
    if c.z > 1.755 and c.y > -0.075:
        return True                      # crown (under the hat)
    if c.y > 0.045 and c.z > 1.60:
        return True                      # back of skull (fringe below rim)
    if c.y > -0.055 and c.z > 1.665 and abs(c.x) > 0.095:
        return True                      # sides above ears
    return False


def beard_zone(c):
    """Full beard: lower face below eye level — cheeks/jaw/chin/moustache.
    Front+cheeks to y<0.06; lower jaw wraps toward the ears (y<0.11).
    The back of the skull above is caught by hair_zone."""
    if c.z <= 1.500:
        return False
    if c.z < 1.665 and c.y < 0.06:
        return True
    if c.z < 1.635 and c.y < 0.13:       # jaw sides wrap toward/over the ears
        return True
    return False


def paint_faces(bm, col, faces, hx):
    c = W.hexv(hx)
    for f in faces:
        for lp in f.loops:
            lp[col] = c


def new_faces(bm, before):
    return [f for f in bm.faces if f not in before]


# ============================================================
# HEAD — base head painted (skin + grey hair + grey beard + eyes)
#        + grey beard shell + brown knit beanie (no visor)
# ============================================================
eh = dup(BH, 'SK_Elder_Head')


def rule_head(c, p, me):
    if beard_zone(c):
        return GREY
    if hair_zone(c):
        return GREY
    return SKIN


W.paint_by_rule(eh, rule_head)

# eyes: two tiny dark quads floating just off the face (base facets too coarse)
me = eh.data
n0 = len(me.vertices)
bm = bmesh.new(); bm.from_mesh(me)
c2 = bm.loops.layers.color.get('Col')
for sx in (-0.048, 0.048):
    near = [v.co.y for v in bm.verts
            if abs(v.co.x - sx) < 0.045 and 1.655 < v.co.z < 1.715]
    yf = (min(near) if near else -0.122) - 0.007
    vs = [bm.verts.new((sx - 0.012, yf, 1.688)), bm.verts.new((sx + 0.012, yf, 1.688)),
          bm.verts.new((sx + 0.012, yf, 1.702)), bm.verts.new((sx - 0.012, yf, 1.702))]
    f = bm.faces.new(vs)
    f.normal_update()
    if f.normal.y > 0:
        f.normal_flip()
    for lp in f.loops:
        lp[c2] = W.hexv(EYES)
bm.to_mesh(me); bm.free(); me.update()
W.transfer_weights(eh, [BH], only_new_from=n0)

# --- beard shell + beanie geometry ---
me = eh.data
N0 = len(me.vertices)
bm = bmesh.new(); bm.from_mesh(me)
col = bm.loops.layers.color.get('Col')

# beard: front-hemisphere lofted cup (top arc on face -> bulged mid -> chin tip).
# Single-surface appliqué (material Two-Sided in UE, like the scarf/chin-strap).
beard = []
top = [(0.120, 0.010, 1.665), (0.108, -0.050, 1.640), (0.078, -0.098, 1.605),
       (0.040, -0.120, 1.612), (0.000, -0.128, 1.620), (-0.040, -0.120, 1.612),
       (-0.078, -0.098, 1.605), (-0.108, -0.050, 1.640), (-0.120, 0.010, 1.665)]
mid = [(0.112, -0.020, 1.588), (0.100, -0.082, 1.560), (0.072, -0.124, 1.545),
       (0.038, -0.152, 1.548), (0.000, -0.164, 1.552), (-0.038, -0.152, 1.548),
       (-0.072, -0.124, 1.545), (-0.100, -0.082, 1.560), (-0.112, -0.020, 1.588)]
tip = bm.verts.new((0.000, -0.124, 1.520))          # beard hangs below the chin
tv = [bm.verts.new(p) for p in top]
mv = [bm.verts.new(p) for p in mid]
for i in range(len(top) - 1):
    beard.append(bm.faces.new([tv[i], tv[i + 1], mv[i + 1], mv[i]]))   # upper bulge
for i in range(len(mid) - 1):
    beard.append(bm.faces.new([mv[i], mv[i + 1], tip]))                # to the tip
paint_faces(bm, col, beard, GREY)

# beanie: low round dome + folded cuff (bulged band), no visor
CY = -0.006
beanie = []
N = 14


def ering(z, rx, ry):
    return [bm.verts.new((rx * math.cos(2 * math.pi * i / N),
                          CY + ry * math.sin(2 * math.pi * i / N), z)) for i in range(N)]


def eloft(a, b, out):
    for i in range(N):
        j = (i + 1) % N
        out.append(bm.faces.new([a[i], a[j], b[j], b[i]]))


rim0 = ering(1.700, 0.150, 0.160)   # cuff bottom (above brows/ears, clears eyes 1.69)
rim1 = ering(1.744, 0.155, 0.165)   # cuff top: slightly bulged = folded knit cuff
dom0 = ering(1.744, 0.148, 0.158)   # dome base, stepped in behind the cuff (crease)
dom1 = ering(1.792, 0.120, 0.128)
dom2 = ering(1.836, 0.072, 0.078)
eloft(rim0, rim1, beanie)           # cuff band
eloft(rim1, dom0, beanie)           # crease lip
eloft(dom0, dom1, beanie)
eloft(dom1, dom2, beanie)
apex = bm.verts.new((0.0, CY, 1.864))
for i in range(N):
    j = (i + 1) % N
    beanie.append(bm.faces.new([dom2[i], dom2[j], apex]))
paint_faces(bm, col, beanie, HAT)

bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
bm.to_mesh(me); bm.free(); me.update()
W.transfer_weights(eh, [BH], only_new_from=N0)

# ============================================================
# TORSO — beige shirt (rolled sleeves, bare forearms) + brown vest + buttons
# ============================================================
et = dup(L1T, 'SK_Elder_Torso')
drop_front_boxes(et)         # remove the base torso's 4 chest pocket boxes


def rule_torso(c, p, me):
    # Trunk under the vest is painted VEST brown so any body poke-through is
    # invisible; beige shirt is left only where it actually shows: bare-arm
    # sleeves, the standing collar, and the front V-neck opening.
    if abs(c.x) > 0.60:
        return SKIN          # bare forearm + hand (sleeves rolled to the elbow)
    if abs(c.x) > 0.30:
        return SHIRT         # upper-arm shirt sleeve
    if collar_zone(c):
        return SHIRT         # shirt collar
    if c.y < 0.0 and abs(c.x) < 0.12 and c.z > 1.28:
        return SHIRT         # shirt visible in the front V-neck opening
    return VEST              # trunk under the vest -> brown (seamless)


W.paint_by_rule(et, rule_torso)

me = et.data
N0 = len(me.vertices)
bm = bmesh.new(); bm.from_mesh(me)
col = bm.loops.layers.color.get('Col')

# rolled-cuff fold ring at each elbow (|x| ~ 0.58), slightly darker beige
folds = []
for sgn in (1, -1):
    vs = [v.co for v in me.vertices if 0.52 < v.co.x * sgn < 0.64]
    if not vs:
        continue
    cyv = sum(v.y for v in vs) / len(vs)
    czv = sum(v.z for v in vs) / len(vs)
    rr = max(((v.y - cyv) ** 2 + (v.z - czv) ** 2) ** 0.5 for v in vs) + 0.010
    before = set(bm.faces)
    bmesh.ops.create_cone(bm, cap_ends=False, segments=8, radius1=rr, radius2=rr,
                          depth=0.055, matrix=Matrix.Translation((sgn * 0.58, cyv, czv)) @
                          Matrix.Rotation(math.pi / 2, 4, 'Y'))
    folds += new_faces(bm, before)
paint_faces(bm, col, folds, SHIRT_FOLD)

# sleeveless vest tube around the trunk (front V-neck opening reveals shirt).
# Rings sampled from the REAL body band (xmax=0.24 excludes the arms) + offset
# outward -> the tube always encloses the trunk, no shirt poke-through.
NP = 16
OFF = 0.040
vest_zs = [0.90, 1.02, 1.14, 1.25, 1.35, 1.42, 1.48]
vest_rings_z = []
for z in vest_zs:
    a, fb, bb = band_of(me, z, xmax=0.24)
    a = max(a, fb, bb)                      # torso ~circular; avoid a<depth pinch
    vest_rings_z.append((z, a + OFF, fb + OFF, bb + OFF))


def vest_gap(z):
    # narrow, high V-neck: vest brown dominates, slim beige shirt/collar shows
    pts = [(1.28, 0.0), (1.36, 0.038), (1.44, 0.055), (1.48, 0.060)]
    if z <= pts[0][0]:
        return 0.0
    for (z0, w0), (z1, w1) in zip(pts, pts[1:]):
        if z <= z1:
            return w0 + (w1 - w0) * (z - z0) / (z1 - z0)
    return pts[-1][1]


ring_pts = []
for (z, a, fb, bb) in vest_rings_z:
    w = vest_gap(z)
    gap = math.asin(min(0.9, w / a)) if w > 1e-6 else 0.0
    pts = []
    for i in range(NP):
        th = gap + (2 * math.pi - 2 * gap) * i / (NP - 1)
        x = a * math.sin(th)
        cy = math.cos(th)
        y = -fb * cy if cy > 0 else -bb * cy
        pts.append(bm.verts.new((x, y, z)))
    ring_pts.append(pts)
vest = []
for k in range(len(ring_pts) - 1):
    A, B = ring_pts[k], ring_pts[k + 1]
    for i in range(NP - 1):
        vest.append(bm.faces.new([A[i], A[i + 1], B[i + 1], B[i]]))
# inner lips along the front V edges (so the opening reads as a lapel, not a hole)
for side in (0, NP - 1):
    prev = None
    for k, pts in enumerate(ring_pts):
        if vest_gap(vest_rings_z[k][0]) <= 1e-6:
            prev = None
            continue
        p = pts[side]
        q = bm.verts.new((p.co.x * 0.80, p.co.y * 0.80, p.co.z))
        if prev is not None:
            vest.append(bm.faces.new([prev[0], p, q, prev[1]]))
        prev = (p, q)
paint_faces(bm, col, vest, VEST)

# 3 buttons down the closed front placket (below the V point), proud of the vest
buttons = []
for cz in (1.00, 1.09, 1.17):
    a, fb, bb = band_of(me, cz, xmax=0.24)
    before = set(bm.faces)
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((0.0, -(fb + OFF + 0.006), cz)) @
                          Matrix.Diagonal((0.024, 0.020, 0.024, 1)))
    buttons += new_faces(bm, before)
paint_faces(bm, col, buttons, BUCKLE)

bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
bm.to_mesh(me); bm.free(); me.update()
W.transfer_weights(et, [L1T], only_new_from=N0)

# ============================================================
# LEGS — dark-grey trousers + brown boots + dark belt (buckle)
# ============================================================
el = dup(L1L, 'SK_Elder_Legs')


def rule_legs(c, p, me):
    h = face_hex(me, p)
    if h == SHOE_HX or c.z < 0.14:
        return BOOTS         # boots (foot + low ankle; trouser hem drapes above)
    if c.z > 0.873:
        return BELT
    return PANTS


W.paint_by_rule(el, rule_legs)

me = el.data
N0 = len(me.vertices)
bm = bmesh.new(); bm.from_mesh(me)
col = bm.loops.layers.color.get('Col')
soles, buckle = [], []
shoe_l = [Vector(p.center) for p in L1L.data.polygons
          if face_hex(L1L.data, p) == SHOE_HX and p.center[0] > 0]
shoe_r = [Vector(p.center) for p in L1L.data.polygons
          if face_hex(L1L.data, p) == SHOE_HX and p.center[0] < 0]
for cluster in (shoe_l, shoe_r):
    if not cluster:
        continue
    xs = [c.x for c in cluster]; ys = [c.y for c in cluster]
    cx = (min(xs) + max(xs)) / 2; cyv = (min(ys) + max(ys)) / 2
    hx_ = (max(xs) - min(xs)) / 2 + 0.006
    hy_ = (max(ys) - min(ys)) / 2 + 0.004        # tight to the foot, no ski plate
    before = set(bm.faces)
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((cx, cyv, 0.012)) @
                          Matrix.Diagonal((hx_ * 2, hy_ * 2, 0.024, 1)))
    soles += new_faces(bm, before)
paint_faces(bm, col, soles, SOLE)
# belt buckle at front center
before = set(bm.faces)
a, fb, bb = band_of(me, 0.89, xmax=0.26)
bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((0.0, -(fb + 0.012), 0.888)) @
                      Matrix.Diagonal((0.050, 0.020, 0.038, 1)))
buckle += new_faces(bm, before)
paint_faces(bm, col, buckle, BUCKLE)

bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
bm.to_mesh(me); bm.free(); me.update()
W.transfer_weights(el, [L1L], only_new_from=N0)

# ============================================================
# finalize + QC
# ============================================================
OUTS = [eh, et, el]
for ob in OUTS:
    while ob.data.uv_layers:
        ob.data.uv_layers.remove(ob.data.uv_layers[0])
    W.finalize_mesh(ob, mat_name=MAT)
    unw = sum(1 for v in ob.data.vertices if not v.groups)
    print('BUILT %-20s tris=%4d verts=%4d unweighted=%d' % (
        ob.name, W.tri_count(ob), len(ob.data.vertices), unw))
for ob in OUTS + [rig]:
    W.assert_identity(ob)
for ob in (L1T, L1L, bpy.data.objects['L1_Head'], BH):
    ob.hide_render = True
    ob.hide_viewport = True
bpy.ops.wm.save_mainfile(filepath=HERE + '_work/elder_work.blend')
print('SAVED', HERE + '_work/elder_work.blend')

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
show_only(OUTS)
for vn, vd in VIEWS.items():
    W.frame_and_shoot(OUTS, vd, QC + 'Elder_set_%s.png' % vn, suns=suns)
print('QC DONE')
