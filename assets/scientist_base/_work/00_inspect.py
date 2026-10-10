"""Look at one source: objects, triangles, bounds, materials, images + four look renders.
Run: blender.exe -b --factory-startup --disable-autoexec --python 00_inspect.py -- <id>
"""
import bpy, sys, math, os
import numpy as np
import addon_utils
from mathutils import Vector

S = 'E:/game-dev-team/assets/scientist_base/_src/'
LOOK = 'E:/game-dev-team/assets/scientist_base/_work/_look/'
SRC = {
    'uaz': ('fbx', S + 'uaz-452-buhanka/source/unrar/UAZ_Buhanka.fbx'),
    'tent': ('obj', S + 'tent-model-free/source/unrar/Tent/Tent.obj'),
    'toz': ('blend', S + 'low-poly-toz-34/source/toz34.blend'),
    'osc': ('blend', S + 'oscillograph/source/oscilloscope.blend'),
    'radio': ('fbx', S + 'gauja-retro-radio-receiver-low-poly/source/unz/audio receiver1.fbx'),
    'crate': ('fbx', 'E:/game-dev-team/assets/lowpoly_market/SM_Crate_01.fbx'),
}
which = sys.argv[sys.argv.index('--') + 1]
kind, path = SRC[which]
if kind == 'blend':
    bpy.ops.wm.open_mainfile(filepath=path, use_scripts=False)
else:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if kind == 'fbx':
        addon_utils.enable('io_scene_fbx'); bpy.ops.import_scene.fbx(filepath=path)
    else:
        bpy.ops.wm.obj_import(filepath=path)
bpy.context.view_layer.update()
print('SCENE unit scale %s, objects %d' % (bpy.context.scene.unit_settings.scale_length, len(bpy.data.objects)))
allc = []
for o in sorted(bpy.data.objects, key=lambda o: o.name):
    if o.type != 'MESH':
        print('OBJ %-28s type %s parent %s' % (o.name, o.type, o.parent.name if o.parent else None)); continue
    me = o.data; mw = o.matrix_world
    c = np.array([mw @ v.co for v in me.vertices]) if len(me.vertices) else np.zeros((1, 3))
    allc.append(c)
    tris = sum(len(p.vertices) - 2 for p in me.polygons)
    mi = np.zeros(len(me.polygons), np.int32); me.polygons.foreach_get('material_index', mi)
    print('OBJ %-28s tris %5d verts %5d min %s max %s size %s parent %s mods %s hidden %s' % (o.name, tris, len(me.vertices), c.min(0).round(3), c.max(0).round(3), (c.max(0) - c.min(0)).round(3),
          o.parent.name if o.parent else None, [m.type for m in o.modifiers], o.hide_render))
    print('    loc %s rot %s scale %s uv %s cols %s mats %s faces per mat %s' % (tuple(round(a, 3) for a in o.location), tuple(round(a, 3) for a in o.rotation_euler), tuple(round(a, 3) for a in o.scale),
          [u.name for u in me.uv_layers], [a.name for a in me.color_attributes], [m.name if m else None for m in me.materials], np.bincount(mi).tolist() if len(mi) else []))
A = np.concatenate(allc)
print('ALL min %s max %s size %s' % (A.min(0).round(3), A.max(0).round(3), (A.max(0) - A.min(0)).round(3)))
for m in bpy.data.materials:
    if m.node_tree:
        for n in m.node_tree.nodes:
            if n.type == 'TEX_IMAGE':
                print('MAT %s image node %s -> %s | linked to %s' % (m.name, n.name, n.image.filepath if n.image else None, [(l.to_node.name, l.to_socket.name) for o_ in n.outputs for l in o_.links]))
        b = m.node_tree.nodes.get('Principled BSDF')
        if b:
            print('MAT %s base colour %s alpha %s blend %s' % (m.name, tuple(round(a, 3) for a in b.inputs['Base Color'].default_value), b.inputs['Alpha'].default_value, getattr(m, 'surface_render_method', None)))
for i in bpy.data.images:
    print('IMG %s %s %s packed %s' % (i.name, tuple(i.size), i.filepath, bool(i.packed_file)))

# ---- look renders
sc = bpy.context.scene
try:
    sc.render.engine = 'BLENDER_EEVEE_NEXT'
except Exception:
    sc.render.engine = 'BLENDER_EEVEE'
sc.view_settings.view_transform = 'Standard'
w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs[0].default_value = (0.5, 0.52, 0.55, 1); w.node_tree.nodes['Background'].inputs[1].default_value = 1.2
for o in list(bpy.data.objects):
    if o.type in ('LIGHT', 'CAMERA'):
        bpy.data.objects.remove(o, do_unlink=True)
sun = bpy.data.objects.new('Sun', bpy.data.lights.new('Sun', 'SUN')); sc.collection.objects.link(sun); sun.data.energy = 3.0
cd = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', cd); sc.collection.objects.link(cam); sc.camera = cam
cen = (A.min(0) + A.max(0)) / 2; R = float(np.linalg.norm(A.max(0) - A.min(0))) / 2
cd.clip_start = R * 0.01; cd.clip_end = R * 100
os.makedirs(LOOK, exist_ok=True)
for name, d in (('px', (1, 0, 0.15)), ('nx', (-1, 0, 0.15)), ('py', (0, 1, 0.15)), ('ny', (0, -1, 0.15)), ('top', (0.01, -0.01, 1)), ('q', (0.7, -0.8, 0.7)), ('q2', (-0.7, 0.8, 0.7))):
    d = Vector(d).normalized()
    cam.location = Vector(cen) + d * R * 3.2
    cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
    cd.angle_x = math.radians(40)
    sun.rotation_euler = (-(d + Vector((0.3, 0.2, 0.8)))).normalized().to_track_quat('-Z', 'Y').to_euler()
    sc.render.resolution_x, sc.render.resolution_y = 900, 700
    sc.render.filepath = LOOK + '%s_%s.png' % (which, name)
    bpy.ops.render.render(write_still=True)
