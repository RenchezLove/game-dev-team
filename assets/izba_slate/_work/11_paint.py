"""Paint T_IzbaSlate_D.png (1024, sRGB) for SM_IzbaSlate: every texel gets its world position
through the UV0 triangles and is coloured by rules per face 'part' (weathered grey logs, slate
with moss, brick, peeled paint ...). Also checks UV0 / UV1 for overlaps.
Run: blender.exe -b izba_work.blend --factory-startup --python 11_paint.py
"""
import bpy, math
import numpy as np

OUT = 'E:/game-dev-team/assets/izba_slate/'
R = 1024
(P_WALL, P_FOUND, P_GLASS, P_DOORLEAF, P_REVEAL, P_SILL, P_CASING, P_DOORFRAME, P_PORCH, P_LOGSIDE, P_LOGCAP,
 P_HIDDEN, P_SHEATH, P_GABLE, P_SLATE, P_SLATE_EDGE, P_RIDGE, P_BARGE, P_CHIM, P_PATCH, P_BOARD, P_SOFFIT) = range(1, 23)
ST, SA = 0.012, 0.045

ob = bpy.data.objects['SM_IzbaSlate']
me = ob.data
T = len(me.polygons)
vco = np.zeros(len(me.vertices) * 3); me.vertices.foreach_get('co', vco); vco = vco.reshape(-1, 3)
lvi = np.zeros(len(me.loops), np.int32); me.loops.foreach_get('vertex_index', lvi)
TV = vco[lvi].reshape(T, 3, 3)
FN = np.zeros(T * 3); me.polygons.foreach_get('normal', FN); FN = FN.reshape(T, 3)
def fattr(name, dt):
    a = np.zeros(T, dt); me.attributes[name].data.foreach_get('value', a); return a
PART, GRP, VIS = fattr('part', np.int32), fattr('grp', np.int32), fattr('vis', np.float32)
def uvs(layer):
    a = np.zeros(len(me.loops) * 2, np.float32); me.uv_layers[layer].data.foreach_get('uv', a); return a.reshape(T, 3, 2).astype(np.float64)
g = np.load(OUT + '_work/_grp.npz')
GMinv = np.linalg.inv(g['M']); GI = g['I']
XN, XP, YN, YP, WTOP, ZR, EAVE_Y, LOGTOP, SZ, TN = g['consts']


def raster(uv, res, pad):
    """-> face id per texel (-1 empty), barycentrics, texels claimed by 2+ triangle interiors."""
    fid = -np.ones((res, res), np.int32); bar = np.zeros((res, res, 3), np.float32)
    best = np.full((res, res), -1e9, np.float32); inner = np.zeros((res, res), np.int16)
    for t in range(len(uv)):
        p = uv[t] * res
        d = (p[1, 0] - p[0, 0]) * (p[2, 1] - p[0, 1]) - (p[1, 1] - p[0, 1]) * (p[2, 0] - p[0, 0])
        if abs(d) < 1e-9:
            continue
        x0 = max(int(math.floor(p[:, 0].min() - pad - 1)), 0); x1 = min(int(math.ceil(p[:, 0].max() + pad + 1)), res)
        y0 = max(int(math.floor(p[:, 1].min() - pad - 1)), 0); y1 = min(int(math.ceil(p[:, 1].max() + pad + 1)), res)
        if x1 <= x0 or y1 <= y0:
            continue
        X, Y = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
        w1 = ((X - p[0, 0]) * (p[2, 1] - p[0, 1]) - (Y - p[0, 1]) * (p[2, 0] - p[0, 0])) / d
        w2 = ((p[1, 0] - p[0, 0]) * (Y - p[0, 1]) - (p[1, 1] - p[0, 1]) * (X - p[0, 0])) / d
        w0 = 1 - w1 - w2
        el = [np.linalg.norm(p[2] - p[1]), np.linalg.norm(p[0] - p[2]), np.linalg.norm(p[1] - p[0])]
        dist = np.minimum(np.minimum(w0 * abs(d) / el[0], w1 * abs(d) / el[1]), w2 * abs(d) / el[2])   # px to nearest edge
        sub_b = best[y0:y1, x0:x1]
        m = (dist > -pad) & (dist > sub_b)
        if m.any():
            sub_b[m] = dist[m]
            fid[y0:y1, x0:x1][m] = t
            W = np.clip(np.stack([w0, w1, w2], -1), 0, None); W /= W.sum(-1, keepdims=True)
            bar[y0:y1, x0:x1][m] = W[m]
        inner[y0:y1, x0:x1] += (dist > 0.6)
    return fid, bar, int((inner > 1).sum())


