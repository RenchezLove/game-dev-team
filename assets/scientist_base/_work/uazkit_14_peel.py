"""T_UAZ452Kit_Peel.png: where the body paint of the UAZ kit is gone (rust, dirt, bare metal) - white, everything else black.
The colour texture and the models are not touched.  The sheet-metal faces are the ones the builder marked nopaint = 0; that mark is not kept
in the work blend, so the geometry half of uazkit_10_build.py is run again (no bake, nothing saved) and its unwrap is compared with the
unwrap of the delivered work mesh, triangle by triangle, before the mask is trusted.
Run: blender.exe -b --factory-startup --python uazkit_14_peel.py
"""
import sys
sys.path.insert(0, 'E:/game-dev-team/assets/scientist_base/_work')
import sb
_t = open(sb.WORK + 'uazkit_10_build.py', encoding='utf-8').read()
exec(_t[:_t.index("img = bpy.data.images.new('bake'")])
me = kit.data; T = len(me.polygons)
def fattr(n):
    a = np.zeros(T, np.int32); me.attributes[n].data.foreach_get('value', a); return a
pidv, nop = fattr('pid'), fattr('nopaint')
uv_new = sb.uvtris(me, 'UVMap')
with bpy.data.libraries.load(sb.WORK + 'uazkit_work.blend', link=False) as (s_, d_):
    d_.objects = ['kit']
old = d_.objects[0]
uv_old = sb.uvtris(old.data, 'UVMap')
same = uv_old.shape == uv_new.shape and float(abs(uv_old - uv_new).max()) < 1e-6
print('PEEL unwrap of the rebuilt mesh against the delivered one: %d and %d triangles, largest difference %.2e -> %s' % (
    len(uv_new), len(uv_old), float(abs(uv_old - uv_new).max()) if uv_old.shape == uv_new.shape else -1, 'SAME' if same else 'DIFFERENT'))
assert same
im = bpy.data.images.load(OUT + 'T_UAZ452Kit_D.png', check_existing=False); im.alpha_mode = 'CHANNEL_PACKED'
px = np.array(im.pixels[:], dtype=np.float32).reshape(im.size[1], im.size[0], 4)
assert im.size[0] == TEX and im.size[1] == TEX
alpha = px[..., 3]
fid, bw = sb.raster(me, 'UVMap', TEX); m = fid >= 0; f = np.clip(fid, 0, None)
sheet_m = m & (nop[f] == 0)
other = m & (nop[f] != 0)
print('PEEL alpha of the colour texture: values %s; painted texels on sheet metal %d, on other faces %d (has to be 0 away from island borders)' % (
    np.unique(np.round(alpha, 3))[:6], int((sheet_m & (alpha > 0.5)).sum()), int((other & (alpha > 0.5)).sum())))
# Sheet metal of the source is not only painted panels: the cabin floor and walls, the underside, the grille and the frames have no paint at all.
# A painted panel = a face that carries paint on a fair share of its texels; faces with (almost) no paint are left black as a whole.
SHARE = 0.20
cnt = np.bincount(fid[sheet_m], minlength=T).astype(np.float64); pnt = np.bincount(fid[sheet_m], weights=alpha[sheet_m], minlength=T)
share = np.where(cnt > 0, pnt / np.maximum(cnt, 1), 0.0)
panel_face = (nop == 0) & (share >= SHARE)
panel = sheet_m & panel_face[f]
# inside a panel the unpainted texels that are not worn paint stay black too: lamps (bright, saturated), white marks, black gaps and seals
rgb = px[..., :3]; mxc = rgb.max(2); mnc = rgb.min(2)
lamp = (rgb[..., 0] > 0.60) & (rgb[..., 1] < 0.45); white = mnc > 0.72; gap = mxc < 0.07
keep = panel & ~lamp & ~white & ~gap
print('PEEL painted panels: %d of %d sheet-metal triangles (paint on at least %d %% of the face), %d of %d texels; left out as lamps %d, white marks %d, black gaps %d texels' % (
    int(panel_face.sum()), int((nop == 0).sum()), SHARE * 100, int(panel.sum()), int(sheet_m.sum()), int((panel & lamp & (alpha < 0.5)).sum()), int((panel & white & (alpha < 0.5)).sum()), int((panel & gap & (alpha < 0.5)).sum())))
