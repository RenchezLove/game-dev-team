import bpy, sys, os
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W
tag = sys.argv[sys.argv.index('--') + 1]
OUT = 'E:/game-dev-team/assets/abandoned_car_tripo/_work/_look/'
for o in bpy.data.objects:
    o.hide_render = o.name != 'Atlas'
ob = bpy.data.objects['Atlas']; me = ob.data
cols = [(0.55,0.65,0.8),(0.1,0.9,0.9),(0.9,0.2,0.2),(0.2,0.8,0.2),(0.9,0.6,0.1),(0.6,0.2,0.9),(0.95,0.95,0.2),(0.9,0.3,0.7),(0.15,0.15,0.15)]
me.materials.clear()
for i, c in enumerate(cols):
    m = bpy.data.materials.new('p%d' % i); m.use_nodes = True
    m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = c + (1,)
    me.materials.append(m)
dark = bpy.data.materials.new('dark'); dark.use_nodes = True
dark.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.02,0.02,0.02,1)
me.materials.append(dark)
lamp = bpy.data.materials.new('lamp'); lamp.use_nodes = True
lamp.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (1,0.3,0,1)
me.materials.append(lamp)
pa = me.attributes['part'].data; ka = me.attributes['kind'].data
for p in me.polygons:
    k = ka[p.index].value
    p.material_index = 9 if k == 1 else 10 if k == 2 else pa[p.index].value
pass
sc, cam, suns = W.setup_render(res=900)
for n, d in (('side', (1, 0, 0.02)), ('sideL', (-1, 0, 0.02)), ('top', (0.001, 0, 1)), ('back', (0, -1, 0.1)), ('q34', (1, 1.2, 0.9)), ('q34b', (-1, -1.2, 0.9))):
    W.frame_and_shoot([ob], d, OUT + '%s_%s.png' % (tag, n), margin=1.03, suns=suns)
