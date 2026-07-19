"""Сверка кодировки цвета: берёза vs существующее SM_Tree_01, одним и тем же замером.

Вопрос: попадёт ли берёза в ту же цветовую кодировку, что уже лежащие деревья
(иначе в UE она будет ярче/темнее соседей). Меряем ЧИСЛО, лежащее в FBX.
"""
import bpy

PAIRS = [
    ('BIRCH', 'E:/game-dev-team/assets/birch/SM_Tree_Birch_01.fbx',
     {'кора берёзы': '#E7E4D8', 'листва светлая': '#5C7A3E', 'листва тёмная': '#3F5A31'}),
    ('TREE_01', 'E:/ForGameLead(Materials)/phase3-assets/SM_Tree_01.fbx',
     {'ствол': '#543622', 'крона': '#38702B'}),
]


def s2l(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


bpy.ops.wm.read_factory_settings(use_empty=True)

for label, path, intended in PAIRS:
    print('=' * 72)
    print('%s  %s' % (label, path))
    print('  ОЖИДАЕМ в FBX (linear = s2l(задуманный sRGB)):')
    for nm, hexs in intended.items():
        h = hexs.lstrip('#')
        srgb = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
        print('     %-16s %s -> linear (%.4f, %.4f, %.4f)' % (
            nm, hexs, s2l(srgb[0]), s2l(srgb[1]), s2l(srgb[2])))
    before = set(o.name for o in bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path)
    for o in [x for x in bpy.data.objects if x.name not in before and x.type == 'MESH']:
        if o.name.startswith('UCX'):
            continue
        ca = o.data.color_attributes[0]
        seen = {}
        for d in ca.data:
            # .color_srgb на реимпорте отдаёт СЫРОЕ число из FBX (см. урок 07-09)
            seen[tuple(round(x, 4) for x in d.color_srgb[:3])] = seen.get(
                tuple(round(x, 4) for x in d.color_srgb[:3]), 0) + 1
        print('  ФАКТ в файле %s:' % o.name)
        for c, n in sorted(seen.items(), key=lambda kv: -kv[1]):
            print('     linear (%.4f, %.4f, %.4f)  углов=%d' % (c[0], c[1], c[2], n))
print('DONE')
