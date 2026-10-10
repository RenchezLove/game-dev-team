"""Close looks at a work model. Run: blender.exe -b <work.blend> --factory-startup --python 92_close.py -- <object> <texture> <tag> yaw,pitch[,dist_factor] ..."""
import bpy, sys, math, os
import numpy as np
sys.path.insert(0, 'E:/game-dev-team/assets/scientist_base/_work')
import sb
a = sb.args(); name, tex, tag = a[0], a[1], a[2]
ob = bpy.data.objects[name]
for o in bpy.data.objects:
    o.hide_render = o is not ob
img = bpy.data.images.load(tex, check_existing=False); sb.tex_material(ob, 'prev', img)
ob.data.uv_layers['UVMap'].active_render = True
c = sb.coords(ob); mn, mx = c.min(0), c.max(0); R = float(np.linalg.norm(mx - mn)) / 2
sc, cam, cd, sun = sb.preview_scene(ground_z=float(mn[2]) - (0 if abs(mn[2]) < 1e-6 else 3 * R))
paths = []
for s in a[3:]:
    v = [float(x) for x in s.split(',')]; f = v[2] if len(v) > 2 else 1.0
    p = sb.WORK + '_prev_tmp/%s_%s_%d_%d.png' % (name, tag, v[0], v[1]); paths.append(p)
    yaw = math.radians(v[0])
    sb.shoot(sc, cam, cd, sun, p, v[0], v[1], R * 3.2 * f * (40 / (v[3] if len(v) > 3 else 40)), (v[3] if len(v) > 3 else 40), tuple((mn + mx) / 2), res=(960, 720), sun_dir=(-math.sin(yaw) * 0.6 + 0.2, math.cos(yaw) * 0.6, -0.66))
sb.sheet(paths, sb.WORK + '_prev_tmp/%s_%s_sheet.png' % (name, tag), 2)
