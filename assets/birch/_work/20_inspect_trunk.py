"""Разбор существующих лиственных деревьев: что именно можно перекрасить.

Ключевой вопрос: сколько КОЛЕЦ вершин у ствола. Цвет вершин живёт в углах граней,
то есть менять цвет можно только там, где есть вершины. Если у ствола всего два
кольца (низ и верх), поперечные чёрточки берёзы геометрически негде разместить.
"""
import bpy, os
from collections import defaultdict

SRC = "E:/ForGameLead(Materials)/phase3-assets/"
TREES = ['SM_Tree_01', 'SM_Tree_02', 'SM_Tree_03']

bpy.ops.wm.read_factory_settings(use_empty=True)

for name in TREES:
    bpy.ops.import_scene.fbx(filepath=SRC + name + '.fbx')
    ob = bpy.data.objects[name]
    me = ob.data
    me.calc_loop_triangles()
    ca = me.color_attributes[0]

    # классификация граней по существующему цвету
    by_col = defaultdict(list)
    for p in me.polygons:
        c = tuple(round(x, 4) for x in ca.data[p.loop_indices[0]].color_srgb[:3])
        by_col[c].append(p.index)

    print('=' * 74)
    print('%s: tris=%d verts=%d  цветов=%d' % (name, len(me.loop_triangles),
                                               len(me.vertices), len(by_col)))
    for c, faces in sorted(by_col.items(), key=lambda kv: -len(kv[1])):
        vids = set()
        for fi in faces:
            vids.update(me.polygons[fi].vertices)
        zs = sorted(set(round(me.vertices[v].co.z, 4) for v in vids))
        zmin = min(me.vertices[v].co.z for v in vids)
        zmax = max(me.vertices[v].co.z for v in vids)
        role = 'СТВОЛ' if len(zs) <= 4 and zmax < 1.6 else 'КРОНА'
        print('  цвет linear(%.4f, %.4f, %.4f) -> %s' % (c[0], c[1], c[2], role))
        print('     граней=%d  вершин=%d  Z от %.3f до %.3f' % (
            len(faces), len(vids), zmin, zmax))
        print('     КОЛЬЦА вершин по Z (%d шт): %s' % (
            len(zs), ', '.join('%.3f' % z for z in zs[:12])))
print('DONE')
