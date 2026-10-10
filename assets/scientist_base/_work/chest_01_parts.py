"""Wooden chest source: objects, parts, textured look renders. Run: blender -b --factory-startup --python chest_01_parts.py -- <model file>"""
import bpy, sys, bmesh, os
import numpy as np
sys.path.insert(0, 'E:/game-dev-team/assets/scientist_base/_work')
import sb
sb.empty()
f = sb.args()[0]; ext = f.lower().rsplit('.', 1)[-1]
if ext == 'dae': sb.load_dae_simple(f)
elif ext == 'fbx': bpy.ops.import_scene.fbx(filepath=f)
elif ext == 'obj': bpy.ops.wm.obj_import(filepath=f)
elif ext in ('glb', 'gltf'): bpy.ops.import_scene.gltf(filepath=f)
bpy.context.view_layer.update()
img = bpy.data.images.load(sb.SRCD + 'wooden-chest/textures/DefaultMaterial_albedo.jpeg'); print('TEXTURE', tuple(img.size))
obs = [o for o in bpy.data.objects if o.type == 'MESH']; allc = []
for o in obs:
    c = np.array([o.matrix_world @ v.co for v in o.data.vertices]); allc.append(c)
    print('OBJ %-20s tris %4d min %s max %s size %s uv %s' % (o.name, sb.tri_count(o), c.min(0).round(3), c.max(0).round(3), np.ptp(c, 0).round(3), [u.name for u in o.data.uv_layers]))
src = sb.join_meshes(obs, 'src')
bm = sb.bm_of(src); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
for comp in sorted(sb.islands(bm), key=lambda c: -len(c)):
    c = np.array([v.co[:] for f_ in comp for v in f_.verts])
    print('PART faces %4d min %s max %s size %s' % (len(comp), c.min(0).round(3), c.max(0).round(3), np.ptp(c, 0).round(3)))
bm.free()
sb.tex_material(src, 'm', img); src.data.materials[0].use_backface_culling = False
A = sb.coords(src); cen = tuple((A.min(0) + A.max(0)) / 2); R = float(np.linalg.norm(np.ptp(A, 0))) / 2
sc, cam, cd, sun = sb.preview_scene(ground=None); cd.clip_start = R * 0.01; cd.clip_end = R * 100
P = []
for i, (yaw, pit) in enumerate(((0, 8), (35, 35), (180, 10), (90, 8), (0, 89), (215, 35))):
    p = sb.WORK + '_look/chest_t%d.png' % i; P.append(p)
    sb.shoot(sc, cam, cd, sun, p, yaw, pit, R * 4.5, 30, cen, res=(700, 600), sun_dir=(0.3, 0.6, -0.5) if yaw < 90 else (-0.3, -0.6, -0.5))
sb.sheet(P, sb.WORK + '_look/chest_sheet.png', 3)
