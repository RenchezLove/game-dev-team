"""Preview of the UAZ kit: assembled in the default colour, doors open with one wheel off, and repainted red (BodyColor works through the mask).
Run: blender -b uazkit_work.blend --factory-startup --python uazkit_12_preview.py"""
import bpy, math, sys, os
import numpy as np
sys.path.insert(0, 'E:/game-dev-team/assets/scientist_base/_work')
import sb, uazkit_common as U
parts = U.split()
imgs = {k: bpy.data.images.load(sb.WORK + '_uazkit_%s_colour.png' % k) for k in ('default', 'red')}
mat = bpy.data.materials.new('prev'); mat.use_nodes = True
tn = mat.node_tree.nodes.new('ShaderNodeTexImage'); tn.image = imgs['default']
mat.node_tree.links.new(tn.outputs['Color'], mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.9
mat.use_backface_culling = False                                  # the car material is two-sided in the game
gm = bpy.data.materials.new('glass'); gm.use_nodes = True
gm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.10, 0.13, 0.15, 1)
for n, o in parts.items():
    o.data.materials.clear(); o.data.materials.append(gm if n == 'Glass' else mat)
wheels = [parts['Wheel']]
for i in (1, 2, 3):
    w = parts['Wheel'].copy(); bpy.context.scene.collection.objects.link(w); wheels.append(w)
for w, c in zip(wheels, U.META['wheels']):
    w.location = c; w.rotation_euler = (0, 0, 0 if c[0] < 0 else math.pi)
sc, cam, cd, sun = sb.preview_scene()
tmp = sb.WORK + '_prev_tmp/'; os.makedirs(tmp, exist_ok=True); P = []
def shots(tag, views):
    for yaw, pit in views:
        p = tmp + 'uazkit_%s_%d_%d.png' % (tag, yaw, pit); P.append(p)
        sb.shoot(sc, cam, cd, sun, p, yaw, pit, 30, 14, (0, 0, 1.0), res=(960, 720), sun_dir=(-0.45, 0.6, -0.66) if yaw < 120 else (0.45, -0.6, -0.66))
shots('closed', ((25, 60), (200, 30)))
OPEN = dict(Door_FL=-60, Door_FR=60, Door_Side=65, RearDoor_L=-75, RearDoor_R=75)        # degrees about +Z in Blender
for n, a in OPEN.items():
    parts[n].rotation_euler = (0, 0, math.radians(a))
wheels[1].hide_render = True
shots('open', ((25, 60), (200, 30), (300, 25)))
parts['Glass'].hide_render = True
tn.image = imgs['red']
shots('red', ((120, 45),))
sb.sheet(P, sb.ROOT + 'SM_UAZ452_kit/SM_UAZ452_kit_preview.png', 3)
