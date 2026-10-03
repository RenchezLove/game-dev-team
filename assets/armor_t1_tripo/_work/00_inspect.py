"""Look at cloth_t1.glb next to the T0 hero: stats, plan yaw, profiles, clay+textured views.
Run: blender.exe -b --factory-startup --python 00_inspect.py
"""
import bpy, sys, math
sys.path.insert(0, 'E:/game-dev-team/assets/hero_tripo/_work')
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import hcommon as H
import wcommon as W
from mathutils import Matrix, Vector
GLB = 'E:/ContrarySurvior/ContrarySurvivor/Saved/Tripo/cloth_t1/cloth_t1.glb'
OUT = 'E:/game-dev-team/assets/armor_t1_tripo/_work/_look/'
R = H.ray

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=GLB)
bpy.context.view_layer.update()
for ob in bpy.data.objects:
    print('GLB OBJ', ob.name, ob.type, ob.parent.name if ob.parent else '-', tuple(round(a, 3) for a in ob.matrix_world.to_scale()))
tr = [o for o in bpy.data.objects if o.type == 'MESH'][0]
me = tr.data
me.transform(tr.matrix_world); tr.matrix_world = Matrix.Identity(4)
cs = [v.co.copy() for v in me.vertices]
mn = Vector((min(c.x for c in cs), min(c.y for c in cs), min(c.z for c in cs)))
mx = Vector((max(c.x for c in cs), max(c.y for c in cs), max(c.z for c in cs)))
print('RAW tris=%d verts=%d bbox=%s..%s uv=%s mats=%s' % (sum(len(p.vertices) - 2 for p in me.polygons), len(me.vertices),
      tuple(round(a, 3) for a in mn), tuple(round(a, 3) for a in mx), [u.name for u in me.uv_layers], [m.name for m in me.materials]))
for im in bpy.data.images:
    print('IMG', im.name, tuple(im.size))
# plan yaw: arms span is the longest horizontal extent -> angle of max extent
best = None
for i in range(-900, 900, 5):
    a = math.radians(i / 10)
    ext = [c.x * math.cos(a) + c.y * math.sin(a) for c in cs]
    w = max(ext) - min(ext)
    if best is None or w > best[0]:
        best = (w, i / 10)
print('YAW arm-span axis at %.1f deg from +X, span %.3f (x extent %.3f, y extent %.3f)' % (best[1], best[0], mx.x - mn.x, mx.y - mn.y))

for vn, vd in (('px', (1, 0, 0.1)), ('mx', (-1, 0, 0.1)), ('py', (0, 1, 0.1)), ('my', (0, -1, 0.1)), ('top', (0.001, -0.02, 1))):
    pass
sc, cam, suns = W.setup_render(res=800)
sc.render.film_transparent = False
for vn, vd in (('px', (1, 0, 0.1)), ('mx', (-1, 0, 0.1)), ('py', (0, 1, 0.1)), ('my', (0, -1, 0.1)), ('top', (0.001, -0.02, 1))):
    W.frame_and_shoot([tr], vd, OUT + 'raw_%s.png' % vn, suns=suns)
