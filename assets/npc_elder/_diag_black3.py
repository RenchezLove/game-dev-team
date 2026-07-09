"""Distinguish build-bug vs export-bug: black% of dark equipment PRE-export (in
wearables_t2t3.blend) vs POST-export (FBX). If pre=0% and post=high -> export
crushes dark colors, not a paint bug. Run: blender.exe -b --factory-startup --python _diag_black3.py
"""
import bpy, addon_utils, os

WA = 'E:/game-dev-team/assets/armor_wearables/'


def is_black(c, eps=0.02):
    return c[0] < eps and c[1] < eps and c[2] < eps


def frac(me):
    ca = me.color_attributes.get('Col') or me.color_attributes[0]
    n = len(ca.data)
    b = sum(1 for d in ca.data if is_black(d.color))
    return n, b, 100.0 * b / max(1, n)


print('=== PRE-EXPORT wearables_t2t3.blend ===')
bpy.ops.wm.open_mainfile(filepath=WA + '_work/wearables_t2t3.blend')
for n in ('SK_Armor_T2_Torso', 'SK_Armor_T2_Legs', 'SK_Armor_T3_Torso', 'SK_Armor_T3_Legs',
          'SK_Armor_T2_Head', 'SK_Armor_T3_Head'):
    if n in bpy.data.objects:
        cnt, b, pct = frac(bpy.data.objects[n].data)
        print('  %-22s n=%d black=%d(%.0f%%)' % (n, cnt, b, pct))

print('=== POST-EXPORT FBX ===')
for n in ('SK_Armor_T2_Torso', 'SK_Armor_T2_Legs', 'SK_Armor_T2_Head',
          'SK_Armor_T3_Torso', 'SK_Armor_T3_Legs', 'SK_Armor_T3_Head'):
    p = WA + n + '.fbx'
    if not os.path.exists(p):
        continue
    bpy.ops.wm.read_factory_settings(use_empty=True)
    addon_utils.enable('io_scene_fbx')
    bpy.ops.import_scene.fbx(filepath=p)
    for ob in [o for o in bpy.data.objects if o.type == 'MESH']:
        cnt, b, pct = frac(ob.data)
        print('  %-22s n=%d black=%d(%.0f%%)' % (n, cnt, b, pct))
print('DIAG3 DONE')
