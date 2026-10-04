"""Paint T_BanditShedTripo_D.png and T_BanditShedTripo_Mask.png (1024) for SM_BanditShed by rules: every texel of
UV0 gets its place on the model (face 'part', position, local frame of its 'grp') and a colour from that place:
dark grey planks with gaps and nailed board patches, boarded window, door frame, the red paint mark by the door,
plank door and step, red rag, rusty tin, weathered slate sheets, dark sheathing and doorway.
The slate and tin sheets are flat quads: their waves are painted (WAVE m per wave across the sheet).
Mask: R wood of walls / door / step / boards, G slate, B rusty tin, A red rags (door and roof) + red mark; dark openings = 0.
Run: blender.exe -b banditshed_work.blend --factory-startup --python 11_paint.py
"""
import bpy, os, math
import numpy as np

OUT = 'E:/game-dev-team/assets/banditshed_tripo/'
R = 1024
(P_WALL, P_GABLE, P_RECESS, P_DOOR, P_STEP, P_RAG, P_BOARD, P_TINPATCH, P_SHEATH, P_SOFFIT,
 P_SLATE, P_TINROOF, P_RIDGE, P_BOTTOM, P_ROOFRAG) = range(1, 16)
WAVE = 0.2095                    # painted wave pitch: 6 waves on a whole sheet
ob = bpy.data.objects['SM_BanditShed']
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
WX, WY, WH, ZE, ZR, TN, HX, HY, DX, DH, WN0, WN1, WZ0, WZ1 = g['consts']


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
def frac(v):
    return v - np.floor(v)
def col(c, k):
    return np.asarray(c, np.float64)[None, :] * np.asarray(k)[:, None]
def seg_dist(u, v, a, b):
    ax, ay = a; bx, by = b
    t = np.clip(((u - ax) * (bx - ax) + (v - ay) * (by - ay)) / ((bx - ax) ** 2 + (by - ay) ** 2), 0, 1)
    return np.hypot(u - (ax + t * (bx - ax)), v - (ay + t * (by - ay)))

WOOD = (0.255, 0.245, 0.23); PATCHW = (0.37, 0.32, 0.265); DARK = (0.03, 0.03, 0.035)
PATCHES = {0: [(-2.25, -0.95, 0.50, 0.68), (-2.3, -1.3, 1.45, 1.60), (0.95, 1.80, 0.55, 0.70)],        # front (u = x)
           1: [(-1.8, -0.4, 0.90, 1.08), (0.3, 1.9, 1.50, 1.66), (-0.5, 0.9, 0.35, 0.50)],            # back (u = x)
           2: [(0.2, 1.3, 1.20, 1.36), (0.1, 1.2, 0.50, 0.66)],                                       # left side (u = y)
           3: [(-1.2, 0.2, 1.30, 1.46), (-0.3, 1.2, 0.60, 0.76), (0.55, 1.1, 0.20, 1.40)]}            # right side (u = y)
MARK = [((0.74, 1.80), (0.96, 0.95)), ((0.88, 1.84), (1.10, 0.98)), ((1.03, 1.82), (1.22, 1.08)), ((0.66, 1.52), (1.24, 1.64)), ((0.68, 1.22), (1.22, 1.32))]


def planks(u, v, wid, seed, base, pitch=0.19):
    pk = (u + 20.0) / pitch + hsh(np.full_like(u, wid), seed=seed) * 0.5
    c = col(base, (0.78 + 0.40 * hsh(pk, np.full_like(u, wid), seed)) * (0.93 + 0.14 * steps(vn(u * 28, v * 1.6, seed + 1), 3)))
    gap = frac(pk) < 0.055
    return np.where(gap[:, None], np.array([0.06, 0.055, 0.05])[None, :], c)


