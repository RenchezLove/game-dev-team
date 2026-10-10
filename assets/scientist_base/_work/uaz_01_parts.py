"""UAZ source: connected parts with size, place and mean texture colour - to tell the body from the add-on gear.
Run: blender.exe -b --factory-startup --python uaz_01_parts.py
"""
import bpy, sys
import numpy as np
sys.path.insert(0, 'E:/game-dev-team/assets/scientist_base/_work')
import sb

sb.empty()
bpy.ops.import_scene.fbx(filepath=sb.SRCD + 'uaz-452-buhanka/source/unrar/UAZ_Buhanka.fbx')
ob = sb.join_meshes([o for o in bpy.data.objects if o.type == 'MESH'], 'src')
img, px = sb.load_px(sb.SRCD + 'uaz-452-buhanka/textures/None_Diffuse.png')
op_img, op = sb.load_px(sb.SRCD + 'uaz-452-buhanka/textures/None_Opacity.png')
print('OPACITY size %s min %.3f max %.3f mean %.3f; share below 0.9: %.4f' % (tuple(op_img.size), op[..., 0].min(), op[..., 0].max(), op[..., 0].mean(), (op[..., 0] < 0.9).mean()))
H, W = px.shape[:2]
bm = sb.bm_of(ob); uvl = bm.loops.layers.uv.active
bmesh_ops = __import__('bmesh').ops
bmesh_ops.triangulate(bm, faces=bm.faces)
bm.faces.ensure_lookup_table(); bm.faces.index_update()
comps = sb.islands(bm)
print('PARTS %d, triangles %d' % (len(comps), len(bm.faces)))
rows = []
for comp in comps:
    vs = {v for f in comp for v in f.verts}
    c = np.array([v.co[:] for v in vs])
    cols = []; ar = []; ops = []
    for f in comp:
        uv = np.mean([l[uvl].uv[:] for l in f.loops], 0)
        x = int(np.clip(uv[0] % 1.0 * W, 0, W - 1)); y = int(np.clip(uv[1] % 1.0 * H, 0, H - 1))
        cols.append(px[y, x, :3]); ar.append(f.calc_area())
        ops.append(op[int(np.clip(uv[1] % 1.0 * op.shape[0], 0, op.shape[0] - 1)), int(np.clip(uv[0] % 1.0 * op.shape[1], 0, op.shape[1] - 1)), 0])
    ar = np.array(ar); col = (np.array(cols) * ar[:, None]).sum(0) / max(ar.sum(), 1e-12)
    rows.append((len(comp), c.min(0), c.max(0), col, float((np.array(ops) * ar).sum() / max(ar.sum(), 1e-12)), ar.sum()))
rows.sort(key=lambda r: -r[0])
for i, (n, mn, mx, col, opa, area) in enumerate(rows):
    print('PART %3d tris %5d area %7.3f min %s max %s size %s colour %s lum %.3f opacity %.2f' % (i, n, area, mn.round(3), mx.round(3), (mx - mn).round(3), col.round(2), col.mean(), opa))
