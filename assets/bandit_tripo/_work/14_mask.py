"""Clothing mask for the bandit in the UV layout of T_BanditTripo_D.png (1024, RGBA, binary, no overlaps):
R = black leather (jacket + cap), G = striped vest, B = track trousers without the stripe, A = red side stripe.
Skin, hair, stubble, sneakers -> zero everywhere.  Each texel gets its place on the model (slot + rest position)
through the UV triangles and is classified by that place plus the colour of the baked texture.
Does not touch the FBX or the colour texture.
Run: blender.exe -b bandit_work.blend --factory-startup --python 14_mask.py [-- stats]
"""
import bpy, sys, os, math
import numpy as np

OUT = 'E:/game-dev-team/assets/bandit_tripo/'
R = 1024
STATS = 'stats' in sys.argv
tex = bpy.data.images.load(OUT + 'T_BanditTripo_D.png')
TP = np.array(tex.pixels[:], dtype=np.float32).reshape(R, R, tex.channels)[..., :3]


def raster(uv, pad):
    fid = -np.ones((R, R), np.int32); bar = np.zeros((R, R, 3), np.float32); best = np.full((R, R), -1e9, np.float32)
    for t in range(len(uv)):
        p = uv[t] * R
        d = (p[1, 0] - p[0, 0]) * (p[2, 1] - p[0, 1]) - (p[1, 1] - p[0, 1]) * (p[2, 0] - p[0, 0])
        if abs(d) < 1e-9:
            continue
        x0 = max(int(math.floor(p[:, 0].min() - pad - 1)), 0); x1 = min(int(math.ceil(p[:, 0].max() + pad + 1)), R)
        y0 = max(int(math.floor(p[:, 1].min() - pad - 1)), 0); y1 = min(int(math.ceil(p[:, 1].max() + pad + 1)), R)
        if x1 <= x0 or y1 <= y0:
            continue
        X, Y = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
        w1 = ((X - p[0, 0]) * (p[2, 1] - p[0, 1]) - (Y - p[0, 1]) * (p[2, 0] - p[0, 0])) / d
        w2 = ((p[1, 0] - p[0, 0]) * (Y - p[0, 1]) - (p[1, 1] - p[0, 1]) * (X - p[0, 0])) / d
        w0 = 1 - w1 - w2
        el = [np.linalg.norm(p[2] - p[1]), np.linalg.norm(p[0] - p[2]), np.linalg.norm(p[1] - p[0])]
        dist = np.minimum(np.minimum(w0 * abs(d) / el[0], w1 * abs(d) / el[1]), w2 * abs(d) / el[2])
        sb = best[y0:y1, x0:x1]
        m = (dist > -pad) & (dist > sb)
        if m.any():
            sb[m] = dist[m]
            fid[y0:y1, x0:x1][m] = t
            Wt = np.clip(np.stack([w0, w1, w2], -1), 0, None); Wt /= Wt.sum(-1, keepdims=True)
            bar[y0:y1, x0:x1][m] = Wt[m]
    return fid, bar


