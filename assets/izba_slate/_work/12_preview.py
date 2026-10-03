"""Preview renders of SM_IzbaSlate (Eevee, textured, flat shade).
Run: blender.exe -b izba_work.blend --factory-startup --python 12_preview.py
"""
import bpy, math, sys
from mathutils import Vector
OUT = 'E:/game-dev-team/assets/izba_slate/renders/'
ob = bpy.data.objects['SM_IzbaSlate']
sc = bpy.context.scene
try:
    sc.render.engine = 'BLENDER_EEVEE_NEXT'
except Exception:
    sc.render.engine = 'BLENDER_EEVEE'
sc.view_settings.view_transform = 'Standard'
sc.render.film_transparent = False
w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes['Background']
bg.inputs[0].default_value = (0.42, 0.45, 0.48, 1); bg.inputs[1].default_value = 0.9

# ground
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, -0.002))
gr = bpy.context.active_object
gm = bpy.data.materials.new('ground'); gm.use_nodes = True
gm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.11, 0.13, 0.085, 1)
gm.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 1.0
gr.data.materials.append(gm)

sun = bpy.data.objects.new('Sun', bpy.data.lights.new('Sun', 'SUN'))
sc.collection.objects.link(sun)
sun.data.energy = 3.0; sun.data.angle = math.radians(3)
cd = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', cd); sc.collection.objects.link(cam); sc.camera = cam
cd.clip_end = 200


def shoot(name, yaw_deg, pitch_deg, dist, fov_deg, target, res=(1280, 960), sun_dir=(-0.45, -0.6, -0.66)):
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


which = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['all']
tgt = (0, -0.1, 1.9)
if 'all' in which or 'main' in which:
    shoot('izba_slate_game_camera.png', 28, 60, 30, 17, tgt)                 # game camera pitch 60, zoomed in
    shoot('izba_slate_facade.png', 12, 9, 22, 19, (0.1, 0, 2.1))
if 'all' in which or 'qc' in which:
    shoot('_qc_back_game.png', 205, 60, 30, 17, tgt, sun_dir=(0.45, 0.6, -0.66))
    shoot('_qc_gable3.png', -78, 12, 22, 19, (0, 0, 2.1), sun_dir=(0.6, -0.4, -0.66))
    shoot('_qc_gable_back.png', 100, 12, 22, 19, (0, 0, 2.1), sun_dir=(-0.6, 0.3, -0.66))
    shoot('_qc_game_true.png', 28, 60, 30, 40, tgt, res=(1280, 720))         # real framing: FOV 40, 30 m
    shoot('_qc_door_close.png', 20, 14, 9, 40, (0.2, -1.8, 1.4))
    shoot('_qc_roof_close.png', 150, 50, 11, 40, (-0.5, 0.8, 3.6), sun_dir=(0.45, 0.6, -0.66))
