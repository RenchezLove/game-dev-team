"""Export the car kit FBX (9 parts) + round-trip verify: tris per part and assembled,
pivots (part geometry against its hinge), one UV, one material, texture alpha, and the
assembled size (parts put back at their pivots, 4 wheels).
Run: blender.exe -b --factory-startup --python 14_export_verify.py
"""
import bpy, os, sys, math
import numpy as np
from mathutils import Vector
sys.path.insert(0, 'E:/game-dev-team/assets/abandoned_car_tripo/_work')
sys.path.insert(0, 'E:/game-dev-team/assets')
import propcommon as PC
import addon_utils
from carconst import *

OUT = 'E:/game-dev-team/assets/abandoned_car_tripo/'
TEX = OUT + 'T_AbandonedCarTripo_D.png'
PIV = {}
for line in open(WORK + '_bake.log', encoding='utf-8'):
    if line.startswith('PART '):
        PIV[line.split()[1]] = Vector(eval(line.split('pivot(blender)=')[1].split(' local')[0]))
WHEELS = [(-0.66, 1.44), (0.66, 1.44), (-0.66, -0.97), (0.66, -0.97)]

bpy.ops.wm.open_mainfile(filepath=WORK + 'car_kit.blend')
addon_utils.enable('io_scene_fbx')
names = ['SM_AbandonedCar_' + n for n in PARTS]
for n in names:
    PC.export_one(bpy.data.objects[n], OUT + n + '.fbx')

res = {}
for n in names:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    addon_utils.enable('io_scene_fbx')
    bpy.ops.import_scene.fbx(filepath=OUT + n + '.fbx')
    ms = [o for o in bpy.data.objects if o.type == 'MESH']
    ob = ms[0]; me = ob.data
    bpy.context.view_layer.update()
    loc, rot, scl = ob.matrix_world.decompose()
    cs = [ob.matrix_world @ v.co for v in me.vertices]
    mn = Vector([min(c[i] for c in cs) for i in range(3)]); mx = Vector([max(c[i] for c in cs) for i in range(3)])
    tris = sum(len(p.vertices) - 2 for p in me.polygons)
    res[n] = (tris, mn, mx, cs)
    print('VERIFY %-24s meshes=%d tris=%3d verts=%3d loc=%s rot=%s scale=%s uv=%s mats=%s min=(%.3f %.3f %.3f) max=(%.3f %.3f %.3f) %s' % (
        n, len(ms), tris, len(me.vertices), tuple(round(a, 4) for a in loc), tuple(round(math.degrees(a), 2) for a in rot.to_euler()),
        tuple(round(a, 4) for a in scl), [u.name for u in me.uv_layers], [m.name for m in me.materials],
        *mn, *mx, 'OK' if (len(ms) == 1 and len(me.uv_layers) == 1 and len(me.materials) == 1 and loc.length < 1e-4
                           and abs(scl.x - 1) < 1e-4) else 'BAD'))

# pivots: doors hinge at the front edge (max local Y = 0) and bottom (min Z = 0); hood hinge
# at the rear edge (min Y ~ 0, top Z ~ 0); trunk hinge at the front edge (max Y ~ 0); wheel centred
chk = []
for s in ('FL', 'FR', 'RL', 'RR'):
    t, mn, mx, _ = res['SM_AbandonedCar_Door_' + s]
    chk.append(('Door_' + s, abs(mx.y) < 0.02 and abs(mn.z) < 0.02, 'front edge y=%.3f bottom z=%.3f' % (mx.y, mn.z)))
t, mn, mx, _ = res['SM_AbandonedCar_Hood']
chk.append(('Hood', abs(mn.y) < 0.06 and abs(mx.z) < 0.02, 'rear edge y=%.3f top z=%.3f' % (mn.y, mx.z)))
t, mn, mx, _ = res['SM_AbandonedCar_Trunk']
chk.append(('Trunk', abs(mx.y) < 0.06 and abs(mx.z) < 0.02, 'front edge y=%.3f top z=%.3f' % (mx.y, mx.z)))
t, mn, mx, _ = res['SM_AbandonedCar_Wheel']
chk.append(('Wheel', (mn + mx).length < 0.03, 'centre=(%.3f %.3f %.3f) r=%.3f' % (*((mn + mx) / 2), (mx.y - mn.y) / 2)))
for c in chk:
    print('PIVOT %-8s %s %s' % (c[0], 'OK' if c[1] else 'BAD', c[2]))

allc = []
for n in names:
    key = n.replace('SM_AbandonedCar_', '')
    if key == 'Wheel':
        for (x, y) in WHEELS:
            allc += [Vector((c.x + x, c.y + y, c.z + WHEEL_R)) for c in res[n][3]]
    else:
        allc += [c + PIV[n] for c in res[n][3]]
mn = [min(c[i] for c in allc) for i in range(3)]; mx = [max(c[i] for c in allc) for i in range(3)]
per = {n.replace('SM_AbandonedCar_', ''): res[n][0] for n in names}
total = sum(per.values()) + 3 * per['Wheel']
print('ASSEMBLED tris=%d (wheel x4) per part %s' % (total, per))
print('ASSEMBLED size X=%.3f (width) Y=%.3f (length) Z=%.3f (height), zmin=%.3f' % (
    mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2], mn[2]))
im = bpy.data.images.load(TEX)
a = np.array(im.pixels[:], dtype=np.float32).reshape(im.size[1], im.size[0], 4)[..., 3]
print('TEXTURE %dx%d channels=%d alpha min=%.2f max=%.2f paint(a>0.99)=%.3f' % (
    im.size[0], im.size[1], im.channels, a.min(), a.max(), (a > 0.99).mean()))
ok = (all(c[1] for c in chk) and 800 <= total <= 900 and im.channels == 4 and a.min() < 0.05 and a.max() > 0.95)
print('ROUNDTRIP', 'PASS' if ok else 'FAIL')
