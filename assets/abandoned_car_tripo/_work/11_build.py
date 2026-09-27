"""Car kit geometry from the oriented Tripo source (_work/car_src.blend, 10_prep.py).
Blender frame: nose +Y, left side -X, ground Z=0 (UE: nose -Y after the FBX Y-mirror).
Steps: shell -> drop the underbody (down-facing faces below FLOOR_Z, left open) ->
planar dissolve + collapse -> bisect the panel seams (measured on the Tripo texture,
_seams.py) on local faces -> split doors / hood / trunk / glass by region -> tail-lamp
faces flagged -> dark plugs for the openings + cabin floor -> mirrors kept (headlight
boxes, handles, wipers, rails dropped: they stay in the baked texture) -> our 10-sided
wheel. All parts live in ONE object 'Atlas' with a face attribute 'part' (for one UV
atlas + one bake, 12_bake.py splits it). Saves _work/car_parts.blend.
Run: blender.exe -b --factory-startup --python 11_build.py
"""
import bpy, bmesh, math, sys
from mathutils import Vector, Matrix
sys.path.insert(0, 'E:/game-dev-team/assets/abandoned_car_tripo/_work')
from carconst import *

bpy.ops.wm.open_mainfile(filepath=WORK + 'car_src.blend')
src = bpy.data.objects['Shell']
body = src.copy(); body.data = src.data.copy(); body.name = body.data.name = 'Atlas'
bpy.context.collection.objects.link(body)
for o in bpy.data.objects:
    if o is not body:
        o.hide_render = True
me = body.data


def tris(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)


# ---------- underbody ----------
bm = bmesh.new(); bm.from_mesh(me)
doomed = [f for f in bm.faces if f.normal.z < -0.3 and f.calc_center_median().z < FLOOR_Z]
bmesh.ops.delete(bm, geom=doomed, context='FACES')
bm.to_mesh(me); bm.free(); me.update()
print('UNDERBODY dropped %d down-facing faces (left open), tris now %d' % (len(doomed), tris(body)))

# ---------- decimate ----------
bpy.context.view_layer.objects.active = body
body.select_set(True)
md = body.modifiers.new('planar', 'DECIMATE'); md.decimate_type = 'DISSOLVE'
md.angle_limit = math.radians(4)
bpy.ops.object.modifier_apply(modifier=md.name)
bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.triangulate(bm, faces=bm.faces[:]); bm.to_mesh(me); bm.free()
if tris(body) > SHELL_TARGET:
    md = body.modifiers.new('col', 'DECIMATE'); md.ratio = SHELL_TARGET / tris(body)
    md.use_symmetry = True; md.symmetry_axis = 'X'
    bpy.ops.object.modifier_apply(modifier=md.name)
print('DECIMATED shell -> %d tris' % tris(body))

# mirrors join the body (Misc islands at z~1, |x|>0.6)
for o in [o for o in bpy.data.objects if o.name.startswith('Misc_') and o.type == 'MESH']:
    c = sum((v.co for v in o.data.vertices), Vector()) / len(o.data.vertices)
    if c.z > 0.9 and abs(c.x) > 0.6:
        bm = bmesh.new(); bm.from_mesh(me); bm.from_mesh(o.data); bm.to_mesh(me); bm.free()
        print('MIRROR joined', o.name, '%d faces' % len(o.data.polygons))

# ---------- seam cuts ----------
bm = bmesh.new(); bm.from_mesh(me)


def cut(co, no, sel):
    faces = [f for f in bm.faces if sel(f.calc_center_median(), f.normal)]
    if not faces:
        return 0
    geom = list({v for f in faces for v in f.verts}) + list({e for f in faces for e in f.edges}) + faces
    r = bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-4, plane_co=Vector(co), plane_no=Vector(no).normalized())
    return len([g for g in r['geom_cut'] if isinstance(g, bmesh.types.BMEdge)])


def slant(xb, xt, zb, zt, s):
    """Plane through the lines x=s*xb @ z=zb and x=s*xt @ z=zt (any y)."""
    d = Vector((s * (xt - xb), 0, zt - zb))
    return Vector((s * xb, 0, zb)), Vector((0, 1, 0)).cross(d)


ncut = 0
for s in (-1, 1):
    side = lambda c, n, s=s: c.x * s > 0.3 and n.x * s > 0.1 and 0.25 < c.z < 1.4 and -1.0 < c.y < 1.05
    for y in (DOOR_RY[0], DOOR_FY[0], DOOR_FY[1]):
        ncut += cut((0, y, 0), (0, 1, 0), side)
    for z in DOOR_Z:
        ncut += cut((0, 0, z), (0, 0, 1), side)
