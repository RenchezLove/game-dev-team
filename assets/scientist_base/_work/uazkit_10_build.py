"""SM_UAZ452 as a kit of parts (the contract of assets/abandoned_car_tripo): Body, Door_FL, Door_FR, Door_Side, RearDoor_L, RearDoor_R, Glass, Wheel.
Same source, same size and place as the one-piece SM_UAZ452 (the first half of uaz_10_build.py is run as it is).  Blender frame: nose +Y,
left side -X; Unreal = (x*100, -y*100, z*100).  Every door has its origin on its hinge line, the wheel in the middle of its axle.
One colour texture RGBA for all parts: A = paint mask (1 = body paint, painted neutral light grey; the material multiplies it by BodyColor).
Run: blender.exe -b --factory-startup --python uazkit_10_build.py
"""
import bpy, bmesh, sys, math, os, json
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0, 'E:/game-dev-team/assets/scientist_base/_work')
import sb

# ---- the source, sorted, scaled and turned exactly as for the one-piece model
_txt = open(sb.WORK + 'uaz_10_build.py', encoding='utf-8').read()
exec(_txt[:_txt.index('# ---- low mesh')])
OUT = sb.ROOT + 'SM_UAZ452_kit/'; os.makedirs(OUT, exist_ok=True)
LIMIT = 1293; TEX = 1024
PARTS = ['Body', 'Door_FL', 'Door_FR', 'Door_Side', 'RearDoor_L', 'RearDoor_R', 'Glass', 'Wheel']
PID = {n: i for i, n in enumerate(PARTS)}
# seams read off the orthographic pictures of the source (_look/uazkit_*.png, 400 px per metre)
SIDE = dict(y=(-0.62, 0.36), z=(0.82, 1.88))         # passenger door of the right side (+X), hinge at its front edge
REAR = dict(x=0.70, z=(0.80, 1.88))                  # two leaves of the rear door, hinges at the outer edges
PLUG_IN = 0.07
NS = 10

# ---- pieces of sheet metal
sheet = src.copy(); sheet.data = src.data.copy(); sheet.name = 'sheet'; bpy.context.scene.collection.objects.link(sheet)
bm = sb.bm_of(sheet); kl = bm.faces.layers.int['kind']; pl = bm.faces.layers.int.new('pid'); nl = bm.faces.layers.int.new('nopaint')
bmesh.ops.delete(bm, geom=[f for f in bm.faces if f[kl] not in (1, 2, 4)], context='FACES')
bm.faces.ensure_lookup_table(); bm.faces.index_update()
for comp in sb.islands(bm):
    c = np.array([f.calc_center_median()[:] for f in comp]).mean(0); n = len(comp); k_ = comp[0][kl]
    if k_ == 1 and n == 136:
        pid = PID['Door_FL'] if c[0] < 0 else PID['Door_FR']
    elif k_ == 2:
        if c[1] < -1.9:
            pid = PID['RearDoor_L'] if c[0] < 0 else PID['RearDoor_R']
        elif abs(c[0]) > 0.6 and c[1] > 0.7:
            pid = PID['Door_FL'] if c[0] < 0 else PID['Door_FR']
        elif c[0] > 0.6:
            pid = PID['Door_Side']
        else:
            pid = PID['Glass']
        print('GLASS pane centre %s -> %s' % (c.round(2), PARTS[pid]))
    else:
        pid = PID['Body']
    for f in comp:
        f[pl] = pid; f[nl] = 0 if k_ == 1 else (2 if k_ == 2 else 1)
# shell and roof become one skin; the floor goes
shell_f = [f for f in bm.faces if f[pl] == PID['Body'] and f[kl] == 1]
bmesh.ops.remove_doubles(bm, verts=list({v for f in shell_f for v in f.verts}), dist=0.0005)
bm.normal_update()
shell_f = [f for f in bm.faces if f[pl] == PID['Body'] and f[kl] == 1]
zfloor = min(v.co.z for f in shell_f for v in f.verts)
floor = [f for f in shell_f if f.normal.z < -0.9 and f.calc_center_median().z < zfloor + 0.12]
bmesh.ops.delete(bm, geom=floor, context='FACES')

