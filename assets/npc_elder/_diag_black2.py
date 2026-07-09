"""Thorough: (1) black% of 'Col' in elder_work.blend (pre-export, per module);
(2) re-import each elder FBX and list ALL color attrs + black% + top colors.
Pin down whether Elder_Legs 100%-black is a real export loss or a diag artifact.
Run: blender.exe -b --factory-startup --python _diag_black2.py
"""
import bpy, addon_utils, os


def is_black(c, eps=0.02):
    return c[0] < eps and c[1] < eps and c[2] < eps


def attr_black(me, ca):
    n = len(ca.data)
    black = sum(1 for d in ca.data if is_black(d.color))
    top = {}
    for d in ca.data:
        k = (round(d.color[0], 2), round(d.color[1], 2), round(d.color[2], 2))
        top[k] = top.get(k, 0) + 1
    top5 = sorted(top.items(), key=lambda kv: -kv[1])[:5]
    return n, black, top5


print('=== (1) PRE-EXPORT elder_work.blend ===')
bpy.ops.wm.open_mainfile(filepath='E:/game-dev-team/assets/npc_elder/_work/elder_work.blend')
for n in ('SK_Elder_Head', 'SK_Elder_Torso', 'SK_Elder_Legs'):
    ob = bpy.data.objects[n]
    me = ob.data
    for ca in me.color_attributes:
        cnt, black, top5 = attr_black(me, ca)
        print('  %-18s attr=%r dom=%s type=%s n=%d black=%d(%.0f%%) top=%s' % (
            n, ca.name, ca.domain, ca.data_type, cnt, black, 100.0 * black / max(1, cnt), top5))

print('=== (2) RE-IMPORT FBX ===')
for path in ('E:/game-dev-team/assets/npc_elder/SK_Elder_Head.fbx',
             'E:/game-dev-team/assets/npc_elder/SK_Elder_Torso.fbx',
             'E:/game-dev-team/assets/npc_elder/SK_Elder_Legs.fbx'):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    addon_utils.enable('io_scene_fbx')
    bpy.ops.import_scene.fbx(filepath=path)
    for ob in [o for o in bpy.data.objects if o.type == 'MESH']:
        me = ob.data
        if not me.color_attributes:
            print('  %-22s NO COLOR ATTRS' % os.path.basename(path))
        for ca in me.color_attributes:
            cnt, black, top5 = attr_black(me, ca)
            print('  %-22s attr=%r dom=%s type=%s n=%d black=%d(%.0f%%) top=%s' % (
                os.path.basename(path), ca.name, ca.domain, ca.data_type,
                cnt, black, 100.0 * black / max(1, cnt), top5))
print('DIAG2 DONE')
