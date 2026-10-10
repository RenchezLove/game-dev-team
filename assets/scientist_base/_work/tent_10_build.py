"""SM_ArmyTent from the Sketchfab tent (joanatrevino816, CC BY): doubled faces welded away, ground levelled, long side 8 m, entrance to -Y,
guy ropes and pegs rebuilt as thin prisms, a dark liner inside (Unreal draws one side of a face - without it the doorway shows the ground
behind the tent), second faces for the sheets that are seen from both sides, canvas lightened, autumn leaves painted on the roof.
Run: blender.exe -b --factory-startup --python tent_10_build.py
"""
import bpy, bmesh, sys, math, os
import numpy as np
from mathutils import Vector
sys.path.insert(0, 'E:/game-dev-team/assets/scientist_base/_work')
import sb

OUT = sb.ROOT + 'SM_ArmyTent/'
LIMIT = 1500
TEX = 1024
LONG = 8.0
LIGHTEN = 1.38
os.makedirs(OUT, exist_ok=True)
rng = np.random.RandomState(11)

sb.empty()
bpy.ops.wm.obj_import(filepath=sb.SRCD + 'tent-model-free/source/unrar/Tent/Tent.obj')
src = sb.join_meshes([o for o in bpy.data.objects if o.type == 'MESH'], 'src')
simg = bpy.data.images.load(sb.SRCD + 'tent-model-free/textures/Tex_0129_0.png')
bm = sb.bm_of(src)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.01)          # every face of the source exists twice (front and back)
bmesh.ops.triangulate(bm, faces=bm.faces); bm.faces.ensure_lookup_table(); bm.faces.index_update()
# the source tent stands a few degrees askew: turn it so that its walls run along the axes (smallest bounding rectangle of the biggest part)
_c = sorted(sb.islands(bm), key=lambda c: -len(c))[0]
_p = np.array([v.co[:2] for v in {v for f in _c for v in f.verts}])
best = None
for deg in np.arange(-12, 12.001, 0.05):
    r = math.radians(deg); q = np.c_[_p[:, 0] * math.cos(r) - _p[:, 1] * math.sin(r), _p[:, 0] * math.sin(r) + _p[:, 1] * math.cos(r)]
    ar_ = np.ptp(q[:, 0]) * np.ptp(q[:, 1])
    if best is None or ar_ < best[0]:
        best = (ar_, deg)
r = math.radians(best[1]); print('ASKEW source turned by %.2f deg about Z' % best[1])
for v in bm.verts:
    x, y = v.co.x, v.co.y
    v.co.x = x * math.cos(r) - y * math.sin(r); v.co.y = x * math.sin(r) + y * math.cos(r)
bm.normal_update()
tagl = bm.faces.layers.int.new('tag')                            # 0 canvas, 1 rope, 2 peg, 3 door posts, 4 liner wall, 5 liner floor, 6 canvas second side
comps = sorted(sb.islands(bm), key=lambda c: -len(c))
canvas = comps[0]
C = np.array([v.co[:] for v in {v for f in canvas for v in f.verts}])
# ---- level the ground: plane through the bottom edge of the canvas
lowv = C[C[:, 2] < 15]
A = np.c_[lowv[:, 0], lowv[:, 1], np.ones(len(lowv))]
pa, pb, pc = np.linalg.lstsq(A, lowv[:, 2], rcond=None)[0]
print('LEVEL ground plane of the source: slope x %.4f y %.4f, offset %.2f (source units, cm)' % (pa, pb, pc))
cmn, cmx = C.min(0), C.max(0)
k = LONG / (cmx[0] - cmn[0]); cx, cy = (cmn[0] + cmx[0]) / 2, (cmn[1] + cmx[1]) / 2
print('SCALE %.5f: source canvas %.1f x %.1f x %.1f -> %.3f x %.3f m' % (k, *(cmx - cmn), (cmx[0] - cmn[0]) * k, (cmx[1] - cmn[1]) * k))
def tf(p):
    """source point -> metres, levelled, entrance (+X of the source) turned to -Y, middle of the canvas footprint at 0"""
    x, y, z = p[0], p[1], p[2]
    return Vector(((y - cy) * k, -(x - cx) * k, (z - (pa * x + pb * y + pc)) * k))