# all three slots share one atlas: collect their triangles (rest positions) with the slot id
TV, UV, SL = [], [], []
for si, s in enumerate(('Head', 'Torso', 'Legs')):
    me = bpy.data.objects['SK_Bandit_' + s].data
    co = np.zeros(len(me.vertices) * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    lv = np.zeros(len(me.loops), np.int32); me.loops.foreach_get('vertex_index', lv)
    uv = np.zeros(len(me.loops) * 2); me.uv_layers['UVMap'].data.foreach_get('uv', uv)
    T = len(me.polygons)
    TV.append(co[lv].reshape(T, 3, 3)); UV.append(uv.reshape(T, 3, 2)); SL.append(np.full(T, si))
TV = np.concatenate(TV); UV = np.concatenate(UV); SL = np.concatenate(SL)
fid, bar = raster(UV, 1.5)
m = fid >= 0
f = fid[m]; Wb = bar[m].astype(np.float64)
P = (TV[f] * Wb[:, :, None]).sum(1)
slot = SL[f]
c = TP[m].astype(np.float64)
r, g, b = c[:, 0], c[:, 1], c[:, 2]
val = c.max(1); sat = val - c.min(1)
x, y, z = P[:, 0], P[:, 1], P[:, 2]

skin = (r > 0.45) & (r > b * 1.3) & (g > b)
red = (r > 0.30) & (r > 2.0 * b) & (r > 1.6 * g)
bluish = (b > r + 0.015) & (val < 0.45)
if STATS:
    def klass():
        k = np.full(len(c), 'other      ', dtype=object)
        k[(sat < 0.09) & (val < 0.28)] = 'dark-grey  '
        k[(sat < 0.09) & (val >= 0.28) & (val < 0.5)] = 'mid-grey   '
        k[(sat < 0.12) & (val >= 0.5)] = 'light      '
        k[(r - b >= 0.09) & (val < 0.45) & ~skin & ~red] = 'dark-warm  '
        k[bluish] = 'bluish     '
        k[skin] = 'skin       '
        k[red] = 'red        '
        return k
    k = klass()
    for si, s in enumerate(('Head', 'Torso', 'Legs')):
        zs = z[slot == si]
        for z0 in np.arange(math.floor(zs.min() * 20) / 20, zs.max(), 0.05):
            q = (slot == si) & (z >= z0) & (z < z0 + 0.05)
            if q.sum() < 30:
                continue
            u, n = np.unique(k[q], return_counts=True)
            print('STAT %-5s z %.2f..%.2f n=%6d  %s   mean rgb of mid/light greys %s' % (s, z0, z0 + 0.05, q.sum(),
                  ' '.join('%s%4.0f%%' % (a.strip(), 100 * nn / q.sum()) for a, nn in zip(u, n)),
                  np.round(c[q & (sat < 0.12) & (val >= 0.28)].mean(0), 2) if (q & (sat < 0.12) & (val >= 0.28)).any() else '-'))
    sys.exit(0)

# ---------- zones: place on the model first, colour second ----------
HEAD, TORSO, LEGS = slot == 0, slot == 1, slot == 2
dark_neutral = (sat < 0.09) & (val < 0.28)
front_open = TORSO & (y < 0.0) & (np.abs(x) < 0.14) & (z > 0.914) & (z < 1.53)        # where the vest shows between the lapels
seed = front_open & ~skin & (bluish | ((sat < 0.13) & (val > 0.42)))                   # certain vest texels: blue or white stripes
# the vest is everything in the chest opening between the lapels: per 2 cm of height take the span of the certain
# stripe texels across the chest and fill it (the dim halves of the stripes are not separable by colour alone)
vest = np.zeros(len(c), bool)
zb = np.floor(z / 0.02).astype(int)
span = {}
for kz in np.unique(zb[seed]):
    xs_ = x[seed & (zb == kz)]
    if len(xs_) >= 12:
        span[int(kz)] = (np.percentile(xs_, 3), np.percentile(xs_, 97))
ks = sorted(span)
for kz in range(ks[0], ks[-1] + 1):
    if kz not in span:                                  # a band with too few certain texels takes its neighbours' span
        lo = max(k for k in ks if k < kz); hi = min(k for k in ks if k > kz)
        span[kz] = (min(span[lo][0], span[hi][0]), max(span[lo][1], span[hi][1]))
    q = front_open & ~skin & (zb == kz) & (x >= span[kz][0]) & (x <= span[kz][1]) & (y < -0.06)
    vest |= q
vest |= seed
print('VEST certain stripe texels %d -> filled chest opening %d texels, z %.2f..%.2f, widest span x %.3f..%.3f' % (
    seed.sum(), vest.sum(), z[vest].min(), z[vest].max(), min(s[0] for s in span.values()), max(s[1] for s in span.values())))
bare = skin | red                                                                       # hands, neck (incl. their shadows)
strip = TORSO & (z < 0.912) & (val >= 0.28) & ~skin                                     # the trouser band under the jacket hem
jacket = TORSO & ~bare & ~vest & ~strip
cap = HEAD & dark_neutral & ((z > 1.695) | ((z > 1.64) & (y > -0.05)))                  # not the eyebrows / eyes on the face
shoe_colour = skin | (val > 0.5)
pants_grey = (sat < 0.10) & (val >= 0.28) & (val < 0.47)
legs_cloth = LEGS & ((z >= 0.12) | ((z >= 0.095) & (pants_grey | red)))                 # below that are the sneakers
stripe = (legs_cloth | strip) & red
trousers = (legs_cloth | strip) & ~red
ZONES = {'R leather (jacket + cap)': jacket | cap, 'G striped vest': vest, 'B trousers': trousers, 'A side stripe': stripe}
names = list(ZONES)
M = np.stack([ZONES[n] for n in names], -1)
print('ZONES overlap on painted texels before saving: %d' % int((M.sum(1) > 1).sum()))

img = np.zeros((R, R, 4)); img[m] = M
filled = m.copy()
for _ in range(8):                                   # bleed past island borders like a baked texture, kept binary
    acc = np.zeros((R, R, 4)); cnt = np.zeros((R, R))
    for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)):
        acc += np.roll(np.roll(img * filled[..., None], dy, 0), dx, 1); cnt += np.roll(np.roll(filled, dy, 0), dx, 1)
    new = (~filled) & (cnt > 0)
    a = acc[new] / cnt[new][:, None]
    one = np.zeros_like(a); k = a.argmax(1); one[np.arange(len(a)), k] = (a.max(1) >= 0.5)
    img[new] = one
    filled |= new
