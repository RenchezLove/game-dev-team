import bpy, sys, math
sys.path.insert(0, 'E:/game-dev-team/assets/hero_tripo/_work')
import hcommon as H
from mathutils import Matrix, Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=H.GLB)
tr = [o for o in bpy.context.selected_objects if o.type == 'MESH'][0]
bpy.context.view_layer.update()
tr.data.transform(Matrix.Rotation(math.radians(-90), 4, 'Z') @ tr.matrix_world)
tr.matrix_world = Matrix.Identity(4)
zmin = min(v.co.z for v in tr.data.vertices)
tr.data.transform(Matrix.Translation((0, 0, -zmin)))
tree, cos = H.bvh_of([tr])
R = H.ray
print('NECK/HEAD profile (x half-width, y front/back at x=0)')
for i in range(40, 80):
    z = i * 0.01 + 1.0
    a = R(tree, (2, 0, z), (-1, 0, 0)); b = R(tree, (-2, 0, z), (1, 0, 0))
    f = R(tree, (0, -2, z), (0, 1, 0)); k = R(tree, (0, 2, z), (0, -1, 0))
    print(' z=%.2f x=[%s..%s] y=[%s..%s]' % (z, b and '%.3f' % b.x, a and '%.3f' % a.x, f and '%.3f' % f.y, k and '%.3f' % k.y))
print('ARM profile')
for i in range(15, 90):
    x = i * 0.01
    best = None
    for dy in [j * 0.01 - 0.08 for j in range(17)]:
        up = R(tree, (x, dy, 1.1), (0, 0, 1)); dn = R(tree, (x, dy, 2.2), (0, 0, -1))
        if up and dn and dn.z > up.z and dn.z - up.z < 0.4:
            t = dn.z - up.z
            if best is None or t > best[0]:
                best = (t, (up.z + dn.z) / 2, dy)
    zc = best[1] if best else 1.43
    f = R(tree, (x, -2, zc), (0, 1, 0)); k = R(tree, (x, 2, zc), (0, -1, 0))
    print(' x=%.2f %s ydepth=[%s..%s]' % (x, best and 'th=%.3f zc=%.3f' % best[:2], f and '%.3f' % f.y, k and '%.3f' % k.y))
print('LEG profile (left leg, x>0)')
for i in range(0, 95, 3):
    z = i * 0.01
    a = R(tree, (2, 0, z), (-1, 0, 0)); b = R(tree, (0.0005, 0, z), (1, 0, 0))
    cx = (a.x + b.x) / 2 if a and b else None
    f = R(tree, (cx or 0.15, -2, z), (0, 1, 0)); k = R(tree, (cx or 0.15, 2, z), (0, -1, 0))
    print(' z=%.2f x=[%s..%s] y=[%s..%s]' % (z, b and '%.3f' % b.x, a and '%.3f' % a.x, f and '%.3f' % f.y, k and '%.3f' % k.y))
