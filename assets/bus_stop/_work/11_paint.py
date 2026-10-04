"""Paint T_BusStop_D.png and T_BusStop_Mask.png (1024) shared by SM_BusStop, SM_BusStopSign, SM_BusStopUrn: every texel of
UV0 gets its place on the model (face 'part', position) and a colour from that place.
Roof, urn and wall profile are painted in LIGHT NEUTRAL GREYS (ribs, dirt, rust, wear - by brightness only): in the game their
colour = texture x tint.  Wood has its own colour.  Sign, timetable and notices take the picture from the source textures.
Mask (read without sRGB): R roof, G urn, B wall profile (back and side walls), A wood; sign, pole, plates, notices = 0.
Also writes _work/_preview_tinted.png: the colour texture with the default tints applied (for preview renders only).
Run: blender.exe -b busstop_work.blend --factory-startup --python 11_paint.py
"""
import bpy, os, math
import numpy as np

OUT = 'E:/game-dev-team/assets/bus_stop/'
SRCT = 'C:/Users/pgr40/Desktop/GamdevAITeam/Автобусная остановка/old-russian-bus-stop/textures/'
R = 1024
NAMES = ['SM_BusStop', 'SM_BusStopSign', 'SM_BusStopUrn']
(P_ROOF, P_ROOFUNDER, P_ROOFEDGE, P_WALL, P_FENCE, P_POST, P_BEAM, P_RAFTER, P_RAIL, P_BENCH, P_BENCHLEG,
 P_SCHED, P_PLATEBACK, P_AD) = range(1, 15)
P_POLE, P_SIGNFACE, P_SIGNBACK, P_BRACKET = 20, 21, 22, 23
P_URNOUT, P_URNIN, P_URNRIM, P_URNBOTTOM = 30, 31, 32, 33
# default tints (linear RGB) for the three tinted zones: a faded village stop
TINT = {'roof': (0.50, 0.56, 0.60), 'urn': (0.62, 0.58, 0.50), 'profile': (0.22, 0.42, 0.62)}
g = np.load(OUT + '_work/_grp.npz')
GMinv = np.linalg.inv(g['M']); GI = g['I']; DEC = g['DEC']; PLACE = g['PLACE']
RX, Y0, D_BACK, D_FRONT, D_BP, D_FP, WALL_H, FENCE_H, BENCH_D, URN_R, URN_H, URN_T, URN_FLOOR, POLE_R, POLE_H, XP = g['consts']