def paint(part, P, L, N, NL, I, gid):
    n = len(P); x, y, z = P[:, 0], P[:, 1], P[:, 2]
    zone = np.zeros(n, np.int8)            # 0 none, 1 wood, 2 slate, 3 tin, 4 red
    if part in (P_WALL, P_GABLE):
        xw = np.abs(N[:, 0]) > 0.5
        wid = np.where(xw, np.where(N[:, 0] < 0, 2, 3), np.where(N[:, 1] < 0, 0, 1))
        u = np.where(xw, y, x)
        c = planks(u, z, wid, 3, WOOD)
        c *= (0.80 + 0.20 * np.clip(z / 0.6, 0, 1))[:, None]                      # damp near the ground
        c *= np.where(z > ZR - np.abs(np.where(xw, y, 0 * y + HY)) * TN - 0.22, 0.80, 1.0)[:, None] if part == P_GABLE else np.where(z > WH - 0.28, 0.78, 1.0)[:, None]
        zone[:] = 1
        if part == P_WALL:
            for w_, rects in PATCHES.items():
                for (u0, u1, z0, z1) in rects:
                    q = (wid == w_) & (u > u0) & (u < u1) & (z > z0) & (z < z1)
                    if not q.any():
                        continue
                    horiz = (u1 - u0) > (z1 - z0)
                    al = np.where(horiz, u, z)[q]; ac = np.where(horiz, z, u)[q]
                    pc = col(PATCHW, (0.85 + 0.25 * hsh(np.full(q.sum(), u0 * 7 + z0 * 13), seed=5)) * (0.92 + 0.16 * steps(vn(al * 2.2, ac * 34, 6), 3)))
                    edge = (np.minimum(u[q] - u0, u1 - u[q]) < 0.012) | (np.minimum(z[q] - z0, z1 - z[q]) < 0.012)
                    c[q] = np.where(edge[:, None], np.array([0.09, 0.08, 0.07])[None, :], pc)
            fr = wid == 0
            frame = fr & (((np.abs(x) > DX) & (np.abs(x) < DX + 0.10) & (z < DH + 0.10)) | ((np.abs(x) < DX + 0.10) & (z > DH) & (z < DH + 0.10)))
            c[frame] = col((0.33, 0.29, 0.25), 0.9 + 0.2 * steps(vn(x[frame] * 3, z[frame] * 30, 8), 3))
            wf = fr & (x > WN0 - 0.08) & (x < WN1 + 0.08) & (z > WZ0 - 0.08) & (z < WZ1 + 0.08)
            c[wf] = col((0.31, 0.275, 0.235), 0.9 + 0.2 * steps(vn(x[wf] * 30, z[wf] * 3, 9), 3))
            hole = fr & (x > WN0) & (x < WN1) & (z > WZ0) & (z < WZ1)
            c[hole] = np.array(DARK); zone[hole] = 0
            d = np.full(n, 9.0)
            for a, b in MARK:
                d = np.minimum(d, seg_dist(x, z, a, b))
            wob = vn(x * 22, z * 22, 12)
            mark = fr & (d < 0.030 + 0.022 * wob) & (vn(x * 60, z * 9, 13) > 0.16) & (np.abs(x) > DX + 0.10)
            c[mark] = c[mark] * 0.15 + col((0.44, 0.10, 0.075), 0.85 + 0.3 * vn(x[mark] * 30, z[mark] * 30, 14)) * 0.85
            zone[mark] = 4
        return c, zone
    if part == P_RECESS:
        c = np.tile(np.array(DARK), (n, 1))
        fl = N[:, 2] > 0.5
        c[fl] = col((0.10, 0.09, 0.08), 0.8 + 0.4 * hsh(x[fl] / 0.2, seed=15)) * np.clip(1 - (y[fl] + WY) / 0.6, 0.15, 1)[:, None]
        return c, zone
    if part == P_DOOR:
        lx, lz = L[:, 0], L[:, 2]
        c = planks(lx, lz, np.full(n, 7.0), 16, (0.37, 0.33, 0.28))
        bat = (np.abs(lz - 0.45) < 0.07) | (np.abs(lz - 1.08) < 0.07) | (np.abs(lz - 1.72) < 0.07)
        c[bat] = col((0.41, 0.36, 0.30), 0.9 + 0.2 * steps(vn(lx[bat] * 3, lz[bat] * 30, 17), 3))
        c[(np.abs(np.abs(lz - 1.08) - 0.07) < 0.008) | (np.abs(np.abs(lz - 0.45) - 0.07) < 0.008) | (np.abs(np.abs(lz - 1.72) - 0.07) < 0.008)] *= 0.45
        zone[:] = 1
        return c, zone
    if part == P_STEP:
        top = N[:, 2] > 0.5
        pk = (y + 5) / 0.145
        c = col((0.34, 0.30, 0.26), (0.8 + 0.35 * hsh(pk, seed=18)) * (0.92 + 0.16 * steps(vn(x * 2.5, y * 30, 19), 3)))
        c[top & (frac(pk) < 0.08)] = np.array([0.07, 0.06, 0.055])
        c[~top] *= 0.72
        zone[:] = 1
        return c, zone
    if part == P_RAG:
        fold = 0.80 + 0.22 * np.sin(x * 26 + z * 9) * 0.5 + 0.2 * vn(x * 9, z * 9, 20)
        c = col((0.47, 0.115, 0.095), fold * np.clip(0.75 + (z - 1.55) * 0.45, 0.7, 1.05))
        zone[:] = 4
        return c, zone
    if part == P_ROOFRAG:                                    # same red as the rag over the door; folds run down the slope
        fold = 0.90 + 0.13 * np.sin(x * 21 + y * 2.5) + 0.2 * vn(x * 8, y * 8, 40)
        c = col((0.47, 0.115, 0.095), fold * (0.94 + 0.12 * steps(vn(x * 3, y * 3, 41), 3)))
        zone[:] = 4
        return c, zone
    if part == P_BOARD:
        lx, lz = L[:, 0], L[:, 2]; hl = I[:, 1]
        c = col((0.42, 0.37, 0.30), (0.88 + 0.2 * hsh(gid * 3.7, seed=21)) * (0.9 + 0.2 * steps(vn(lx * 2.2 + gid, lz * 40, 22), 3)))
        c[hl - np.abs(lx) < 0.02] *= 0.75
        nail = ((hl - np.abs(lx)) > 0.05) & ((hl - np.abs(lx)) < 0.08) & (np.abs(np.abs(lz) - 0.035) < 0.012)
        c[nail] = np.array([0.08, 0.075, 0.07])
        zone[:] = 1
        return c, zone
    if part in (P_TINPATCH, P_TINROOF):
        if part == P_TINPATCH:
            a_, b_ = L[:, 0], L[:, 2]; wave = np.sin(a_ * 2 * math.pi / 0.085)
            edge = (I[:, 1] - np.abs(a_) < 0.015) | (I[:, 2] - np.abs(b_) < 0.015)
        else:
            a_, b_ = L[:, 0], L[:, 1]; wave = np.cos((a_ + I[:, 4] / 2) * 2 * math.pi / WAVE)
            edge = (b_ > I[:, 5] - 0.04) | (I[:, 4] / 2 - np.abs(a_) < 0.015)
        rn = vn(a_ * 3.2 + gid, b_ * 2.4, 23) * 0.6 + vn(a_ * 11, b_ * 9, 24) * 0.4
        c = col((0.30, 0.175, 0.12), 0.85 + 0.3 * rn)
        c = np.where((rn > 0.62)[:, None], col((0.38, 0.205, 0.12), 0.9 + 0.2 * rn), c)
        c = np.where((rn < 0.36)[:, None], col((0.23, 0.14, 0.105), 0.9 + 0.3 * rn), c)
        grey = vn(a_ * 5 + 3, b_ * 5, 25) > 0.80                      # leftovers of the zinc coat
        c = np.where(grey[:, None], col((0.30, 0.30, 0.29), 0.9 + 0.2 * rn), c)
        c *= (0.86 + 0.18 * wave)[:, None] if part == P_TINROOF else (0.88 + 0.14 * wave)[:, None]
        c *= (0.9 + 0.1 * steps(vn(a_ * 14, b_ * 0.7, 26), 3))[:, None]             # streaks down the sheet
        c[edge] *= 0.6
        zone[:] = 3
        return c, zone
    if part == P_SLATE:
        a_, b_ = L[:, 0], L[:, 1]; s_, w_, ln = I[:, 1], I[:, 4], I[:, 5]
        ph = (a_ + w_ / 2) * 2 * math.pi / WAVE
        hr = 0.5 + 0.5 * np.cos(ph)                                              # painted wave: 1 on a crest, 0 in a trough
        c = col((0.40, 0.385, 0.355), 0.86 + 0.24 * hsh(gid * 1.3, seed=27))
        c *= np.where(hr < 0.3, 0.72, np.where(hr > 0.8, 1.10, np.where(np.sin(ph) > 0, 1.0, 0.90)))[:, None]   # trough, crest, lit and shaded flanks
        c *= (0.88 + 0.16 * steps(vn(x * 9, np.abs(y) * 0.9 + s_, 28), 4))[:, None]
        c *= (0.92 + 0.14 * steps(vn(x * 0.9, y * 0.9, 29), 3))[:, None]
        c = np.where((vn(x * 5.5, y * 5.5, 30) > 0.87)[:, None], c * 0.65 + np.array([0.48, 0.46, 0.41])[None, :] * 0.35, c)    # lichen
        c *= np.where(b_ > ln - 0.045, 0.66, np.where((b_ < 0.03) | (w_ / 2 - np.abs(a_) < 0.018), 0.82, 1.0))[:, None]
        ck = hsh(gid * 2.1, seed=31)
        crack = (ck < 0.4) & (np.abs(a_ - (ck - 0.2) * w_ - 0.06 * np.sin(b_ * 7 + gid)) < 0.007) & (b_ > ln * 0.25)
        c[crack] = np.array([0.08, 0.075, 0.07])
        ms = vn(x * 2.6, y * 2.6, 32) * 0.6 + vn(x * 8, y * 8, 33) * 0.25 + 0.42 * (np.abs(y) / HY) ** 3 + 0.08 * (hr < 0.3)
        c = np.where((ms > 0.90)[:, None], np.array([0.24, 0.27, 0.19])[None, :], c)                                       # a little moss at the eaves
        zone[:] = 2
        return c, zone
    if part == P_RIDGE:
        pk = (x + 20) / 1.3
        c = col((0.30, 0.27, 0.24), (0.85 + 0.25 * hsh(pk, N[:, 1] > 0, seed=34)) * (0.92 + 0.16 * steps(vn(x * 2.2, y * 30, 35), 3)))
        c[frac(pk) < 0.012] *= 0.4
        zone[:] = 1
        return c, zone
    if part == P_SHEATH:
        return col((0.07, 0.065, 0.06), 0.8 + 0.4 * hsh((x + 20) / 0.16, seed=36)), zone
    if part == P_SOFFIT:
        return col((0.10, 0.09, 0.08), 0.8 + 0.4 * hsh((x + 20) / 0.19, seed=37)), zone
    return np.tile(np.array([0.05, 0.05, 0.05]), (n, 1)), zone


