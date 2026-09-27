"""Own QC renders of the car kit (car_kit.blend): assembled with 4 wheels in 3 paint
colours (material as in UE: lerp(tex.rgb, tex.rgb * Paint, tex.a)), a stripped car (left
doors + hood + trunk removed, glass hidden) to check the dark plugs, rear close-up.
Run: blender.exe -b _work/car_kit.blend --factory-startup --python 13_preview.py
"""
import bpy, sys, os, math
import numpy as np
from mathutils import Vector, Matrix
sys.path.insert(0, 'E:/game-dev-team/assets/abandoned_car_tripo/_work')
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
sys.path.insert(0, 'E:/game-dev-team/assets/hero_tripo/_work')
import wcommon as W, hpose as P
from carconst import *

OUT = WORK + '_look/'
os.makedirs(OUT, exist_ok=True)
O = {n: bpy.data.objects['SM_AbandonedCar_' + n] for n in PARTS}
PIV = {}
for line in open(WORK + '_bake.log', encoding='utf-8'):
    if line.startswith('PART '):
        name = line.split()[1].replace('SM_AbandonedCar_', '')
        PIV[name] = Vector(eval(line.split('pivot(blender)=')[1].split(' local')[0]))
for n, ob in O.items():
    if n != 'Wheel':
        ob.location = PIV[n]
# wheels: left ones as built (hubcap to -X), right ones turned 180 about Z
wheels = []
for (x, y) in ((-0.66, 1.44), (0.66, 1.44), (-0.66, -0.97), (0.66, -0.97)):
    w = O['Wheel'] if not wheels else O['Wheel'].copy()
    if wheels:
        bpy.context.scene.collection.objects.link(w)
    w.location = (x, y, WHEEL_R)
    w.rotation_euler = (0, 0, math.pi if x > 0 else 0)
    wheels.append(w)

mat = bpy.data.materials['M_CarTripo']
nt = mat.node_tree
tex = [n for n in nt.nodes if n.type == 'TEX_IMAGE'][0]
bs = nt.nodes['Principled BSDF']
paint = nt.nodes.new('ShaderNodeRGB')
mul = nt.nodes.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'
mul.inputs['Factor'].default_value = 1
nt.links.new(tex.outputs['Color'], mul.inputs['A']); nt.links.new(paint.outputs['Color'], mul.inputs['B'])
lerp = nt.nodes.new('ShaderNodeMix'); lerp.data_type = 'RGBA'
nt.links.new(tex.outputs['Alpha'], lerp.inputs['Factor'])
nt.links.new(tex.outputs['Color'], lerp.inputs['A']); nt.links.new(mul.outputs['Result'], lerp.inputs['B'])
nt.links.new(lerp.outputs['Result'], bs.inputs['Base Color'])
gm = bpy.data.materials['M_CarTripoGlass']
gb = gm.node_tree.nodes['Principled BSDF']
gb.inputs['Alpha'].default_value = 0.55
gm.blend_method = 'BLEND' if hasattr(gm, 'blend_method') else None


def s2l(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lin(hx):
    return tuple(s2l(int(hx[i:i + 2], 16) / 255) for i in (1, 3, 5)) + (1.0,)


sc, cam, suns = W.setup_render(res=760)
sc.render.film_transparent = False
allobs = list(O.values()) + wheels[1:]
VIEWS = {'q34': (1, 1.2, 0.9), 'q34b': (-1, -1.2, 0.9), 'game': (0.0, 0.5, 0.87)}
for pn, hx in (('blue', '#7C95B3'), ('red', '#8E2A22'), ('green', '#4A5A36')):
    paint.outputs['Color'].default_value = lin(hx)
    for vn, vd in VIEWS.items():
        if pn != 'blue' and vn != 'q34':
            continue
        W.frame_and_shoot(allobs, vd, OUT + 'kit_%s_%s.png' % (pn, vn), margin=1.05, suns=suns)
paint.outputs['Color'].default_value = lin('#7C95B3')
P.shoot((0, -1, 0.05), (0, -2, 0.62), 1.9, OUT + 'kit_rear.png', suns)
for n in ('Door_FL', 'Door_RL', 'Hood', 'Trunk', 'Glass'):
    O[n].hide_render = True
W.frame_and_shoot(allobs, (-1, 0.6, 0.8), OUT + 'kit_stripped_left.png', margin=1.05, suns=suns)
W.frame_and_shoot(allobs, (0.2, 0.7, 1.0), OUT + 'kit_stripped_top.png', margin=1.05, suns=suns)
