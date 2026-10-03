"""Radius + colour of the raw Tripo surface along rays (outside -> vertical axis) at several
angles, to pick hem / collar / chin landmarks by numbers.
Run: blender.exe -b --factory-startup --python 04_probe.py -- <glb>
"""
import bpy, bmesh, sys, math
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
from mathutils.interpolate import poly_3d_calc
GLB = sys.argv[sys.argv.index('--') + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=GLB)
tr = [o for o in bpy.context.selected_objects if o.type == 'MESH'][0]
bpy.context.view_layer.update()
me = tr.data
me.transform(Matrix.Rotation(math.radians(-90), 4, 'Z') @ tr.matrix_world)
zmin = min(v.co.z for v in me.vertices)
ch = [v.co for v in me.vertices if 1.0 < v.co.z - zmin < 1.3]
xc = (min(c.x for c in ch) + max(c.x for c in ch)) / 2; yc = (min(c.y for c in ch) + max(c.y for c in ch)) / 2
me.transform(Matrix.Translation((-xc, -0.001 - yc, -zmin)))
img = [i for i in bpy.data.images if i.size[0] > 0][0]
W_, H_ = img.size
px = img.pixels[:]
bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.triangulate(bm, faces=bm.faces[:]); bm.faces.ensure_lookup_table()
uvl = bm.loops.layers.uv.active
tree = BVHTree.FromBMesh(bm)


def probe(ax_y, ang, z):
    d = Vector((math.sin(math.radians(ang)), -math.cos(math.radians(ang)), 0))     # 0 = front (-Y), 90 = +X side, 180 = back
    o = Vector((0, ax_y, z)) + d * 1.5
    loc, nor, fi, dist = tree.ray_cast(o, -d, 1.5)
    if loc is None:
        return ' ----        '
    f = bm.faces[fi]
    w = poly_3d_calc([v.co for v in f.verts], loc)
    uv = sum((l[uvl].uv * wi for l, wi in zip(f.loops, w)), Vector((0, 0)))
    x = min(W_ - 1, max(0, int(uv.x * W_))); y = min(H_ - 1, max(0, int(uv.y * H_)))
    i = (y * W_ + x) * 4
    return '%.3f %02d%02d%02d' % ((loc - Vector((0, ax_y, z))).length, round(px[i] * 99), round(px[i + 1] * 99), round(px[i + 2] * 99))


ANG = (0, 30, 60, 90, 120, 150, 180)
print('PROBE columns: angle from front; value = radius and rgb (00..99 each)')
print('PROBE angles      ' + ''.join('%-15d' % a for a in ANG))
for rng, ax in ((range(60, 108, 2), 0.0), (range(140, 172, 1), 0.03)):
    for i in rng:
        z = i * 0.01
        print('PROBE z=%.2f  ' % z + '  '.join(probe(ax, a, z) for a in ANG))
    print('PROBE')
for z0, z1 in ((1.62, 1.72), (1.72, 1.80)):
    s = [v.co for v in me.vertices if z0 < v.co.z < z1 and abs(v.co.x) < 0.15]
    print('HEADBOX z %.2f..%.2f: x %.3f..%.3f y %.3f..%.3f (centre y %.3f)' % (z0, z1, min(c.x for c in s), max(c.x for c in s), min(c.y for c in s), max(c.y for c in s), (min(c.y for c in s) + max(c.y for c in s)) / 2))
