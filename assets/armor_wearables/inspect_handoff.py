"""Inspect UE-exported humanoid FBX handoff (base body + SK_Cloth_L1 set).
Dumps per file: objects, armature bones (order/names), mesh stats (verts/tris,
vgroups, vcol layers + unique colors, UV, materials, world bbox, modifiers).
Run: blender.exe -b --factory-startup --python inspect_handoff.py
"""
import bpy, addon_utils, os

SRC = 'E:/game-dev-team/assets/_handoff/humanoid-export/'
FILES = [
    'HeadAndSkeletonfbx_Head.fbx',
    'TorsoAndSkeleton_Torso.fbx',
    'LegsAndSkeleton_Legs.fbx',
    'SK_Cloth_L1_Head.fbx',
    'SK_Cloth_L1_Torso.fbx',
    'SK_Cloth_L1_Legs.fbx',
]


def l2s(c):
    return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055


def import_fbx(path):
    try:
        addon_utils.enable('io_scene_fbx')
        bpy.ops.import_scene.fbx(filepath=path)
        return 'io_scene_fbx'
    except Exception as e:
        print('  legacy importer failed: %r' % e)
        bpy.ops.wm.fbx_import(filepath=path)
        return 'wm.fbx_import'


for fname in FILES:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    path = SRC + fname
    print('\n===== FILE %s (%.1f KB) =====' % (fname, os.path.getsize(path) / 1024))
    used = import_fbx(path)
    print('importer:', used)
    for ob in bpy.data.objects:
        print(' OBJ name=%r type=%s loc=%s rot_eul=%s scale=%s' % (
            ob.name, ob.type,
            tuple(round(v, 4) for v in ob.location),
            tuple(round(v, 3) for v in ob.rotation_euler),
            tuple(round(v, 4) for v in ob.scale)))
        if ob.type == 'ARMATURE':
            bones = ob.data.bones
            print('  ARMATURE datablock=%r bones=%d' % (ob.data.name, len(bones)))
            for b in bones:
                hw = ob.matrix_world @ b.head_local
                print('   bone %-20s parent=%-14s headW=(%.3f,%.3f,%.3f)' % (
                    b.name, b.parent.name if b.parent else '-', hw.x, hw.y, hw.z))
        elif ob.type == 'MESH':
            me = ob.data
            me.calc_loop_triangles()
            deps = bpy.context.evaluated_depsgraph_get()
            bb = [ob.matrix_world @ v.co for v in me.vertices]
            xs = [v.x for v in bb]; ys = [v.y for v in bb]; zs = [v.z for v in bb]
            print('  MESH verts=%d polys=%d tris=%d' % (
                len(me.vertices), len(me.polygons), len(me.loop_triangles)))
            print('  bboxW x=[%.3f..%.3f] y=[%.3f..%.3f] z=[%.3f..%.3f]' % (
                min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)))
            print('  vgroups=%d names=%s' % (len(ob.vertex_groups),
                                             [g.name for g in ob.vertex_groups]))
            unweighted = sum(1 for v in me.vertices if not v.groups)
            print('  unweighted_verts=%d' % unweighted)
            print('  uv_layers=%s' % [u.name for u in me.uv_layers])
            print('  materials=%s' % [m.name if m else None for m in me.materials])
            print('  modifiers=%s' % [(m.type, getattr(m, "object", None).name
                                       if getattr(m, "object", None) else None)
                                      for m in ob.modifiers])
            for ca in me.color_attributes:
                print('  vcol %r domain=%s type=%s' % (ca.name, ca.domain, ca.data_type))
                seen = {}
                for d in ca.data:
                    c = d.color
                    key = (round(c[0], 3), round(c[1], 3), round(c[2], 3), round(c[3], 2))
                    seen[key] = seen.get(key, 0) + 1
                    if len(seen) > 40:
                        break
                print('  unique_colors(raw,count)<=40:')
                for k, n in sorted(seen.items(), key=lambda kv: -kv[1]):
                    srgb_hex = '#%02X%02X%02X' % tuple(
                        max(0, min(255, round(l2s(k[i]) * 255))) for i in range(3))
                    raw_hex = '#%02X%02X%02X' % tuple(
                        max(0, min(255, round(k[i] * 255))) for i in range(3))
                    print('    raw=%s a=%.2f n=%d rawhex=%s ifLinThenSrgb=%s' % (
                        k[:3], k[3], n, raw_hex, srgb_hex))
print('\nINSPECT DONE')