top = lambda c, n: c.z > 0.6 and n.z > 0.2
ncut += cut((0, HOOD_Y[0], 0), (0, 1, 0), lambda c, n: top(c, n) and 0.85 < c.y < 1.1 and abs(c.x) < 0.75)
ncut += cut((0, HOOD_Y[1], 0), (0, 1, 0), lambda c, n: top(c, n) and c.y > 1.8)
ncut += cut((0, TRUNK_Y[0], 0), (0, 1, 0), lambda c, n: top(c, n) and c.y < -1.85)
ncut += cut((0, TRUNK_Y[1], 0), (0, 1, 0), lambda c, n: top(c, n) and -1.55 < c.y < -1.3 and abs(c.x) < 0.75)
for s in (-1, 1):
    ncut += cut((s * HOOD_HX, 0, 0), (1, 0, 0), lambda c, n: top(c, n) and c.y > 0.9)
    ncut += cut((s * TRUNK_HX, 0, 0), (1, 0, 0), lambda c, n: top(c, n) and c.y < -1.35)
for G in (WS, RW):
    reg = lambda c, n, G=G: G['y'][0] < c.y < G['y'][1] and c.z > 0.85 and abs(c.x) < 0.72
    for z in G['z']:
        ncut += cut((0, 0, z), (0, 0, 1), reg)
    for s in (-1, 1):
        co, no = slant(G['x'][0], G['x'][1], G['z'][0], G['z'][1], s)
        ncut += cut(co, no, reg)
rear = lambda c, n: c.y < -1.85 and n.y < -0.4 and 0.45 < c.z < 0.85
for s in (-1, 1):
    for x in LAMP_X:
        ncut += cut((s * x, 0, 0), (1, 0, 0), rear)
for z in LAMP_Z:
    ncut += cut((0, 0, z), (0, 0, 1), rear)
bmesh.ops.triangulate(bm, faces=bm.faces[:])
print('CUTS: %d new edges, shell now %d tris' % (ncut, len(bm.faces)))

# ---------- assign parts ----------
pl = bm.faces.layers.int.new('part')
kl = bm.faces.layers.int.new('kind')


def in_glass(c, n, G, front):
    if not (G['y'][0] < c.y < G['y'][1] and G['z'][0] < c.z < G['z'][1] and n.z > 0.15):
        return False
    if (n.y > 0.15) != front:
        return False
    t = (c.z - G['z'][0]) / (G['z'][1] - G['z'][0])
    return abs(c.x) < G['x'][0] + t * (G['x'][1] - G['x'][0])


cnt = {}
for f in bm.faces:
    c, n = f.calc_center_median(), f.normal
    p = 'Body'
    for s, sl in ((-1, 'L'), (1, 'R')):
        if c.x * s > 0.55 and n.x * s > 0.5 and DOOR_Z[0] < c.z < DOOR_Z[1]:
            if DOOR_FY[0] < c.y < DOOR_FY[1]:
                p = 'Door_F' + sl
            elif DOOR_RY[0] < c.y < DOOR_RY[1]:
                p = 'Door_R' + sl
    if n.z > 0.35 and c.z > 0.7:
        if HOOD_Y[0] < c.y < HOOD_Y[1] and abs(c.x) < HOOD_HX:
            p = 'Hood'
        elif TRUNK_Y[0] < c.y < TRUNK_Y[1] and abs(c.x) < TRUNK_HX:
            p = 'Trunk'
    if in_glass(c, n, WS, True) or in_glass(c, n, RW, False):
        p = 'Glass'
    f[pl] = PID[p]
    f[kl] = KIND_LAMP if (p == 'Body' and c.y < -1.85 and n.y < -0.4 and LAMP_Z[0] < c.z < LAMP_Z[1]
                          and LAMP_X[0] < abs(c.x) < LAMP_X[1]) else KIND_PAINT
    cnt[p] = cnt.get(p, 0) + 1
    f.material_index = f[pl] * 3 + f[kl]
print('SPLIT', cnt, 'lamp faces', sum(1 for f in bm.faces if f[kl] == KIND_LAMP))
# the cuts also crossed faces that are not part borders: merge flat neighbours back
# (part+kind borders kept by material delimit) and re-triangulate
bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(DISSOLVE_DEG), use_dissolve_boundaries=False,
                         verts=bm.verts[:], edges=bm.edges[:], delimit={'MATERIAL'})
bmesh.ops.triangulate(bm, faces=bm.faces[:])
print('RE-DISSOLVE %.0f deg -> %d tris' % (DISSOLVE_DEG, len(bm.faces)))