for layer in ('UVMap', 'LightmapUV'):
    f_, b_, ov = raster(uvs(layer), 0.0)
    u_ = uvs(layer)
    print('UVCHECK %s range %.4f..%.4f overlapping texels at 1024: %d, covered %.3f' % (layer, u_.min(), u_.max(), ov, (f_ >= 0).mean()))
fid, bar, _ = raster(uvs('UVMap'), 1.5)
m = fid >= 0
f = fid[m]; Wb = bar[m].astype(np.float64)
P = (TV[f] * Wb[:, :, None]).sum(1)
N = FN[f]; gid = GRP[f]; prt = PART[f]
Mi = GMinv[gid]
L = np.einsum('nij,nj->ni', Mi[:, :3, :3], P) + Mi[:, :3, 3]
NL = np.einsum('nij,nj->ni', Mi[:, :3, :3], N)
I = GI[gid]
out = np.zeros((len(f), 3)); zone = np.zeros(len(f), np.int8)
for p in np.unique(prt):
    s = prt == p
    out[s], zone[s] = paint(int(p), P[s], L[s], N[s], NL[s], I[s], gid[s].astype(np.float64))
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
c_img[~(m | (c_img.sum(-1) > 0))] = np.array([0.12, 0.115, 0.11])
save(OUT + 'T_BanditShedTripo_D.png', np.concatenate([c_img, np.ones((R, R, 1))], -1), False)
ZN = ['R wood', 'G slate', 'B rusty tin', 'A red rag + mark']
M = np.stack([zone == 1, zone == 2, zone == 3, zone == 4], -1)
mk = np.zeros((R, R, 4)); mk[m] = M
mk = bleed(mk, True)
save(OUT + 'T_BanditShedTripo_Mask.png', mk, True, True)

