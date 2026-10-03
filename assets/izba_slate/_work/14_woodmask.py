"""Wood mask for SM_IzbaSlate in the UVMap layout of T_IzbaSlate_D.png: white = bare wood
(wall logs, log ends, porch, gable planks, boards over the window, door, recess wood),
black = everything else. Reuses the definitions of 11_paint.py (same raster, same rules);
does not write the colour texture, the blend or the FBX.
Run: blender.exe -b izba_work.blend --factory-startup --python 14_woodmask.py
"""
import bpy, os
import numpy as np
W_DIR = 'E:/game-dev-team/assets/izba_slate/_work/'
src = open(W_DIR + '11_paint.py', encoding='utf-8').read()
exec(src[:src.index("for layer, res in (('UVMap', R)")])          # helpers + paint(), nothing is saved

fid, bar, _ = raster(uvs('UVMap'), R, 1.5)
m = fid >= 0
f = fid[m]; W = bar[m].astype(np.float64)
P = (TV[f] * W[:, :, None]).sum(1)
N = FN[f]; gid = GRP[f]; prt = PART[f]; vis = VIS[f]
Mi = GMinv[gid]
L = np.einsum('nij,nj->ni', Mi[:, :3, :3], P) + Mi[:, :3, 3]
NL = np.einsum('nij,nj->ni', Mi[:, :3, :3], N)
I = GI[gid]
X, Y, Z = P[:, 0], P[:, 1], P[:, 2]

# same sub-regions as in paint()
wood = np.isin(prt, (P_WALL, P_LOGSIDE, P_LOGCAP, P_REVEAL, P_SILL, P_DOORLEAF, P_PORCH, P_GABLE, P_BOARD))
s = prt == P_DOORLEAF                                   # door handle
wood[s] &= ~((np.abs(L[s, 0] - 0.30) < 0.025) & (np.abs(L[s, 2] + 0.05) < 0.07))
s = prt == P_PORCH                                      # moss on the porch sides
wood[s] &= ~((N[s, 2] <= 0.7) & (vn3(P[s], 3.0, 13) + (0.25 - Z[s]) * 1.5 > 0.8))
s = prt == P_GABLE                                      # painted frieze board, attic window, fallen planks
front = N[s, 0] < 0; pk = np.floor((Y[s] + 3.0) / 0.17)
gone = (~front) & ((pk == 14) | ((pk == 21) & (Z[s] > 3.05)) | ((pk == 9) & (Z[s] < 2.95)))
win = front & (np.abs(Y[s]) < 0.33) & (np.abs(Z[s] - (WTOP + 0.19 + 0.42)) < 0.27)
wood[s] &= ~(gone | win | (Z[s] < WTOP + 0.19))
s = prt == P_BOARD                                      # nails
d = I[s, 1] - np.abs(L[s, 0])
wood[s] &= ~((d > 0.05) & (d < 0.078) & (np.abs(np.abs(L[s, 2]) - 0.035) < 0.012))

# colour recomputed with the same code path -> must equal the PNG on disk
col = np.zeros((len(f), 3))
for p in np.unique(prt):
    q = prt == p
    col[q] = paint(int(p), P[q], L[q], N[q], NL[q], I[q], vis[q], gid[q].astype(np.float64))
ao = np.where(prt == P_SLATE, 1.0, 0.74 + 0.26 * np.clip(vis, 0, 1) ** 0.8)
col = np.clip(col * ao[:, None], 0, 1)
tex = bpy.data.images.load(OUT + 'T_IzbaSlate_D.png')
tp = np.array(tex.pixels[:], dtype=np.float32).reshape(R, R, tex.channels)[..., :3]
diff = np.abs(tp[m] - col).max()
print('CHECK colour recomputed here vs T_IzbaSlate_D.png on painted texels: max abs diff %.4f (1/255 = 0.0039)' % diff)

# green channel: painted wooden details (flaking paint incl. the bare patches inside them)
painted = np.isin(prt, (P_CASING, P_DOORFRAME, P_BARGE))
s = prt == P_GABLE
front = N[s, 0] < 0; a_, b_ = np.abs(Y[s]), np.abs(Z[s] - (WTOP + 0.19 + 0.42))
win = front & (a_ < 0.33) & (b_ < 0.27)
painted[s] = (Z[s] < WTOP + 0.19) | (win & ((a_ > 0.26) | (b_ > 0.20) | (a_ < 0.022)))
s = prt == P_GLASS                                      # window sashes around the panes
painted[s] = (np.minimum(I[s, 1], I[s, 2]) < 0.05) | (np.abs(L[s, 0]) > I[s, 1] - 0.022) | (np.abs(L[s, 2]) > I[s, 2] - 0.022)

def bleed(val):                                         # same 8 px bleed as the colour texture, kept binary
    mask = np.zeros((R, R)); mask[m] = val
    filled = m.copy()
    for _ in range(8):
        acc = np.zeros((R, R)); cnt = np.zeros((R, R))
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            acc += np.roll(np.roll(mask * filled, dy, 0), dx, 1); cnt += np.roll(np.roll(filled, dy, 0), dx, 1)
        new = (~filled) & (cnt > 0)
        mask[new] = (acc[new] / cnt[new]) >= 0.5
        filled |= new
    return mask