# ---------- plugs, cabin floor, wheel ----------
def quad(pts, part, kind=KIND_DARK):
    vs = [bm.verts.new(p) for p in pts]
    f = bm.faces.new(vs)
    f[pl] = PID[part]; f[kl] = kind
    return f


def span(part_name):
    ps = [v.co for f in bm.faces if f[pl] == PID[part_name] for v in f.verts]
    return ps


def outline(pid):
    """Largest boundary loop (ordered verts) of the faces of one part."""
    fs = {f for f in bm.faces if f[pl] == pid and f[kl] != KIND_DARK}
    be = [e for e in {e for f in fs for e in f.edges} if sum(1 for g in e.link_faces if g in fs) == 1]
    nxt = {}
    for e in be:
        a, b = e.verts
        nxt.setdefault(a, []).append(b); nxt.setdefault(b, []).append(a)
    loops, seen = [], set()
    for v0 in nxt:
        if v0 in seen:
            continue
        loop, prev, v = [v0], None, v0
        seen.add(v0)
        while True:
            cand = [w for w in nxt[v] if w is not prev and w not in seen]
            if not cand:
                break
            prev, v = v, cand[0]
            seen.add(v); loop.append(v)
        loops.append(loop)
    return max(loops, key=len), fs


def plug(name, offset):
    """Dark copy of the panel outline, pushed inside by offset; faces outward like the panel."""
    loop, fs = outline(PID[name])
    pts = [v.co.copy() for v in loop]
    changed = True
    while changed and len(pts) > 4:          # drop nearly straight corners
        changed = False
        for i in range(len(pts)):
            a, b, c = pts[i - 1], pts[i], pts[(i + 1) % len(pts)]
            if (b - a).length < 1e-6 or (c - b).length < 1e-6 or (b - a).angle(c - b) < math.radians(PLUG_SIMPLE):
                pts.pop(i); changed = True
                break
    nrm = sum((f.normal * f.calc_area() for f in fs), Vector()).normalized()
    vs = [bm.verts.new(p + offset) for p in pts]
    f = bm.faces.new(vs)
    f.normal_update()
    if f.normal.dot(nrm) < 0:
        f.normal_flip()
    f[pl] = PID['Body']; f[kl] = KIND_DARK
    return len(pts)


plugs = 0
for s, sl in ((-1, 'L'), (1, 'R')):
    for dn in ('Door_F', 'Door_R'):
        plugs += plug(dn + sl, Vector((-s * PLUG_IN, 0, 0)))
for name in ('Hood', 'Trunk'):
    plugs += plug(name, Vector((0, 0, -PLUG_IN)))
# cabin floor seen through a broken windshield / rear window
quad([(-0.60, RW['y'][0], CABIN_Z), (0.60, RW['y'][0], CABIN_Z), (0.60, WS['y'][1] - 0.05, CABIN_Z),
      (-0.60, WS['y'][1] - 0.05, CABIN_Z)], 'Body')

# wheel: 10-sided, axis X, built at the Tripo wheel spot for the bake (12_bake moves it to 0)
ring = []
for sx in (-1, 1):
    ring.append([bm.verts.new(WHEEL_SRC + Vector((sx * WHEEL_HW, WHEEL_R * math.cos(WHEEL_A0 + 2 * math.pi * i / WHEEL_N),
                                                 WHEEL_R * math.sin(WHEEL_A0 + 2 * math.pi * i / WHEEL_N))))
                 for i in range(WHEEL_N)])
for i in range(WHEEL_N):
    j = (i + 1) % WHEEL_N
    f = bm.faces.new((ring[0][i], ring[0][j], ring[1][j], ring[1][i])); f[pl] = PID['Wheel']; f[kl] = KIND_PAINT
for k, r in enumerate(ring):
    f = bm.faces.new(r if k else r[::-1]); f[pl] = PID['Wheel']; f[kl] = KIND_PAINT
bmesh.ops.recalc_face_normals(bm, faces=[f for f in bm.faces if f[pl] == PID['Wheel']])
bmesh.ops.triangulate(bm, faces=bm.faces[:])
bm.to_mesh(me); bm.free(); me.update()
print('PLUGS %d outline verts; ATLAS total tris %d' % (plugs, tris(body)))
tot = {}
for p in me.polygons:
    n = PARTS[me.attributes['part'].data[p.index].value]
    tot[n] = tot.get(n, 0) + 1
print('TRIS per part', tot, 'assembled (4 wheels) =', sum(tot.values()) + 3 * tot['Wheel'])
for o in [o for o in bpy.data.objects if o is not body]:
    o.hide_render = False
bpy.ops.wm.save_as_mainfile(filepath=WORK + 'car_parts.blend')
print('SAVED', WORK + 'car_parts.blend')
