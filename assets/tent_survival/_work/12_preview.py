"""Preview renders of the survival tent (Eevee, flat shade, back faces culled as in Unreal): game-camera angle, from an open end, QC views.
Run: blender.exe -b tent_work.blend --factory-startup --python 12_preview.py -- <texture png> [all] [mask]
"""
import bpy, math, sys
from mathutils import Vector
OUT = 'E:/game-dev-team/assets/tent_survival/renders/'
args = sys.argv[sys.argv.index('--') + 1:]
ob = bpy.data.objects['SM_Tent']
img = bpy.data.images.load(args[0])
mat = bpy.data.materials.new('prev'); mat.use_nodes = True
t = mat.node_tree.nodes.new('ShaderNodeTexImage'); t.image = img; t.interpolation = 'Closest' if 'mask' in args else 'Linear'
mat.node_tree.links.new(t.outputs['Color'], mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.9
mat.use_backface_culling = True                       # Unreal does not draw the back of a face - show the same here
ob.data.materials.clear(); ob.data.materials.append(mat)
ob.data.uv_layers['UVMap'].active_render = True
sc = bpy.context.scene
try:
    sc.render.engine = 'BLENDER_EEVEE_NEXT'
except Exception:
    sc.render.engine = 'BLENDER_EEVEE'
sc.view_settings.view_transform = 'Standard'
w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs[0].default_value = (0.42, 0.45, 0.48, 1); w.node_tree.nodes['Background'].inputs[1].default_value = 0.9
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0))
gr = bpy.context.active_object
gm = bpy.data.materials.new('ground'); gm.use_nodes = True
gm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.16, 0.15, 0.10, 1)
gr.data.materials.append(gm)
sun = bpy.data.objects.new('Sun', bpy.data.lights.new('Sun', 'SUN')); sc.collection.objects.link(sun); sun.data.energy = 3.0
cd = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', cd); sc.collection.objects.link(cam); sc.camera = cam; cd.clip_end = 200


def shoot(name, yaw_deg, pitch_deg, dist, fov_deg, target, res=(1280, 960), sun_dir=(-0.45, 0.6, -0.66)):
    yaw, pit = math.radians(yaw_deg), math.radians(pitch_deg)
    d = Vector((math.sin(yaw) * math.cos(pit), -math.cos(yaw) * math.cos(pit), math.sin(pit)))   # yaw 0 = camera on -Y
    cam.location = Vector(target) + d * dist
    cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
    cd.sensor_fit = 'HORIZONTAL'; cd.angle_x = math.radians(fov_deg)
    sun.rotation_euler = Vector(sun_dir).normalized().to_track_quat('-Z', 'Y').to_euler()
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = OUT + name
    bpy.ops.render.render(write_still=True)
    print('RENDER', OUT + name)


tgt = (0, 0, 0.45)
pre = 'qc_mask_on_' if 'mask' in args else ''
shoot(pre + 'tent_game_camera.png', 28, 60, 30, 6.5, tgt)                 # the game camera (pitch 60, 30 m), zoomed in on the tent
shoot(pre + 'tent_entrance_side.png', 22, 14, 14, 13, (0, 0, 0.5))
if 'all' in args:
    shoot('qc_game_camera_true_scale.png', 28, 60, 30, 40, tgt)           # the real field of view of the game: the tent as small as in play
    shoot('qc_game_edge_low.png', 70, 48, 30, 6.5, tgt)                   # the lowest look of the game camera (edge of the view), from the side: the underside through the open end
    shoot('qc_back.png', 200, 30, 14, 13, tgt, sun_dir=(0.45, -0.6, -0.66))
    shoot('qc_side.png', 90, 20, 14, 13, tgt, sun_dir=(-0.6, -0.3, -0.66))
    shoot('qc_top.png', 0, 89, 14, 11, tgt)
    shoot('qc_inside.png', 8, 6, 5, 30, (0, 0, 0.5))
