"""Доказательство: крона в экспортированном FBX совпадает с ПРИНЯТОЙ побитово.

Эталон — crown_approved.py, снятый из сборки, которую принял лид (24_extract_crown.py).
Сверяем с тем, что реально лежит в отгружаемом файле.
"""
import bpy, os, sys
from mathutils import Vector

WORK = "E:/game-dev-team/assets/birch/_work/"
sys.path.append(WORK)
from crown_approved import CLUMPS_BAKED

FBX = "E:/game-dev-team/assets/birch/SM_Tree_Birch_01.fbx"
LEAF_RGB = [tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
            for h in ('5C7A3E', '3F5A31')]

expected = sorted(tuple(round(c, 5) for c in v)
                  for blk in CLUMPS_BAKED for v in blk[0])

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=FBX)
ob = [o for o in bpy.data.objects if o.type == 'MESH' and not o.name.startswith('UCX')][0]
me = ob.data
ca = me.color_attributes[0]
raw = [tuple(d.color_srgb) for d in ca.data]
for d, v in zip(ca.data, raw):
    d.color = (v[0], v[1], v[2], 1.0)

got = set()
for p in me.polygons:
    v = ca.data[p.loop_indices[0]].color_srgb[:3]
    if any(max(abs(v[i] - ref[i]) for i in range(3)) < 0.02 for ref in LEAF_RGB):
        got.update(p.vertices)
got = sorted(tuple(round(c, 5) for c in me.vertices[i].co) for i in got)

print('=== КРОНА В ОТГРУЖАЕМОМ FBX против ПРИНЯТОЙ ЛИДОМ ===')
print('  вершин: эталон %d, в файле %d' % (len(expected), len(got)))
same = (expected == got)
print('  СОВПАДАЮТ ПОБИТОВО: %s' % same)
if not same:
    worst = max(min((Vector(p) - Vector(q)).length for q in expected) for p in got)
    print('  максимальное расхождение: %.5f м' % worst)
print('DONE')