peel = np.where(keep, 1.0 - alpha, 0.0).astype(np.float32)
other = other | (sheet_m & ~panel)
sheet_all = sheet_m; sheet_m = panel
# the same border padding as the colour texture has: no dark or light seams when the game samples between texels
out = sb.dilate(np.repeat(peel[..., None], 4, 2), sheet_m, 10)[..., 0]
out[other] = 0.0
far = sb.dilate(np.repeat(m[..., None].astype(np.float32), 4, 2), m, 10)[..., 0] > 0
out[~far] = 0.0
grey = np.repeat(out[..., None], 3, 2)
res = bpy.data.images.new('T_UAZ452Kit_Peel', TEX, TEX, alpha=False); res.colorspace_settings.name = 'Non-Color'
res.pixels.foreach_set(np.concatenate([grey, np.ones((TEX, TEX, 1), np.float32)], 2).ravel())
res.filepath_raw = OUT + 'T_UAZ452Kit_Peel.png'; res.file_format = 'PNG'
bpy.context.scene.render.image_settings.color_mode = 'BW'; bpy.context.scene.render.image_settings.color_depth = '8'
res.save()
print('PEEL white texels in the whole picture %d of %d = %.1f %%; on sheet metal %.1f %% of it' % (int((out > 0.5).sum()), TEX * TEX, 100.0 * (out > 0.5).mean(), 100.0 * peel[sheet_m].mean()))
nr = np.zeros(T * 3); me.polygons.foreach_get('normal', nr); nr = nr.reshape(-1, 3)
roof = sheet_m & (nr[f][..., 2] > 0.7) & (pidv[f] == PID['Body'])
print('PEEL roof and other sheet metal of the body that looks up: %d texels, peeled %.1f %%' % (int(roof.sum()), 100.0 * peel[roof].mean()))
print('PEEL sides of the body (sheet metal looking sideways): %d texels, peeled %.1f %%' % (int((sheet_m & (abs(nr[f][..., 0]) > 0.7)).sum()), 100.0 * peel[sheet_m & (abs(nr[f][..., 0]) > 0.7)].mean()))
for i, n in enumerate(PARTS):
    s = sheet_m & (pidv[f] == i); o = other & (pidv[f] == i)
    print('PEEL %-11s sheet metal texels %7d peeled %5.1f %% | other texels %7d, white among them %d' % (n, int(s.sum()), 100.0 * peel[s].mean() if s.any() else 0.0, int(o.sum()), int((out[o] > 0.02).sum())))
for k in sorted(set(nop.tolist())):
    o = m & (nop[f] == k)
    print('PEEL faces with mark %d: %4d triangles, %7d texels, white among them %d' % (k, int((nop == k).sum()), int(o.sum()), int((out[o] > 0.5).sum())))
# check picture, not for the game: default body colour on the paint, magenta on the peel mask
dbg = px.copy(); pm = alpha > 0.5; dbg[pm, :3] = np.clip(dbg[pm, :3] * np.array(json.load(open(sb.WORK + '_uazkit_meta.json'))['body_color'])[None], 0, 1)
dbg[..., :3] = dbg[..., :3] * (1 - out[..., None]) + np.array([1.0, 0.0, 1.0]) * out[..., None]; dbg[..., 3] = 1
sb.save_png(dbg, sb.WORK + '_uazkit_peel_check.png', 'peel_check')
chk = bpy.data.images.load(OUT + 'T_UAZ452Kit_Peel.png', check_existing=False)
print('PEEL file %s %dx%d channels %d depth %d, %.1f KB' % (chk.filepath, chk.size[0], chk.size[1], chk.channels, chk.depth, os.path.getsize(OUT + 'T_UAZ452Kit_Peel.png') / 1024))
