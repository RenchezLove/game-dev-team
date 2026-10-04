"""Paint T_TentSurvival_D.png and T_TentSurvival_Mask.png (512) for SM_Tent by rules: every texel of UV0 gets its place on the
model (face 'part', local frame of its 'grp') and a colour from that place: faded khaki-green tarp with folds running down from
the ridge, sun-bleached top, dirty hem, worn spots, a seam, stitched patches; dark underside; bark-brown poles with light cut ends.
Mask (read without sRGB): R tarp (both sides), G wood of the poles, B and A empty.
Run: blender.exe -b tent_work.blend --factory-startup --python 11_paint.py
"""
import bpy, os, math
import numpy as np

OUT = 'E:/game-dev-team/assets/tent_survival/'
R = 512
P_TARP, P_TARPIN, P_POLE, P_POLECAP = 1, 2, 3, 4
ob = bpy.data.objects['SM_Tent']
me = ob.data
T = len(me.polygons)
co = np.zeros(len(me.vertices) * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
lv = np.zeros(len(me.loops), np.int32); me.loops.foreach_get('vertex_index', lv)
TV = co[lv].reshape(T, 3, 3)
FN = np.zeros(T * 3); me.polygons.foreach_get('normal', FN); FN = FN.reshape(T, 3)
def fattr(name):
    a = np.zeros(T, np.int32); me.attributes[name].data.foreach_get('value', a); return a
PART, GRP = fattr('part'), fattr('grp')
def uvs(layer):
    a = np.zeros(len(me.loops) * 2); me.uv_layers[layer].data.foreach_get('uv', a); return a.reshape(T, 3, 2)
g = np.load(OUT + '_work/_grp.npz')
GMinv = np.linalg.inv(g['M']); GI = g['I']


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


def _h(ix, iy, iz, seed=0):
    n = (ix.astype(np.int64) * 374761393 + iy.astype(np.int64) * 668265263 + iz.astype(np.int64) * 2147483647 + seed * 974711) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    n = n ^ (n >> 16)
    return (n & 0xFFFFFF) / float(0x1000000)
def hsh(a, b=None, seed=0):
    z_ = np.zeros_like(np.asarray(a, np.float64))
    return _h(np.floor(a), np.floor(z_ if b is None else b), np.floor(z_), seed)
def vn(x_, y_, seed=0):
    p = np.stack([x_, y_, np.zeros_like(x_)], -1)
    f = np.floor(p); t = p - f; t = t * t * (3 - 2 * t); i = f.astype(np.int64)
    out = 0.0
    for dx in (0, 1):
        for dy in (0, 1):
            w = (t[:, 0] if dx else 1 - t[:, 0]) * (t[:, 1] if dy else 1 - t[:, 1])
            out = out + w * _h(i[:, 0] + dx, i[:, 1] + dy, i[:, 2], seed)
    return out
def steps(v, n):
    return np.floor(np.clip(v, 0, 0.9999) * n) / (n - 1)
def col(c, k):
    return np.asarray(c, np.float64)[None, :] * np.asarray(k)[:, None]

TARP = (0.37, 0.40, 0.29); WORN = (0.50, 0.51, 0.42); DIRT = (0.27, 0.24, 0.17); PATCH = (0.44, 0.42, 0.29)
BARK = (0.31, 0.22, 0.14); CUT = (0.58, 0.47, 0.31)
PATCHES = {0: [(0.42, 0.72, 0.38, 0.62), (1.18, 1.36, 0.80, 1.02)], 1: [(0.95, 1.30, 0.22, 0.46)]}     # per tarp: (u0, u1, v0, v1) in metres


def paint(part, L, I, gid):
    n = len(L)
    zone = np.zeros(n, np.int8)            # 0 none, 1 tarp, 2 wood
    if part in (P_TARP, P_TARPIN):
        u, v = L[:, 0], L[:, 1]; ln, sl, side = I[:, 1], I[:, 2], I[:, 4]
        k = v / sl                                                                   # 0 at the ridge, 1 at the hem
        fold = vn(u * 6.5 + 1.2 * vn(u * 2, v * 1.5, 3) + side * 11, v * 0.7, 4)       # folds hang down from the ridge
        c = col(TARP, 0.84 + 0.30 * steps(fold, 4))
        c *= (1.10 - 0.20 * k)[:, None]                                               # bleached by the sun towards the ridge
        c *= (0.94 + 0.12 * steps(vn(u * 2.1 + side * 5, v * 2.1, 5), 3))[:, None]
        worn = vn(u * 3.4 + side * 7, v * 3.4, 6) * 0.7 + vn(u * 11, v * 11, 7) * 0.3
        c = np.where((worn > 0.66)[:, None], c * 0.55 + np.array(WORN)[None, :] * 0.45, c)
        dirt = k + 0.16 * vn(u * 9, v * 4, 8) + 0.05 * vn(u * 30, v * 30, 9)
        c = np.where((dirt > 0.99)[:, None], c * 0.35 + np.array(DIRT)[None, :] * 0.65, np.where((dirt > 0.90)[:, None], c * 0.72 + np.array(DIRT)[None, :] * 0.28, c))
        c[np.abs(v - sl * 0.52) < 0.007] *= 0.62                                      # seam between two widths of cloth
        hem = (u < 0.022) | (ln - u < 0.022) | (sl - v < 0.022)
        c[hem] *= 0.74
        c[v < 0.035] *= 0.80                                                          # shadow under the ridge pole
        if part == P_TARP:
            for s_, rects in PATCHES.items():
                for (u0, u1, v0, v1) in rects:
                    q = (side == s_) & (u > u0) & (u < u1) & (v > v0) & (v < v1)
                    if not q.any():
                        continue
                    pc = col(PATCH, (0.9 + 0.2 * hsh(np.full(q.sum(), u0 * 9 + v0 * 5), seed=10)) * (0.94 + 0.12 * steps(vn(u[q] * 40, v[q] * 3, 11), 3)))
                    edge = (np.minimum(u[q] - u0, u1 - u[q]) < 0.012) | (np.minimum(v[q] - v0, v1 - v[q]) < 0.012)
                    c[q] = np.where(edge[:, None], np.array([0.17, 0.17, 0.12])[None, :], pc)
        else:
            c *= 0.50                                                                 # the underside lies in shade
        zone[:] = 1
        return c, zone
    if part == P_POLE:
        a_, b_, t = L[:, 0], L[:, 1], L[:, 2]; ln, h = I[:, 1], I[:, 2]
        sidei = np.where(np.abs(a_) > np.abs(b_), np.where(a_ > 0, 0, 1), np.where(b_ > 0, 2, 3))
        w = np.where(sidei < 2, b_, a_)                                               # across the side of the pole
        c = col(BARK, (0.88 + 0.22 * hsh(sidei + gid * 4, seed=12)) * (0.82 + 0.36 * steps(vn(t * 5 + gid, w * 55 + sidei * 9, 13), 4)))
        knot = vn(t * 9 + gid * 3, w * 30 + sidei * 5, 14) > 0.84
        c[knot] *= 0.55
        peel = vn(t * 4 + gid * 2, w * 14 + sidei * 3, 15) > 0.80                     # bark peeled off: lighter wood
        c = np.where(peel[:, None], c * 0.4 + np.array(CUT)[None, :] * 0.5, c)
        c[(t < 0.02) | (ln - t < 0.02)] *= 0.75
        zone[:] = 2
        return c, zone
    if part == P_POLECAP:
        a_, b_ = L[:, 0], L[:, 1]; h = I[:, 2]
        r = np.hypot(a_, b_) / h
        c = col(CUT, 0.9 + 0.2 * vn(a_ * 60 + gid, b_ * 60, 16))
        c[(np.abs(r - 0.45) < 0.08)] *= 0.80                                          # a growth ring
        c[np.maximum(np.abs(a_), np.abs(b_)) > h * 0.82] = np.array(BARK) * 0.8       # bark around the cut
        zone[:] = 2
        return c, zone
    return np.tile(np.array([0.05, 0.05, 0.05]), (n, 1)), zone


for layer in ('UVMap', 'LightmapUV'):
    f_, b_, ov = raster(uvs(layer), 0.0)
    u_ = uvs(layer)
    print('UVCHECK %s range %.4f..%.4f overlapping texels at %d: %d, covered %.3f' % (layer, u_.min(), u_.max(), R, ov, (f_ >= 0).mean()))
fid, bar, _ = raster(uvs('UVMap'), 1.5)
m = fid >= 0
f = fid[m]; Wb = bar[m].astype(np.float64)
P = (TV[f] * Wb[:, :, None]).sum(1)
gid = GRP[f]; prt = PART[f]
Mi = GMinv[gid]
L = np.einsum('nij,nj->ni', Mi[:, :3, :3], P) + Mi[:, :3, 3]
I = GI[gid]
out = np.zeros((len(f), 3)); zone = np.zeros(len(f), np.int8)
for p in np.unique(prt):
    s = prt == p
    out[s], zone[s] = paint(int(p), L[s], I[s], gid[s].astype(np.float64))
out = np.clip(out, 0, 1)


def bleed(img_, binary):
    filled = m.copy(); ch = img_.shape[-1]
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


c_img = np.zeros((R, R, 3)); c_img[m] = out
c_img = bleed(c_img, False)
c_img[~(m | (c_img.sum(-1) > 0))] = np.array([0.20, 0.21, 0.15])
save(OUT + 'T_TentSurvival_D.png', np.concatenate([c_img, np.ones((R, R, 1))], -1), False)
ZN = ['R tarp', 'G pole wood', 'B (empty)', 'A (empty)']
M = np.stack([zone == 1, zone == 2, zone == 3, zone == 4], -1)
mk = np.zeros((R, R, 4)); mk[m] = M
mk = bleed(mk, True)
save(OUT + 'T_TentSurvival_Mask.png', mk, True, True)

chk = bpy.data.images.load(OUT + 'T_TentSurvival_Mask.png'); chk.alpha_mode = 'CHANNEL_PACKED'; chk.colorspace_settings.name = 'Non-Color'
K = np.array(chk.pixels[:], dtype=np.float32).reshape(R, R, chk.channels)
tex = bpy.data.images.load(OUT + 'T_TentSurvival_D.png')
TXP = np.array(tex.pixels[:], dtype=np.float32).reshape(R, R, tex.channels)[..., :3]
print('TEXTURE %dx%d %.1f KB | MASK %dx%d channels=%d %.1f KB values R%s G%s B%s A%s' % (tex.size[0], tex.size[1], os.path.getsize(OUT + 'T_TentSurvival_D.png') / 1024,
      chk.size[0], chk.size[1], chk.channels, os.path.getsize(OUT + 'T_TentSurvival_Mask.png') / 1024, *[np.unique(K[..., i]).round(3) for i in range(4)]))
print('CHECK mask file equals computed zones on painted texels: %s; texels set in two or more channels (whole file): %d; painted texels in no channel: %d' % (
    bool(((K[m] > 0.5) == M).all()), int(((K > 0.5).sum(-1) > 1).sum()), int((~M.any(1)).sum())))
PN = {P_TARP: 'tarp', P_TARPIN: 'tarp underside', P_POLE: 'poles', P_POLECAP: 'pole ends'}
tc = TXP[m]
for i, nme in enumerate(ZN):
    q = M[:, i]
    print('ZONE %-12s texels %6d (%.1f%% of painted)%s' % (nme, q.sum(), 100 * q.mean(), '' if not q.any() else ', mean rgb %s; by part: %s' % (np.round(tc[q].mean(0), 2),
          ', '.join('%s %d' % (PN[int(p)], (q & (prt == p)).sum()) for p in np.unique(prt[q])))))
