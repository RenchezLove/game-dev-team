"""Look at the downloaded tent (Sketchfab, simonaskLDE) and at the old SM_Tent: objects, triangles, bounds, materials, views.
Run: blender.exe -b --factory-startup --python 00_inspect.py
"""
import bpy, math, addon_utils
import numpy as np
from mathutils import Vector
SRC = 'C:/Users/pgr40/Desktop/GamdevAITeam/Палатка/low-poly-survival-tent/source/tent.fbx'
OLD = 'E:/ForGameLead(Materials)/demo-assets/SM_Tent.fbx'
OUT = 'E:/game-dev-team/assets/tent_survival/_work/_look/'
def load(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    addon_utils.enable('io_scene_fbx')
    bpy.ops.import_scene.fbx(filepath=path)
    bpy.context.view_layer.update()
    return [o for o in bpy.data.objects if o.type == 'MESH']
def info(tag, ms):
    print('%s objects: %s' % (tag, [(o.name, o.type, o.parent.name if o.parent else None) for o in bpy.data.objects]))
    allc = []
    for o in ms:
        me = o.data; mw = o.matrix_world
        cs = np.array([mw @ v.co for v in me.vertices]); allc.append(cs)
        tris = sum(len(p.vertices) - 2 for p in me.polygons)
        print('%s mesh %s: faces=%d tris=%d verts=%d min=%s max=%s scale=%s rot=%s mats=%s uv=%s vcol=%s' % (tag, o.name, len(me.polygons), tris, len(me.vertices), cs.min(0).round(3), cs.max(0).round(3),
              tuple(round(a, 4) for a in mw.to_scale()), tuple(round(math.degrees(a), 1) for a in mw.to_euler()), [m.name if m else None for m in me.materials], [u.name for u in me.uv_layers], [c.name for c in me.color_attributes]))
        for m in me.materials:
            if m and m.node_tree:
                for n in m.node_tree.nodes:
                    if n.type == 'TEX_IMAGE':
                        print('%s   material %s texture %s' % (tag, m.name, n.image.filepath if n.image else None))
                    if n.type == 'BSDF_PRINCIPLED':
                        print('%s   material %s base colour %s linked=%s' % (tag, m.name, tuple(round(a, 3) for a in n.inputs['Base Color'].default_value), n.inputs['Base Color'].is_linked))
        cnt = {}
        for p in me.polygons:
            cnt[p.material_index] = cnt.get(p.material_index, 0) + len(p.vertices) - 2
        print('%s   tris by material slot: %s' % (tag, cnt))
    c = np.concatenate(allc)
    print('%s TOTAL tris=%d min=%s max=%s size=%s' % (tag, sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in ms), c.min(0).round(3), c.max(0).round(3), (c.max(0) - c.min(0)).round(3)))
    return c
def shots(tag, c):
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_WORKBENCH'
    sc.display.shading.light = 'STUDIO'; sc.display.shading.color_type = 'MATERIAL' if tag == 'src' else 'VERTEX'
    sc.display.shading.show_backface_culling = True
    cd = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', cd); sc.collection.objects.link(cam); sc.camera = cam
    mid = Vector((c.min(0) + c.max(0)) / 2); size = float((c.max(0) - c.min(0)).max())
    for name, yaw, pit in (('front', 0, 12), ('back', 180, 12), ('left', -90, 12), ('right', 90, 12), ('top', 0, 89), ('q1', 35, 45), ('q2', 215, 45), ('game', 28, 60)):
        y, p = math.radians(yaw), math.radians(pit)
        d = Vector((math.sin(y) * math.cos(p), -math.cos(y) * math.cos(p), math.sin(p)))
        cam.location = mid + d * size * 4.5; cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
        cd.angle = math.radians(22); cd.clip_end = size * 20; cd.clip_start = size * 0.05
        sc.render.resolution_x, sc.render.resolution_y = 800, 600
        sc.render.filepath = OUT + '%s_%s.png' % (tag, name); bpy.ops.render.render(write_still=True)
ms = load(SRC); c = info('SRC', ms)
# colour the source by material slot so that the parts are told apart
shots('src', c)
ms = load(OLD); c = info('OLD', ms); shots('old', c)
