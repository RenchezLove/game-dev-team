"""Look at the downloaded bus stop (Sketchfab 'Old Russian bus stop' by halkiridze): objects, triangles, bounds, materials, views.
Run: blender.exe -b --factory-startup --python 00_inspect.py
"""
import bpy, math, addon_utils
import numpy as np
from mathutils import Vector
D = 'C:/Users/pgr40/Desktop/GamdevAITeam/Автобусная остановка/old-russian-bus-stop/'
OUT = 'E:/game-dev-team/assets/bus_stop/_work/_look/'
bpy.ops.wm.read_factory_settings(use_empty=True)
addon_utils.enable('io_scene_fbx')
bpy.ops.import_scene.fbx(filepath=D + 'source/FBX.fbx')
bpy.context.view_layer.update()
ms = [o for o in bpy.data.objects if o.type == 'MESH']
print('SRC objects: %s' % [(o.name, o.type, o.parent.name if o.parent else None) for o in bpy.data.objects])
allc = []
for o in ms:
    me = o.data; mw = o.matrix_world
    cs = np.array([mw @ v.co for v in me.vertices]); allc.append(cs)
    tris = sum(len(p.vertices) - 2 for p in me.polygons)
    cnt = {}
    for p in me.polygons:
        cnt[p.material_index] = cnt.get(p.material_index, 0) + len(p.vertices) - 2
    print('SRC mesh %-28s tris=%5d verts=%5d min=%s max=%s size=%s scale=%s mats=%s tris_by_slot=%s uv=%s' % (o.name, tris, len(me.vertices), cs.min(0).round(3), cs.max(0).round(3), (cs.max(0) - cs.min(0)).round(3),
          tuple(round(a, 4) for a in mw.to_scale()), [m.name if m else None for m in me.materials], cnt, [u.name for u in me.uv_layers]))
    # loose parts
    import bmesh
    bm = bmesh.new(); bm.from_mesh(me); bm.transform(mw); bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
    seen = set(); parts = []
    for v in bm.verts:
        if v.index in seen:
            continue
        st = [v]; seen.add(v.index); comp = []
        while st:
            a = st.pop(); comp.append(a)
            for e in a.link_edges:
                b = e.other_vert(a)
                if b.index not in seen:
                    seen.add(b.index); st.append(b)
        fs = set(f.index for a in comp for f in a.link_faces)
        c = np.array([a.co[:] for a in comp])
        mi = set(bm.faces[i].material_index for i in fs) if fs else set()
        bm.faces.ensure_lookup_table()
        parts.append((len(fs), c.min(0), c.max(0), mi))
    for n, lo, hi, mi in sorted(parts, key=lambda q: -q[0]):
        print('SRC    part faces=%4d min=(%6.2f %6.2f %6.2f) max=(%6.2f %6.2f %6.2f) size=(%5.2f %5.2f %5.2f) slots=%s' % (n, *lo, *hi, *(hi - lo), sorted(mi)))
    bm.free()
c = np.concatenate(allc)
print('SRC TOTAL tris=%d min=%s max=%s size=%s' % (sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in ms), c.min(0).round(3), c.max(0).round(3), (c.max(0) - c.min(0)).round(3)))
for m in bpy.data.materials:
    print('SRC material %s: %s' % (m.name, [(n.type, n.image.filepath if n.type == 'TEX_IMAGE' and n.image else '') for n in m.node_tree.nodes] if m.node_tree else None))
# hook the colour textures by hand (the FBX may not carry the paths)
TEX = {'BUSS': 'DefaultMaterial_Base_Color.png', 'RASP': 'DefaultMaterial_Base_Color.png', 'Материал.003': 'DefaultMaterial_Base_Color.png', 'ZNAK': 'Материал.001_Base_Color.png'}
for m in bpy.data.materials:
    key = [k for k in TEX if m.name.startswith(k)]
    if not key:
        print('SRC material %s: no texture guess' % m.name); continue
    m.use_nodes = True
    for n in [n for n in m.node_tree.nodes if n.type in ('TEX_IMAGE', 'NORMAL_MAP')]:
        m.node_tree.nodes.remove(n)
    t = m.node_tree.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(D + 'textures/' + TEX[key[0]])
    b = [n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'][0]
    b.inputs['Metallic'].default_value = 0.0; b.inputs['Roughness'].default_value = 0.9
    m.node_tree.links.new(t.outputs['Color'], b.inputs['Base Color'])
    m.use_backface_culling = False
    print('SRC material %s <- %s %dx%d' % (m.name, TEX[key[0]], t.image.size[0], t.image.size[1]))
sc = bpy.context.scene
sc.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
sc.view_settings.view_transform = 'Standard'
w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs[0].default_value = (0.6, 0.6, 0.6, 1); w.node_tree.nodes['Background'].inputs[1].default_value = 1.2
sun = bpy.data.objects.new('Sun', bpy.data.lights.new('Sun', 'SUN')); sc.collection.objects.link(sun); sun.data.energy = 2.5
sun.rotation_euler = Vector((-0.45, 0.6, -0.66)).normalized().to_track_quat('-Z', 'Y').to_euler()
cd = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', cd); sc.collection.objects.link(cam); sc.camera = cam
mid = Vector((c.min(0) + c.max(0)) / 2); size = float((c.max(0) - c.min(0)).max())
for name, yaw, pit in (('front', 0, 10), ('back', 180, 10), ('left', -90, 10), ('right', 90, 10), ('top', 0, 89), ('q1', 35, 35), ('q2', 215, 35), ('q3', -35, 20), ('under', 20, -25)):
    y, p = math.radians(yaw), math.radians(pit)
    d = Vector((math.sin(y) * math.cos(p), -math.cos(y) * math.cos(p), math.sin(p)))
    cam.location = mid + d * size * 4.0; cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
    cd.angle = math.radians(24); cd.clip_end = size * 20; cd.clip_start = size * 0.05
    sc.render.resolution_x, sc.render.resolution_y = 1100, 800
    sc.render.filepath = OUT + 'src_%s.png' % name; bpy.ops.render.render(write_still=True)