def cut(sel, plane_co, plane_no):
    faces = [f for f in bm.faces if f.is_valid and sel(f)]
    geom = list({e for f in faces for e in f.edges}) + list({v for f in faces for v in f.verts}) + faces
    bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=plane_co, plane_no=plane_no)
def zr(f):
    z = [v.co.z for v in f.verts]; return min(z), max(z)
def yr(f):
    y = [v.co.y for v in f.verts]; return min(y), max(y)
def xr(f):
    x = [v.co.x for v in f.verts]; return min(x), max(x)
is_shell = lambda f: f[pl] == PID['Body'] and f[kl] == 1
right = lambda f: is_shell(f) and f.calc_center_median().x > 0.5 and f.normal.x > 0.3
rear = lambda f: is_shell(f) and f.calc_center_median().y < -1.8 and f.normal.y < -0.3
M = 0.02
for y in SIDE['y']:
    cut(lambda f: right(f) and zr(f)[1] > SIDE['z'][0] - M and zr(f)[0] < SIDE['z'][1] + M, (0, y, 0), (0, 1, 0))
for z in SIDE['z']:
    cut(lambda f: right(f) and yr(f)[1] > SIDE['y'][0] - M and yr(f)[0] < SIDE['y'][1] + M, (0, 0, z), (0, 0, 1))
for x in (-REAR['x'], 0.0, REAR['x']):
    cut(lambda f: rear(f) and zr(f)[1] > REAR['z'][0] - M and zr(f)[0] < REAR['z'][1] + M, (x, 0, 0), (1, 0, 0))
for z in REAR['z']:
    cut(lambda f: rear(f) and xr(f)[1] > -REAR['x'] - M and xr(f)[0] < REAR['x'] + M, (0, 0, z), (0, 0, 1))
bm.normal_update()
E = 1e-4
ns = nr_ = 0
for f in bm.faces:
    if not is_shell(f):
        continue
    c = f.calc_center_median()
    if right(f) and SIDE['y'][0] - E < yr(f)[0] and yr(f)[1] < SIDE['y'][1] + E and SIDE['z'][0] - E < zr(f)[0] and zr(f)[1] < SIDE['z'][1] + E:
        f[pl] = PID['Door_Side']; ns += 1
    elif rear(f) and -REAR['x'] - E < xr(f)[0] and xr(f)[1] < REAR['x'] + E and REAR['z'][0] - E < zr(f)[0] and zr(f)[1] < REAR['z'][1] + E:
        f[pl] = PID['RearDoor_L'] if c.x < 0 else PID['RearDoor_R']; nr_ += 1
print('CUT side door faces %d, rear door faces %d' % (ns, nr_))
bmesh.ops.triangulate(bm, faces=bm.faces)
bm.to_mesh(sheet.data); bm.free()

def piece(pid_, only_kind=None):
    o = sheet.copy(); o.data = sheet.data.copy(); o.name = 'p_' + PARTS[pid_] + ('' if only_kind is None else '_k%d' % only_kind)
    bpy.context.scene.collection.objects.link(o)
    b = sb.bm_of(o); p_ = b.faces.layers.int['pid']; k__ = b.faces.layers.int['kind']
    bmesh.ops.delete(b, geom=[f for f in b.faces if f[p_] != pid_ or (only_kind is not None and f[k__] != only_kind) or (only_kind is None and f[k__] == 1)], context='FACES')
    b.to_mesh(o.data); b.free()
    return o
skins = {n: piece(PID[n], 1) for n in PARTS[:6]}          # sheet metal of the body and of the five doors
fixed = {n: piece(PID[n]) for n in PARTS[:7]}             # glass panes and bumpers: kept as they are
for n, o in skins.items():
    b = sb.bm_of(o); bmesh.ops.remove_doubles(b, verts=b.verts, dist=0.0005); b.to_mesh(o.data); b.free()
# seam points must not move in the decimation: the outline of the cut doors and the same points on the body
seam = []
for n in ('Door_Side', 'RearDoor_L', 'RearDoor_R'):
    b = sb.bm_of(skins[n]); seam += [v.co.copy() for e in b.edges if len(e.link_faces) == 1 for v in e.verts]; b.free()
