"""Вынимает ПРИНЯТУЮ крону из _qc_birch.blend1 и записывает её данными в .py.

Зачем: дрожание вершин в clump() применялось при обходе МНОЖЕСТВА bmesh-вершин,
порядок которого зависит от числа вершин ствола. Из-за этого крона молча
пересобиралась при любой правке ствола (замерено: до 0.103 м на вершину).
Лечение: крону, которую принял лид, зафиксировать данными и больше не
генерировать заново. Каждый комок сохраняется отдельным куском, чтобы для
упрощённых версий можно было взять подмножество комков.
"""
import bpy, os
from mathutils import Vector

WORK = "E:/game-dev-team/assets/birch/_work/"
OUT = WORK + "crown_approved.py"

LEAF_RGB = {'5C7A3E': tuple(int('5C7A3E'[i:i + 2], 16) / 255.0 for i in (0, 2, 4)),
            '3F5A31': tuple(int('3F5A31'[i:i + 2], 16) / 255.0 for i in (0, 2, 4))}
# центры комков из билдера — по ним опознаём, какой кусок каким был
CLUMP_CENTERS = [(0.02, 0.16, 1.62), (-0.26, 0.04, 1.44), (0.25, 0.30, 1.54),
                 (0.02, 0.19, 1.88), (-0.07, -0.14, 1.34)]

bpy.ops.wm.open_mainfile(filepath=WORK + '_qc_birch.blend1')
ob = bpy.data.objects['SM_Tree_Birch_01']
me = ob.data
ca = me.color_attributes[0]


def face_hex(p):
    v = ca.data[p.loop_indices[0]].color_srgb[:3]
    for h, ref in LEAF_RGB.items():
        if max(abs(v[i] - ref[i]) for i in range(3)) < 0.02:
            return h
    return None


crown_faces = [p for p in me.polygons if face_hex(p)]
print('граней кроны: %d' % len(crown_faces))

# связные куски (каждый комок — отдельная замкнутая оболочка)
adj = {}
for p in crown_faces:
    for v in p.vertices:
        adj.setdefault(v, []).append(p.index)
seen, parts = set(), []
for p in crown_faces:
    if p.index in seen:
        continue
    stack, comp = [p.index], []
    seen.add(p.index)
    while stack:
        fi = stack.pop()
        comp.append(fi)
        for v in me.polygons[fi].vertices:
            for nb in adj[v]:
                if nb not in seen:
                    seen.add(nb)
                    stack.append(nb)
    parts.append(comp)
print('кусков (комков): %d' % len(parts))

blocks = []
for comp in parts:
    vids = sorted({v for fi in comp for v in me.polygons[fi].vertices})
    remap = {v: i for i, v in enumerate(vids)}
    verts = [tuple(round(c, 6) for c in me.vertices[v].co) for v in vids]
    faces = [tuple(remap[v] for v in me.polygons[fi].vertices) for fi in comp]
    hexes = {face_hex(me.polygons[fi]) for fi in comp}
    ctr = Vector((sum(v[0] for v in verts) / len(verts),
                  sum(v[1] for v in verts) / len(verts),
                  sum(v[2] for v in verts) / len(verts)))
    idx = min(range(len(CLUMP_CENTERS)),
              key=lambda i: (ctr - Vector(CLUMP_CENTERS[i])).length)
    blocks.append((idx, verts, faces, sorted(hexes)[0]))
    print('  комок %d: вершин=%d граней=%d цвет=%s центр=(%.3f, %.3f, %.3f)'
          % (idx, len(verts), len(faces), sorted(hexes)[0], ctr.x, ctr.y, ctr.z))

blocks.sort(key=lambda b: b[0])
assert [b[0] for b in blocks] == list(range(len(CLUMP_CENTERS))), 'комки не опознались'

with open(OUT, 'w', encoding='utf-8') as f:
    f.write('"""ПРИНЯТАЯ ЛИДОМ крона берёзы, зафиксирована данными.\n\n'
            'Снята из _qc_birch.blend1 (сборка, которую принял лид) скриптом\n'
            '24_extract_crown.py. Заново НЕ генерируется: процедурное дрожание\n'
            'вершин было недетерминированным и меняло крону при правках ствола.\n'
            'Формат: CLUMPS_BAKED[i] = (вершины, треугольники, цвет sRGB).\n"""\n\n')
    f.write('CLUMPS_BAKED = [\n')
    for idx, verts, faces, hx in blocks:
        f.write('    (  # комок %d, цвет #%s\n' % (idx, hx))
        f.write('        %r,\n' % (verts,))
        f.write('        %r,\n' % (faces,))
        f.write("        '#%s',\n    ),\n" % hx)
    f.write(']\n')

print('ЗАПИСАНО %s exists=%s size=%d' % (OUT, os.path.exists(OUT), os.path.getsize(OUT)))
print('DONE')
