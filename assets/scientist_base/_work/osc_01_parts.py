"""Oscilloscope source: parts, texture, textured look renders. Run: blender.exe -b --factory-startup --python osc_01_parts.py"""
import bpy, sys, bmesh
import numpy as np
sys.path.insert(0, 'E:/game-dev-team/assets/scientist_base/_work')
import sb
bpy.ops.wm.open_mainfile(filepath=sb.SRCD + 'oscillograph/source/oscilloscope.blend', use_scripts=False)
ob = bpy.data.objects['oscilloscope']
for o in list(bpy.data.objects):
    if o is not ob: bpy.data.objects.remove(o, do_unlink=True)
print('IMAGES', [(i.name, tuple(i.size), bool(i.packed_file)) for i in bpy.data.images])
img = bpy.data.images.load(sb.SRCD + 'oscillograph/textures/oscilloscope_01.png'); px = np.array(img.pixels[:]).reshape(img.size[1], img.size[0], -1)
print('TEXTURE file', tuple(img.size))
H, W = px.shape[:2]
bm = sb.bm_of(ob); bmesh.ops.triangulate(bm, faces=bm.faces); bm.faces.ensure_lookup_table(); bm.faces.index_update(); bm.normal_update()
uvl = bm.loops.layers.uv.active
rows = []
for comp in sb.islands(bm):
    c = np.array([v.co[:] for v in {v for f in comp for v in f.verts}]); ar = np.array([f.calc_area() for f in comp])
    uvc = np.array([np.mean([l[uvl].uv[:] for l in f.loops], 0) for f in comp]) % 1.0
    col = (px[np.clip((uvc[:, 1] * H).astype(int), 0, H - 1), np.clip((uvc[:, 0] * W).astype(int), 0, W - 1), :3] * ar[:, None]).sum(0) / ar.sum()
    rows.append((len(comp), c.min(0), c.max(0), col, ar.sum()))
rows.sort(key=lambda r: -r[4])
print('PARTS %d' % len(rows))
for n, mn, mx, col, a in rows:
    print('PART tris %4d area %7.1f min %s max %s size %s colour %s' % (n, a, mn.round(1), mx.round(1), (mx - mn).round(1), col.round(2)))
bm.free()
sb.tex_material(ob, 'm', img); ob.data.materials[0].use_backface_culling = False
sc, cam, cd, sun = sb.preview_scene(ground=None)
P = []
for i, (yaw, pit) in enumerate(((0, 5), (35, 30), (180, 10), (90, 5), (0, 89), (215, 35))):
    p = sb.WORK + '_look/osc_t%d.png' % i; P.append(p)
    sb.shoot(sc, cam, cd, sun, p, yaw, pit, 110, 30, (0, -1.5, 14), res=(700, 600), sun_dir=(0.3, 0.6, -0.5) if yaw < 90 else (-0.3, -0.6, -0.5))
sb.sheet(P, sb.WORK + '_look/osc_sheet.png', 3)