from mathutils.kdtree import KDTree
kd = KDTree(len(seam))
for i, p in enumerate(seam):
    kd.insert(p, i)
kd.balance()
for n, o in skins.items():
    vg = o.vertex_groups.new(name='dec'); keep = 0
    for v in o.data.vertices:
        on = kd.find(v.co)[2] < 1e-4
        vg.add([v.index], 0.0 if on else 1.0, 'REPLACE'); keep += on
    print('SKIN %-11s tris %4d, seam points kept still %d' % (n, sb.tri_count(o), keep))

# ---- rebuilt parts
def boxmesh(bm, lo, hi, pid_, nop=1, skip=()):
    vs = [bm.verts.new((x, y, z)) for z in (lo[2], hi[2]) for y in (lo[1], hi[1]) for x in (lo[0], hi[0])]
    faces = {'bottom': (0, 1, 3, 2), 'top': (4, 5, 7, 6), 'ylo': (0, 1, 5, 4), 'yhi': (2, 3, 7, 6), 'xlo': (0, 2, 6, 4), 'xhi': (1, 3, 7, 5)}
    for nm, q in faces.items():
        if nm not in skip:
            f = bm.faces.new([vs[i] for i in q]); f[bm.faces.layers.int['pid']] = pid_; f[bm.faces.layers.int['nopaint']] = nop
bm = bmesh.new(); pl = bm.faces.layers.int.new('pid'); nl = bm.faces.layers.int.new('nopaint'); tagl = bm.faces.layers.int.new('tag')
WC = []
for mn_, mx_ in wheels:
    a, b = tf(mn_)[0], tf(mx_)[0]; lo = np.minimum(a, b); hi = np.maximum(a, b); WC.append(((lo + hi) / 2, (hi - lo) / 2))
WC.sort(key=lambda w: (-round(float(w[0][1]), 1), w[0][0]))            # front left, front right, rear left, rear right
wc, wr = WC[0]                                        # the wheel is built (and baked) in the place of the front left one
wheel_r = float(wr[2]); wheel_hw = float(wr[0])            # round wheel that stands on the ground
ring = [[bm.verts.new((wc[0] + sx_ * wheel_hw, wc[1] + wheel_r * math.cos(2 * math.pi * (k_ + 0.5) / NS), wc[2] + wheel_r * math.sin(2 * math.pi * (k_ + 0.5) / NS))) for k_ in range(NS)] for sx_ in (1, -1)]
for k_ in range(NS):
    f = bm.faces.new((ring[0][k_], ring[0][(k_ + 1) % NS], ring[1][(k_ + 1) % NS], ring[1][k_])); f[pl] = PID['Wheel']; f[nl] = 1
for r_ in ring:
    f = bm.faces.new(r_); f[pl] = PID['Wheel']; f[nl] = 1
for kind, mn_, mx_ in boxes:
    a, b = tf(mn_)[0], tf(mx_)[0]; lo = np.minimum(a, b); hi = np.maximum(a, b)
    if kind == 'step':
        boxmesh(bm, lo, hi, PID['Body'])
    else:                                              # a mirror with its arm belongs to its front door
        pid_ = PID['Door_FL'] if lo[0] < 0 else PID['Door_FR']
        n0 = len(bm.faces); boxmesh(bm, lo, hi, pid_)
        sgn = 1.0 if lo[0] > 0 else -1.0
        xa, xb = sgn * 0.74, (lo[0] if sgn > 0 else hi[0]); ym = (lo[1] + hi[1]) / 2; zm = lo[2] + 0.25 * (hi[2] - lo[2]); h = 0.016
        r = [[bm.verts.new((x, ym + dy, zm + dz)) for dy, dz in ((-h, -h), (h, -h), (h, h), (-h, h))] for x in (xa, xb)]
        for k_ in range(4):
            f = bm.faces.new((r[0][k_], r[0][(k_ + 1) % 4], r[1][(k_ + 1) % 4], r[1][k_])); f[pl] = pid_; f[nl] = 1
        bm.faces.ensure_lookup_table()
        for f in bm.faces[n0:]:
            f[tagl] = 1