# ---------- helpers ----------
def C(hx):
    return np.array([int(hx[i:i + 2], 16) / 255.0 for i in (1, 3, 5)])
def _h(ix, iy, iz, seed=0):
    n = (ix.astype(np.int64) * 374761393 + iy.astype(np.int64) * 668265263 + iz.astype(np.int64) * 2147483647 + seed * 974711) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    n = n ^ (n >> 16)
    return (n & 0xFFFFFF) / float(0x1000000)
def hsh(a, b=None, c=None, seed=0):
    z = np.zeros_like(np.asarray(a, np.float64))
    return _h(np.floor(a), np.floor(z if b is None else b), np.floor(z if c is None else c), seed)
def vn(x, y, z=None, seed=0):
    p = np.stack([x, y, np.zeros_like(x) if z is None else z], -1)
    f = np.floor(p); t = p - f; t = t * t * (3 - 2 * t); i = f.astype(np.int64)
    r = 0.0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (t[:, 0] if dx else 1 - t[:, 0]) * (t[:, 1] if dy else 1 - t[:, 1]) * (t[:, 2] if dz else 1 - t[:, 2])
                r = r + w * _h(i[:, 0] + dx, i[:, 1] + dy, i[:, 2] + dz, seed)
    return r
def vn3(P, f, seed=0):
    return vn(P[:, 0] * f, P[:, 1] * f, P[:, 2] * f, seed)
def steps(x, n):
    return np.floor(np.clip(x, 0, 0.9999) * n) / (n - 1)
def mix(a, b, t):
    t = np.asarray(t, np.float64)[:, None]
    return a * (1 - t) + b * t
def tone(c, k):
    return c * np.asarray(k)[:, None]
def frac(x):
    return x - np.floor(x)

WOOD_L, WOOD_M, WOOD_D, WOOD_SEAM = C('#8B887F'), C('#75726B'), C('#5D5B56'), C('#2F2D2A')
PAINT, GLASS_C = C('#9FA6A4'), C('#14181B')
LOGP, LOGH = 0.2830 * SZ, 0.416
def peel(P, base_paint, thr, N):
    """Flaking paint over grey wood."""
    pn = vn3(P, 7.0, 3) * 0.6 + vn3(P, 19.0, 4) * 0.4
    wood = tone(WOOD_M[None, :] * np.ones((len(P), 1)), 0.9 + 0.2 * steps(vn(P[:, 0] * 3, P[:, 1] * 3, P[:, 2] * 22, 5), 3))
    pc = tone(base_paint[None, :] * np.ones((len(P), 1)), 0.93 + 0.1 * steps(vn3(P, 2.5, 6), 3))
    return np.where((pn > thr)[:, None], wood, pc)