chk = bpy.data.images.load(OUT + 'T_BanditShedTripo_Mask.png'); chk.alpha_mode = 'CHANNEL_PACKED'; chk.colorspace_settings.name = 'Non-Color'
K = np.array(chk.pixels[:], dtype=np.float32).reshape(R, R, chk.channels)
tex = bpy.data.images.load(OUT + 'T_BanditShedTripo_D.png')
TXP = np.array(tex.pixels[:], dtype=np.float32).reshape(R, R, tex.channels)[..., :3]
print('TEXTURE %dx%d %.1f KB | MASK %dx%d channels=%d %.1f KB values R%s G%s B%s A%s' % (tex.size[0], tex.size[1], os.path.getsize(OUT + 'T_BanditShedTripo_D.png') / 1024,
      chk.size[0], chk.size[1], chk.channels, os.path.getsize(OUT + 'T_BanditShedTripo_Mask.png') / 1024, *[np.unique(K[..., i]).round(3) for i in range(4)]))
print('CHECK mask file equals computed zones on painted texels: %s; texels set in two or more channels (whole file): %d' % (bool(((K[m] > 0.5) == M).all()), int(((K > 0.5).sum(-1) > 1).sum())))
PN = {P_ROOFRAG: 'roof rag', P_WALL: 'walls', P_GABLE: 'gables', P_RECESS: 'doorway', P_DOOR: 'door', P_STEP: 'step', P_RAG: 'rag', P_BOARD: 'window boards', P_TINPATCH: 'tin patches',
      P_SHEATH: 'sheathing', P_SOFFIT: 'soffit', P_SLATE: 'slate', P_TINROOF: 'tin roof sheet', P_RIDGE: 'ridge', P_BOTTOM: 'bottom'}