ropes = []; pegs = []
for comp in comps[1:]:
    c = np.array([v.co[:] for v in {v for f in comp for v in f.verts}]); n = len(comp); size = np.ptp(c, 0)
    if size[2] > 80 and n >= 30:
        mu = c.mean(0); w, v = np.linalg.eigh(np.cov((c - mu).T)); ax = v[:, 2]; t = (c - mu) @ ax
        if ax[2] < 0:
            ax = -ax; t = -t
        ropes.append((mu + ax * t.min(), mu + ax * t.max()))
        bmesh.ops.delete(bm, geom=comp, context='FACES')
    elif n == 22:
        mu = c.mean(0); w, v = np.linalg.eigh(np.cov((c - mu).T)); ax = v[:, 2]; t = (c - mu) @ ax
        if ax[2] < 0:
            ax = -ax; t = -t
        pegs.append((mu + ax * t.min(), mu + ax * t.max()))
        bmesh.ops.delete(bm, geom=comp, context='FACES')
    else:
        for f in comp:
            f[tagl] = 3
        print('POSTS part tris %d min %s max %s' % (n, c.min(0).round(0), c.max(0).round(0)))
print('PARTS canvas %d tris, ropes %d, pegs %d' % (len(canvas), len(ropes), len(pegs)))
assert len(ropes) == 9 and len(pegs) == 9
for v in bm.verts:
    v.co = tf(v.co)
    if v.co.z < 0.06 * 1.0 and v.co.z < 0.12:                    # the bottom edge and the feet of the posts stand on the ground
        pass
# bottom edge of the canvas onto the ground
bm.edges.ensure_lookup_table()
bott = {v for e in bm.edges if len(e.link_faces) == 1 for v in e.verts if v.co.z < 0.22}
for v in bott:
    v.co.z = 0.0
for v in bm.verts:
    v.co.z = max(v.co.z, 0.0)
bm.normal_update()
me = bpy.data.meshes.new('canvas'); bm.to_mesh(me); bm.free()
canv = bpy.data.objects.new('canvas', me); bpy.context.scene.collection.objects.link(canv)
# the source for the bake: the same welded canvas with its own UV and texture
bsrc = canv.copy(); bsrc.data = canv.data.copy(); bsrc.name = 'bake_src'; bpy.context.scene.collection.objects.link(bsrc)
sb.tex_material(bsrc, 'src', simg); bsrc.data.materials[0].use_backface_culling = False
sb.fix_facing(canv, tag='CANVAS')
c = sb.coords(canv)
tg = np.zeros(len(canv.data.polygons), np.int32); canv.data.attributes['tag'].data.foreach_get('value', tg)
pv = np.zeros(len(canv.data.loops), np.int32); canv.data.loops.foreach_get('vertex_index', pv); pv = pv.reshape(-1, 3)
cv = c[np.unique(pv[tg == 0])]
smn, smx = cv.min(0), cv.max(0)
print('SHELL canvas min %s max %s' % (smn.round(3), smx.round(3)))

# ---- main room of the tent (without the porch) and the liner in it
ys = np.sort(cv[cv[:, 2] < 0.05][:, 1])
y_front = float(ys[ys > smn[1] + 0.3][0])                        # the entrance wall: first bottom points behind the porch
eave = float(np.median(cv[(abs(cv[:, 0]) > smx[0] - 0.12)][:, 2].max()))
wall_top = float(cv[(cv[:, 0] > smx[0] - 0.10)][:, 2].max())
print('ROOM entrance wall at y %.3f (porch reaches y %.3f), side walls x +-%.3f, back wall y %.3f, wall top %.3f, ridge %.3f' % (y_front, smn[1], smx[0], smx[1], wall_top, smx[2]))
IN = 0.10
lx0, lx1, ly0, ly1, lz1 = smn[0] + IN, smx[0] - IN, y_front + IN, smx[1] - IN, wall_top - 0.05
bm = bmesh.new(); tagl = bm.faces.layers.int.new('tag')
def quad(pts, tag, look):
    """face through pts that looks along 'look'"""
    vs = [bm.verts.new(p) for p in pts]
    f = bm.faces.new(vs); f.normal_update()
    if f.normal.dot(Vector(look)) < 0:
        f.normal_flip()
    f[tagl] = tag
    return f
