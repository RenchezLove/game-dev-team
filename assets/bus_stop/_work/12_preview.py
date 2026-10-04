"""Preview renders of the bus stop, the three objects standing in their places (Eevee, flat shade, back faces culled as in Unreal).
Run: blender.exe -b busstop_work.blend --factory-startup --python 12_preview.py -- <texture png> [all] [mask] [raw]
"""
import bpy, math, sys
from mathutils import Vector
OUT = 'E:/game-dev-team/assets/bus_stop/renders/'
args = sys.argv[sys.argv.index('--') + 1:]
img = bpy.data.images.load(args[0])
mat = bpy.data.materials.new('prev'); mat.use_nodes = True
t = mat.node_tree.nodes.new('ShaderNodeTexImage'); t.image = img; t.interpolation = 'Closest' if 'mask' in args else 'Linear'
mat.node_tree.links.new(t.outputs['Color'], mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.9
mat.use_backface_culling = True                       # Unreal does not draw the back of a face - show the same here
for name in ('SM_BusStop', 'SM_BusStopSign', 'SM_BusStopUrn'):
    ob = bpy.data.objects[name]
    ob.data.materials.clear(); ob.data.materials.append(mat)
    ob.data.uv_layers['UVMap'].active_render = True
show_ucx = 'ucx' in args
for o in bpy.data.objects:
    if o.name.startswith('UCX_'):
        o.hide_render = not show_ucx
        if show_ucx:
            cm = bpy.data.materials.new('ucx'); cm.use_nodes = True
            cm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (1.0, 0.25, 0.1, 1)
            cm.node_tree.nodes['Principled BSDF'].inputs['Alpha'].default_value = 0.45
            cm.surface_render_method = 'BLENDED'
            o.data.materials.clear(); o.data.materials.append(cm)
sc = bpy.context.scene
try:
    sc.render.engine = 'BLENDER_EEVEE_NEXT'
except Exception:
    sc.render.engine = 'BLENDER_EEVEE'
sc.view_settings.view_transform = 'Standard'
w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs[0].default_value = (0.42, 0.45, 0.48, 1); w.node_tree.nodes['Background'].inputs[1].default_value = 0.9
bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, 0))
gr = bpy.context.active_object
gm = bpy.data.materials.new('ground'); gm.use_nodes = True
gm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.14, 0.14, 0.10, 1)
gr.data.materials.append(gm)
# the hero for scale: 1.8 m tall, 0.4 m radius - standing as deep under the roof as the blocks let him
bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.40, depth=1.8, location=(0.6, 0.25 - 0.56 - 0.40, 0.9))
hero = bpy.context.active_object
hm = bpy.data.materials.new('hero'); hm.use_nodes = True
hm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.8, 0.5, 0.1, 1)
hero.data.materials.append(hm); hero.hide_render = 'hero' not in args
sun = bpy.data.objects.new('Sun', bpy.data.lights.new('Sun', 'SUN')); sc.collection.objects.link(sun); sun.data.energy = 3.0
cd = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', cd); sc.collection.objects.link(cam); sc.camera = cam; cd.clip_end = 200


def shoot(name, yaw_deg, pitch_deg, dist, fov_deg, target, res=(1280, 960), sun_dir=(-0.45, 0.6, -0.66)):
    yaw, pit = math.radians(yaw_deg), math.radians(pitch_deg)
    d = Vector((math.sin(yaw) * math.cos(pit), -math.cos(yaw) * math.cos(pit), math.sin(pit)))   # yaw 0 = camera on -Y (the open side)
    cam.location = Vector(target) + d * dist
    cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
    cd.sensor_fit = 'HORIZONTAL'; cd.angle_x = math.radians(fov_deg)
    sun.rotation_euler = Vector(sun_dir).normalized().to_track_quat('-Z', 'Y').to_euler()
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = OUT + name
    bpy.ops.render.render(write_still=True)
    print('RENDER', OUT + name)


tgt = (-0.3, -0.4, 1.2)
pre = 'qc_mask_on_' if 'mask' in args else ('qc_untinted_' if 'raw' in args else ('qc_blocks_' if show_ucx else ('qc_hero_' if 'hero' in args else '')))
shoot(pre + 'busstop_game_camera.png', 20, 60, 30, 16, tgt)                # the game camera (pitch 60, 30 m), zoomed in
shoot(pre + 'busstop_open_side.png', 18, 12, 26, 17, (-0.3, 0, 1.3))
if 'all' in args:
    shoot('qc_game_camera_true_scale.png', 20, 60, 30, 40, tgt)            # the real field of view of the game
    shoot('qc_game_edge_low.png', 0, 48, 30, 16, tgt)                      # the lowest look of the game camera (edge of the view)
    shoot('qc_back.png', 200, 25, 26, 17, tgt, sun_dir=(0.45, -0.6, -0.66))
    shoot('qc_side.png', 90, 15, 26, 14, tgt, sun_dir=(-0.6, -0.3, -0.66))
    shoot('qc_top.png', 0, 89, 26, 15, tgt)
    shoot('qc_sign_close.png', 10, 8, 7, 30, (-3.0, -1.53, 1.6))
    shoot('qc_urn_close.png', 15, 45, 4, 30, (1.62, -1.0, 0.3))
    shoot('qc_inside_close.png', 25, 10, 7, 40, (0.6, 0.2, 1.3))
