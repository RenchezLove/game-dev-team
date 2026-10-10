"""Tent source: connected parts with size, place, mean colour, open edges. Run: blender.exe -b --factory-startup --python tent_01_parts.py"""
import bpy, sys, bmesh
import numpy as np
sys.path.insert(0, 'E:/game-dev-team/assets/scientist_base/_work')
import sb
sb.empty()
bpy.ops.wm.obj_import(filepath=sb.SRCD + 'tent-model-free/source/unrar/Tent/Tent.obj')
ob = sb.join_meshes([o for o in bpy.data.objects if o.type == 'MESH'], 'src')
img, px = sb.load_px(sb.SRCD + 'tent-model-free/textures/Tex_0129_0.png'); H, W = px.shape[:2]
bm = sb.bm_of(ob)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.01)
bmesh.ops.triangulate(bm, faces=bm.faces); bm.faces.ensure_lookup_table(); bm.faces.index_update(); bm.normal_update()
uvl = bm.loops.layers.uv.active
comps = sb.islands(bm)
print('PARTS %d triangles %d verts %d' % (len(comps), len(bm.faces), len(bm.verts)))
rows = []
for comp in comps:
    c = np.array([v.co[:] for v in {v for f in comp for v in f.verts}])
    ar = np.array([f.calc_area() for f in comp])
    uvc = np.array([np.mean([l[uvl].uv[:] for l in f.loops], 0) for f in comp])
    xi = np.clip((uvc[:, 0] % 1 * W).astype(int), 0, W - 1); yi = np.clip((uvc[:, 1] % 1 * H).astype(int), 0, H - 1)
    col = (px[yi, xi, :3] * ar[:, None]).sum(0) / ar.sum()
    open_e = len({e for f in comp for e in f.edges if len(e.link_faces) == 1})
    nz = np.array([f.normal.z for f in comp])
    rows.append((len(comp), c.min(0), c.max(0), col, open_e, ar.sum(), uvc.min(0), uvc.max(0), (nz > 0.3).sum(), (nz < -0.3).sum()))
rows.sort(key=lambda r: -r[5])
for i, r in enumerate(rows):
    print('PART %3d tris %4d area %9.0f min %s max %s colour %s open edges %3d uv %s..%s up %d down %d' % (i, r[0], r[5], r[1].round(0), r[2].round(0), r[3].round(2), r[4], r[6].round(2), r[7].round(2), r[8], r[9]))
