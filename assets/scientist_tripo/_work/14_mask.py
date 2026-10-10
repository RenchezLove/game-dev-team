"""Scientist: hair made neutral grey in the colour texture (shading kept) + the mask T_ScientistTripo_Mask.png in the same UV (1024, RGBA, binary):
R = hair and eyebrows, G = lab coat, B = sweater, A = trousers.  Skin, eyes, boots, buttons -> zero.  Every texel gets its place on the
model (slot + rest position) through the UV triangles and is sorted by that place and by the colour of the baked texture.
The FBX are not touched.  The untouched bake is kept as _work/_bake_orig.png (the script always starts from it).
Run: blender.exe -b scientist_work.blend --factory-startup --python 14_mask.py [-- stats]
"""
import bpy, sys, os, math, shutil
import numpy as np
sys.path.insert(0, 'E:/game-dev-team/assets/scientist_base/_work')
import sb
OUT = 'E:/game-dev-team/assets/scientist_tripo/'
R = 1024
STATS = 'stats' in sys.argv
ORIG = OUT + '_work/_bake_orig.png'
if not os.path.exists(ORIG):
    shutil.copyfile(OUT + 'T_ScientistTripo_D.png', ORIG)
tex = bpy.data.images.load(ORIG)
TP = np.array(tex.pixels[:], dtype=np.float32).reshape(R, R, tex.channels)[..., :3].astype(np.float64)
TV, UV, SL = [], [], []
for si, s in enumerate(('Head', 'Torso', 'Legs')):
    me = bpy.data.objects['SK_Scientist_' + s].data
    co = np.zeros(len(me.vertices) * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    lv = np.zeros(len(me.loops), np.int32); me.loops.foreach_get('vertex_index', lv)
    uv = np.zeros(len(me.loops) * 2); me.uv_layers['UVMap'].data.foreach_get('uv', uv)
    T = len(me.polygons)
    TV.append(co[lv].reshape(T, 3, 3)); UV.append(uv.reshape(T, 3, 2)); SL.append(np.full(T, si))
TV = np.concatenate(TV); UV = np.concatenate(UV); SL = np.concatenate(SL)
# rasterise (later triangles do not overwrite earlier ones: the T0 pelvis graft sits on one trouser texel)
fid = -np.ones((R, R), np.int32); bw = np.zeros((R, R, 3))
for t in range(len(UV)):
    p = UV[t] * R
    d = (p[1, 0] - p[0, 0]) * (p[2, 1] - p[0, 1]) - (p[1, 1] - p[0, 1]) * (p[2, 0] - p[0, 0])
    if abs(d) < 1e-9:
        continue
    x0 = max(int(math.floor(p[:, 0].min())) - 2, 0); x1 = min(int(math.ceil(p[:, 0].max())) + 3, R)
    y0 = max(int(math.floor(p[:, 1].min())) - 2, 0); y1 = min(int(math.ceil(p[:, 1].max())) + 3, R)
    X, Y = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
    w1 = ((X - p[0, 0]) * (p[2, 1] - p[0, 1]) - (Y - p[0, 1]) * (p[2, 0] - p[0, 0])) / d
    w2 = ((p[1, 0] - p[0, 0]) * (Y - p[0, 1]) - (p[1, 1] - p[0, 1]) * (X - p[0, 0])) / d
    w0 = 1 - w1 - w2
    el = [np.linalg.norm(p[2] - p[1]), np.linalg.norm(p[0] - p[2]), np.linalg.norm(p[1] - p[0])]
    dist = np.minimum(np.minimum(w0 * abs(d) / el[0], w1 * abs(d) / el[1]), w2 * abs(d) / el[2])
    ins = (dist > -1.5) & (fid[y0:y1, x0:x1] < 0)
    fid[y0:y1, x0:x1][ins] = t
    Wt = np.clip(np.stack([w0, w1, w2], -1), 0, None); Wt /= Wt.sum(-1, keepdims=True)
    bw[y0:y1, x0:x1][ins] = Wt[ins]
m = fid >= 0; f = np.clip(fid, 0, None)
P = (TV[f] * bw[..., None]).sum(2); slot = SL[f]
r, g, b = TP[..., 0], TP[..., 1], TP[..., 2]
val = TP.max(2); sat = val - TP.min(2)
x, y, z = P[..., 0], P[..., 1], P[..., 2]
skin = (r > 0.42) & (r > b * 1.22) & (g > b) & (sat > 0.10)
brownish = (r - b > 0.045) & (val < 0.50) & ~skin
if STATS:
    for si, s in enumerate(('Head', 'Torso', 'Legs')):
        q = m & (slot == si)
        print('%s texels %d: skin %d, white (val>0.5 sat<0.15) %d, dark grey (val<0.42 sat<0.07) %d, brownish dark %d' % (s, q.sum(), (q & skin).sum(), (q & (val > 0.5) & (sat < 0.15)).sum(),
              (q & (val < 0.42) & (sat < 0.07)).sum(), (q & brownish).sum()))
    hq = m & (slot == 0) & ~skin
    for z0 in np.arange(1.53, 1.80, 0.02):
        zz = hq & (z >= z0) & (z < z0 + 0.02)
        fr = zz & (y < -0.07); bk = zz & (y >= -0.07)
        def mc(q):
            return TP[q].mean(0).round(2) if q.any() else None
        print('HEAD not skin z %.2f: face side (y<-0.07) %5d texels mean %s (x %.2f..%.2f) | rest %5d mean %s' % (z0, fr.sum(), mc(fr), x[fr].min() if fr.any() else 0, x[fr].max() if fr.any() else 0, bk.sum(), mc(bk)))
    tq = m & (slot == 1) & ~skin
    for z0 in np.arange(0.58, 1.56, 0.08):
        zz = tq & (z >= z0) & (z < z0 + 0.08)
        print('TORSO z %.2f: white %6d, dark %6d (mean %s), other %6d' % (z0, (zz & (val > 0.5)).sum(), (zz & (val < 0.42)).sum(), TP[zz & (val < 0.42)].mean(0).round(2) if (zz & (val < 0.42)).any() else None, (zz & (val >= 0.42) & (val <= 0.5)).sum()))
    lq = m & (slot == 2)
    for z0 in np.arange(0.0, 0.92, 0.08):
        zz = lq & (z >= z0) & (z < z0 + 0.08)
        print('LEGS z %.2f: texels %6d mean %s, r-b mean %.3f' % (z0, zz.sum(), TP[zz].mean(0).round(2) if zz.any() else None, (r - b)[zz].mean() if zz.any() else 0))
    sys.exit(0)

# ---- zones
head, torso, legs = (m & (slot == 0)), (m & (slot == 1)), (m & (slot == 2))
hairish = ~skin & (val < 0.40) & (r - b > 0.05) & (r - b < 0.20)
hair = head & hairish & (((y >= -0.07) & (z >= 1.60)) | ((y < -0.07) & (z >= 1.683)))    # sides, back and top; on the face only the brows and the fringe
white = (val > 0.50) & (sat < 0.16)
dark = (val < 0.44) & ~skin
coat = torso & white
sweater = torso & dark & ((z >= 0.84) | (np.abs(x) > 0.45))                              # chest, turtleneck, cuffs
boots = legs & ((z < 0.19) | ((z < 0.23) & (r - b > 0.085)))
trousers = (legs & ~boots) | (torso & dark & (z < 0.84) & (np.abs(x) <= 0.45))            # and the hips seen between the coat flaps
MASK = np.zeros((R, R, 4), np.float32)
for i, q in enumerate((hair, coat, sweater, trousers)):
    MASK[..., i] = q
multi = int((MASK.sum(2) > 1).sum())
# ---- hair to neutral grey, shading kept
hm = np.median(TP[hair], 0); lum = TP.mean(2); lm = np.median(lum[hair])
out = TP.copy(); out[hair] = np.clip(lum[hair] / lm * 0.80, 0, 1)[:, None]
default_hair = hm / 0.80
print('ZONES texels: hair and brows %d, coat %d, sweater %d, trousers %d; in two zones at once %d; not in any zone %d (skin %d, boots %d)' % (
    hair.sum(), coat.sum(), sweater.sum(), trousers.sum(), multi, int((m & (MASK.sum(2) == 0)).sum()), int((m & skin).sum()), int(boots.sum())))
print('HAIR median colour of the source %s -> neutral grey with median 0.80; default hair colour for the material parameter (0..1, screen values) %s' % (hm.round(3), default_hair.round(3)))
chk = (out[hair] * default_hair[None]); print('HAIR check: grey * default colour differs from the source hair by %.3f on average' % np.abs(chk - TP[hair]).mean())
img = bpy.data.images.new('T_ScientistTripo_D', R, R, alpha=False)
px = np.ones((R, R, 4), np.float32); px[..., :3] = out
img.pixels.foreach_set(px.ravel()); img.filepath_raw = OUT + 'T_ScientistTripo_D.png'; img.file_format = 'PNG'; img.save()
mi = bpy.data.images.new('T_ScientistTripo_Mask', R, R, alpha=True); mi.alpha_mode = 'CHANNEL_PACKED'; mi.colorspace_settings.name = 'Non-Color'
mi.pixels.foreach_set(MASK.ravel()); mi.filepath_raw = OUT + 'T_ScientistTripo_Mask.png'; mi.file_format = 'PNG'; mi.save()
# read both files back
for pth in (OUT + 'T_ScientistTripo_Mask.png', 'E:/game-dev-team/assets/scientist_base/SM_UAZ452_kit/T_UAZ452Kit_D.png'):
    t2 = bpy.data.images.load(pth, check_existing=False); t2.alpha_mode = 'CHANNEL_PACKED'
    K = np.array(t2.pixels[:], dtype=np.float32).reshape(t2.size[1], t2.size[0], t2.channels)
    print('FILE %s: %dx%d channels %d; set texels per channel %s; colour under alpha 0: mean %s, share of non-black %.3f' % (os.path.basename(pth), t2.size[0], t2.size[1], t2.channels,
          [int((K[..., i] > 0.5).sum()) for i in range(t2.channels)], K[K[..., 3] < 0.5][:, :3].mean(0).round(3), (K[K[..., 3] < 0.5][:, :3].max(1) > 0.02).mean()))
# previews of the recolour: brown (default), blond, and the mask itself
for nm, colr in (('brown', default_hair), ('blond', np.array([0.95, 0.80, 0.50]))):
    pv = out.copy(); pv[hair] = np.clip(out[hair] * colr[None], 0, 1)
    p4 = np.ones((R, R, 4), np.float32); p4[..., :3] = pv; sb.save_png(p4, OUT + '_work/_prev_hair_%s.png' % nm, 'pv_' + nm)
mv = np.ones((R, R, 4), np.float32); mv[..., :3] = MASK[..., :3] + MASK[..., 3:4] * np.array([0.6, 0.6, 0.0])[None, None]
sb.save_png(mv, OUT + '_work/_prev_mask.png', 'pv_mask')
