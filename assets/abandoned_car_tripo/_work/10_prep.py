"""Tripo car2.glb -> oriented, scaled source for the car kit (_work/car_src.blend).
Facts (02_orient.py): the Tripo car lies turned 16.8 deg in plan (that is the 2.61 m
"width"); unturned it is 3.71 x 1.71 x 1.40 m with the nose at +X. Here: unturn, nose
to +Y (Blender build convention of the kit; UE import mirrors Y -> nose -Y), centre on
the ground, scale non-uniformly to VAZ-2105 4.13 x 1.62 x 1.45 m (length over bumpers,
body width without mirrors, ground to roof).
Islands are tagged into objects: Shell, Wheel_0..3, Mirror_*, Handle_*, Wiper_*, Under_*, Misc_*.
Run: blender.exe -b --factory-startup --python 10_prep.py
"""
import bpy, bmesh, math
import numpy as np
from mathutils import Matrix, Vector

GLB = 'E:/ContrarySurvior/ContrarySurvivor/Saved/Tripo/car2/car2.glb'
WORK = 'E:/game-dev-team/assets/abandoned_car_tripo/_work/'
YAW = 16.8                          # measured: min plan width at this turn
L_T, W_T, H_T = 4.13, 1.62, 1.45    # VAZ-2105

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=GLB)
o = [o for o in bpy.data.objects if o.type == 'MESH'][0]
bpy.context.view_layer.update()
o.data.transform(o.matrix_world)
o.parent = None
o.matrix_world = Matrix.Identity(4)
for x in [x for x in bpy.data.objects if x is not o]:
    bpy.data.objects.remove(x, do_unlink=True)
# unturn, then nose (+X) -> +Y
o.data.transform(Matrix.Rotation(math.radians(90), 4, 'Z') @ Matrix.Rotation(math.radians(YAW), 4, 'Z'))
me = o.data
bm = bmesh.new(); bm.from_mesh(me)
bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
bm.to_mesh(me); bm.free(); me.update()

# islands
bm = bmesh.new(); bm.from_mesh(me)
bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
lab = {}
k = 0
for v in bm.verts:
    if v.index in lab:
        continue
    st = [v]; lab[v.index] = k
    while st:
        u = st.pop()
        for e in u.link_edges:
            w = e.other_vert(u)
            if w.index not in lab:
                lab[w.index] = k; st.append(w)
    k += 1
isl = {}
for f in bm.faces:
    isl.setdefault(lab[f.verts[0].index], []).append(f.index)
bm.free()
sizes = sorted(isl, key=lambda i: -len(isl[i]))
shell = sizes[0]
P = np.array([v.co[:] for v in me.vertices])
sP = P[[v for v in range(len(P)) if lab[v] == shell]]
mn, mx = sP.min(0), sP.max(0)
zmin = P[:, 2].min()                       # wheel bottoms
sx = W_T / (mx[0] - mn[0]); sy = L_T / (mx[1] - mn[1]); sz = H_T / (mx[2] - zmin)
print('SHELL before scale: %.3f x %.3f, ground..roof %.3f -> scale x%.3f y%.3f z%.3f' % (
    mx[0] - mn[0], mx[1] - mn[1], mx[2] - zmin, sx, sy, sz))
me.transform(Matrix.Diagonal((sx, sy, sz, 1)) @ Matrix.Translation((-(mn[0] + mx[0]) / 2, -(mn[1] + mx[1]) / 2, -zmin)))
me.update()


def classify(fidx):
    cs = np.array([me.polygons[i].center[:] for i in fidx])
    c = cs.mean(0); n = len(fidx)
    ext = cs.max(0) - cs.min(0)
    if n == len(isl[shell]):
        return 'Shell'
    if n >= 60 and c[2] < 0.5:
        return 'Wheel'
    if c[2] < 0.35:
        return 'Under'
    if abs(c[0]) > 0.75 and c[2] > 0.8 and ext[1] < 0.2:
        return 'Mirror'
    if abs(c[0]) > 0.75:
        return 'Handle'
    if ext[0] > 0.3 and c[2] > 0.8:
        return 'Wiper'
    return 'Misc'


objs = {}
for i in sizes:
    tag = classify(isl[i])
    n = sum(1 for k2 in objs if k2.startswith(tag))
    name = tag if tag == 'Shell' else '%s_%d' % (tag, n)
    ob = o.copy(); ob.data = me.copy(); ob.name = ob.data.name = name
    bpy.context.collection.objects.link(ob)
    bm = bmesh.new(); bm.from_mesh(ob.data)
    keep = set(isl[i])
    bm.faces.ensure_lookup_table()
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.index not in keep], context='FACES')
    bm.to_mesh(ob.data); bm.free()
    cs = [v.co for v in ob.data.vertices]
    a = [min(c[j] for c in cs) for j in range(3)]; b = [max(c[j] for c in cs) for j in range(3)]
    print('PART %-9s faces=%4d min=(%.2f %.2f %.2f) max=(%.2f %.2f %.2f)' % (name, len(keep), *a, *b))
    objs[name] = ob
bpy.data.objects.remove(o, do_unlink=True)
allc = [v.co for ob in objs.values() for v in ob.data.vertices]
print('TOTAL size %.3f x %.3f x %.3f, zmin %.3f' % tuple(
    [max(c[j] for c in allc) - min(c[j] for c in allc) for j in range(3)] + [min(c[2] for c in allc)]))
bpy.ops.wm.save_as_mainfile(filepath=WORK + 'car_src.blend')
print('SAVED', WORK + 'car_src.blend')