PATH = OUT + 'T_BanditTripo_Mask.png'
im = bpy.data.images.new('T_BanditTripo_Mask', R, R, alpha=True)
im.alpha_mode = 'CHANNEL_PACKED'
im.colorspace_settings.name = 'Non-Color'
im.pixels.foreach_set(img.astype(np.float32).ravel())
im.filepath_raw = PATH; im.file_format = 'PNG'; im.save()

# ---------- checks on the saved file ----------
chk = bpy.data.images.load(PATH); chk.alpha_mode = 'CHANNEL_PACKED'; chk.colorspace_settings.name = 'Non-Color'
K = np.array(chk.pixels[:], dtype=np.float32).reshape(R, R, chk.channels)
print('MASK %s %dx%d channels=%d depth=%d %.1f KB values per channel R%s G%s B%s A%s' % (PATH, chk.size[0], chk.size[1], chk.channels, chk.depth, os.path.getsize(PATH) / 1024,
      *[np.unique(K[..., i]).round(3) for i in range(4)]))
print('CHECK saved file equals computed zones on painted texels: %s' % bool(((K[m] > 0.5) == M).all()))
print('CHECK texels set in two or more channels (whole file): %d' % int(((K > 0.5).sum(-1) > 1).sum()))
for i, n in enumerate(names):
    q = M[:, i]
    print('ZONE %-26s texels %6d (%.1f%% of the painted area): head %d torso %d legs %d; mean rgb in the colour texture %s, z %.2f..%.2f' % (
        n, q.sum(), 100 * q.mean(), (q & HEAD).sum(), (q & TORSO).sum(), (q & LEGS).sum(), np.round(c[q].mean(0), 2), z[q].min(), z[q].max()))
