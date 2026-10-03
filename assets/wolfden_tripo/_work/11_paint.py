"""Colours and mask of the new wolf den.  Every texel of UV0 gets its place on the model (kind of face, position)
and a zone from the baked Tripo colour: rock / moss / blood / bone / ground pad / dark inside.  Then the zones are
graded towards ref.png (grey rock, dull green moss, dark red blood, pale bones), the pad is painted as trampled
earth, the inside is black.  Writes T_WolfDenTripo_D.png, T_WolfDenTripo_Mask.png (R rock, G moss, B blood,
A bones; pad and inside = 0), the overlay sheet, and checks UV0 / UV1 for overlaps.
Run: blender.exe -b wolfden_work.blend --factory-startup --python 11_paint.py [-- stats]
"""
import bpy, sys, os, math
import numpy as np

OUT = 'E:/game-dev-team/assets/wolfden_tripo/'
R = 1024
STATS = 'stats' in sys.argv
ob = bpy.data.objects['SM_WolfDenCave']
me = ob.data
T = len(me.polygons)
co = np.zeros(len(me.vertices) * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
lv = np.zeros(len(me.loops), np.int32); me.loops.foreach_get('vertex_index', lv)
TV = co[lv].reshape(T, 3, 3)
FN = np.zeros(T * 3); me.polygons.foreach_get('normal', FN); FN = FN.reshape(T, 3)
KIND = np.zeros(T, np.int32); me.attributes['kind'].data.foreach_get('value', KIND)
def uvs(layer):
    a = np.zeros(len(me.loops) * 2); me.uv_layers[layer].data.foreach_get('uv', a); return a.reshape(T, 3, 2)
raw = bpy.data.images.load(OUT + '_work/_bake_raw.png')
RAW = np.array(raw.pixels[:], dtype=np.float32).reshape(R, R, raw.channels)[..., :3].astype(np.float64)
PADC = np.load(OUT + '_work/_pad.npy')          # pad centre x, y, mouth x, mouth front y, mouth height


def raster(uv, pad):
    fid = -np.ones((R, R), np.int32); bar = np.zeros((R, R, 3), np.float32); best = np.full((R, R), -1e9, np.float32); inner = np.zeros((R, R), np.int16)
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
        m_ = (dist > -pad) & (dist > sb)
        if m_.any():
            sb[m_] = dist[m_]
            fid[y0:y1, x0:x1][m_] = t
            Wt = np.clip(np.stack([w0, w1, w2], -1), 0, None); Wt /= Wt.sum(-1, keepdims=True)
            bar[y0:y1, x0:x1][m_] = Wt[m_]
        inner[y0:y1, x0:x1] += (dist > 0.6)
    return fid, bar, int((inner > 1).sum())


for layer in ('UVMap', 'LightmapUV'):
    f_, b_, ov = raster(uvs(layer), 0.0)
    u = uvs(layer)
    print('UVCHECK %s range %.4f..%.4f overlapping texels at 1024: %d, covered %.3f' % (layer, u.min(), u.max(), ov, (f_ >= 0).mean()))
fid, bar, _ = raster(uvs('UVMap'), 1.5)
m = fid >= 0
f = fid[m]; Wb = bar[m].astype(np.float64)
P = (TV[f] * Wb[:, :, None]).sum(1)
N = FN[f]; kind = KIND[f]
c = RAW[m]
r, g, b = c[:, 0], c[:, 1], c[:, 2]
val = c.max(1); sat = val - c.min(1)
x, y, z = P[:, 0], P[:, 1], P[:, 2]
SHELL, SMALL, PAD = kind == 0, kind == 1, kind == 2
if STATS:
    for nm, q in (('shell', SHELL), ('small', SMALL)):
        print('STAT %s texels %d, value quantiles 5/25/50/75/95: %s' % (nm, q.sum(), np.quantile(val[q], [0.05, 0.25, 0.5, 0.75, 0.95]).round(2)))
        print('STAT %s rows r-g from -0.06 step 0.03, columns g-b from -0.03 step 0.03: count (mean value)' % nm)
        for i in range(-2, 9):
            row = ''
            for j in range(-1, 9):
                qq = q & (r - g >= i * 0.03) & (r - g < (i + 1) * 0.03) & (g - b >= j * 0.03) & (g - b < (j + 1) * 0.03)
                row += '%6d(%.2f) ' % (qq.sum(), val[qq].mean() if qq.any() else 0)
            print('STAT %s r-g %+.2f: %s' % (nm, i * 0.03, row))
        big = q & (r - g >= 0.27)
        print('STAT %s r-g >= 0.27: %d texels, mean rgb %s' % (nm, big.sum(), c[big].mean(0).round(2) if big.any() else '-'))
    sys.exit(0)

# ---------- zones ----------
def _h(ix, iy, iz, seed=0):
    n = (ix.astype(np.int64) * 374761393 + iy.astype(np.int64) * 668265263 + iz.astype(np.int64) * 2147483647 + seed * 974711) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    n = n ^ (n >> 16)
    return (n & 0xFFFFFF) / float(0x1000000)
def vn(px_, py_, seed=0):
    p = np.stack([px_, py_, np.zeros_like(px_)], -1)
    fl = np.floor(p); t = p - fl; t = t * t * (3 - 2 * t); i = fl.astype(np.int64)
    out = 0.0
    for dx in (0, 1):
        for dy in (0, 1):
            w = (t[:, 0] if dx else 1 - t[:, 0]) * (t[:, 1] if dy else 1 - t[:, 1])
            out = out + w * _h(i[:, 0] + dx, i[:, 1] + dy, i[:, 2], seed)
    return out
def steps(v, n):
    return np.floor(np.clip(v, 0, 0.9999) * n) / (n - 1)

MX, MY, MH = PADC[2], PADC[3], PADC[4]                   # mouth centre x, y of the scan start, clear height
in_cave = (np.abs(x - MX) < 1.1) & (y > MY - 0.1) & (y < MY + 2.2) & (z < MH + 0.5)
inside = SHELL & (val < 0.21) & in_cave                  # Tripo painted the cavity dark
bone = SMALL & (r - g >= 0.075)
stone = (SHELL | SMALL) & ~inside & ~bone
s_blood = np.clip((r - g - 0.05) / 0.06, 0, 1) * stone                    # how much blood / moss the Tripo colour shows
s_moss = np.clip((g - b - (0.06 - 0.02 * np.clip(N[:, 2], 0, 1))) / 0.05, 0, 1) * SHELL * ~inside * (s_blood < 0.5)
blood = stone & (s_blood > 0.5)
moss = stone & ~blood & (s_moss > 0.5)
rock = stone & ~blood & ~moss
dm = np.hypot(x - MX, y - (MY + 0.25))                   # distance from the mouth threshold, on the pad
pad_in = PAD & (y > MY + 0.55)                           # pad inside the cave: goes black
pad_blood = PAD & ~pad_in & (dm < 1.1) & (vn(x * 2.6, y * 2.6, 5) * 0.65 + vn(x * 7.0, y * 7.0, 6) * 0.35 > 0.56 + 0.2 * (dm / 1.1))

out = np.zeros_like(c)
def graded(q, target, keep, gamma=1.0, lo=0.45, hi=1.7):
    """Zone colour = target hue carried by the Tripo brightness pattern (+ a share of the Tripo hue)."""
    l = np.clip(val[q] / np.median(val[q]), lo, hi) ** gamma
    base = np.array(target)[None, :] * l[:, None]
    tint = c[q] / np.maximum(val[q], 1e-3)[:, None] * (np.max(target) * l)[:, None]
    return np.clip(base * (1 - keep) + tint * keep, 0, 1)
lr = np.clip(val / np.median(val[rock]), 0.45, 1.7)[:, None]              # one brightness pattern for the stone, hues mixed by strength
rock_c = np.array([0.37, 0.37, 0.36])[None, :] * lr ** 1.15
moss_c = np.array([0.25, 0.285, 0.15])[None, :] * lr
blood_c = np.array([0.27, 0.06, 0.05])[None, :] * np.clip(lr, 0.7, 1.3)
mix_ = rock_c * (1 - s_moss[:, None]) + moss_c * s_moss[:, None]
mix_ = mix_ * (1 - s_blood[:, None]) + blood_c * s_blood[:, None]
out[stone] = np.clip(mix_[stone], 0, 1)
out[bone] = graded(bone, (0.69, 0.60, 0.47), 0.10, 0.8)
out[inside] = np.array([0.025, 0.025, 0.028])
earth = np.array([0.27, 0.225, 0.17])[None, :] * (0.82 + 0.3 * steps(vn(x[PAD] * 1.7, y[PAD] * 1.7, 7), 4))[:, None]
dark = np.clip((y[PAD] - (MY + 0.15)) / 0.55, 0, 1)[:, None]           # the earth fades to black going into the cave
out[PAD] = earth * (1 - dark) + np.array([0.025, 0.025, 0.028])[None, :] * dark
bl = np.array([0.25, 0.06, 0.05])[None, :] * (0.85 + 0.3 * vn(x[pad_blood] * 9, y[pad_blood] * 9, 8))[:, None]
out[pad_blood] = out[pad_blood] * 0.25 + bl * 0.75


def bleed(img_, binary):
    filled = m.copy()
    ch = img_.shape[-1]
    for _ in range(8):
        acc = np.zeros((R, R, ch)); cnt = np.zeros((R, R))
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            acc += np.roll(np.roll(img_ * filled[..., None], dy, 0), dx, 1); cnt += np.roll(np.roll(filled, dy, 0), dx, 1)
        new = (~filled) & (cnt > 0)
        a = acc[new] / cnt[new][:, None]
        if binary:
            one = np.zeros_like(a); k = a.argmax(1); one[np.arange(len(a)), k] = (a.max(1) >= 0.5); a = one
        img_[new] = a
        filled |= new
    return img_


def save(path, arr, alpha, noncolor=False):
    im = bpy.data.images.new(os.path.basename(path)[:-4], R, R, alpha=alpha)
    if alpha:
        im.alpha_mode = 'CHANNEL_PACKED'
    if noncolor:
        im.colorspace_settings.name = 'Non-Color'
    im.pixels.foreach_set(arr.astype(np.float32).ravel())
    im.filepath_raw = path; im.file_format = 'PNG'; im.save()
    return im


col = np.zeros((R, R, 3)); col[m] = out
col = bleed(col, False)
save(OUT + 'T_WolfDenTripo_D.png', np.concatenate([col, np.ones((R, R, 1))], -1), False)
ZN = ['R rock', 'G moss', 'B blood', 'A bones']
M = np.stack([rock, moss, blood | pad_blood, bone], -1)
print('ZONES overlap on painted texels: %d' % int((M.sum(1) > 1).sum()))
mk = np.zeros((R, R, 4)); mk[m] = M
mk = bleed(mk, True)
save(OUT + 'T_WolfDenTripo_Mask.png', mk, True, True)

# ---------- checks on the saved files ----------
chk = bpy.data.images.load(OUT + 'T_WolfDenTripo_Mask.png'); chk.alpha_mode = 'CHANNEL_PACKED'; chk.colorspace_settings.name = 'Non-Color'
K = np.array(chk.pixels[:], dtype=np.float32).reshape(R, R, chk.channels)
tex = bpy.data.images.load(OUT + 'T_WolfDenTripo_D.png')
TXP = np.array(tex.pixels[:], dtype=np.float32).reshape(R, R, tex.channels)[..., :3]
print('TEXTURE T_WolfDenTripo_D.png %dx%d %.1f KB | MASK T_WolfDenTripo_Mask.png %dx%d channels=%d %.1f KB values R%s G%s B%s A%s' % (
    tex.size[0], tex.size[1], os.path.getsize(OUT + 'T_WolfDenTripo_D.png') / 1024, chk.size[0], chk.size[1], chk.channels, os.path.getsize(OUT + 'T_WolfDenTripo_Mask.png') / 1024,
    *[np.unique(K[..., i]).round(3) for i in range(4)]))
print('CHECK mask file equals computed zones on painted texels: %s; texels set in two or more channels (whole file): %d' % (
    bool(((K[m] > 0.5) == M).all()), int(((K > 0.5).sum(-1) > 1).sum())))
tc = TXP[m]
for i, n in enumerate(ZN):
    q = M[:, i]
    print('ZONE %-8s texels %6d (%.1f%% of painted): shell %d small parts %d pad %d; mean rgb in the new texture %s (in the Tripo bake %s); mean height %.2f m' % (
        n, q.sum(), 100 * q.mean(), (q & SHELL).sum(), (q & SMALL).sum(), (q & PAD).sum(), np.round(tc[q].mean(0), 2), np.round(c[q].mean(0), 2), z[q].mean()))
none = ~M.any(1)
print('ZONE none     texels %6d (%.1f%%): dark inside %d, ground pad without blood %d, other %d' % (none.sum(), 100 * none.mean(), (none & inside).sum(), (none & PAD).sum(), (none & ~inside & ~PAD).sum()))
print('CHECK inside texels in any channel: %d; pad texels in R/G/A: %d; pad texels in B (blood on the earth): %d' % ((inside & M.any(1)).sum(), (PAD & (M[:, 0] | M[:, 1] | M[:, 3])).sum(), (PAD & M[:, 2]).sum()))
up = N[:, 2] > 0.5
print('CHECK moss sits on top: %.0f%% of moss texels are on faces looking up (rock: %.0f%%)' % (100 * (moss & up).sum() / moss.sum(), 100 * (rock & up).sum() / rock.sum()))
print('CHECK blood near the mouth: %.0f%% of blood texels are within 1.6 m of the mouth centre' % (100 * ((blood | pad_blood) & (np.hypot(x - MX, y - MY) < 1.6)).sum() / (blood | pad_blood).sum()))

tint = np.array([[0.9, 0.1, 0.1], [0.1, 0.8, 0.1], [0.15, 0.3, 1.0], [1.0, 0.9, 0.0]])
ov = TXP.astype(np.float64) * 0.45
for i in range(4):
    q = K[..., i] > 0.5
    ov[q] = ov[q] * 0.5 + tint[i] * 0.55
save(OUT + 'renders/_mask_overlay_uv.png', np.concatenate([ov, np.ones((R, R, 1))], -1), False)
