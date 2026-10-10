"""Scientist from Tripo: raw size, colours along the front, back and side lines (to read chin, collar, coat hem, trousers), look renders.
Run: blender.exe -b --factory-startup --python 00_probe.py"""
import bpy, sys, math
import numpy as np
sys.path.insert(0, 'E:/game-dev-team/assets/scientist_base/_work')
import sb
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
GLB = 'E:/ContrarySurvior/ContrarySurvivor/Saved/Tripo/scientist/scientist.glb'
sb.empty()
bpy.ops.import_scene.gltf(filepath=GLB)
bpy.context.view_layer.update()
o = [o for o in bpy.data.objects if o.type == 'MESH'][0]; me = o.data
me.transform(Matrix.Rotation(math.radians(-90), 4, 'Z') @ o.matrix_world); o.parent = None; o.matrix_world = Matrix.Identity(4)
c = sb.coords(o); zmin = c[:, 2].min()
ch = c[(c[:, 2] - zmin > 1.0) & (c[:, 2] - zmin < 1.3)]
me.transform(Matrix.Translation((-(ch[:, 0].min() + ch[:, 0].max()) / 2, -(ch[:, 1].min() + ch[:, 1].max()) / 2, -zmin)))
c = sb.coords(o)
print('RAW tris %d verts %d min %s max %s; images %s' % (sb.tri_count(o), len(c), c.min(0).round(3), c.max(0).round(3), [(i.name, tuple(i.size)) for i in bpy.data.images]))
hands = c[np.abs(c[:, 0]) > 0.6]
print('FACING check: nose side: head verts y range %.3f..%.3f; feet y range %.3f..%.3f (toes should be at -Y)' % (c[c[:, 2] > 1.55][:, 1].min(), c[c[:, 2] > 1.55][:, 1].max(), c[c[:, 2] < 0.08][:, 1].min(), c[c[:, 2] < 0.08][:, 1].max()))
img = [i for i in bpy.data.images if i.size[0] > 0][0]
px = np.array(img.pixels[:], dtype=np.float32).reshape(img.size[1], img.size[0], -1)
bm = sb.bm_of(o); bm.faces.ensure_lookup_table(); uvl = bm.loops.layers.uv.active
tree = BVHTree.FromBMesh(bm)
def col(orig, d):
    loc, n, fi, dist = tree.ray_cast(Vector(orig), Vector(d), 5)
    if loc is None:
        return None
    f = bm.faces[fi]; vs = [l.vert.co for l in f.loops]; uvs = [l[uvl].uv for l in f.loops]
    from mathutils.geometry import barycentric_transform
    p = barycentric_transform(loc, vs[0], vs[1], vs[2], Vector((uvs[0].x, uvs[0].y, 0)), Vector((uvs[1].x, uvs[1].y, 0)), Vector((uvs[2].x, uvs[2].y, 0)))
    t = px[int(p.y % 1 * img.size[1]) % img.size[1], int(p.x % 1 * img.size[0]) % img.size[0], :3]
    return loc, t
def name(t):
    r, g, b = t; v = max(t); s = v - min(t)
    if r > 0.5 and r > b * 1.25 and s > 0.12: return 'skin '
    if v > 0.6 and s < 0.12: return 'white'
    if v < 0.33 and s < 0.08: return 'dkgry'
    if r - b > 0.07 and v < 0.5: return 'brown'
    return 'other'
for label, x, d, y0 in (('FRONT x=0', 0.0, (0, 1, 0), -2), ('FRONT x=0.06', 0.06, (0, 1, 0), -2), ('BACK x=0', 0.0, (0, -1, 0), 2), ('FRONT leg x=0.12', 0.12, (0, 1, 0), -2), ('FRONT chest x=0.15', 0.15, (0, 1, 0), -2)):
    out = []
    for i in range(2, 180):
        z = i * 0.01; r = col((x, y0, z), d)
        out.append((z, name(r[1]) if r else '-----', r[0].y if r else 0, r[1] if r else None))
    runs = []; cur = None
    for z, n, y, t in out:
        if cur and cur[0] == n:
            cur[2] = z; cur[3].append(y)
        else:
            cur = [n, z, z, [y]]; runs.append(cur)
    print(label + ': ' + ' | '.join('%s %.2f-%.2f (y %.2f)' % (n, a, b, float(np.mean(ys))) for n, a, b, ys in runs))
for z in (1.40, 1.45, 1.50, 1.55, 1.60, 1.65, 1.70, 1.75):
    s = c[np.abs(c[:, 2] - z) < 0.015]; s = s[np.abs(s[:, 0]) < 0.25]
    if len(s): print('RING z %.2f: x %.3f..%.3f y %.3f..%.3f' % (z, s[:, 0].min(), s[:, 0].max(), s[:, 1].min(), s[:, 1].max()))
for z in (0.3, 0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 1.0):
    s = c[np.abs(c[:, 2] - z) < 0.015]; s = s[np.abs(s[:, 0]) < 0.4]
    if len(s): print('RING z %.2f: x %.3f..%.3f y %.3f..%.3f' % (z, s[:, 0].min(), s[:, 0].max(), s[:, 1].min(), s[:, 1].max()))
bm.free()
sc, cam, cd, sun = sb.preview_scene(ground=None)
P = []
for i, (yaw, pit, tg, fov) in enumerate(((0, 5, (0, 0, 0.9), 40), (90, 5, (0, 0, 0.9), 40), (180, 5, (0, 0, 0.9), 40), (0, 5, (0, 0, 1.55), 9), (90, 5, (0, 0, 1.55), 9), (180, 5, (0, 0, 1.55), 9))):
    p = 'E:/game-dev-team/assets/scientist_tripo/_work/_look/raw_%d.png' % i; P.append(p)
    sb.shoot(sc, cam, cd, sun, p, yaw, pit, 3.2, fov, tg, res=(700, 800), sun_dir=(0.2, 0.6, -0.5) if yaw < 90 else (-0.3, -0.6, -0.5))
sb.sheet(P, 'E:/game-dev-team/assets/scientist_tripo/_work/_look/raw_sheet.png', 3)
