"""Differentiating test for the dark-vcol export bug: export SK_Elder_Legs 3x,
varying ONLY the FBX vertex-color-space setting (bpy.ops.export_scene.fbx
colors_type). Geometry/weights/skeleton identical to the shipped legs — only
colors_type differs. game-lead reads each in UE (Geometry Script) to pick the
one where the trousers come out ~#48453F = (0.28,0.27,0.25), not black.

Variants (colors_type enum in Blender 5.1.2 FBX exporter):
  v1_linear = 'LINEAR'  (CURRENT/shipped setting — reproduces the bug, baseline)
  v2_srgb   = 'SRGB'    (predicted FIX: FBX carries palette sRGB bytes as-is)
  v3_none   = 'NONE'    (control: no color attr exported at all)
Also re-imports each and reports black% + top colors as a Blender-side proxy
(authority = game-lead's UE read).
Run: blender.exe -b --factory-startup --python 13_probe_colorspace.py
"""
import bpy, addon_utils, sys, os
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W

OUT = 'E:/game-dev-team/assets/npc_elder/_diag_export/'
os.makedirs(OUT, exist_ok=True)
VARIANTS = [('v1_linear', 'LINEAR'), ('v2_srgb', 'SRGB'), ('v3_none', 'NONE')]


def export_legs(colors_type, path):
    bpy.ops.wm.open_mainfile(filepath='E:/game-dev-team/assets/npc_elder/_work/elder_work.blend')
    addon_utils.enable('io_scene_fbx')
    rig = bpy.data.objects['RootAnim']
    for pb in rig.pose.bones:                       # rest pose before export
        pb.rotation_mode = 'XYZ'
        pb.rotation_euler = (0, 0, 0)
        pb.location = (0, 0, 0)
        pb.scale = (1, 1, 1)
    ob = bpy.data.objects['SK_Elder_Legs']
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    rig.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.export_scene.fbx(
        filepath=path, use_selection=True,
        object_types={'MESH', 'ARMATURE'}, mesh_smooth_type='FACE',
        use_mesh_modifiers=False, add_leaf_bones=False, bake_anim=False,
        path_mode='AUTO', colors_type=colors_type)


def is_black(c, eps=0.02):
    return c[0] < eps and c[1] < eps and c[2] < eps


for name, ct in VARIANTS:
    path = OUT + 'SK_Elder_Legs_%s.fbx' % name
    export_legs(ct, path)
    print('EXPORTED %s colors_type=%s (%.1f KB)' % (path, ct, os.path.getsize(path) / 1024))

print('\n=== RE-IMPORT PROXY (authority = UE) ===')
for name, ct in VARIANTS:
    path = OUT + 'SK_Elder_Legs_%s.fbx' % name
    bpy.ops.wm.read_factory_settings(use_empty=True)
    addon_utils.enable('io_scene_fbx')
    bpy.ops.import_scene.fbx(filepath=path)
    for ob in [o for o in bpy.data.objects if o.type == 'MESH']:
        me = ob.data
        if not me.color_attributes:
            print('  %-10s NO COLOR ATTR (control)' % name)
            continue
        ca = me.color_attributes.get('Col') or me.color_attributes[0]
        n = len(ca.data)
        black = sum(1 for d in ca.data if is_black(d.color))
        top = {}
        for d in ca.data:
            k = (round(d.color[0], 2), round(d.color[1], 2), round(d.color[2], 2))
            top[k] = top.get(k, 0) + 1
        top3 = sorted(top.items(), key=lambda kv: -kv[1])[:3]
        print('  %-10s colors_type=%-7s black=%d/%d(%.0f%%) top=%s' % (
            name, ct, black, n, 100.0 * black / max(1, n), top3))
print('PROBE DONE')
