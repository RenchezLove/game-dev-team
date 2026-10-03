"""Second UV check + clay close-ups of body / casing / door.
Run: blender.exe -b _src_import.blend --factory-startup --python 03_look.py
"""
import bpy, bmesh, sys
import numpy as np
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W
OUT = 'E:/game-dev-team/assets/izba_slate/_work/'
ob = [o for o in bpy.data.objects if o.type == 'MESH'][0]
me = ob.data
for p in me.polygons:
    p.use_smooth = False
sc, cam, suns = W.setup_render(res=1000)
me.uv_layers['UVMap.001'].active_render = True
me.uv_layers.active = me.uv_layers['UVMap.001']
for vn, vd in (('pX', (1, 0.25, 0.2)), ('mY', (0.25, -1, 0.2)), ('pY', (-0.25, 1, 0.2))):
    W.frame_and_shoot([ob], vd, OUT + '_uv2_%s.png' % vn, margin=0.8, suns=suns)

# clay: split loose, colour by normal
bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); bpy.context.view_layer.objects.active = ob
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.separate(type='LOOSE')
bpy.ops.object.mode_set(mode='OBJECT')
parts = [o for o in bpy.data.objects if o.type == 'MESH']
clay = bpy.data.materials.new('clay'); clay.use_nodes = True
clay.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.6, 0.6, 0.6, 1)
for o in parts:
    o.data.materials.clear(); o.data.materials.append(clay)
    bpy.context.view_layer.update()
big = sorted(parts, key=lambda o: -len(o.data.polygons))
def tris(o): return sum(len(p.vertices) - 2 for p in o.data.polygons)
for o in big[:8]:
    print('PART', o.name, tris(o), [round(a, 2) for a in o.dimensions])
body = [o for o in parts if tris(o) == 244][0]
roof = [o for o in parts if tris(o) == 234][0]
cas = [o for o in parts if tris(o) == 268]
door = [o for o in parts if tris(o) == 96][0]
porch = [o for o in parts if tris(o) == 44][0]
def only(objs):
    for o in parts:
        o.hide_render = o not in objs
only([body])
for vn, vd in (('pYq', (-0.5, 1, 0.5)), ('pXq', (1, -0.5, 0.5)), ('mYq', (0.5, -1, 0.5)), ('bot', (0.3, 0.3, -1)), ('top', (0.2, 0.3, 1))):
    W.frame_and_shoot([body], vd, OUT + '_clay_body_%s.png' % vn, margin=1.0, suns=suns)
only([roof])
for vn, vd in (('pXq', (1, -0.5, 0.4)), ('mXq', (-1, 0.5, 0.4)), ('bot', (0.3, 0.3, -1))):
    W.frame_and_shoot([roof], vd, OUT + '_clay_roof_%s.png' % vn, margin=1.0, suns=suns)
only([cas[0]])
W.frame_and_shoot([cas[0]], (1, -0.5, 0.3), OUT + '_clay_casing.png', margin=1.0, suns=suns)
W.frame_and_shoot([cas[0]], (-1, 0.5, 0.3), OUT + '_clay_casing_back.png', margin=1.0, suns=suns)
only([door, porch])
W.frame_and_shoot([door, porch], (-0.5, 1, 0.4), OUT + '_clay_door.png', margin=1.0, suns=suns)
W.frame_and_shoot([door, porch], (0.5, -1, 0.4), OUT + '_clay_door_back.png', margin=1.0, suns=suns)
# body vertex z/x/y levels
bm = bmesh.new(); bm.from_mesh(body.data)
mw = body.matrix_world
cs = np.array([mw @ v.co for v in bm.verts])
for ax, n in enumerate('xyz'):
    print('BODY', n, sorted(set(np.round(cs[:, ax], 2))))
print('BODY faces by normal')
for f in bm.faces:
    n = (mw.to_3x3() @ f.normal).normalized(); c = mw @ f.calc_center_median()
    if f.calc_area() * 1.2875 > 0.15:
        print('  F n(%.2f %.2f %.2f) c(%.2f %.2f %.2f) area %.2f nv %d' % (n.x, n.y, n.z, c.x, c.y, c.z, f.calc_area() * 1.2875, len(f.verts)))
bm.free()
