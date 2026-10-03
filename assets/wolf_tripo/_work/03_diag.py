"""Profiles of the old wolf (rest) and of the Tripo wolf turned to +Y, feet on Z0.
Run: blender.exe -b --factory-startup --python 03_diag.py
"""
import bpy, bmesh, sys, math
sys.path.insert(0, 'E:/game-dev-team/assets/hero_tripo/_work')
import hcommon as H
from mathutils import Matrix, Vector
R = H.ray
def f(p, k): return '  -- ' if p is None else '%.3f' % getattr(p, k)
def prof(tag, ob, y0, y1):
    tree, cos = H.bvh_of([ob])
    print(tag, 'bbox x %.3f..%.3f y %.3f..%.3f z %.3f..%.3f' % (min(c.x for c in cos), max(c.x for c in cos), min(c.y for c in cos), max(c.y for c in cos), min(c.z for c in cos), max(c.z for c in cos)))
    print(tag, 'SPINE: y | top z (ray down at x=0) | belly z (ray up from z=0.45 at x=0) | half-width at mid height')
    y = y0
    while y <= y1 + 1e-6:
        t = R(tree, (0, y, 3), (0, 0, -1)); b = R(tree, (0, y, -1), (0, 0, 1))
        w = R(tree, (2, y, ((t.z + b.z) / 2) if t and b else 0.7), (-1, 0, 0))
        print(tag, ' y=%+.2f top %s bottom %s halfwidth %s' % (y, f(t, 'z'), f(b, 'z'), f(w, 'x')))
        y += 0.05
    print(tag, 'LEGS (left side x>0.03): z | front leg: y range, x range | rear leg: y range, x range')
    ymid = (y0 + y1) / 2
    for i in range(0, 15):
        z0 = i * 0.05; z1 = z0 + 0.05
        out = []
        for name, pred in (('front', lambda c: c.y > split), ('rear', lambda c: c.y <= split)):
            pass
        s = [c for c in cos if c.x > 0.03 and z0 <= c.z < z1]
        fr = [c for c in s if c.y > SPLIT[tag]]; re = [c for c in s if c.y <= SPLIT[tag]]
        def d(l): return 'y %+.3f..%+.3f x %.3f..%.3f n=%d' % (min(c.y for c in l), max(c.y for c in l), min(c.x for c in l), max(c.x for c in l), len(l)) if l else 'none'
        print(tag, ' z %.2f..%.2f | front %s | rear %s' % (z0, z1, d(fr), d(re)))
    return tree, cos
SPLIT = {'OLD': -0.05, 'NEW': 0.0}
bpy.ops.wm.open_mainfile(filepath='E:/game-dev-team/assets/anim_wolf/_work/_qc_wolf_death.blend')
rig = bpy.data.objects['WolfRig']; rig.animation_data.action = None
for pb in rig.pose.bones: pb.matrix_basis = Matrix.Identity(4)
bpy.context.view_layer.update()
prof('OLD', bpy.data.objects['SK_Wolf'], -0.95, 0.90)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath='E:/ContrarySurvior/ContrarySurvivor/Saved/Tripo/wolf/wolf.glb')
tr = [o for o in bpy.context.selected_objects if o.type == 'MESH'][0]
bpy.context.view_layer.update()
tr.data.transform(Matrix.Rotation(math.radians(90), 4, 'Z') @ tr.matrix_world); tr.matrix_world = Matrix.Identity(4)
zmin = min(v.co.z for v in tr.data.vertices)
tr.data.transform(Matrix.Translation((0, 0, -zmin)))
prof('NEW', tr, -1.10, 1.10)