def paint(part, P, L, N, NL, I, vis, gid):
    n = len(P); X, Y, Z = P[:, 0], P[:, 1], P[:, 2]
    one = np.ones((n, 1))
    if part == P_WALL:
        xw = np.abs(N[:, 0]) > 0.5
        al = np.where(xw, Y, X); side = xw * 2 + ((N[:, 0] + N[:, 1]) > 0)
        zr = (Z - (LOGTOP + 0.018 - 5 * LOGP)) / LOGP
        k = np.floor(zr); t = zr - k
        col = np.where((t < 0.34)[:, None], WOOD_D, np.where((t < 0.68)[:, None], WOOD_M, WOOD_L))
        col = tone(col, 0.9 + 0.2 * hsh(k, side, seed=1))
        col = tone(col, 0.93 + 0.14 * steps(vn(al * 1.3, Z * 24, side * 3.1, 2), 3))
        crack = (vn(al * 0.9 + k * 7.3, t * 7, side * 5.7, 11) > 0.80) & (t > 0.2) & (t < 0.9)
        col = np.where(crack[:, None], col * 0.6, col)
        col = np.where(((t < 0.055) | (t > 0.945))[:, None], WOOD_SEAM, col)
        col = np.where((k < 0)[:, None], WOOD_D * 0.8, col)
        col = np.where((k > 4)[:, None], WOOD_D * 0.72, col)
        damp = steps(np.clip((0.95 - (Z + 0.45 * (vn(al * 1.1, side * 9.0, seed=5) - 0.5))) / 0.7, 0, 1), 4) * 0.55
        col = mix(col, C('#474B41') * (col.mean(1, keepdims=True) / 0.42), damp)
        col = tone(col, np.where(Z > 2.22, 0.84, 1.0))
        return tone(col, 0.92 + 0.12 * steps(vn3(P, 0.8, 8), 3))
    if part in (P_LOGSIDE,):
        col = np.where((N[:, 2] > 0.5)[:, None], WOOD_L, np.where((N[:, 2] < -0.5)[:, None], WOOD_D, WOOD_M))
        col = tone(col, 0.92 + 0.16 * steps(vn(X * 3, Y * 3, Z * 22, 5), 3))
        return mix(col, C('#474B41') * one, steps(np.clip((0.8 - Z) / 0.7, 0, 1), 3) * 0.45)
    if part == P_LOGCAP:
        u = np.where(I[:, 1] < 0.5, L[:, 1], L[:, 0]) / 1.5; v = L[:, 2] / 1.6
        r = np.sqrt(u * u + v * v); th = np.arctan2(v, u)
        col = tone(C('#918C80') * one, 0.94 + 0.12 * (np.floor(r / 0.022) % 2))
        col = np.where((r < 0.022)[:, None], C('#5B574F'), col)
        col = np.where(((np.abs(np.sin(1.5 * th + gid * 1.7)) < 0.045) & (r > 0.03))[:, None], C('#3D3A36'), col)
        col = np.where((r > 0.118)[:, None], WOOD_D, col)
        return mix(col, C('#474B41') * one, steps(np.clip((0.8 - Z) / 0.7, 0, 1), 3) * 0.4)
    if part == P_FOUND:
        col = tone(C('#605E58') * one, 0.88 + 0.24 * steps(vn3(P, 2.2, 12), 3))
        moss = vn3(P, 3.0, 13) + (0.3 - Z) * 1.3 > 0.82
        return np.where(moss[:, None], C('#3F4937'), col)
    if part == P_GLASS:
        u, v = L[:, 0], L[:, 2]; hw, hh = I[:, 1], I[:, 2]
        bar = (np.minimum(hw, hh) < 0.05) | (np.abs(u) > hw - 0.022) | (np.abs(v) > hh - 0.022)
        fr = peel(P, PAINT * 0.95, 0.52, N)
        gl = np.where(((frac((u + v * 0.6) / 0.42 + gid * 0.37) < 0.2) & (hsh(gid, seed=3) > 0.3))[:, None], C('#232B31'), GLASS_C)
        gl = np.where((v < -hh + 0.07)[:, None], C('#1D1F1E'), gl)
        return np.where(bar[:, None], fr, gl)
    if part == P_DOORLEAF:
        u, v = L[:, 0], L[:, 2]; hw = I[:, 1]
        pk = (u + hw) / 0.15
        col = tone(C('#4E4B46') * one, 0.84 + 0.3 * hsh(pk, seed=4))
        col = np.where((vn(u * 5, v * 3, seed=14) > 0.56)[:, None], tone(C('#55625C') * one, 0.9 + 0.2 * hsh(pk, seed=4)), col)
        col = np.where(((np.abs(v - 0.45) < 0.06) | (np.abs(v + 0.5) < 0.06))[:, None], col * 0.78, col)
        col = np.where((frac(pk) < 0.08)[:, None], C('#1B1A19'), col)
        return np.where(((np.abs(u - 0.30) < 0.025) & (np.abs(v + 0.05) < 0.07))[:, None], C('#151515'), col)
    if part in (P_REVEAL, P_SILL):
        return tone(C('#494743') * one, 0.9 + 0.2 * steps(vn3(P, 4.0, 15), 3))
    if part == P_CASING:
        return peel(P, PAINT, 0.47 + 0.08 * np.clip((Z - 0.6) / 1.6, 0, 1), N)
    if part == P_DOORFRAME:
        return peel(P, C('#939B98'), 0.40, N)
    if part == P_BARGE:
        return peel(P, C('#A3A9A5'), 0.46, N)
    if part == P_PORCH:
        top = N[:, 2] > 0.7
        pk = X / 0.17
        col = tone(C('#7A776F') * one, 0.86 + 0.26 * hsh(pk, seed=6))
        col = tone(col, 0.94 + 0.12 * steps(vn(X * 30, Y * 1.5, seed=16), 3))
        col = np.where((frac(pk) < 0.07)[:, None], C('#2A2927'), col)
        side = tone(C('#5F5D58') * one, 0.85 + 0.3 * hsh(Z / 0.11, seed=7))
        side = np.where((vn3(P, 3.0, 13) + (0.25 - Z) * 1.5 > 0.8)[:, None], C('#3F4937'), side)
        return np.where(top[:, None], col, side)
    if part == P_GABLE:
        front = N[:, 0] < 0
        pk = (Y + 3.0) / 0.17
        col = tone(C('#6F6C66') * one, 0.84 + 0.3 * hsh(pk, front, seed=8))
        col = tone(col, 0.94 + 0.12 * steps(vn(Y * 28, Z * 1.6, front * 3.0, 17), 3))
        col = np.where((frac(pk) < 0.08)[:, None], C('#23211F'), col)
        gone = (~front) & ((np.floor(pk) == 14) | ((np.floor(pk) == 21) & (Z > 3.05)) | ((np.floor(pk) == 9) & (Z < 2.95)))
        col = np.where(gone[:, None], C('#131211'), col)
        col = np.where((Z < WTOP + 0.19)[:, None], peel(P, PAINT * 0.97, 0.5, N), col)
        col = tone(col, np.where((ZR - np.abs(Y) * TN) - Z < 0.16, 0.7, 1.0))
        # attic window on the three-window facade
        cz = WTOP + 0.19 + 0.42; a, b = np.abs(Y), np.abs(Z - cz)
        win = front & (a < 0.33) & (b < 0.27)
        frm = (a > 0.26) | (b > 0.20) | (a < 0.022)
        col = np.where((win & frm)[:, None], peel(P, PAINT, 0.5, N), col)
        return np.where((win & ~frm)[:, None], GLASS_C, col)
    if part == P_SLATE:
        a, b, h = L[:, 0], L[:, 1], L[:, 2]; s, w, ln = I[:, 1], I[:, 4], I[:, 5]
        hr = (h - ST) / SA
        col = tone(C('#858784') * one, 0.92 + 0.15 * hsh(gid, seed=9))
        col = tone(col, np.where(hr < 0.3, 0.83, np.where(hr > 0.8, 1.05, 1.0)))
        col = tone(col, 0.90 + 0.14 * steps(vn(X * 9, np.abs(Y) * 0.9, s, 18), 4))
        col = tone(col, 0.94 + 0.11 * steps(vn3(P, 0.9, 19), 3))
        col = np.where((vn3(P, 5.5, 20) > 0.84)[:, None], mix(col, C('#A2A296') * one, np.full(n, 0.6)), col)
        col = tone(col, np.where(b > ln - 0.045, 0.70, np.where((b < 0.03) | (np.abs(a) > w / 2 - 0.02), 0.84, 1.0)))
        soot = (s > 0) & (np.abs(X + 0.75) < 0.26 + 0.12 * vn(Y * 4, X * 0, seed=23)) & (Y > 0.62)
        col = np.where(soot[:, None], col * 0.74, col)
        rust = (s < 0) & (np.abs(X - 1.75) < 0.30) & (Y < -0.96) & (vn(X * 16, Y * 0.5, seed=24) > 0.52) & (Y > -0.96 - 1.1 * vn(X * 16, X * 0, seed=25))
        col = np.where(rust[:, None], mix(col, C('#6A4636') * one, np.full(n, 0.45)), col)
        ms = vn3(P, 2.6, 21) * 0.6 + vn3(P, 8.0, 22) * 0.25 + 0.45 * (np.abs(Y) / EAVE_Y) ** 3 + 0.10 * (hr < 0.3) + 0.06 * (s > 0)
        col = np.where((ms > 0.84)[:, None], C('#3E4A36'), col)
        return np.where((ms > 0.95)[:, None], C('#4B573B'), col)
    if part == P_SLATE_EDGE:
        return tone(C('#5E605D') * one, 0.9 + 0.2 * hsh(gid, seed=9))
    if part == P_RIDGE:
        rn = vn3(P, 3.2, 31) * 0.7 + vn3(P, 9.0, 32) * 0.3
        col = tone(C('#6C7275') * one, 0.92 + 0.14 * steps(vn3(P, 1.3, 33), 3))
        col = np.where((rn > 0.58)[:, None], C('#6A4636'), col)
        col = np.where((rn > 0.66)[:, None], C('#4E342A'), col)
        return np.where((frac((X + 0.3) / 1.39) < 0.012)[:, None], C('#34373A'), col)
    if part == P_PATCH:
        pn = vn3(P, 6.0, 41)
        col = np.where((pn > 0.6)[:, None], C('#6C7275'), np.where((pn < 0.34)[:, None], C('#4E342A'), C('#6A4636')))
        return col * one
    if part == P_CHIM:
        lx, ly, lz = L[:, 0], L[:, 1], L[:, 2]
        yface = np.abs(NL[:, 1]) > 0.5
        al = np.where(yface, lx, ly); fidn = yface * 2 + ((NL[:, 0] + NL[:, 1]) > 0)
        row = np.floor(lz / 0.078); bx = (al + 0.3 + (row % 2) * 0.13) / 0.26
        hb = hsh(row, bx, fidn, seed=10)
        col = tone(C('#68493F') * one, 0.8 + 0.36 * hb)
        col = np.where((hsh(row, bx, fidn, seed=12) < 0.13)[:, None], C('#3B2B27'), col)
        col = np.where(((frac(lz / 0.078) < 0.15) | (frac(bx) < 0.055))[:, None], C('#8C887E'), col)
        col = mix(col, C('#262321') * one, steps(np.clip((lz - 0.55) / 0.85, 0, 1), 4) * 0.78)
        col = np.where((vn3(P, 3.5, 13) + (0.55 - lz) * 0.9 > 0.85)[:, None], C('#3F4937'), col)
        topf = NL[:, 2] > 0.7
        col = np.where(topf[:, None], C('#2E2927'), col)
        hole = topf & (np.maximum(np.abs(lx), np.abs(ly)) < 0.165) & (lz > 1.38)
        return np.where(hole[:, None], C('#080808'), col)
    if part == P_BOARD:
        lx, lz = L[:, 0], L[:, 2]; hl = I[:, 1]
        col = tone(C('#8D8979') * one, 0.9 + 0.16 * steps(vn(lx * 2 + gid * 3.3, lz * 40, seed=26), 3))
        col = tone(col, np.where(hl - np.abs(lx) < 0.02, 0.78, 1.0))
        nail = ((hl - np.abs(lx)) > 0.05) & ((hl - np.abs(lx)) < 0.078) & (np.abs(np.abs(lz) - 0.035) < 0.012)
        return np.where(nail[:, None], C('#262422'), col)
    if part in (P_SHEATH, P_SOFFIT):
        return C('#2B2926') * one
    return C('#242322') * one


