"""Export SM_TripoBarrel.fbx + round-trip verify (tris, size, origin, one UV, one
material, texture 512 with the paint mask in alpha).
Run: blender.exe -b --factory-startup --python 12_export_verify.py
"""
import bpy, os, sys
import numpy as np
sys.path.insert(0, 'E:/game-dev-team/assets')
import propcommon as PC
import addon_utils

OUT = 'E:/game-dev-team/assets/barrel_tripo/'
FBX = OUT + 'SM_TripoBarrel.fbx'
TEX = OUT + 'T_TripoBarrel_D.png'
bpy.ops.wm.open_mainfile(filepath=OUT + '_work/barrel_work.blend')
addon_utils.enable('io_scene_fbx')
PC.export_one(bpy.data.objects['SM_TripoBarrel'], FBX)
print('FILE %s %.1f KB' % (FBX, os.path.getsize(FBX) / 1024))

bpy.ops.wm.read_factory_settings(use_empty=True)
addon_utils.enable('io_scene_fbx')
bpy.ops.import_scene.fbx(filepath=FBX)
ms = [o for o in bpy.data.objects if o.type == 'MESH']
ob = ms[0]; me = ob.data
bpy.context.view_layer.update()
cs = [ob.matrix_world @ v.co for v in me.vertices]
mn = [min(c[i] for c in cs) for i in range(3)]
mx = [max(c[i] for c in cs) for i in range(3)]
tris = sum(len(p.vertices) - 2 for p in me.polygons)
loc, rot, scl = ob.matrix_world.decompose()
imgs = [n.image.filepath for m in me.materials if m and m.node_tree
        for n in m.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image]
print('VERIFY meshes=%d tris=%d verts=%d size=(%.3f, %.3f, %.3f) zmin=%.3f centre_xy=(%.3f, %.3f)' % (
    len(ms), tris, len(me.vertices), mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2], mn[2],
    (mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2))
print('VERIFY transform loc=%s rot=%s scale=%s' % (tuple(round(a, 4) for a in loc),
      tuple(round(a, 4) for a in rot.to_euler()), tuple(round(a, 4) for a in scl)))
print('VERIFY uv=%s mats=%s tex=%s' % ([u.name for u in me.uv_layers], [m.name for m in me.materials], imgs))

im = bpy.data.images.load(TEX)
px = np.array(im.pixels[:], dtype=np.float32).reshape(im.size[1], im.size[0], 4)
a = px[..., 3]
rust = px[a < 0.1][:, :3]         # clean rust (edges a 0.1..0.9 are half-painted)
paint = px[a > 0.99][:, :3]
print('VERIFY texture %dx%d channels=%d alpha min=%.2f max=%.2f paint(a>0.99)=%.3f rust(a<0.1)=%.3f' % (
    im.size[0], im.size[1], im.channels, a.min(), a.max(), (a > 0.99).mean(), (a < 0.1).mean()))
print('VERIFY median rgb paint=%s (neutral grey expected) rust=%s (orange expected, not zeroed)' % (
    np.median(paint, 0).round(3), np.median(rust, 0).round(3)))
ok = (len(ms) == 1 and 50 <= tris <= 100 and len(me.uv_layers) == 1 and len(me.materials) == 1
      and abs(mn[2]) < 1e-4 and abs((mn[0] + mx[0]) / 2) < 1e-3 and abs((mn[1] + mx[1]) / 2) < 1e-3
      and im.size[0] == 512 and im.channels == 4 and a.min() < 0.05 and a.max() > 0.95
      and np.median(rust, 0)[0] > np.median(rust, 0)[2] + 0.1)
print('ROUNDTRIP', 'PASS' if ok else 'FAIL')
