"""Build the trader NPC (kit "A": bandana + utility vest, ref TraiderReference/1.png,
prompts npc-elder-trader-prompts.md par.3) as 3 modular skinned meshes on the shared
21-bone RootAnim rig, from armor_wearables/_work/master.blend. Same pipeline as the
elder (10_build_elder.py). Rinat's order 07-12: cheaper than the elder — most of the
outfit is vertex paint; geometry only where the silhouette needs it:
  Head : bandana dome (flat, lower than the elder beanie) + back knot + 2 tails; eyes.
         Stubble/hair = paint only (no beard shell).
  Torso: NO vest tube — the vest is painted on the trunk; the 4 pocket boxes baked
         into base L1_Torso are KEPT and repainted as vest pouches (the elder dropped
         them); one back pocket cube added; the character-LEFT chest box gets the
         amber flap (top half + top face) = the one bright spot, visible top-down.
  Legs : cargo side-pocket cubes on the thighs + sole slabs; boots/pants/sweater-hem
         painted.
Palette: approved table in npc-elder-trader-prompts.md (ColdSteel/Concrete/#4A3826/
#C89A7A/AmberLoot #E0A32E); shade variants of the dominants are modeler's craft.
Outputs: _work/trader_work.blend + QC renders in _qc_trader/.
Run: blender.exe -b --factory-startup --python 10_build_trader.py
"""
import bpy, bmesh, sys, os, math
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W
from mathutils import Vector, Matrix

HERE = 'E:/game-dev-team/assets/npc_trader/'
QC = HERE + '_qc_trader/'
os.makedirs(QC, exist_ok=True)
os.makedirs(HERE + '_work', exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=W.WORKDIR + '_work/master.blend')
__import__('addon_utils').enable('io_scene_fbx')

rig = bpy.data.objects['RootAnim']
BH = bpy.data.objects['BaseHead']
L1T = bpy.data.objects['L1_Torso']
L1L = bpy.data.objects['L1_Legs']

# --- palette (approved trader column of npc-elder-trader-prompts.md) ---
SKIN = '#C89A7A'          # face + hands
STUBBLE = '#4A3826'       # approved stubble hex; doubles as the short dark hair
EYES = '#2B2823'
# 08-01 touch-up (game-lead order, match TraiderReference/1.png closer):
# bandana darker, vest de-blued to neutral grey, trousers olive -> grey.
BANDANA = '#3A3D42'       # dark bandana, near-black grey (ref key feature)
SWEATER = '#33302B'       # dark sweater: sleeves, collar, hem under the vest
VEST = '#606266'          # neutral grey utility vest (was ColdSteel #5A6470)
POCKET = '#515358'        # vest pouches: vest darkened a step for read
AMBER = '#E0A32E'         # AmberLoot — ONE small flap, the only bright spot
PANTS = '#717274'         # grey cargo trousers (was olive Concrete #6E6A60)
PANTS_PKT = '#616264'     # thigh patch pockets, a step darker than pants
BOOTS = '#2B2823'         # sturdy dark boots (approved dark-parts hex)
SOLE = '#1D1A17'

MAT = 'M_Trader_Flat'


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


def pocket_boxes(me):
    """The 4 chest/belly pocket boxes baked into base L1_Torso (same detector the
    elder used to DROP them — the trader keeps them as vest pouches)."""
    out = []
    for comp in islands(me):
        vs = set()
        for fi in comp:
            vs.update(me.polygons[fi].vertices)
        cos = [me.vertices[i].co for i in vs]
        mn = Vector((min(c.x for c in cos), min(c.y for c in cos), min(c.z for c in cos)))
        mx = Vector((max(c.x for c in cos), max(c.y for c in cos), max(c.z for c in cos)))
        if (3 <= len(comp) <= 80 and (mx - mn).length < 0.30 and mx.y < -0.02 and
                0.90 < mn.z and mx.z < 1.45 and mn.x > -0.30 and mx.x < 0.30):
            out.append((comp, mn, mx))
    return out


def paint_faces(bm, col, faces, hx):
    c = W.hexv(hx)
    for f in faces:
        for lp in f.loops:
            lp[col] = c


def new_faces(bm, before):
    return [f for f in bm.faces if f not in before]


def band_of(me, z, dz=0.05, xmax=0.30):
    vs = [v.co for v in me.vertices if abs(v.co.z - z) < dz and abs(v.co.x) < xmax]
    if not vs:
        return (0.20, 0.19, 0.18)
    return (max(abs(v.x) for v in vs), max(-v.y for v in vs), max(v.y for v in vs))


SHOE_HX = mode_hex(L1L, lambda c: c.z < 0.06)
print('SHOE_HX =', SHOE_HX)


def collar_zone(c):
    return c.z > 1.47 and (c.x * c.x + c.y * c.y) ** 0.5 < 0.14


# ============================================================
# HEAD — skin + painted dark hair/stubble + bandana dome + knot + tails + eyes
# ============================================================
th = dup(BH, 'SK_Trader_Head')