quad([(lx0, ly0, 0), (lx1, ly0, 0), (lx1, ly0, lz1), (lx0, ly0, lz1)], 4, (0, 1, 0))
quad([(lx0, ly1, 0), (lx1, ly1, 0), (lx1, ly1, lz1), (lx0, ly1, lz1)], 4, (0, -1, 0))
quad([(lx0, ly0, 0), (lx0, ly1, 0), (lx0, ly1, lz1), (lx0, ly0, lz1)], 4, (1, 0, 0))
quad([(lx1, ly0, 0), (lx1, ly1, 0), (lx1, ly1, lz1), (lx1, ly0, lz1)], 4, (-1, 0, 0))
quad([(lx0, ly0, 0.012), (lx1, ly0, 0.012), (lx1, ly1, 0.012), (lx0, ly1, 0.012)], 5, (0, 0, 1))
quad([(lx0, ly0, lz1), (lx1, ly0, lz1), (lx1, ly1, lz1), (lx0, ly1, lz1)], 4, (0, 0, -1))
me = bpy.data.meshes.new('liner'); bm.to_mesh(me); bm.free()
liner = bpy.data.objects.new('liner', me); bpy.context.scene.collection.objects.link(liner)
bpy.context.view_layer.update()

# ---- sheets seen from both sides (porch, door flaps): a second face looking the other way
front, back = sb.open_sides(canv, ground=True, rays=64, extra=[liner])
bm = sb.bm_of(canv); tagl = bm.faces.layers.int['tag']; bm.normal_update()
two = [f for f in bm.faces if min(front[f.index], back[f.index]) > 0.10]
print('TWO-SIDED sheets: %d faces get a second side (back open > 0.10); canvas faces with a closed front and open back: %d' % (len(two), sum(1 for f in bm.faces if front[f.index] < 0.02 and back[f.index] > 0.1)))
for f in two:
    vs = [bm.verts.new(v.co - f.normal * 0.004) for v in reversed(f.verts)]
    for v_ in vs:
        v_.co.z = max(v_.co.z, 0.0)
    g = bm.faces.new(vs); g[tagl] = 6
bm.to_mesh(canv.data); bm.free()

# ---- ropes and pegs: 3-sided prisms
bm = bmesh.new(); tagl = bm.faces.layers.int.new('tag')
def prism(a, b, r, tag, cap_top=False):
    a, b = Vector(a), Vector(b); ax = (b - a).normalized()
    u = ax.cross(Vector((0, 0, 1))); u = u.normalized() if u.length > 1e-4 else Vector((1, 0, 0)); w = ax.cross(u)
    ring = [[bm.verts.new(p + (u * math.cos(t) + w * math.sin(t)) * r) for t in (math.radians(90), math.radians(210), math.radians(330))] for p in (a, b)]
    mid = (a + b) / 2
    for i in range(3):
        f = bm.faces.new((ring[0][i], ring[0][(i + 1) % 3], ring[1][(i + 1) % 3], ring[1][i])); f.normal_update()
        cc = f.calc_center_median() - mid; cc -= ax * cc.dot(ax)
        if f.normal.dot(cc) < 0:
            f.normal_flip()
        f[tagl] = tag
    if cap_top:
        f = bm.faces.new(ring[1]); f.normal_update()
        if f.normal.dot(ax) < 0:
            f.normal_flip()
        f[tagl] = tag
for (a, b), (pa_, pb_) in zip(ropes, pegs):
    pass
peg_tf = []
for a, b in pegs:
    a, b = tf(a), tf(b); d = b - a
    a2 = Vector((a.x, a.y, 0.03))                                 # the tip goes to ground level
    b2 = a2 + d
    peg_tf.append((a2, b2)); prism(a2, b2, 0.026, 2, cap_top=True)
for a, b in ropes:
    a, b = tf(a), tf(b)
    # lower end to the nearest peg (two thirds up the peg), upper end stays at the canvas
    j = min(range(len(peg_tf)), key=lambda i: (peg_tf[i][0] - a).length)
    a = peg_tf[j][0] + (peg_tf[j][1] - peg_tf[j][0]) * 0.65
    prism(a, b, 0.022, 1)
bmesh.ops.triangulate(bm, faces=bm.faces)
me = bpy.data.meshes.new('guy'); bm.to_mesh(me); bm.free()
guy = bpy.data.objects.new('guy', me); bpy.context.scene.collection.objects.link(guy)
for o in (liner,):
    b2 = sb.bm_of(o); bmesh.ops.triangulate(b2, faces=b2.faces); b2.to_mesh(o.data); b2.free()
n_other = sb.tri_count(guy) + sb.tri_count(liner)
n_canvas = sb.tri_count(canv)
print('BUDGET canvas with posts and second sides %d + ropes and pegs %d + liner %d = %d of %d' % (n_canvas, sb.tri_count(guy), sb.tri_count(liner), n_canvas + n_other, LIMIT))
assert n_canvas + n_other <= LIMIT
for o in (canv, liner, guy):
    sb.clear_uv(o.data)
low = sb.join_meshes([canv, liner, guy], 'SM_ArmyTent')
sb.flat(low)

