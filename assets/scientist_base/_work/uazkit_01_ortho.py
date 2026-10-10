"""Orthographic views of the textured UAZ source (already turned and scaled, object 'src' in uaz_work.blend) with a 10 cm grid of ticks -
to read the door seams off the picture. Run: blender -b uaz_work.blend --factory-startup --python uazkit_01_ortho.py"""
import bpy, sys, math
import numpy as np
from mathutils import Vector
sys.path.insert(0, 'E:/game-dev-team/assets/scientist_base/_work')
import sb
src = bpy.data.objects['src']
for o in bpy.data.objects:
    o.hide_render = o is not src
src.data.materials[0].use_backface_culling = True
sc = bpy.context.scene
sc.render.engine = 'BLENDER_EEVEE'
sc.view_settings.view_transform = 'Standard'
w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs[0].default_value = (1, 1, 1, 1); w.node_tree.nodes['Background'].inputs[1].default_value = 3.0
# flat look: emission from the texture
m = src.data.materials[0]; nt = m.node_tree; tex = [n for n in nt.nodes if n.type == 'TEX_IMAGE'][0]
em = nt.nodes.new('ShaderNodeEmission'); nt.links.new(tex.outputs['Color'], em.inputs['Color'])
out = [n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'][0]; nt.links.new(em.outputs['Emission'], out.inputs['Surface'])
cd = bpy.data.cameras.new('C'); cam = bpy.data.objects.new('C', cd); sc.collection.objects.link(cam); sc.camera = cam
cd.type = 'ORTHO'; cd.clip_end = 50
PPM = 400
def shot(name, d, cen, wm, hm):
    d = Vector(d); cam.location = Vector(cen) + d * 10; cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
    cd.ortho_scale = max(wm, hm); cd.sensor_fit = 'HORIZONTAL' if wm >= hm else 'VERTICAL'
    sc.render.resolution_x = int(wm * PPM); sc.render.resolution_y = int(hm * PPM)
    sc.render.filepath = sb.WORK + '_look/uazkit_%s.png' % name; bpy.ops.render.render(write_still=True)
    img, px = sb.load_px(sc.render.filepath); px = px.copy(); H, W = px.shape[:2]
    # ticks every 10 cm (long every 50) on the left and bottom borders; picture centre = cen
    for i in range(int(wm * 10) + 1):
        x = int(i * PPM / 10); L = 24 if i % 5 == 0 else 10
        if x < W: px[:L, x:x + 2, :3] = (1, 0, 0)
    for j in range(int(hm * 10) + 1):
        y = int(j * PPM / 10); L = 24 if j % 5 == 0 else 10
        if y < H: px[y:y + 2, :L, :3] = (1, 0, 0)
    sb.save_png(px[..., :3], sc.render.filepath)
    print('ORTHO %s: %dx%d px, %d px per m, centre %s, view from %s' % (name, W, H, PPM, cen, tuple(d)))
shot('left', (-1, 0, 0), (0, 0, 1.1), 4.6, 2.2)     # looking at the -X side: +Y (nose) is to the LEFT of the picture
shot('right', (1, 0, 0), (0, 0, 1.1), 4.6, 2.2)     # looking at the +X side: nose to the RIGHT
shot('rear', (0, -1, 0), (0, 0, 1.1), 2.4, 2.2)     # looking at the back (-Y): +X to the right
shot('front', (0, 1, 0), (0, 0, 1.1), 2.4, 2.2)
shot('top', (0, 0, 1), (0, 0, 1.1), 2.4, 4.6)
