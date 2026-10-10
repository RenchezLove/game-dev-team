"""Our crate: geometry parts, palette colours used, look renders. Run: blender.exe -b --factory-startup --python crate_01_look.py"""
import bpy, sys, bmesh
import numpy as np
sys.path.insert(0, 'E:/game-dev-team/assets/scientist_base/_work')
import sb
sb.empty()
bpy.ops.import_scene.fbx(filepath='E:/game-dev-team/assets/lowpoly_market/SM_Crate_01.fbx')
ob = [o for o in bpy.data.objects if o.type == 'MESH'][0]
img, px = sb.load_px('E:/ContrarySurvior/ContrarySurvivor/Content/Environment/Props/LowPolyMarket/T_PropColorMap.psd')
print('PSD size %s channels %d' % (tuple(img.size), px.shape[2]))
sb.save_png(px[..., :3], sb.WORK + '_look/crate_palette.png')
H, W = px.shape[:2]
bm = sb.bm_of(ob); uvl = bm.loops.layers.uv.active; bm.normal_update()
print('FACES %d (tris %d) verts %d' % (len(bm.faces), sum(len(f.verts) - 2 for f in bm.faces), len(bm.verts)))
cols = {}
for f in bm.faces:
    uv = np.array([l[uvl].uv[:] for l in f.loops])
    c = px[int(np.clip(uv[:, 1].mean() * H, 0, H - 1)), int(np.clip(uv[:, 0].mean() * W, 0, W - 1)), :3]
    k = tuple(np.round(c, 2)); cols.setdefault(k, []).append(f)
    
for k, fs in sorted(cols.items(), key=lambda kv: -len(kv[1])):
    c = np.array([v.co[:] for f in fs for v in f.verts]); a = sum(f.calc_area() for f in fs)
    uv = np.array([l[uvl].uv[:] for f in fs for l in f.loops])
    print('COLOUR %s faces %3d area %.3f min %s max %s uv %s..%s' % (k, len(fs), a, c.min(0).round(3), c.max(0).round(3), uv.min(0).round(3), uv.max(0).round(3)))
comps = sb.islands(bm)
print('PARTS %d' % len(comps))
for comp in sorted(comps, key=lambda c: -len(c)):
    c = np.array([v.co[:] for f in comp for v in f.verts])
    print('PART faces %3d min %s max %s size %s' % (len(comp), c.min(0).round(3), c.max(0).round(3), np.ptp(c, 0).round(3)))
uvall = np.array([l[uvl].uv[:] for f in bm.faces for l in f.loops]); print('UV range', uvall.min(0), uvall.max(0), 'uv spans per face max', max(np.ptp(np.array([l[uvl].uv[:] for l in f.loops]), 0).max() for f in bm.faces))
bm.free()
sb.tex_material(ob, 'm', img)
sc, cam, cd, sun = sb.preview_scene(ground=None)
P = []
for i, (yaw, pit) in enumerate(((30, 30), (120, 60), (210, 10), (0, 89))):
    p = sb.WORK + '_look/crate_v%d.png' % i; P.append(p)
    sb.shoot(sc, cam, cd, sun, p, yaw, pit, 4, 30, (0, 0, 0), res=(700, 600))
sb.sheet(P, sb.WORK + '_look/crate_sheet.png', 2)