TV, FN, PART, GRP, OBJ, UV0 = [], [], [], [], [], []
for k, name in enumerate(NAMES):
    me = bpy.data.objects[name].data; T = len(me.polygons)
    co = np.zeros(len(me.vertices) * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    lv = np.zeros(len(me.loops), np.int32); me.loops.foreach_get('vertex_index', lv)
    TV.append(co[lv].reshape(T, 3, 3))                        # object-local coordinates
    n = np.zeros(T * 3); me.polygons.foreach_get('normal', n); FN.append(n.reshape(T, 3))
    for lst, an in ((PART, 'part'), (GRP, 'grp')):
        a = np.zeros(T, np.int32); me.attributes[an].data.foreach_get('value', a); lst.append(a)
    OBJ.append(np.full(T, k, np.int32))
    a = np.zeros(len(me.loops) * 2); me.uv_layers['UVMap'].data.foreach_get('uv', a); UV0.append(a.reshape(T, 3, 2))
TV, FN, PART, GRP, OBJ, UV0 = [np.concatenate(a) for a in (TV, FN, PART, GRP, OBJ, UV0)]
SRC = []
for f in ('DefaultMaterial_Base_Color.png', 'Материал.001_Base_Color.png'):
    im = bpy.data.images.load(SRCT + f)
    SRC.append(np.array(im.pixels[:], dtype=np.float32).reshape(im.size[1], im.size[0], im.channels)[..., :3])
    print('SOURCE texture %s %dx%d' % (f, im.size[0], im.size[1]))


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
def grey(k):
    return np.repeat(np.asarray(k, np.float64)[:, None], 3, 1)

WOOD = (0.44, 0.36, 0.27); METAL = (0.50, 0.51, 0.52); RUST = (0.42, 0.25, 0.16)


def ribs(u, pitch, lit=1.0):
    """Trapezoid profile seen face-on: crest, lit flank, shaded flank, valley -> brightness."""
    t = frac(u / pitch)
    return np.where(t < 0.36, 1.0, np.where(t < 0.47, 0.80 if lit > 0 else 1.06, np.where(t < 0.89, 0.88, 1.06 if lit > 0 else 0.80)))
def wear(a, b, seed):
    """Neutral dirt and rust: 1 = clean; dark blotches with speckled edges."""
    n1 = vn(a * 1.7, b * 1.7, seed) * 0.6 + vn(a * 6, b * 6, seed + 1) * 0.3 + vn(a * 19, b * 19, seed + 2) * 0.1
    return np.where(n1 > 0.70, 0.62, np.where(n1 > 0.63, 0.80, np.where(n1 < 0.30, 1.05, 1.0)))
def wood(al, ac, seed, base=WOOD):
    c = col(base, (0.86 + 0.26 * hsh(np.full_like(al, seed * 1.7), seed=seed)) * (0.84 + 0.30 * steps(vn(al * 2.4 + seed, ac * 48 + seed * 3, 40 + seed % 7), 4)))
    c[vn(al * 6 + seed, ac * 26, 50) > 0.83] *= 0.62                                 # knots and cracks
    c = np.where((vn(al * 1.3 + seed * 2, ac * 5, 51) > 0.72)[:, None], c * 0.75 + np.array([0.50, 0.49, 0.46])[None, :] * 0.25, c)     # weathered grey
    return c
def metal(a, b, seed):
    rn = vn(a * 4 + seed, b * 3, 60) * 0.6 + vn(a * 15, b * 15, 61) * 0.4
    c = col(METAL, 0.85 + 0.25 * steps(vn(a * 2, b * 9 + seed, 62), 4))
    return np.where((rn > 0.66)[:, None], col(RUST, 0.8 + 0.5 * rn), c)
def sample(img, u, v):
    H, W = img.shape[:2]
    x = np.clip(u * W - 0.5, 0, W - 1.001); y = np.clip(v * H - 0.5, 0, H - 1.001)
    x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int); fx = (x - x0)[:, None]; fy = (y - y0)[:, None]
    return (img[y0, x0] * (1 - fx) + img[y0, x0 + 1] * fx) * (1 - fy) + (img[y0 + 1, x0] * (1 - fx) + img[y0 + 1, x0 + 1] * fx) * fy