def rule_head(c, p, me):
    if c.z > 1.705:
        return BANDANA       # skull crown under the dome (poke-through guard)
    if c.y > 0.085 and c.z > 1.600:
        return STUBBLE       # nape hair below the bandana rim (true skull back
    if c.y > -0.020 and c.z > 1.655 and abs(c.x) > 0.100:
        return STUBBLE       # only; v2 painted the ears — ears stay skin)
    if c.z < 1.615 and c.y < 0.02:
        return STUBBLE       # moustache/chin stubble (paint only, no shell;
    if c.z < 1.585 and c.y < 0.10:
        return STUBBLE       # jaw wrap) — nose/cheeks stay skin (v1 read as a mask)
    return SKIN


W.paint_by_rule(th, rule_head)

# eyes: two tiny dark quads floating just off the face (same as the elder,
# 2 mm lower so the whole eye stays below the bandana rim at z=1.700)
me = th.data
n0 = len(me.vertices)
bm = bmesh.new(); bm.from_mesh(me)
c2 = bm.loops.layers.color.get('Col')
for sx in (-0.048, 0.048):
    near = [v.co.y for v in bm.verts
            if abs(v.co.x - sx) < 0.045 and 1.650 < v.co.z < 1.712]
    yf = (min(near) if near else -0.122) - 0.007
    vs = [bm.verts.new((sx - 0.012, yf, 1.686)), bm.verts.new((sx + 0.012, yf, 1.686)),
          bm.verts.new((sx + 0.012, yf, 1.700)), bm.verts.new((sx - 0.012, yf, 1.700))]
    f = bm.faces.new(vs)
    f.normal_update()
    if f.normal.y > 0:
        f.normal_flip()
    for lp in f.loops:
        lp[c2] = W.hexv(EYES)
bm.to_mesh(me); bm.free(); me.update()
W.transfer_weights(th, [BH], only_new_from=n0)

# --- bandana geometry: flat low dome + back knot + two hanging tails ---
me = th.data
N0 = len(me.vertices)
bm = bmesh.new(); bm.from_mesh(me)
col = bm.loops.layers.color.get('Col')

CY = 0.012                   # dome centre shifted back (skull bulges to +y)
N = 12
bandana = []


def ering(z, rx, ry):
    return [bm.verts.new((rx * math.cos(2 * math.pi * i / N),
                          CY + ry * math.sin(2 * math.pi * i / N), z)) for i in range(N)]


def eloft(a, b, out):
    for i in range(N):
        j = (i + 1) % N
        out.append(bm.faces.new([a[i], a[j], b[j], b[i]]))


# ring radii grounded on _inspect.log skull bands (z1.70 |x|.125 / z1.74 |x|.128
# y-.082..112 / z1.78 |x|.094, crown zmax 1.801); apex 1.830 << beanie 1.864
rim0 = ering(1.700, 0.145, 0.150)
r1 = ering(1.755, 0.140, 0.125)
r2 = ering(1.800, 0.105, 0.095)
eloft(rim0, r1, bandana)
eloft(r1, r2, bandana)
apex = bm.verts.new((0.0, CY, 1.830))
for i in range(N):
    j = (i + 1) % N
    bandana.append(bm.faces.new([r2[i], r2[j], apex]))

# knot at the nape: bulge tucked against the dome back. 08-01: enlarged —
# the 07-12 knot was so small the head read as a CAP, and the knot is THE
# feature separating bandana from cap in the reference back view.
before = set(bm.faces)
bmesh.ops.create_cube(bm, size=1.0,
                      matrix=Matrix.Translation((0.0, 0.158, 1.683)) @
                      Matrix.Rotation(math.radians(20), 4, 'X') @
                      Matrix.Diagonal((0.088, 0.060, 0.066, 1)))
bandana += new_faces(bm, before)

# two hanging tails under the knot (single-sided; material Two-Sided in UE).
# 08-01: lengthened to the collar line (~1.51) and widened at the bottom —
# the 07-12 stubs (7 cm) were invisible from the game camera. Sides differ
# on purpose so the back does not read mirror-stamped.
for pts in (((0.010, 0.172, 1.665), (0.052, 0.178, 1.652),
             (0.070, 0.208, 1.505), (0.022, 0.200, 1.518)),
            ((-0.010, 0.172, 1.665), (-0.050, 0.176, 1.655),
             (-0.062, 0.205, 1.522), (-0.018, 0.198, 1.535))):
    bandana.append(bm.faces.new([bm.verts.new(p) for p in pts]))
paint_faces(bm, col, bandana, BANDANA)

bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
bm.to_mesh(me); bm.free(); me.update()
W.transfer_weights(th, [BH], only_new_from=N0)

# ============================================================
# TORSO — dark sweater (paint) + ColdSteel vest (paint) + kept pouch boxes
#         + amber flap on the character-left chest box + back pocket cube
# ============================================================
tt = dup(L1T, 'SK_Trader_Torso')     # NO drop_front_boxes: pouches stay


