"""Radio source: parts with texture colours, textured look renders. Run: blender.exe -b --factory-startup --python radio_01_parts.py"""
import bpy, sys, bmesh
import numpy as np
sys.path.insert(0, 'E:/game-dev-team/assets/scientist_base/_work')
import sb
sb.empty()
bpy.ops.import_scene.fbx(filepath=sb.SRCD + 'gauja-retro-radio-receiver-low-poly/source/unz/audio receiver1.fbx')
img = bpy.data.images.load(sb.SRCD + 'gauja-retro-radio-receiver-low-poly/textures/_BaseColor.png'); print('TEXTURE', tuple(img.size))
obs = [o for o in bpy.data.objects if o.type == 'MESH']
bpy.context.view_layer.update()
allc = []
for o in sorted(obs, key=lambda o: o.name):
    c = np.array([o.matrix_world @ v.co for v in o.data.vertices]); allc.append(c)
    print('OBJ %-14s tris %4d min %s max %s size %s' % (o.name, sb.tri_count(o), c.min(0).round(3), c.max(0).round(3), np.ptp(c, 0).round(3)))
    sb.tex_material(o, 'm_' + o.name, img); o.data.materials[0].use_backface_culling = False
A = np.concatenate(allc); print('ALL min %s max %s size %s' % (A.min(0).round(3), A.max(0).round(3), np.ptp(A, 0).round(3)))
cen = tuple((A.min(0) + A.max(0)) / 2)
sc, cam, cd, sun = sb.preview_scene(ground=None)
P = []
for i, (yaw, pit) in enumerate(((0, 5), (35, 30), (180, 10), (90, 5), (0, 89), (215, 35), (180, -30), (0, -60), (270, 5))):
    p = sb.WORK + '_look/radio_t%d.png' % i; P.append(p)
    sb.shoot(sc, cam, cd, sun, p, yaw, pit, 14, 30, cen, res=(700, 600), sun_dir=(0.3, 0.6, -0.5) if yaw < 90 else (-0.3, -0.6, -0.5))
sb.sheet(P, sb.WORK + '_look/radio_sheet.png', 3)