for layer, res in (('UVMap', R), ('LightmapUV', R)):
    f_, b_, ov = raster(uvs(layer), res, 0.0)
    print('UVCHECK %s overlapping texels at %d: %d, covered %.3f' % (layer, res, ov, (f_ >= 0).mean()))

fid, bar, _ = raster(uvs('UVMap'), R, 1.5)
m = fid >= 0
f = fid[m]; W = bar[m].astype(np.float64)
P = (TV[f] * W[:, :, None]).sum(1)
N = FN[f]; gid = GRP[f]; prt = PART[f]; vis = VIS[f]
Mi = GMinv[gid]
L = np.einsum('nij,nj->ni', Mi[:, :3, :3], P) + Mi[:, :3, 3]
NL = np.einsum('nij,nj->ni', Mi[:, :3, :3], N)
I = GI[gid]
col = np.zeros((len(f), 3))
for p in np.unique(prt):
    s = prt == p
    col[s] = paint(int(p), P[s], L[s], N[s], NL[s], I[s], vis[s], gid[s].astype(np.float64))
ao = np.where(prt == P_SLATE, 1.0, 0.74 + 0.26 * np.clip(vis, 0, 1) ** 0.8)
col = np.clip(col * ao[:, None], 0, 1)
img = np.zeros((R, R, 3)); img[m] = col
filled = m.copy()
for _ in range(8):                                   # bleed past island borders
    acc = np.zeros_like(img); cnt = np.zeros((R, R))
    for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)):
        acc += np.roll(np.roll(img * filled[..., None], dy, 0), dx, 1); cnt += np.roll(np.roll(filled, dy, 0), dx, 1)
    new = (~filled) & (cnt > 0)
    img[new] = acc[new] / cnt[new][:, None]
    filled |= new
