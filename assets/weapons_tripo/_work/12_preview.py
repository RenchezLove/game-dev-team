"""New weapon next to the current one (same scale, same origin height).  -- pistol|knife"""
import bpy, sys
import numpy as np
import addon_utils
from mathutils import Vector
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W
OUT = 'E:/game-dev-team/assets/weapons_tripo/'
OLD = {'pistol': 'E:/ForGameLead(Materials)/demo-assets/SM_Pistol.fbx', 'knife': 'E:/ForGameLead(Materials)/phase3-assets/SM_Knife.fbx'}
NEW = {'pistol': 'SM_Pistol', 'knife': 'SM_Knife'}
TEX = {'pistol': 'T_PistolPM_D.png', 'knife': 'T_KnifeTripo_D.png'}
which = sys.argv[sys.argv.index('--') + 1]
bpy.ops.wm.read_factory_settings(use_empty=True); addon_utils.enable('io_scene_fbx')


def load(path, name):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path)
    ob = [o for o in bpy.data.objects if o not in before and o.type == 'MESH'][0]
    ob.name = name
    return ob


new = load(OUT + NEW[which] + '.fbx', 'new')
old = load(OLD[which], 'old')
m = bpy.data.materials.new('n'); m.use_nodes = True
t = m.node_tree.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(OUT + TEX[which]); t.interpolation = 'Linear'
m.node_tree.links.new(t.outputs['Color'], m.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.85
new.data.materials.clear(); new.data.materials.append(m)
if old.data.color_attributes:
    mo = bpy.data.materials.new('o'); mo.use_nodes = True
    vc = mo.node_tree.nodes.new('ShaderNodeVertexColor'); vc.layer_name = old.data.color_attributes[0].name
    mo.node_tree.links.new(vc.outputs['Color'], mo.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
    old.data.materials.clear(); old.data.materials.append(mo)
sc, cam, suns = W.setup_render(res=900); sc.render.film_transparent = False
# solo close-ups of the new one
if which == 'pistol':
    views = (('side_right', (1, 0, 0.02)), ('side_left', (-1, 0, 0.02)), ('top', (0.001, 0.02, 1)), ('q', (1, -1, 0.6)), ('front', (0.02, -1, 0.1)))
    off = Vector((0, 0, -0.21)); pair = (('pair_side', (1, 0, 0.02)), ('pair_q', (1, -0.8, 0.5)))
else:
    views = (('flat_up', (0.001, 0.02, 1)), ('flat_down', (0.001, 0.02, -1)), ('edge', (1, 0.02, 0.02)), ('q', (1, -0.6, 0.8)))
    off = Vector((0.09, 0, 0)); pair = (('pair_flat', (0.001, 0.02, 1)), ('pair_q', (1, -0.6, 0.8)))
old.hide_render = True
for n, v in views:
    W.frame_and_shoot([new], v, OUT + 'renders/%s_%s.png' % (which, n), suns=suns)
old.hide_render = False
old.location = off
bpy.context.view_layer.update()
for n, v in pair:
    W.frame_and_shoot([new, old], v, OUT + 'renders/%s_%s.png' % (which, n), suns=suns)