def rule_torso(c, p, me):
    if abs(c.x) > 0.91:
        return SKIN          # bare hands (sleeves run to the wrist ring x=.891)
    if abs(c.x) > 0.30:
        return SWEATER       # full-length sweater sleeve
    if collar_zone(c):
        return SWEATER       # high sweater collar above the vest
    if c.z < 0.945:
        return SWEATER       # sweater hem showing under the vest
    return VEST              # zipped-up utility vest = the whole trunk


W.paint_by_rule(tt, rule_torso)

me = tt.data
boxes = pocket_boxes(me)
print('  kept pocket boxes: %d' % len(boxes))
# character-LEFT chest box (+x, chest z-band) gets the amber flap
amber_box = None
for comp, mn, mx in boxes:
    if mn.x > 0.04 and mn.z > 1.15:
        amber_box = (comp, mn, mx)
FLAP_Z = 1.288               # chest boxes span z 1.205..1.335 -> flap = top ~1/3

N0 = len(me.vertices)
bm = bmesh.new(); bm.from_mesh(me)
bm.faces.ensure_lookup_table()
col = bm.loops.layers.color.get('Col')
# 1) repaint all 4 kept boxes as pouches (indices valid before topology changes)
for comp, mn, mx in boxes:
    paint_faces(bm, col, [bm.faces[i] for i in comp], POCKET)
# 2) split the amber box at flap height, paint the cap amber (front+sides+top
#    face above FLAP_Z -> the "amber dot" reads from the top-down camera too)
if amber_box:
    comp, mn, mx = amber_box
    geom = set()
    for i in comp:
        f = bm.faces[i]
        geom.add(f)
        geom.update(f.verts)
        geom.update(f.edges)
    bmesh.ops.bisect_plane(bm, geom=list(geom),
                           plane_co=(0, 0, FLAP_Z), plane_no=(0, 0, 1))
    grow = 0.004
    for f in bm.faces:
        c = f.calc_center_median()
        if (mn.x - grow < c.x < mx.x + grow and mn.y - grow < c.y < mx.y + grow and
                FLAP_Z - 1e-4 < c.z < mx.z + grow):
            for lp in f.loops:
                lp[col] = W.hexv(AMBER)
else:
    print('  !! amber chest box NOT found — check detector')
# 3) big back pocket of the vest (ref back view), one shallow cube
before = set(bm.faces)
bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((0.0, 0.200, 1.245)) @
                      Matrix.Diagonal((0.21, 0.05, 0.17, 1)))
paint_faces(bm, col, new_faces(bm, before), POCKET)

bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
bm.to_mesh(me); bm.free(); me.update()
W.transfer_weights(tt, [L1T], only_new_from=N0)

# ============================================================
# LEGS — Concrete cargo trousers + high dark boots + thigh pockets + soles
# ============================================================
tl = dup(L1L, 'SK_Trader_Legs')


def rule_legs(c, p, me):
    h = face_hex(me, p)
    if h == SHOE_HX or c.z < 0.17:
        return BOOTS         # sturdy boots, taller shaft than the elder's (ref)
    if c.z > 0.873:
        return SWEATER       # sweater hem band across the module seam (no belt:
    return PANTS             # the vest covers the waist in the reference)


W.paint_by_rule(tl, rule_legs)

me = tl.data
N0 = len(me.vertices)
bm = bmesh.new(); bm.from_mesh(me)
col = bm.loops.layers.color.get('Col')
# cargo patch pockets on the outer thighs (thigh surface x~.245..252 per inspect)
pkts = []
for sgn in (1, -1):
    before = set(bm.faces)
    bmesh.ops.create_cube(bm, size=1.0,
                          matrix=Matrix.Translation((sgn * 0.262, -0.015, 0.635)) @
                          Matrix.Diagonal((0.050, 0.110, 0.160, 1)))
    pkts += new_faces(bm, before)
paint_faces(bm, col, pkts, PANTS_PKT)
# sole slabs under the shoe clusters (same as the elder)
soles = []
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
    hy_ = (max(ys) - min(ys)) / 2 + 0.004
    before = set(bm.faces)
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((cx, cyv, 0.012)) @
                          Matrix.Diagonal((hx_ * 2, hy_ * 2, 0.024, 1)))
    soles += new_faces(bm, before)
paint_faces(bm, col, soles, SOLE)

bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
bm.to_mesh(me); bm.free(); me.update()
W.transfer_weights(tl, [L1L], only_new_from=N0)

# ============================================================
# finalize + QC
# ============================================================
OUTS = [th, tt, tl]
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
bpy.ops.wm.save_mainfile(filepath=HERE + '_work/trader_work.blend')
print('SAVED', HERE + '_work/trader_work.blend')

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
    W.frame_and_shoot(OUTS, vd, QC + 'Trader_set_%s.png' % vn, suns=suns)
print('QC DONE')
