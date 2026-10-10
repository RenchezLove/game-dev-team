"""Scientist with the hair recoloured through the mask (brown default, blond) and with the mask shown on the model.
Run: blender.exe -b scientist_work.blend --factory-startup --python 15_mask_preview.py"""
import bpy, sys, os
sys.path.insert(0, 'E:/game-dev-team/assets/scientist_base/_work')
import sb
OUT = 'E:/game-dev-team/assets/scientist_tripo/'
obs = [bpy.data.objects['SK_Scientist_' + s] for s in ('Head', 'Torso', 'Legs')]
for o in bpy.data.objects:
    o.hide_render = o not in obs
mat = bpy.data.materials.new('pv'); mat.use_nodes = True
tn = mat.node_tree.nodes.new('ShaderNodeTexImage')
mat.node_tree.links.new(tn.outputs['Color'], mat.node_tree.nodes['Principled BSDF'].inputs['Base Color']); mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.9
for o in obs:
    o.data.materials.clear(); o.data.materials.append(mat)
sc, cam, cd, sun = sb.preview_scene(ground=None, bg=(0.3, 0.3, 0.33))
P = []
for nm in ('brown', 'blond', 'mask'):
    tn.image = bpy.data.images.load(OUT + '_work/_prev_%s.png' % (('hair_' + nm) if nm != 'mask' else 'mask'))
    for yaw, pit, tg, fov, d in ((15, 10, (0, 0, 1.63), 9, 3.2), (165, 15, (0, 0, 1.63), 9, 3.2), (15, 8, (0, 0, 0.9), 34, 3.4)):
        p = OUT + '_work/_look/mask_%s_%d.png' % (nm, yaw + int(fov)); P.append(p)
        sb.shoot(sc, cam, cd, sun, p, yaw, pit, d, fov, tg, res=(600, 700), sun_dir=(0.2, 0.6, -0.5) if yaw < 90 else (-0.3, -0.6, -0.5))
sb.sheet(P, OUT + 'renders/scientist_hair_and_mask.png', 3)