# ---- UV + bake
me = low.data
sb.uv_clean(low, 'UVMap', 0.008)
img = bpy.data.images.new('T_ArmyTent_D', TEX, TEX, alpha=False)
sb.tex_material(low, 'M_ArmyTent', img)
px = sb.bake_colour([bsrc], low, img, cage=0.02, maxdist=0.06, margin=2)
px = px.copy()
T = len(me.polygons)
tg = np.zeros(T, np.int32); me.attributes['tag'].data.foreach_get('value', tg)
nr = np.zeros(T * 3); me.polygons.foreach_get('normal', nr); nr = nr.reshape(-1, 3)
co = sb.coords(low); pv = np.zeros(T * 3, np.int32); me.loops.foreach_get('vertex_index', pv); pv = pv.reshape(-1, 3)
fid, bw = sb.raster(me, 'UVMap', TEX)
m = fid >= 0; f = np.clip(fid, 0, None)
P = (co[pv[f]] * bw[..., None]).sum(2)                           # world point of every texel
t = tg[f]
rgb = px[..., :3]
print('BAKE canvas texels mean colour before %s' % rgb[m & (t == 0)].mean(0).round(3))
cm = m & ((t == 0) | (t == 6))
# 2026-10-09, Rinat: the tent came out too dark under the warm sun -> the faded khaki of a Soviet army cape-tent. The baked picture keeps
# only its folds and seams (as a mild lighter/darker factor), the hue is one canvas for the walls and the roof; no dark shading is painted in.
KHAKI = np.array([0.585, 0.560, 0.365])
lum = rgb[cm].mean(1); rel = lum / lum.mean()
fct = np.clip(0.66 + 0.36 * rel, 0.70, 1.20)
canvas_col = KHAKI[None] * fct[:, None]
wallm = np.abs(nr[f][cm][:, 2]) < 0.3
low_ = np.clip(1 - P[cm][:, 2] / 0.55, 0, 1) * wallm                 # the bottom of the walls: a little darker and dirtier
canvas_col = canvas_col * (1 - 0.16 * low_[:, None]) * (1 - low_[:, None] * 0.10 * np.array([0.0, 0.25, 0.9])[None])
rgb[cm] = np.clip(canvas_col, 0, 1)
# inside faces of the porch sit in shade
rgb[m & (t == 6)] *= 0.86
pm_ = m & (t == 3); rgb[pm_] = np.array([0.46, 0.40, 0.32])[None] * np.clip(0.75 + 0.5 * rgb[pm_].mean(1) / max(rgb[pm_].mean(), 1e-6) * 0.5, 0.8, 1.2)[:, None]
noise = rng.rand(TEX, TEX, 1) * 0.06 - 0.03
# liner: dark inside of the tent, a little lighter towards the ground; floor - trodden earth
lw = m & (t == 4)
rgb[lw] = (np.array([0.15, 0.14, 0.095])[None] * (1.25 - 0.45 * np.clip(P[lw][:, 2:3] / max(lz1, 1e-3), 0, 1))) + noise[lw]
lf = m & (t == 5)
dist_door = np.clip((P[lf][:, 1:2] - ly0) / 2.5, 0, 1)
rgb[lf] = np.array([0.30, 0.25, 0.17])[None] * (1.0 - 0.55 * dist_door) + noise[lf]
rp = m & (t == 1)
rgb[rp] = np.array([0.60, 0.54, 0.38])[None] + noise[rp] * 1.5
pg = m & (t == 2)
rgb[pg] = np.array([0.42, 0.36, 0.28])[None] + noise[pg]

# ---- autumn leaves on the roof (painted): yellow, orange, rust
roof = m & (t == 0) & (nr[f][:, :, 2] > 0.30) & (P[..., 2] > wall_top - 0.25)
ry, rx = np.nonzero(roof)
RP = P[roof]
NL = 330
ctr = np.c_[rng.uniform(smn[0], smx[0], NL), rng.uniform(y_front, smx[1], NL)]
# a part of the leaves lies in heaps (drifts) rather than evenly
for h in range(7):
    hc = np.array([rng.uniform(smn[0] + 0.5, smx[0] - 0.5), rng.uniform(y_front + 0.5, smx[1] - 0.5)])
    idx = rng.choice(NL, 16, replace=False); ctr[idx] = hc + rng.normal(0, 0.28, (16, 2))