tc = TXP[m]
for i, nme in enumerate(ZN):
    q = M[:, i]
    print('ZONE %-18s texels %6d (%.1f%% of painted), mean rgb %s; by part: %s' % (nme, q.sum(), 100 * q.mean(), np.round(tc[q].mean(0), 2),
          ', '.join('%s %d' % (PN[int(p)], (q & (prt == p)).sum()) for p in np.unique(prt[q]))))
none = ~M.any(1)
print('ZONE none               texels %6d (%.1f%%); by part: %s' % (none.sum(), 100 * none.mean(), ', '.join('%s %d' % (PN[int(p)], (none & (prt == p)).sum()) for p in np.unique(prt[none]))))
redc = (tc[:, 0] > 0.3) & (tc[:, 0] > 2.5 * tc[:, 2]) & (tc[:, 0] > 2.2 * tc[:, 1])
print('CHECK by colour: strongly red texels %d, of them in A %d; rust-brown texels (r > 1.5 b, not red) %d, of them in B %d' % (
    redc.sum(), (redc & M[:, 3]).sum(), ((tc[:, 0] > 1.5 * tc[:, 2]) & ~redc & (tc[:, 0] > 0.2)).sum(), ((tc[:, 0] > 1.5 * tc[:, 2]) & ~redc & (tc[:, 0] > 0.2) & M[:, 2]).sum()))

tint = np.array([[0.9, 0.1, 0.1], [0.1, 0.8, 0.1], [0.15, 0.3, 1.0], [1.0, 0.9, 0.0]])
ov = TXP.astype(np.float64) * 0.45
for i in range(4):
    q = K[..., i] > 0.5
    ov[q] = ov[q] * 0.5 + tint[i] * 0.55
save(OUT + 'renders/qc_mask_overlay_uv.png', np.concatenate([ov, np.ones((R, R, 1))], -1), False)
