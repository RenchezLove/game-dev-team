"""New and old wolf side by side as the game camera sees them (pitch 60, 30 m, FOV 40), run frame 4.
Run: blender.exe -b --factory-startup --python 14_game_scale.py"""
import bpy, math
from mathutils import Vector, Matrix
bpy.ops.wm.open_mainfile(filepath='E:/game-dev-team/assets/wolf_tripo/_work/wolf_work.blend')
sc = bpy.context.scene
rig = bpy.data.objects['WolfRig']; new = bpy.data.objects['SK_Wolf']; old = bpy.data.objects['SK_Wolf_old']
act = bpy.data.actions['Anim_Wolf_Run']; rig.animation_data.action = act
if hasattr(rig.animation_data, 'action_slot') and act.slots: rig.animation_data.action_slot = act.slots[0]
sc.frame_set(4)
rig2 = rig.copy(); sc.collection.objects.link(rig2); rig2.location = (1.6, 0, 0)        # same pose, shifted: carries the old wolf
old.parent = rig2
for m in old.modifiers:
    if m.type == 'ARMATURE': m.object = rig2
try: sc.render.engine = 'BLENDER_EEVEE_NEXT'
except Exception: sc.render.engine = 'BLENDER_EEVEE'
sc.view_settings.view_transform = 'Standard'
w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs[0].default_value = (0.4, 0.42, 0.45, 1)
bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, -0.001)); g = bpy.context.active_object
gm = bpy.data.materials.new('g'); gm.use_nodes = True; gm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.12, 0.15, 0.09, 1); g.data.materials.append(gm)
sun = bpy.data.objects.new('S', bpy.data.lights.new('S', 'SUN')); sc.collection.objects.link(sun); sun.data.energy = 3
sun.rotation_euler = Vector((-0.4, 0.5, -0.7)).normalized().to_track_quat('-Z', 'Y').to_euler()
cd = bpy.data.cameras.new('C'); cam = bpy.data.objects.new('C', cd); sc.collection.objects.link(cam); sc.camera = cam
tgt = Vector((0.8, 0, 0.4)); d = Vector((0, -math.cos(math.radians(60)), math.sin(math.radians(60))))
cam.location = tgt + d * 30; cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
cd.sensor_fit = 'HORIZONTAL'; cd.angle_x = math.radians(40); cd.clip_end = 200
sc.render.resolution_x, sc.render.resolution_y = 1280, 720
sc.render.filepath = 'E:/game-dev-team/assets/wolf_tripo/renders/qc_game_camera_scale.png'
bpy.ops.render.render(write_still=True); print('RENDER', sc.render.filepath)
