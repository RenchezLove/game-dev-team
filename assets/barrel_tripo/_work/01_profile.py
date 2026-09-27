import bpy, math
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath='E:/ContrarySurvior/ContrarySurvivor/Saved/Tripo/barrel.glb')
bpy.context.view_layer.update()
o = [o for o in bpy.data.objects if o.type == 'MESH'][0]
cs = [o.matrix_world @ v.co for v in o.data.vertices]
z0 = min(c.z for c in cs)
bins = {}
for c in cs:
    k = int((c.z - z0) / 0.01)
    r = math.hypot(c.x, c.y)
    bins.setdefault(k, []).append(r)
for k in sorted(bins):
    rs = bins[k]
    print('Z %.2f n=%3d rmax=%.3f rmin=%.3f' % (k * 0.01, len(rs), max(rs), min(rs)))
import numpy as np
im = bpy.data.images[0]; a = np.array(im.pixels[:]).reshape(-1, 4)
print('ALPHA min/max', a[:,3].min(), a[:,3].max())
