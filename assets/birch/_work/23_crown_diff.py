"""Сверка кроны: принятая лидом сборка (_qc_birch.blend1) против новой.

Причина проверки: в clump() дрожание вершин применялось при обходе МНОЖЕСТВА
(set) bmesh-вершин. Порядок обхода множества зависит от адресов объектов, а они
сдвигаются, когда меняется число вершин ствола. То есть крона молча
пересобиралась при любой правке ствола. Надо понять, насколько разошлось.
"""
import bpy, os
from mathutils import Vector

WORK = "E:/game-dev-team/assets/birch/_work/"
NEW_FBX = "E:/game-dev-team/assets/birch/SM_Tree_Birch_01.fbx"

LEAF_RGB = [tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
            for h in ('5C7A3E', '3F5A31')]


def crown_verts(ob, from_fbx):
    """Вершины кроны: грани, покрашенные в листву.

    В .blend цвет лежит правильно -> задуманный sRGB читается из .color_srgb.
    В реимпортнутом FBX в .color_srgb лежит СЫРОЕ linear-число из файла ->
    сначала возвращаем его в .color, и только тогда .color_srgb даёт sRGB.
    """
    me = ob.data
    ca = me.color_attributes[0]
    if from_fbx:
        raw = [tuple(d.color_srgb) for d in ca.data]
        for d, v in zip(ca.data, raw):
            d.color = (v[0], v[1], v[2], 1.0)
    out = set()
    for p in me.polygons:
        v = ca.data[p.loop_indices[0]].color_srgb[:3]
        # сравниваем с допуском: байтовое округление даёт расхождение в 1/255
        for ref in LEAF_RGB:
            if max(abs(v[i] - ref[i]) for i in range(3)) < 0.02:
                out.update(p.vertices)
                break
    return sorted(tuple(round(x, 5) for x in me.vertices[i].co) for i in out)


def bbox(pts):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]; zs = [p[2] for p in pts]
    return (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))


# --- принятая сборка ---
bpy.ops.wm.open_mainfile(filepath=WORK + '_qc_birch.blend1')
old = crown_verts(bpy.data.objects['SM_Tree_Birch_01'], from_fbx=False)

# --- новая сборка (из экспортированного FBX) ---
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=NEW_FBX)
ob = [o for o in bpy.data.objects if o.type == 'MESH' and not o.name.startswith('UCX')][0]
new = crown_verts(ob, from_fbx=True)

print('=== КРОНА: принятая сборка против новой ===')
print('  вершин кроны: было %d, стало %d' % (len(old), len(new)))
ob_, nb = bbox(old), bbox(new)
print('  габарит кроны БЫЛО : X[%.3f..%.3f] Y[%.3f..%.3f] Z[%.3f..%.3f]' % ob_)
print('  габарит кроны СТАЛО: X[%.3f..%.3f] Y[%.3f..%.3f] Z[%.3f..%.3f]' % nb)
print('  сдвиг границ: %s' % ', '.join('%+.3f' % (n - o) for o, n in zip(ob_, nb)))
identical = (old == new)
print('  ВЕРШИНЫ СОВПАДАЮТ ПОБИТОВО: %s' % identical)
if not identical:
    # насколько далеко уехала каждая вершина от ближайшей старой
    worst = 0.0
    for p in new:
        d = min((Vector(p) - Vector(q)).length for q in old)
        worst = max(worst, d)
    print('  максимальное расхождение вершины: %.4f м' % worst)
print('DONE')