ang = rng.uniform(0, math.pi, NL); ln = rng.uniform(0.085, 0.14, NL); wd = ln * rng.uniform(0.42, 0.62, NL)
PAL = np.array([[0.86, 0.66, 0.13], [0.90, 0.55, 0.10], [0.80, 0.40, 0.08], [0.66, 0.29, 0.07], [0.78, 0.72, 0.22], [0.58, 0.36, 0.12]])
colr = PAL[rng.randint(0, len(PAL), NL)] * rng.uniform(0.85, 1.08, (NL, 1))
leaf_col = np.zeros((len(RP), 3)); leaf_m = np.zeros(len(RP), bool); shade = np.zeros(len(RP), bool)
for i in range(NL):
    d = RP[:, :2] - ctr[i]
    near = (abs(d[:, 0]) < 0.2) & (abs(d[:, 1]) < 0.2)
    if not near.any():
        continue
    dn = d[near]; ca, sa = math.cos(ang[i]), math.sin(ang[i])
    u = dn[:, 0] * ca + dn[:, 1] * sa; v = -dn[:, 0] * sa + dn[:, 1] * ca
    a, b = ln[i], wd[i]
    R = (a * a + b * b) / (2 * b)                                 # a lens: two circle arcs meeting in sharp tips
    ins = (u * u + (abs(v) + R - b) ** 2) < R * R
    us = u - 0.012; vs = v + 0.012
    sh = (us * us + (abs(vs) + R - b) ** 2) < R * R
    ii = np.nonzero(near)[0]
    vein = (abs(v) < 0.006) & ins
    leaf_col[ii[ins]] = colr[i]; leaf_col[ii[vein]] = colr[i] * 0.78; leaf_m[ii[ins]] = True; shade[ii[sh]] = True
sub = rgb[ry, rx]
sub[shade & ~leaf_m] *= 0.86
sub[leaf_m] = leaf_col[leaf_m]
rgb[ry, rx] = sub
print('LEAVES %d placed, texels painted %d of %d roof texels (%.1f%%); roof texel size about %.1f mm' % (NL, leaf_m.sum(), len(RP), 100 * leaf_m.mean(), 1000 * math.sqrt((smx[0] - smn[0]) * (smx[1] - y_front) / max(len(RP), 1))))
px[..., :3] = np.clip(rgb, 0, 1); px[..., 3] = 1
px = sb.dilate(px, m, 6)
print('COLOUR canvas texels mean after %s; unpainted (black) texels inside faces: %d' % (px[..., :3][m & (t == 0)].mean(0).round(3), int((px[..., :3][m].max(1) < 0.02).sum())))
img.pixels.foreach_set(px.ravel()); img.filepath_raw = OUT + 'T_ArmyTent_D.png'; img.file_format = 'PNG'; img.save()
ang_, lov = sb.lightmap_uv(low)
print('UV LightmapUV angle %d overlapping texels %d' % (ang_, lov))
sb.store_facing(low)
# ---- numbers for the lead: the tent body without ropes and pegs
body = np.unique(pv[(tg == 0) | (tg == 3) | (tg == 6)])
b0, b1 = co[body].min(0) * 100, co[body].max(0) * 100
print('TENT BODY without ropes and pegs, cm: min (%.1f, %.1f, %.1f) max (%.1f, %.1f, %.1f)' % (*b0, *b1))
print('TENT MAIN ROOM, cm: x %.1f..%.1f, y %.1f..%.1f (entrance wall at y %.1f, porch out to y %.1f), wall top z %.1f, ridge z %.1f' % (smn[0] * 100, smx[0] * 100, y_front * 100, smx[1] * 100, y_front * 100, smn[1] * 100, wall_top * 100, smx[2] * 100))
dv = co[np.unique(pv[tg == 3])]
print('DOOR posts, cm: x %.1f..%.1f y %.1f..%.1f z up to %.1f' % (dv[:, 0].min() * 100, dv[:, 0].max() * 100, dv[:, 1].min() * 100, dv[:, 1].max() * 100, dv[:, 2].max() * 100))
gv = co[np.unique(pv[(tg == 1) | (tg == 2)])]
print('ROPES and pegs reach, cm: min (%.1f, %.1f, %.1f) max (%.1f, %.1f, %.1f)' % (*(gv.min(0) * 100), *(gv.max(0) * 100)))
print('RESULT tris %d min %s max %s size %s; origin: middle of the canvas footprint on the ground' % (sb.tri_count(low), co.min(0).round(3), co.max(0).round(3), np.ptp(co, 0).round(3)))
me.attributes.remove(me.attributes['tag'])
bsrc.hide_render = True
bpy.ops.wm.save_as_mainfile(filepath=sb.WORK + 'tent_work.blend')