img[~filled] = C('#3A3937')
px = np.concatenate([img, np.ones((R, R, 1))], -1).astype(np.float32)
im = bpy.data.images.new('T_IzbaSlate_D', R, R, alpha=False)
im.pixels.foreach_set(px.ravel())
im.filepath_raw = OUT + 'T_IzbaSlate_D.png'
im.file_format = 'PNG'
sc = bpy.context.scene
sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGB'
im.save_render(OUT + 'T_IzbaSlate_D.png', scene=sc) if False else im.save()
print('TEXTURE', im.filepath_raw, 'texels painted %.3f' % m.mean(), 'mean rgb', img[m].mean(0).round(3))

tex = bpy.data.images.load(OUT + 'T_IzbaSlate_D.png')
mat = me.materials[0]
nt = mat.node_tree
bs = [n_ for n_ in nt.nodes if n_.type == 'BSDF_PRINCIPLED'][0]
for n_ in [n_ for n_ in nt.nodes if n_.type == 'TEX_IMAGE']:
    nt.nodes.remove(n_)
tn = nt.nodes.new('ShaderNodeTexImage'); tn.image = tex; tn.interpolation = 'Closest'
nt.links.new(tn.outputs['Color'], bs.inputs['Base Color'])
bs.inputs['Roughness'].default_value = 0.9
bpy.ops.wm.save_as_mainfile(filepath=OUT + '_work/izba_work.blend')