def paint(part, P, N, L, I, gid):
    n = len(P); x, y, z = P[:, 0], P[:, 1], P[:, 2]
    zone = np.zeros(n, np.int8)            # 0 none, 1 roof, 2 urn, 3 profile, 4 wood
    if part in (P_ROOF, P_ROOFUNDER):
        d = Y0 - y                                                                    # 0.95 at the open edge, -0.45 at the back
        k = ribs(x + RX + 0.05, 0.335) * 0.80
        k *= 0.93 + 0.10 * steps(vn(x * 0.8, y * 0.8, 1), 3)
        k *= wear(x, y * 1.6, 2)
        k *= np.where(vn(x * 14, y * 0.9, 5) > 0.74, 0.90, 1.0)                        # dirt streaks down the slope
        k *= np.clip(0.80 + (d - D_BACK) / 0.5, 0.80, 1.0)                             # dirt gathers at the low back edge
        sheet = frac((x + RX) / 1.175)
        k = np.where((sheet < 0.012) | (sheet > 0.988), k * 0.55, k)                   # overlaps of the four sheets
        for dc in (D_BP, D_FP):                                                        # rows of screws into the beams, and the beams showing as a faint band
            row = np.abs(d - dc)
            k = np.where(row < 0.08, k * 0.95, k)
            k = np.where((row < 0.016) & (np.abs(frac((x + RX + 0.05) / 0.335) - 0.18) < 0.05), 0.30, k)
        for sx in (-1, 1):                                                             # rafters under the sheet
            k = np.where(np.abs(x - sx * XP) < 0.06, k * 0.95, k)
        edge = (RX - np.abs(x) < 0.03) | (d > D_FRONT - 0.03) | (d < D_BACK + 0.03)
        k = np.where(edge, k * 0.78, k)
        if part == P_ROOFUNDER:
            k = ribs(x + RX + 0.05, 0.335, -1) * 0.50 * (0.9 + 0.2 * vn(x * 3, y * 3, 6))
        zone[:] = 1
        return grey(k), zone
    if part == P_ROOFEDGE:
        along = np.where(np.abs(N[:, 0]) > 0.5, y, x + RX + 0.05)
        k = np.where(np.abs(N[:, 0]) > 0.5, 0.62, np.where(frac(along / 0.335) < 0.42, 0.74, 0.40)) * (0.9 + 0.2 * vn(along * 5, z * 30, 7))
        zone[:] = 1
        return grey(k), zone
    if part in (P_WALL, P_FENCE):
        xw = np.abs(N[:, 0]) > 0.5
        u = np.where(xw, y, x); top = N[:, 2] > 0.5
        side = np.where(xw, np.where(N[:, 0] > 0, 1.0, 2.0), np.where(N[:, 1] > 0, 3.0, 4.0))
        k = ribs(u + 7.03, 0.20) * 0.80
        k *= 0.93 + 0.10 * steps(vn(u * 0.9 + side * 3, z * 0.9, 10), 3)
        k *= wear(u + side * 5, z, 11)
        k *= np.clip(0.72 + z / 0.45, 0.72, 1.0)                                       # mud splashed up from the ground
        k *= np.where(vn(u * 16 + side, z * 0.8, 12) > 0.76, 0.91, 1.0)                # streaks
        h = np.where(part == P_WALL, WALL_H, FENCE_H)
        k = np.where((h - z < 0.025) | top, k * 0.72, k)
        if part == P_WALL:                                                             # screw rows into two cross rails
            for zr in (0.55, 1.75):
                k = np.where((np.abs(z - zr) < 0.014) & (np.abs(frac((u + 7.03) / 0.20) - 0.68) < 0.07), 0.32, k)
            k = np.where(side == 3.0, k * 0.92, k)
        zone[:] = 3
        return grey(k), zone
    if part in (P_POST, P_BENCHLEG):
        ac = np.where(np.abs(N[:, 0]) > 0.5, y, x)
        seed = np.round(x * 3 + y * 7).astype(int) % 5 + (3 if part == P_POST else 9)
        c = np.zeros((n, 3))
        for s_ in np.unique(seed):
            q = seed == s_
            c[q] = wood(z[q], ac[q], int(s_))
        c *= np.clip(0.70 + z / 0.5, 0.70, 1.0)[:, None]
        zone[:] = 4
        return c, zone
    if part in (P_BEAM, P_RAFTER, P_RAIL):
        if part == P_BEAM:
            al, ac = x, np.where(np.abs(N[:, 2]) > 0.5, y, z)
        else:
            al, ac = y, np.where(np.abs(N[:, 2]) > 0.5, x, z)
        c = wood(al, ac, {P_BEAM: 11, P_RAFTER: 12, P_RAIL: 13}[part] + (1 if (x > 0).mean() > 0.5 else 0))
        if part != P_RAIL:
            c *= 0.82                                                                  # in the shade of the roof
        ends = (np.abs(N[:, 1]) > 0.5) if part != P_BEAM else np.zeros(n, bool)
        if ends.any():                                                                 # sawn ends of rafters and rails
            c[ends] = col((0.56, 0.47, 0.34), 0.85 + 0.25 * vn(x[ends] * 70, z[ends] * 70, 14))
        zone[:] = 4
        return c, zone
    if part == P_BENCH:
        top = N[:, 2] > 0.5
        pk = (Y0 - y) / (BENCH_D / 3)                                                  # three planks
        c = np.zeros((n, 3))
        for i in range(3):
            q = np.floor(np.clip(pk, 0, 2.999)) == i
            c[q] = wood(x[q], y[q] if top[q].any() else z[q], 20 + i, (0.47, 0.39, 0.29))
        c[top & (frac(pk) < 0.05)] = np.array([0.10, 0.085, 0.07])
        c[~top] *= 0.75
        zone[:] = 4
        return c, zone
    if part in (P_SCHED, P_AD, P_SIGNFACE):
        a, b = L[:, 0] / I[:, 0], L[:, 1] / I[:, 1]
        dc = DEC[gid.astype(int)]
        u = dc[:, 1] + (dc[:, 3] - dc[:, 1]) * a + (dc[:, 5] - dc[:, 1]) * b
        v = dc[:, 2] + (dc[:, 4] - dc[:, 2]) * a + (dc[:, 6] - dc[:, 2]) * b
        c = np.zeros((n, 3))
        for im in (0, 1):
            q = dc[:, 0] == im
            if q.any():
                c[q] = sample(SRC[im], u[q], v[q])
        if part == P_AD:
            c *= (0.80 + 0.12 * vn(L[:, 0] * 30, L[:, 1] * 30, 30))[:, None] * np.array([1.0, 0.97, 0.88])[None, :]     # yellowed paper
            c[(np.minimum(a, 1 - a) < 0.015) | (np.minimum(b, 1 - b) < 0.012)] *= 0.8
        return c, zone
    if part in (P_PLATEBACK, P_SIGNBACK, P_BRACKET, P_POLE):
        if part == P_POLE:
            ang = np.arctan2(y, x)
            c = metal(ang * 0.6, z, 3)
            c *= np.clip(0.75 + z / 0.4, 0.75, 1.0)[:, None]
            c = np.where((N[:, 2] > 0.5)[:, None], col(METAL, 0.8 + 0.0 * z), c)
        else:
            c = metal(x + y, z, int(part))
            c *= 0.92
        return c, zone
    if part in (P_URNOUT, P_URNIN, P_URNRIM, P_URNBOTTOM):
        ang = np.arctan2(y, x); rr = np.hypot(x, y)
        if part == P_URNOUT:
            k = 0.80 * (0.92 + 0.12 * steps(vn(ang * 1.5, z * 3, 70), 3)) * wear(ang * 0.5, z * 1.5, 71)
            k *= np.clip(0.70 + z / 0.25, 0.70, 1.0)
            k *= np.where(vn(ang * 9, z * 0.8, 72) > 0.72, 0.88, 1.0)                  # streaks running down
            k = np.where((np.abs(z - 0.50) < 0.012) | (np.abs(z - 0.10) < 0.012), k * 0.70, k)     # two pressed hoops
            k = np.where(URN_H - z < 0.02, k * 0.80, k)
        elif part == P_URNRIM:
            k = 0.74 * (0.9 + 0.2 * vn(ang * 6, rr * 40, 73))
        elif part == P_URNIN:
            k = 0.42 * np.clip(0.55 + (z - URN_FLOOR) / (URN_H - URN_FLOOR) * 0.7, 0.55, 1.2) * (0.9 + 0.2 * vn(ang * 5, z * 8, 74))
        else:
            k = 0.26 * (0.7 + 0.8 * steps(vn(x * 22, y * 22, 75), 3))                  # rubbish at the bottom
        zone[:] = 2
        return grey(k), zone
    return np.tile(np.array([0.05, 0.05, 0.05]), (n, 1)), zone