# dark plugs behind the five doors and a dark cabin floor (two-sided material: no cabin is modelled)
HINGE = {}
def skin_co(n):
    return sb.coords(skins[n])
for n in ('Door_FL', 'Door_FR'):
    c = skin_co(n); sgn = -1.0 if n.endswith('L') else 1.0
    z0, z1 = c[:, 2].min(), c[:, 2].max(); y0 = c[:, 1].min()
    lowp = c[c[:, 2] < z0 + 0.35]; top = c[c[:, 2] > z1 - 0.12]
    yfb = lowp[:, 1].max(); yft = top[:, 1].max()
    xb = np.abs(lowp[:, 0]).max(); xt = np.abs(top[:, 0]).min()
    HINGE[n] = Vector((sgn * float(np.abs(lowp[lowp[:, 1] > yfb - 0.08][:, 0]).max()), float(yfb), float(z0)))
    q = [(sgn * (xb - PLUG_IN), y0 + 0.03, z0 + 0.03), (sgn * (xb - PLUG_IN), yfb - 0.06, z0 + 0.03), (sgn * (xt - PLUG_IN), yft - 0.06, z1 - 0.03), (sgn * (xt - PLUG_IN), y0 + 0.03, z1 - 0.03)]
    f = bm.faces.new([bm.verts.new(p) for p in q]); f[pl] = PID['Body']; f[nl] = 3
    print('DOOR %s y %.3f..%.3f (front edge: bottom %.3f, top %.3f) z %.3f..%.3f, side x bottom %.3f top %.3f' % (n, y0, c[:, 1].max(), yfb, yft, z0, z1, xb, xt))
c = skin_co('Door_Side'); lowp = c[c[:, 2] < SIDE['z'][0] + 0.2]; top = c[c[:, 2] > SIDE['z'][1] - 0.1]
front = c[c[:, 1] > SIDE['y'][1] - 0.02]
HINGE['Door_Side'] = Vector((float(front[front[:, 2] < SIDE['z'][0] + 0.3][:, 0].max()), SIDE['y'][1], SIDE['z'][0]))
q = [(lowp[:, 0].max() - PLUG_IN, SIDE['y'][0] + 0.03, SIDE['z'][0] + 0.03), (lowp[:, 0].max() - PLUG_IN, SIDE['y'][1] - 0.03, SIDE['z'][0] + 0.03),
     (top[:, 0].min() - PLUG_IN, SIDE['y'][1] - 0.03, SIDE['z'][1] - 0.03), (top[:, 0].min() - PLUG_IN, SIDE['y'][0] + 0.03, SIDE['z'][1] - 0.03)]
f = bm.faces.new([bm.verts.new(p) for p in q]); f[pl] = PID['Body']; f[nl] = 3
cl = skin_co('RearDoor_L'); cr = skin_co('RearDoor_R'); call = np.concatenate([cl, cr])
lowp = call[call[:, 2] < REAR['z'][0] + 0.2]; top = call[call[:, 2] > REAR['z'][1] - 0.1]
for n, c_, sgn in (('RearDoor_L', cl, -1.0), ('RearDoor_R', cr, 1.0)):
    edge = c_[np.abs(c_[:, 0]) > REAR['x'] - 0.02]
    HINGE[n] = Vector((sgn * REAR['x'], float(edge[edge[:, 2] < REAR['z'][0] + 0.3][:, 1].min()), REAR['z'][0]))
q = [(-REAR['x'] + 0.03, lowp[:, 1].min() + PLUG_IN, REAR['z'][0] + 0.03), (REAR['x'] - 0.03, lowp[:, 1].min() + PLUG_IN, REAR['z'][0] + 0.03),
     (REAR['x'] - 0.03, top[:, 1].max() + PLUG_IN, REAR['z'][1] - 0.03), (-REAR['x'] + 0.03, top[:, 1].max() + PLUG_IN, REAR['z'][1] - 0.03)]
