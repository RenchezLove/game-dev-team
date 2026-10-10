import bpy, sys
import numpy as np
sys.path.insert(0, 'E:/game-dev-team/assets/scientist_base/_work')
import sb
bpy.ops.wm.open_mainfile(filepath=sb.SRCD + 'low-poly-toz-34/source/toz34.blend', use_scripts=False)
o = bpy.data.objects['toz34 barrels']; me = o.data; mw = o.matrix_world
names = [m.name for m in me.materials]
V = np.array([mw @ v.co for v in me.vertices])
print('obj bounds', V.min(0).round(3), V.max(0).round(3))
used = set()
for p in me.polygons:
    if names[p.material_index] == '1b':
        used.update(p.vertices)
B = V[sorted(used)]
print('black bounds', B.min(0).round(3), B.max(0).round(3))
for x0 in (1.0, 3.0, 6.0, 9.0, 10.9):
    s = B[abs(B[:, 0] - x0) < 0.6]
    pts = sorted({(round(float(a), 2), round(float(b), 2)) for a, b in s[:, 1:3]})
    print('x~%.1f n %d  (y,z):' % (x0, len(s)), pts[:40])