fid, bar, ov = raster(UV0, 0.0)
print('UVCHECK shared UVMap of the three objects: range %.4f..%.4f overlapping texels at %d: %d, covered %.3f' % (UV0.min(), UV0.max(), R, ov, (fid >= 0).mean()))
fid, bar, _ = raster(UV0, 1.5)
m = fid >= 0
f = fid[m]; Wb = bar[m].astype(np.float64)
P = (TV[f] * Wb[:, :, None]).sum(1)                           # object-local position
N = FN[f]; gid = GRP[f]; prt = PART[f]; obj = OBJ[f]
Pw = P + PLACE[obj]
Mi = GMinv[gid]
L = np.einsum('nij,nj->ni', Mi[:, :3, :3], Pw) + Mi[:, :3, 3]
I = GI[gid]
out = np.zeros((len(f), 3)); zone = np.zeros(len(f), np.int8)
for p in np.unique(prt):
    s = prt == p
    out[s], zone[s] = paint(int(p), P[s], N[s], L[s], I[s], gid[s].astype(np.float64))
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
c_img[~(m | (c_img.sum(-1) > 0))] = np.array([0.45, 0.45, 0.45])
save(OUT + 'T_BusStop_D.png', np.concatenate([c_img, np.ones((R, R, 1))], -1), False)
ZN = ['R roof', 'G urn', 'B wall profile', 'A wood']
M = np.stack([zone == 1, zone == 2, zone == 3, zone == 4], -1)
mk = np.zeros((R, R, 4)); mk[m] = M
mk = bleed(mk, True)
save(OUT + 'T_BusStop_Mask.png', mk, True, True)
# preview only: colour x default tint per zone, the multiply done in linear light as the game material does
s2l = lambda c: np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
l2s = lambda c: np.where(c <= 0.0031308, c * 12.92, 1.055 * np.clip(c, 0, None) ** (1 / 2.4) - 0.055)
lin = s2l(c_img)
for i, key in ((0, 'roof'), (1, 'urn'), (2, 'profile')):
    q = mk[..., i] > 0.5
    lin[q] = lin[q] * np.array(TINT[key])[None, :]
