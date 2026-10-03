"""Inspect source Izba.fbx and the old SM_VillageHouse.fbx; render source from 6 sides.
Run: blender.exe -b --factory-startup --python 01_inspect.py
"""
import bpy, sys, os
import numpy as np
import addon_utils
from mathutils import Vector
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W

SRC = 'C:/Users/pgr40/Desktop/GamdevAITeam/Izba/source/Izba.fbx'
TEX = 'C:/Users/pgr40/Desktop/GamdevAITeam/Izba/textures/Baked_Textures.png'
OLD = 'E:/ForGameLead(Materials)/demo-assets/SM_VillageHouse.fbx'
OUT = 'E:/game-dev-team/assets/izba_slate/_work/'


def dump(tag):
    bpy.context.view_layer.update()
    for o in bpy.data.objects:
        print(tag, 'OBJ', o.name, o.type, 'parent=', o.parent.name if o.parent else None,
              'loc', tuple(round(a, 4) for a in o.matrix_world.to_translation()),
              'rot', tuple(round(a, 4) for a in o.matrix_world.to_euler()),
              'scl', tuple(round(a, 4) for a in o.matrix_world.to_scale()))
        if o.type != 'MESH':
            continue
        me = o.data
        cs = np.array([o.matrix_world @ v.co for v in me.vertices])
        tris = sum(len(p.vertices) - 2 for p in me.polygons)
        print(tag, '  tris', tris, 'verts', len(me.vertices), 'polys', len(me.polygons),
              'min', cs.min(0).round(4), 'max', cs.max(0).round(4), 'size', (cs.max(0) - cs.min(0)).round(4))
        print(tag, '  uv', [u.name for u in me.uv_layers], 'mats', [m.name if m else None for m in me.materials],
              'cols', [(c.name, c.domain, c.data_type) for c in me.color_attributes])
        import bmesh
        bm = bmesh.new(); bm.from_mesh(me)
        print(tag, '  open_edges', sum(1 for e in bm.edges if len(e.link_faces) == 1),
              'nonmanifold>2', sum(1 for e in bm.edges if len(e.link_faces) > 2),
              'smooth', sum(1 for f in bm.faces if f.smooth), '/', len(bm.faces))
        bm.free()
        for m in me.materials:
            if m and m.node_tree:
                for n in m.node_tree.nodes:
                    if n.type == 'TEX_IMAGE':
                        print(tag, '  tex', n.image.filepath if n.image else None)


bpy.ops.wm.read_factory_settings(use_empty=True)
addon_utils.enable('io_scene_fbx')
bpy.ops.import_scene.fbx(filepath=OLD)
dump('OLD')
# where is the old door: darkest warm faces low on the walls -> print census of colours on each side wall strip
for o in [o for o in bpy.data.objects if o.type == 'MESH']:
    me = o.data
    ca = me.color_attributes[0]
    mw = o.matrix_world
    side = {}
    for p in me.polygons:
        c = mw @ p.center
        n = (mw.to_3x3() @ p.normal).normalized()
        if c.z > 2.0 or c.z < 0.3:
            continue
        col = ca.data[p.loop_indices[0]].color_srgb
        key = ('+X' if n.x > 0.9 else '-X' if n.x < -0.9 else '+Y' if n.y > 0.9 else '-Y' if n.y < -0.9 else None)
        if key is None:
            continue
        hx = '%02X%02X%02X' % tuple(round(a * 255) for a in col[:3])
        side.setdefault(key, {}).setdefault(hx, [0.0, None])
        side[key][hx][0] += p.area
    for k in sorted(side):
        print('OLD side', k, {h: round(v[0], 2) for h, v in sorted(side[k].items(), key=lambda t: -t[1][0])})
    # extremes per side (porch/step sticks out)
    cs = np.array([mw @ v.co for v in me.vertices])
    low = cs[cs[:, 2] < 0.4]
    print('OLD low(z<0.4) min', low.min(0).round(3), 'max', low.max(0).round(3))
    body = cs[(cs[:, 2] > 0.6) & (cs[:, 2] < 2.2)]
    print('OLD walls(z 0.6..2.2) min', body.min(0).round(3), 'max', body.max(0).round(3))

sc, cam, suns = W.setup_render(res=700)
olds = [o for o in bpy.data.objects if o.type == 'MESH']
for vn, vd in (('front_mY', (0.25, -1, 0.25)), ('back_pY', (-0.25, 1, 0.25)), ('top', (0.001, -0.02, 1))):
    W.frame_and_shoot(olds, vd, OUT + '_old_%s.png' % vn, suns=suns)

bpy.ops.wm.read_factory_settings(use_empty=True)
addon_utils.enable('io_scene_fbx')
bpy.ops.import_scene.fbx(filepath=SRC)
dump('SRC')
img = bpy.data.images.load(TEX)
print('SRC texture', img.size[:], img.channels)
ms = [o for o in bpy.data.objects if o.type == 'MESH']
for o in ms:
    for m in o.data.materials:
        if not m:
            continue
        m.use_nodes = True
        nt = m.node_tree
        b = [n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED']
        if not b:
            continue
        t = nt.nodes.new('ShaderNodeTexImage'); t.image = img
        nt.links.new(t.outputs['Color'], b[0].inputs['Base Color'])
sc, cam, suns = W.setup_render(res=800)
for vn, vd in (('mY', (0.3, -1, 0.3)), ('pY', (-0.3, 1, 0.3)), ('pX', (1, 0.3, 0.3)), ('mX', (-1, -0.3, 0.3)),
               ('top', (0.001, -0.02, 1)), ('game', (0.6, -1, 1.5))):
    W.frame_and_shoot(ms, vd, OUT + '_src_%s.png' % vn, suns=suns)
bpy.ops.wm.save_as_mainfile(filepath=OUT + '_src_import.blend')