mask = bleed(wood)
gmask = bleed(painted) * (mask < 0.5)                   # a border texel never belongs to both
px = np.stack([mask, gmask, np.zeros((R, R)), np.ones((R, R))], -1).astype(np.float32)
PATH = OUT + 'T_IzbaSlate_WoodMask.png'
im = bpy.data.images.new('T_IzbaSlate_WoodMask', R, R, alpha=False)
im.pixels.foreach_set(px.ravel())
im.filepath_raw = PATH; im.file_format = 'PNG'; im.save()

# ---------- checks on the saved file ----------
chk = bpy.data.images.load(PATH)
ck = np.array(chk.pixels[:], dtype=np.float32).reshape(R, R, chk.channels)
mk, gk, bk = ck[..., 0], ck[..., 1], ck[..., 2]
print('MASK %s %dx%d channels=%d depth=%d %.1f KB red values=%s green values=%s blue max=%.3f red=%.3f green=%.3f of texture' % (
    PATH, chk.size[0], chk.size[1], chk.channels, chk.depth, os.path.getsize(PATH) / 1024, np.unique(mk).round(3), np.unique(gk).round(3), bk.max(), (mk > 0.5).mean(), (gk > 0.5).mean()))
print('CHECK saved channels equal computed on painted texels: red %s green %s' % (bool(((mk[m] > 0.5) == wood).all()), bool(((gk[m] > 0.5) == painted).all())))
print('CHECK texels set in both red and green (whole file): %d' % int(((mk > 0.5) & (gk > 0.5)).sum()))
prev = bpy.data.images.load(W_DIR + '_woodmask_v1_red_only.png')
pv = np.array(prev.pixels[:], dtype=np.float32).reshape(R, R, prev.channels)[..., 0]
print('CHECK red channel vs previous mask file (all 1024x1024 texels): differing texels %d' % int(((pv > 0.5) != (mk > 0.5)).sum()))
names = {P_WALL: 'wall logs', P_FOUND: 'foundation', P_GLASS: 'glass+frames', P_DOORLEAF: 'door', P_REVEAL: 'recess sides', P_SILL: 'recess sills',
         P_CASING: 'casings', P_DOORFRAME: 'door frame', P_PORCH: 'porch', P_LOGSIDE: 'log ends side', P_LOGCAP: 'log end caps', P_HIDDEN: 'hidden',
         P_GABLE: 'gable', P_SLATE: 'slate', P_SLATE_EDGE: 'slate edges', P_RIDGE: 'ridge', P_BARGE: 'barge boards', P_CHIM: 'chimney',
         P_PATCH: 'tin patch', P_BOARD: 'window boards', P_SHEATH: 'sheathing', P_SOFFIT: 'soffit'}
for p in np.unique(prt):
    q = prt == p
    print('PART %-14s texels %6d red %5.1f%% green %5.1f%%' % (names[int(p)], q.sum(), 100 * wood[q].mean(), 100 * painted[q].mean()))
r, g, b = tp[m][:, 0], tp[m][:, 1], tp[m][:, 2]
green = (g - b > 14 / 255) & (g - r > 7 / 255)                      # moss
rust = (r - b > 30 / 255)                                           # rust, brick
pale = (b >= r) & (tp[m].mean(1) > 0.5)                             # flaking pale paint, tin
slate = prt == P_SLATE
print('CHECK by colour of T_IzbaSlate_D.png: moss-green texels white %d / black %d; rust-brick texels white %d / black %d; pale-paint texels white %d / black %d' % (
    (green & wood).sum(), (green & ~wood).sum(), (rust & wood).sum(), (rust & ~wood).sum(), (pale & wood).sum(), (pale & ~wood).sum()))
sat = tp[m].max(1) - tp[m].min(1)
print('CHECK white area: mean rgb %s, max saturation %.3f | black area: mean rgb %s' % (tp[m][wood].mean(0).round(3), sat[wood].max(), tp[m][~wood].mean(0).round(3)))

# overlay for the eye: wood kept, everything else tinted magenta
ov = tp.copy()
ov[(mk < 0.5) & (gk < 0.5)] = ov[(mk < 0.5) & (gk < 0.5)] * 0.35 + np.array([0.45, 0.0, 0.45])
ov[gk > 0.5] = ov[gk > 0.5] * 0.6 + np.array([0.0, 0.4, 0.0])
gp = (gk[m] > 0.5)
print('CHECK by colour of T_IzbaSlate_D.png: pale-paint texels in green %d, in red %d, in neither %d (tin of ridge/patch expected)' % ((pale & gp).sum(), (pale & wood).sum(), (pale & ~gp & ~wood).sum()))
o = bpy.data.images.new('ov', R, R, alpha=False)
o.pixels.foreach_set(np.concatenate([ov, np.ones((R, R, 1))], -1).astype(np.float32).ravel())
o.filepath_raw = OUT + 'renders/_qc_woodmask_overlay.png'; o.file_format = 'PNG'; o.save()
print('OVERLAY', o.filepath_raw)