save(OUT + '_work/_preview_tinted.png', np.concatenate([l2s(lin), np.ones((R, R, 1))], -1), False)
print('TINT defaults (linear RGB): roof %s, urn %s, wall profile %s' % (TINT['roof'], TINT['urn'], TINT['profile']))

chk = bpy.data.images.load(OUT + 'T_BusStop_Mask.png'); chk.alpha_mode = 'CHANNEL_PACKED'; chk.colorspace_settings.name = 'Non-Color'
K = np.array(chk.pixels[:], dtype=np.float32).reshape(R, R, chk.channels)
tex = bpy.data.images.load(OUT + 'T_BusStop_D.png')
TXP = np.array(tex.pixels[:], dtype=np.float32).reshape(R, R, tex.channels)[..., :3]
print('TEXTURE %dx%d %.1f KB | MASK %dx%d channels=%d %.1f KB values R%s G%s B%s A%s' % (tex.size[0], tex.size[1], os.path.getsize(OUT + 'T_BusStop_D.png') / 1024,
      chk.size[0], chk.size[1], chk.channels, os.path.getsize(OUT + 'T_BusStop_Mask.png') / 1024, *[np.unique(K[..., i]).round(3) for i in range(4)]))
print('CHECK mask file equals computed zones on painted texels: %s; texels set in two or more channels (whole file): %d' % (bool(((K[m] > 0.5) == M).all()), int(((K > 0.5).sum(-1) > 1).sum())))
PN = {P_ROOF: 'roof', P_ROOFUNDER: 'roof underside', P_ROOFEDGE: 'roof edge', P_WALL: 'back wall', P_FENCE: 'side walls', P_POST: 'posts', P_BEAM: 'beams', P_RAFTER: 'rafters', P_RAIL: 'rails',
      P_BENCH: 'bench', P_BENCHLEG: 'bench leg', P_SCHED: 'timetable', P_PLATEBACK: 'timetable back', P_AD: 'notices', P_POLE: 'sign pole', P_SIGNFACE: 'sign face', P_SIGNBACK: 'sign back',
      P_BRACKET: 'sign clamps', P_URNOUT: 'urn outside', P_URNIN: 'urn inside', P_URNRIM: 'urn rim', P_URNBOTTOM: 'urn bottom'}
tc = TXP[m]
for i, nme in enumerate(ZN):
    q = M[:, i]
    sat = (tc[q].max(1) - tc[q].min(1)).max() if q.any() else 0.0
    print('ZONE %-14s texels %6d (%.1f%% of painted), mean rgb %s, brightness %.2f..%.2f, largest r-g-b spread %.3f; by part: %s' % (nme, q.sum(), 100 * q.mean(), np.round(tc[q].mean(0), 2),
          tc[q].mean(1).min(), tc[q].mean(1).max(), sat, ', '.join('%s %d' % (PN[int(p)], (q & (prt == p)).sum()) for p in np.unique(prt[q]))))
none = ~M.any(1)
print('ZONE none           texels %6d (%.1f%%); by part: %s' % (none.sum(), 100 * none.mean(), ', '.join('%s %d' % (PN[int(p)], (none & (prt == p)).sum()) for p in np.unique(prt[none]))))