f = bm.faces.new([bm.verts.new(p) for p in q]); f[pl] = PID['Body']; f[nl] = 3
bc = skin_co('Body'); fz = SIDE['z'][0] - 0.02
q = [(-0.80, bc[:, 1].min() + 0.12, fz), (0.80, bc[:, 1].min() + 0.12, fz), (0.80, bc[:, 1].max() - 0.45, fz), (-0.80, bc[:, 1].max() - 0.45, fz)]
f = bm.faces.new([bm.verts.new(p) for p in q]); f[pl] = PID['Body']; f[nl] = 3
bmesh.ops.triangulate(bm, faces=bm.faces)
me = bpy.data.meshes.new('rebuilt'); bm.to_mesh(me); bm.free()
reb = bpy.data.objects.new('rebuilt', me); bpy.context.scene.collection.objects.link(reb)
for n, h in HINGE.items():
    print('HINGE %-11s Blender (%.3f, %.3f, %.3f)' % (n, *h))

# ---- decimation of the skins to the budget (three more wheels are counted)
n_fixed = sum(sb.tri_count(o) for o in fixed.values()) + sb.tri_count(reb)
n_wheel = 2 * NS + 2 * (NS - 2)
room = LIMIT - n_fixed - 3 * n_wheel
n_skin0 = sum(sb.tri_count(o) for o in skins.values())
ratio = room / n_skin0
for it in range(60):
    out = {}
    for n, o in skins.items():
        t = o.copy(); t.data = o.data.copy(); bpy.context.scene.collection.objects.link(t)
        md = t.modifiers.new('d', 'DECIMATE'); md.ratio = ratio; md.use_collapse_triangulate = True
        md.vertex_group = 'dec'; md.vertex_group_factor = 1000.0
        sb.only(t); bpy.ops.object.modifier_apply(modifier='d'); out[n] = t
    tot = sum(sb.tri_count(o) for o in out.values())
    if tot <= room:
        break
    for o in out.values():
        bpy.data.objects.remove(o, do_unlink=True)
    ratio *= 0.985
print('BUDGET glass, bumpers and rebuilt parts %d (one wheel inside) + three more wheels %d + skins %d (were %d, ratio %.3f) = %d of %d' % (
    n_fixed, 3 * n_wheel, tot, n_skin0, ratio, n_fixed + 3 * n_wheel + tot, LIMIT))
lost = 0
for n, o in out.items():
    kd2 = KDTree(len(o.data.vertices))
    for v in o.data.vertices:
        kd2.insert(v.co, v.index)
    kd2.balance()
    b = sb.bm_of(skins[n]); sp = [v.co.copy() for v in b.verts if kd.find(v.co)[2] < 1e-4]; b.free()
    lost += sum(1 for p in sp if kd2.find(p)[2] > 1e-4)
    print('SKIN %-11s after: %4d tris' % (n, sb.tri_count(o)))
print('SEAM points moved or lost by the decimation: %d' % lost)
allp = list(out.values()) + list(fixed.values()) + [reb]
for o in allp:
    sb.clear_uv(o.data)
    for a in list(o.data.attributes):
        if a.name in ('kind',):
            o.data.attributes.remove(a)
    for g in list(o.vertex_groups):
        o.vertex_groups.remove(g)
for o in list(skins.values()) + [sheet]:
    bpy.data.objects.remove(o, do_unlink=True)
kit = sb.join_meshes(allp, 'kit')
sb.flat(kit)
sb.fix_facing(kit, tag='KIT')

# ---- one UV for all parts, bake, paint mask
sb.uv_clean(kit, 'UVMap', 0.008)
img = bpy.data.images.new('bake', TEX, TEX, alpha=False)
sb.tex_material(kit, 'M_UAZ452Kit', img)
px = sb.bake_colour([src], kit, img, cage=0.03, maxdist=0.14, margin=2).copy()
me = kit.data; T = len(me.polygons)
def fattr(n):
    a = np.zeros(T, np.int32); me.attributes[n].data.foreach_get('value', a); return a
