"""Preview of one finished model from its work blend (Eevee, flat shade, back faces culled as in Unreal): the game camera view,
a low front-side view, the back and the top glued into one sheet.
Run: blender.exe -b <work.blend> --factory-startup --python 90_preview.py -- <object> <texture png> <out png> [yaw]
"""
import bpy, sys, math, os
import numpy as np
sys.path.insert(0, 'E:/game-dev-team/assets/scientist_base/_work')
import sb
a = sb.args()
name, tex, out = a[0], a[1], a[2]
yaw0 = float(a[3]) if len(a) > 3 else 25.0
ob = bpy.data.objects[name]
for o in bpy.data.objects:
    if o is not ob:
        o.hide_render = True
ob.hide_render = False
img = bpy.data.images.load(tex, check_existing=False)
mat = sb.tex_material(ob, 'prev', img)
ob.data.uv_layers['UVMap'].active_render = True
c = sb.coords(ob); mn, mx = c.min(0), c.max(0); R = float(np.linalg.norm(mx - mn)) / 2
tgt = tuple((mn + mx) / 2)
sc, cam, cd, sun = sb.preview_scene(ground_z=float(mn[2]) if abs(mn[2]) < 1e-6 else float(mn[2]) - R * 3)
tmp = sb.WORK + '_prev_tmp/'; os.makedirs(tmp, exist_ok=True)
D = 30.0 if R > 0.6 else 30.0 * R / 0.6
fov = math.degrees(2 * math.atan(R * 1.25 / D))
shots = [('game', yaw0, 60, (-0.45, 0.6, -0.66)), ('front', yaw0 + 20, 14, (-0.45, 0.6, -0.66)), ('back', yaw0 + 200, 30, (0.45, -0.6, -0.66)), ('top', 0, 89, (-0.3, 0.3, -0.9))]
paths = []
for n, yaw, pit, sd in shots:
    p = tmp + '%s_%s.png' % (name, n); paths.append(p)
    sb.shoot(sc, cam, cd, sun, p, yaw, pit, D, fov, tgt, res=(960, 720), sun_dir=sd)
os.makedirs(os.path.dirname(out), exist_ok=True)
sb.sheet(paths, out, 2)
