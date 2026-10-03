"""Old SM_WolfDenCave.fbx and the Tripo wolfden.glb: sizes, parts, holes, views from every side.
Run: blender.exe -b --factory-startup --python 00_inspect.py
"""
import bpy, bmesh, sys, math
import numpy as np
import addon_utils
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W
from mathutils import Vector, Matrix
OLD = 'E:/ForGameLead(Materials)/demo-assets/SM_WolfDenCave.fbx'
GLB = 'E:/ContrarySurvior/ContrarySurvivor/Saved/Tripo/wolfden/wolfden.glb'
OUT = 'E:/game-dev-team/assets/wolfden_tripo/_work/_look/'
VIEWS = (('mY', (0.2, -1, 0.35)), ('pY', (-0.2, 1, 0.35)), ('pX', (1, 0.2, 0.35)), ('mX', (-1, -0.2, 0.35)), ('top', (0.001, -0.02, 1)))


def dump(tag, ob):
    me = ob.data; mw = ob.matrix_world
    cs = np.array([mw @ v.co for v in me.vertices])
    print(tag, 'tris', sum(len(p.vertices) - 2 for p in me.polygons), 'verts', len(me.vertices), 'min', cs.min(0).round(3), 'max', cs.max(0).round(3), 'size', (cs.max(0) - cs.min(0)).round(3),
          'scale', tuple(round(a, 3) for a in mw.to_scale()), 'uv', [u.name for u in me.uv_layers], 'cols', [c.name for c in me.color_attributes], 'mats', [m.name for m in me.materials if m])
    bm = bmesh.new(); bm.from_mesh(me); bm.transform(mw)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
    print(tag, 'welded verts', len(bm.verts), 'open edges', sum(1 for e in bm.edges if len(e.link_faces) == 1), 'edges with 3+ faces', sum(1 for e in bm.edges if len(e.link_faces) > 2))
    seen = set(); parts = []
    for v in bm.verts:
        if v in seen:
            continue
        st = [v]; seen.add(v); c = []
        while st:
            a = st.pop(); c.append(a)
            for e in a.link_edges:
                b = e.other_vert(a)
                if b not in seen:
                    seen.add(b); st.append(b)
        co = np.array([q.co for q in c]); fs = {f for q in c for f in q.link_faces}
        parts.append((len(fs), co.min(0).round(2), co.max(0).round(2)))
    parts.sort(key=lambda p: -p[0])
    print(tag, 'loose parts', len(parts))
    for p in parts[:14]:
        print(tag, '   part tris %4d min %s max %s' % p)
    # darkest region = the cave mouth: mean position of faces whose normals point into ... (reported by views instead)
    low = cs[cs[:, 2] < cs[:, 2].min() + 0.06]
    print(tag, 'verts within 6 cm of the bottom: %d, x %.2f..%.2f y %.2f..%.2f' % (len(low), low[:, 0].min(), low[:, 0].max(), low[:, 1].min(), low[:, 1].max()))
    bm.free()


bpy.ops.wm.read_factory_settings(use_empty=True)
addon_utils.enable('io_scene_fbx')
bpy.ops.import_scene.fbx(filepath=OLD)
old = [o for o in bpy.data.objects if o.type == 'MESH'][0]
bpy.context.view_layer.update()
dump('OLD', old)
ca = old.data.color_attributes[0]
# the old mouth: the darkest faces
dark = []
for p in old.data.polygons:
    c = ca.data[p.loop_indices[0]].color
    if max(c[0], c[1], c[2]) < 0.03:
        dark.append(old.matrix_world @ p.center)
if dark:
    d = np.array(dark)
    print('OLD darkest faces (mouth): %d, centre %s, min %s max %s' % (len(d), d.mean(0).round(2), d.min(0).round(2), d.max(0).round(2)))
mat = bpy.data.materials.new('v'); mat.use_nodes = True
vc = mat.node_tree.nodes.new('ShaderNodeVertexColor'); vc.layer_name = ca.name
mat.node_tree.links.new(vc.outputs['Color'], mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
old.data.materials.clear(); old.data.materials.append(mat)
sc, cam, suns = W.setup_render(res=700); sc.render.film_transparent = False
for vn, vd in VIEWS:
    W.frame_and_shoot([old], vd, OUT + 'old_%s.png' % vn, suns=suns)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=GLB)
bpy.context.view_layer.update()
new = [o for o in bpy.data.objects if o.type == 'MESH'][0]
dump('GLB', new)
for im in bpy.data.images:
    print('IMG', im.name, tuple(im.size))
for p in new.data.polygons:
    p.use_smooth = False
sc, cam, suns = W.setup_render(res=800); sc.render.film_transparent = False
for vn, vd in VIEWS + (('bottom', (0.02, 0.02, -1)), ('game', (0.3, -0.6, 1.2))):
    W.frame_and_shoot([new], vd, OUT + 'glb_%s.png' % vn, suns=suns)
