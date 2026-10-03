"""Profiles of cloth_t1.glb (oriented like the hero build) + T0 hero rings at the slot cuts.
Run: blender.exe -b --factory-startup --python 03_diag.py
"""
import bpy, sys, math
sys.path.insert(0, 'E:/game-dev-team/assets/hero_tripo/_work')
import hcommon as H
from mathutils import Matrix, Vector
GLB = 'E:/ContrarySurvior/ContrarySurvivor/Saved/Tripo/cloth_t1/cloth_t1.glb'
R = H.ray


def f3(p, k):
    return p and '%.3f' % getattr(p, k)


bpy.ops.wm.open_mainfile(filepath='E:/game-dev-team/assets/hero_tripo/_work/hero_work.blend')
parts = [bpy.data.objects[n] for n in ('SK_Cloth_T0_Head', 'SK_Cloth_T0_Torso', 'SK_Cloth_T0_Legs')]
rig = bpy.data.objects['RootAnim']
for b in rig.data.bones:
    print('BONE %-18s head=(%.3f,%.3f,%.3f) tail=(%.3f,%.3f,%.3f)' % (b.name, *b.head_local, *b.tail_local))
tree, cos = H.bvh_of(parts)
print('T0 height %.3f x=[%.3f..%.3f] y=[%.3f..%.3f]' % (max(c.z for c in cos), min(c.x for c in cos), max(c.x for c in cos), min(c.y for c in cos), max(c.y for c in cos)))
for z in (0.80, 0.86, 0.90, 0.905, 0.91, 0.95, 1.00, 1.10, 1.20, 1.30, 1.40, 1.46, 1.50, 1.532, 1.54, 1.549, 1.58, 1.65, 1.75):
    a = R(tree, (2, -0.001, z), (-1, 0, 0)); f = R(tree, (0, -2, z), (0, 1, 0)); k = R(tree, (0, 2, z), (0, -1, 0))
    print('T0 z=%.3f half-width x=%s y=[%s..%s]' % (z, f3(a, 'x'), f3(f, 'y'), f3(k, 'y')))
for z, yc in ((0.905, 0.0), (1.540, 0.0)):
    ring = []
    for i in range(24):
        th = 2 * math.pi * i / 24
        h = R(tree, (0, yc, z), (math.cos(th), math.sin(th), 0))
        ring.append(h and math.hypot(h.x, h.y - yc))
    print('T0 ring z=%.3f r(theta, 15deg steps from +X)=%s' % (z, ['%.3f' % r if r else None for r in ring]))
for z in (0.3, 0.5, 0.7, 0.8):
    a = R(tree, (2, 0, z), (-1, 0, 0)); b = R(tree, (0.0005, 0, z), (1, 0, 0))
    cx = (a.x + b.x) / 2 if a and b else 0.12
    f = R(tree, (cx, -2, z), (0, 1, 0)); k = R(tree, (cx, 2, z), (0, -1, 0))
    print('T0 leg z=%.2f x=[%s..%s] y=[%s..%s]' % (z, f3(b, 'x'), f3(a, 'x'), f3(f, 'y'), f3(k, 'y')))
for x in (0.35, 0.5, 0.7, 0.85):
    up = R(tree, (x, 0, 1.1), (0, 0, 1)); dn = R(tree, (x, 0, 2.2), (0, 0, -1))
    print('T0 arm x=%.2f z=[%s..%s]' % (x, f3(up, 'z'), f3(dn, 'z')))

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=GLB)
tr = [o for o in bpy.context.selected_objects if o.type == 'MESH'][0]
bpy.context.view_layer.update()
tr.data.transform(Matrix.Rotation(math.radians(-90), 4, 'Z') @ tr.matrix_world)
tr.matrix_world = Matrix.Identity(4)
vs = tr.data.vertices
zmin = min(v.co.z for v in vs)
chest = [v.co for v in vs if 1.0 < v.co.z - zmin < 1.3]
xc = (min(c.x for c in chest) + max(c.x for c in chest)) / 2
yc = (min(c.y for c in chest) + max(c.y for c in chest)) / 2
tr.data.transform(Matrix.Translation((-xc, -0.001 - yc, -zmin)))
print('NEW shift', -xc, -0.001 - yc, -zmin)
tree, cos = H.bvh_of([tr])
print('NEW height %.3f x=[%.3f..%.3f] y=[%.3f..%.3f]' % (max(c.z for c in cos), min(c.x for c in cos), max(c.x for c in cos), min(c.y for c in cos), max(c.y for c in cos)))
print('NEW crotch', R(tree, (0, -0.001, 0.3), (0, 0, 1)))
print('NECK/HEAD profile')
for i in range(30, 82):
    z = i * 0.01 + 1.0
    a = R(tree, (2, 0, z), (-1, 0, 0)); b = R(tree, (-2, 0, z), (1, 0, 0))
    f = R(tree, (0, -2, z), (0, 1, 0)); k = R(tree, (0, 2, z), (0, -1, 0))
    print(' z=%.2f x=[%s..%s] y=[%s..%s]' % (z, f3(b, 'x'), f3(a, 'x'), f3(f, 'y'), f3(k, 'y')))
print('TORSO profile')
for i in range(70, 130, 2):
    z = i * 0.01
    a = R(tree, (2, -0.001, z), (-1, 0, 0)); f = R(tree, (0, -2, z), (0, 1, 0)); k = R(tree, (0, 2, z), (0, -1, 0))
    f2 = R(tree, (0.12, -2, z), (0, 1, 0)); k2 = R(tree, (0.12, 2, z), (0, -1, 0))
    print(' z=%.2f half-width x=%s y(x=0)=[%s..%s] y(x=.12)=[%s..%s]' % (z, f3(a, 'x'), f3(f, 'y'), f3(k, 'y'), f3(f2, 'y'), f3(k2, 'y')))
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
    print(' x=%.2f %s ydepth=[%s..%s]' % (x, best and 'th=%.3f zc=%.3f' % best[:2], f3(f, 'y'), f3(k, 'y')))
print('LEG profile (x>0)')
for i in range(0, 95, 3):
    z = i * 0.01
    a = R(tree, (2, 0, z), (-1, 0, 0)); b = R(tree, (0.0005, 0, z), (1, 0, 0))
    cx = (a.x + b.x) / 2 if a and b else None
    f = R(tree, (cx or 0.15, -2, z), (0, 1, 0)); k = R(tree, (cx or 0.15, 2, z), (0, -1, 0))
    print(' z=%.2f x=[%s..%s] y=[%s..%s]' % (z, f3(b, 'x'), f3(a, 'x'), f3(f, 'y'), f3(k, 'y')))
