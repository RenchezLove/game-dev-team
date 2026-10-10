"""TOZ source: every loose island of every object - triangles, open edges, bounds (in final metres: muzzle -Y), material.
Run: blender -b --factory-startup --python toz_02_parts.py"""
import bpy, sys, bmesh
import numpy as np
sys.path.insert(0, 'E:/game-dev-team/assets/scientist_base/_work')
import sb
sb.empty()
with bpy.data.libraries.load(sb.SRCD + 'low-poly-toz-34/source/toz34.blend', link=False) as (df, dt):
    dt.objects = [n for n in df.objects]
k = 1.15 / 19.013
for o in dt.objects:
    if o is None or o.type != 'MESH' or o.name in ('12/76', '1276'):
        continue
    bpy.context.scene.collection.objects.link(o); bpy.context.view_layer.update()
    bm = bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bm.faces.ensure_lookup_table(); bm.faces.index_update()
    names = [m.name for m in o.data.materials]
    print('OBJECT %s: faces %d' % (o.name, len(bm.faces)))
    for comp in sorted(sb.islands(bm), key=lambda c: -len(c)):
        c = np.array([v.co[:] for f in comp for v in f.verts]); c = np.stack([c[:, 1] * k * 1.5, -c[:, 0] * k, c[:, 2] * k], 1)
        es = {e for f in comp for e in f.edges}
        op = sum(1 for e in es if len(e.link_faces) == 1); nm = sum(1 for e in es if len(e.link_faces) > 2)
        tris = sum(len(f.verts) - 2 for f in comp)
        mats = sorted({names[f.material_index] for f in comp})
        print('   island tris %4d open edges %3d, 3+ faces on an edge %2d | x %.3f..%.3f y %.3f..%.3f z %.3f..%.3f | %s' % (tris, op, nm, c[:, 0].min(), c[:, 0].max(), c[:, 1].min(), c[:, 1].max(), c[:, 2].min(), c[:, 2].max(), mats))
    bm.free()