none = ~M.any(1)
print('ZONE none: texels %d (%.1f%%): head %d torso %d legs %d' % (none.sum(), 100 * none.mean(), (none & HEAD).sum(), (none & TORSO).sum(), (none & LEGS).sum()))
print('CHECK by colour of T_BanditTripo_D.png:')
sk = skin & ~red
print('  skin-coloured (not red) texels: in R %d, G %d, B %d, A %d, in none %d' % ((sk & M[:, 0]).sum(), (sk & M[:, 1]).sum(), (sk & M[:, 2]).sum(), (sk & M[:, 3]).sum(), (sk & none).sum()))
legred = red & LEGS & (z > 0.07)
print('  red texels on the legs above the shoes: %d, of them in A %d (%.1f%%)' % (legred.sum(), (legred & M[:, 3]).sum(), 100 * (legred & M[:, 3]).sum() / max(legred.sum(), 1)))
wb = front_open & (bluish | ((sat < 0.13) & (val > 0.42))) & ~skin
print('  blue-or-white texels of the chest opening: %d, of them in G %d' % (wb.sum(), (wb & M[:, 1]).sum()))
dk = TORSO & dark_neutral & ~bluish & ~front_open
print('  dark neutral texels of the torso slot outside the chest opening: %d, of them in R %d (%.1f%%), in G %d' % (dk.sum(), (dk & M[:, 0]).sum(), 100 * (dk & M[:, 0]).sum() / dk.sum(), (dk & M[:, 1]).sum()))
shoes = LEGS & (z < 0.095)
print('  legs slot below z 0.095 (sneakers): %d texels, in any channel %d' % (shoes.sum(), (shoes & M.any(1)).sum()))
hd = HEAD & (z > 1.70)
print('  head slot above z 1.70 (the cap): %d texels, in R %d (%.1f%%)' % (hd.sum(), (hd & M[:, 0]).sum(), 100 * (hd & M[:, 0]).sum() / hd.sum()))
hl = HEAD & (z < 1.62)
print('  head slot below z 1.62 (face, neck): %d texels, in any channel %d' % (hl.sum(), (hl & M.any(1)).sum()))
gaps = [round(float(z0), 2) for z0 in np.arange(0.15, 0.90, 0.05) if not (M[:, 3] & LEGS & (z >= z0) & (z < z0 + 0.05)).any()]
print('  side stripe present in every 5 cm band of the legs from 0.15 to 0.90: %s (bands without it: %s)' % (not gaps, gaps))
for sgn, nm in ((1, 'left'), (-1, 'right')):
    q = M[:, 3] & LEGS & (x * sgn > 0)
    print('  side stripe on the %s leg: %d texels, z %.2f..%.2f' % (nm, q.sum(), z[q].min() if q.any() else 0, z[q].max() if q.any() else 0))

# overlay in UV space: zones tinted over the darkened colour texture
tint = np.array([[0.9, 0.1, 0.1], [0.1, 0.8, 0.1], [0.15, 0.3, 1.0], [1.0, 0.9, 0.0]])
ov = TP.astype(np.float64) * 0.45
for i in range(4):
    q = K[..., i] > 0.5
    ov[q] = ov[q] * 0.5 + tint[i] * 0.55
o = bpy.data.images.new('ov', R, R, alpha=False)
o.pixels.foreach_set(np.concatenate([ov, np.ones((R, R, 1))], -1).astype(np.float32).ravel())
o.filepath_raw = OUT + 'renders/qc_mask_overlay_uv.png'; o.file_format = 'PNG'; o.save()
print('OVERLAY', o.filepath_raw)

# the same tint on the model: front, back, side
sys.path.insert(0, 'E:/game-dev-team/assets/hero_tripo/_work'); sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W, hpose as HP
ovi = bpy.data.images.load(OUT + 'renders/qc_mask_overlay_uv.png')
for mt in bpy.data.materials:
    if mt.node_tree:
        for n in mt.node_tree.nodes:
            if n.type == 'TEX_IMAGE':
                n.image = ovi; n.interpolation = 'Closest'
sc2, cam, suns = W.setup_render(res=900)
sc2.render.film_transparent = False
tiles = []
for vn, vd in (('front', (0.15, -1, 0.1)), ('back', (-0.15, 1, 0.15)), ('side', (1, -0.2, 0.1))):
    p = OUT + 'renders/_m_%s.png' % vn
    HP.shoot(vd, (0, 0, 0.93), 2.1, p, suns); tiles.append(p)
def load(p):
    i2 = bpy.data.images.load(p); w, h = i2.size
    a = np.array(i2.pixels[:], dtype=np.float32).reshape(h, w, 4); bpy.data.images.remove(i2); return a
sh = np.concatenate([load(t) for t in tiles], axis=1)
s = bpy.data.images.new('s', sh.shape[1], sh.shape[0], alpha=False); s.pixels = sh.ravel()
s.filepath_raw = OUT + 'renders/qc_mask_on_model.png'; s.file_format = 'PNG'; s.save()
for t in tiles:
    os.remove(t)
print('OVERLAY', s.filepath_raw)