pidv, nop, tg = fattr('pid'), fattr('nopaint'), fattr('tag')
nr = np.zeros(T * 3); me.polygons.foreach_get('normal', nr); nr = nr.reshape(-1, 3)
fid, bw = sb.raster(me, 'UVMap', TEX); m = fid >= 0; f = np.clip(fid, 0, None)
rgb = px[..., :3].astype(np.float64)
# mirrors and arms: plain dark housing, pale glass on the side that looks back
mm = m & (tg[f] == 1)
rgb[mm] = np.where((nr[f][mm][:, 1] < -0.9)[:, None], np.array([[0.36, 0.41, 0.45]]), np.array([[0.09, 0.09, 0.09]]))
dk = m & (nop[f] == 3)
rgb[dk] = np.array([0.035, 0.035, 0.04])
miss = m & (rgb.max(2) < 0.01)
# paint = clearly green texels of the sheet metal (dust, dirt, rust, lights, plates and handles are not green enough and stay as they are)
r_, g_, b_ = rgb[..., 0], rgb[..., 1], rgb[..., 2]
mxc = rgb.max(2) + 1e-6
green = (g_ >= r_) & ((g_ - b_) / mxc > 0.10) & ((g_ - r_) / mxc > 0.03) & (mxc < 0.42)
paint = m & (nop[f] == 0) & green & ~miss
sheet_m = m & (nop[f] == 0)
pcol = np.median(rgb[paint], 0); plum = rgb[paint].mean(1); med = np.median(plum)
grey = np.clip(rgb.mean(2) / med * 0.80, 0, 1)
outc = rgb.copy(); outc[paint] = grey[paint][:, None]
body_color = pcol / 0.80
print('PAINT texels %d = %.1f%% of the sheet metal; median paint colour of the source %s -> default BodyColor (sRGB values 0..1) %s' % (
    paint.sum(), 100 * paint.sum() / max(sheet_m.sum(), 1), pcol.round(3), body_color.round(3)))
fin = np.zeros((TEX, TEX, 4), np.float32); fin[..., :3] = outc; fin[..., 3] = paint
valid = m & ~miss
fin = sb.dilate(fin, valid, 10)
fin[..., 3] = (fin[..., 3] > 0.5)
print('BAKE texels the bake missed %d of %d' % (int(miss.sum()), int(m.sum())))
fimg = bpy.data.images.new('T_UAZ452Kit_D', TEX, TEX, alpha=True); fimg.alpha_mode = 'STRAIGHT'
fimg.pixels.foreach_set(fin.ravel()); fimg.filepath_raw = OUT + 'T_UAZ452Kit_D.png'; fimg.file_format = 'PNG'; fimg.save()
# preview picture of the default colour: texture * BodyColor under the mask
prev = fin.copy(); pm = fin[..., 3] > 0.5; prev[pm, :3] = np.clip(prev[pm, :3] * body_color[None], 0, 1); prev[..., 3] = 1
sb.save_png(prev, sb.WORK + '_uazkit_default_colour.png', 'prev_default')
red = fin.copy(); red[pm, :3] = np.clip(red[pm, :3] * np.array([0.62, 0.16, 0.12])[None], 0, 1); red[..., 3] = 1
sb.save_png(red, sb.WORK + '_uazkit_red_colour.png', 'prev_red')
sb.store_facing(kit)
meta = dict(hinge={n: tuple(h) for n, h in HINGE.items()}, wheels=[tuple(float(a) for a in w[0]) for w in WC], wheel_r=wheel_r, wheel_hw=wheel_hw,
            body_color=[float(a) for a in body_color], parts=PARTS)
json.dump(meta, open(sb.WORK + '_uazkit_meta.json', 'w'), indent=1)
for i, n in enumerate(PARTS):
    print('PART %-11s tris %4d' % (n, int((pidv == i).sum())))
print('RESULT kit tris in one piece of each part %d; assembled with four wheels %d of %d' % (T, T + 3 * int((pidv == PID['Wheel']).sum()), LIMIT))
me.attributes.remove(me.attributes['tag']); me.attributes.remove(me.attributes['nopaint'])
src.hide_render = True
bpy.ops.wm.save_as_mainfile(filepath=sb.WORK + 'uazkit_work.blend')
