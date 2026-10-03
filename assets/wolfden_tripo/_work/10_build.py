"""Tripo wolf den (wolfden.glb) -> SM_WolfDenCave on the footprint of the old den.
Turn the mouth to -Y (as the old one), drop Tripo's ragged ground flaps, sit the rocks on Z0, scale onto the
old footprint, add one clean ground pad (cave floor + apron under the bones) a little above zero,
new UV0 + bake of the Tripo colours, UV1 for the lightmap. Colours / mask are done by 11_paint.py.
Run: blender.exe -b --factory-startup --python 10_build.py
"""
import bpy, bmesh, sys, os, math
import numpy as np
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

GLB = 'E:/ContrarySurvior/ContrarySurvivor/Saved/Tripo/wolfden/wolfden.glb'
OUT = 'E:/game-dev-team/assets/wolfden_tripo/'
OLD_MIN, OLD_MAX = (-2.161, -1.495), (2.170, 1.573)      # old SM_WolfDenCave.fbx footprint (Blender axes), mouth towards -Y
MOUTH_H = 1.15                                           # clear height of the mouth after scaling (wolf with ears is 1.06 m)
PAD_Z = 0.02
NAME = 'SM_WolfDenCave'

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=GLB)
ob = [o for o in bpy.context.selected_objects if o.type == 'MESH'][0]
for o in list(bpy.context.selected_objects):
    if o is not ob:
        bpy.data.objects.remove(o, do_unlink=True)
bpy.context.view_layer.update()
me = ob.data
me.transform(Matrix.Rotation(math.radians(-90), 4, 'Z') @ ob.matrix_world)       # Tripo mouth looks +X -> -Y
ob.parent = None
ob.matrix_world = Matrix.Identity(4)
me.transform(Matrix.Translation((0, 0, -min(v.co.z for v in me.vertices))))
bm = bmesh.new(); bm.from_mesh(me)
bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
bmesh.ops.triangulate(bm, faces=bm.faces[:])
bm.to_mesh(me); bm.free(); me.update()
print('TRIPO tris %d verts %d' % (len(me.polygons), len(me.vertices)))
src = ob.copy(); src.data = me.copy(); src.name = 'TripoSrc'
bpy.context.collection.objects.link(src)

bm = bmesh.new(); bm.from_mesh(me)
bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
KIND = bm.faces.layers.int.new('kind')            # 0 rock shell, 1 small loose part (bones, pebbles), 2 ground pad
# loose parts
seen = set(); parts = []
for v in bm.verts:
    if v in seen:
        continue
    st = [v]; seen.add(v); c = []
    while st:
        a = st.pop(); c.append(a)
        for e in a.link_edges:
            b = e.other_vert(a)
            if b not in seen:
                seen.add(b); st.append(b)
    parts.append(c)
parts.sort(key=lambda c: -len(c))
shell = set(parts[0])
small = [c for c in parts[1:]]
for c in small:
    for v in c:
        for f in v.link_faces:
            f[KIND] = 1
print('PARTS shell verts %d, small parts %d (%s tris)' % (len(shell), len(small), [len({f for v in c for f in v.link_faces}) for c in small]))

# Tripo's ground: flat faces lying at the bottom of the shell (the ragged flap in front, slivers, the cave floor)
flat = [f for f in bm.faces if f[KIND] == 0 and abs(f.normal.z) > 0.8 and max(v.co.z for v in f.verts) < 0.06]
fs = set(flat); groups = []
left = set(flat)
while left:
    f = left.pop(); g = [f]; st = [f]
    while st:
        a = st.pop()
        for e in a.edges:
            for b in e.link_faces:
                if b in left:
                    left.discard(b); g.append(b); st.append(b)
    groups.append(g)
for g in sorted(groups, key=lambda g: -len(g)):
    co = np.array([v.co for f in g for v in f.verts])
    print('GROUND patch of Tripo: %2d tris, x %.2f..%.2f y %.2f..%.2f z %.3f..%.3f' % (len(g), co[:, 0].min(), co[:, 0].max(), co[:, 1].min(), co[:, 1].max(), co[:, 2].min(), co[:, 2].max()))
bmesh.ops.delete(bm, geom=flat, context='FACES')
bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
print('GROUND removed %d flat tris, %d tris left' % (len(flat), len(bm.faces)))

# mouth: the tallest free column straight in front (scan x at the front, ray up from the ground)
# shell only (the bones in front would block the rays)
sb = bm.copy()
bmesh.ops.delete(sb, geom=[f for f in sb.faces if f[sb.faces.layers.int['kind']] != 0], context='FACES')
tree = BVHTree.FromBMesh(sb)
deep = []                                   # rays from the front that go far inside = the mouth (see 05_mouth.py for the map)
for iz in range(1, 40):
    for ix in range(-35, 36):
        h = tree.ray_cast(Vector((ix * 0.02, -3, iz * 0.02)), Vector((0, 1, 0)), 6.0)[0]
        if h is not None and h.y > -0.05:
            deep.append((ix * 0.02, iz * 0.02, h.y))
sb.free()
core = [d for d in deep if d[1] < 0.3]
mx0, mx1 = min(d[0] for d in core), max(d[0] for d in core)
deep = [d for d in deep if mx0 <= d[0] <= mx1]
best = (max(d[1] for d in deep) + 0.02, (mx0 + mx1) / 2, -0.3)
print('MOUTH raw: width x %.2f..%.2f, clear height %.2f, back wall y %.2f' % (mx0, mx1, best[0], max(d[2] for d in deep)))

# sit the rocks on the ground: every open edge of the shell near the bottom goes to Z0
nsn = 0
for e in bm.edges:
    if len(e.link_faces) == 1:
        for v in e.verts:
            if v.co.z < 0.10 and v.co.z != 0.0:
                v.co.z = 0.0; nsn += 1
co = np.array([v.co for v in bm.verts])
mn, mx = co.min(0), co.max(0)
SX = (OLD_MAX[0] - OLD_MIN[0]) / (mx[0] - mn[0])
SY = (OLD_MAX[1] - OLD_MIN[1]) / (mx[1] - mn[1])
SZ = min(MOUTH_H / best[0], 3.617 / mx[2])
for v in bm.verts:
    v.co = Vector((OLD_MIN[0] + (v.co.x - mn[0]) * SX, OLD_MIN[1] + (v.co.y - mn[1]) * SY, v.co.z * SZ))
FIT = Matrix.Translation((OLD_MIN[0], OLD_MIN[1], 0)) @ Matrix.Diagonal((SX, SY, SZ, 1)) @ Matrix.Translation((-mn[0], -mn[1], 0))
src.data.transform(FIT)
print('FIT raw size %.3f x %.3f x %.3f -> scale x %.3f y %.3f z %.3f; %d open-edge verts snapped to Z0' % (mx[0] - mn[0], mx[1] - mn[1], mx[2], SX, SY, SZ, nsn))

# small parts rest on the pad
bm.verts.ensure_lookup_table()
for c in small:
    vs = [v for v in c if v.is_valid]
    if not vs:
        continue
    dz = PAD_Z + 0.002 - min(v.co.z for v in vs)
    for v in vs:
        v.co.z += dz

# one clean ground pad: under the rocks (inside their contact line), across the cave floor and as an apron under the bones
low = [v.co for v in bm.verts if v.co.z < 0.35 and any(f[KIND] == 0 for f in v.link_faces)]
cx = sum(c.x for c in low) / len(low); cy = sum(c.y for c in low) / len(low)
NB = 40
rock_r = [0.0] * NB; bone_r = [0.0] * NB
def bin_of(c):
    return int(((math.atan2(c.y - cy, c.x - cx) + math.pi) / (2 * math.pi)) * NB) % NB
for c in low:
    b = bin_of(c); rock_r[b] = max(rock_r[b], math.hypot(c.x - cx, c.y - cy))
for cpart in small:
    for v in cpart:
        if v.is_valid:
            b = bin_of(v.co); bone_r[b] = max(bone_r[b], math.hypot(v.co.x - cx, v.co.y - cy))
for i in range(NB):                                   # bins without rock verts (the mouth gap) take their neighbours
    if rock_r[i] == 0.0:
        j = 1
        while rock_r[(i - j) % NB] == 0.0 and rock_r[(i + j) % NB] == 0.0:
            j += 1
        rock_r[i] = max(rock_r[(i - j) % NB], rock_r[(i + j) % NB])
bone_s = [max(bone_r[(i - 1) % NB], bone_r[i], bone_r[(i + 1) % NB]) for i in range(NB)]
ring = []
for i in range(NB):
    a = -math.pi + (i + 0.5) * 2 * math.pi / NB
    r = max(0.88 * rock_r[i], bone_s[i] + 0.22 if bone_s[i] > 0 else 0.0)
    p = Vector((cx + r * math.cos(a), cy + r * math.sin(a), PAD_Z))
    p.x = min(max(p.x, OLD_MIN[0] + 0.03), OLD_MAX[0] - 0.03); p.y = min(max(p.y, OLD_MIN[1] + 0.03), OLD_MAX[1] - 0.03)
    ring.append(bm.verts.new(p))
cv = bm.verts.new((cx, cy, PAD_Z))
for i in range(NB):
    f = bm.faces.new((cv, ring[i], ring[(i + 1) % NB]))
    f[KIND] = 2
    if f.normal.z < 0:
        f.normal_flip()
bm.normal_update()
print('PAD centre (%.2f, %.2f), %d tris at z %.2f, radius %.2f..%.2f' % (cx, cy, NB, PAD_Z, min((v.co - cv.co).length for v in ring), max((v.co - cv.co).length for v in ring)))
bm.to_mesh(me); bm.free(); me.update()
for p in me.polygons:
    p.use_smooth = False
ob.name = me.name = NAME

# ---------- UV0 + bake of the Tripo colours, UV1 for the lightmap ----------
while me.uv_layers:
    me.uv_layers.remove(me.uv_layers[0])
me.uv_layers.new(name='UVMap')
me.uv_layers.new(name='LightmapUV')
bpy.context.scene.tool_settings.use_uv_select_sync = True
def overlaps(layer, res=1024):
    """Texels claimed by the interiors of two or more UV triangles."""
    T_ = len(me.polygons)
    a = np.zeros(len(me.loops) * 2); me.uv_layers[layer].data.foreach_get('uv', a)
    uv = a.reshape(T_, 3, 2)
    inner = np.zeros((res, res), np.int16)
    for t in range(T_):
        p = uv[t] * res
        d = (p[1, 0] - p[0, 0]) * (p[2, 1] - p[0, 1]) - (p[1, 1] - p[0, 1]) * (p[2, 0] - p[0, 0])
        if abs(d) < 1e-9:
            continue
        x0 = max(int(math.floor(p[:, 0].min())), 0); x1 = min(int(math.ceil(p[:, 0].max())) + 1, res)
        y0 = max(int(math.floor(p[:, 1].min())), 0); y1 = min(int(math.ceil(p[:, 1].max())) + 1, res)
        X, Y = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
        w1 = ((X - p[0, 0]) * (p[2, 1] - p[0, 1]) - (Y - p[0, 1]) * (p[2, 0] - p[0, 0])) / d
        w2 = ((p[1, 0] - p[0, 0]) * (Y - p[0, 1]) - (p[1, 1] - p[0, 1]) * (X - p[0, 0])) / d
        w0 = 1 - w1 - w2
        el = [np.linalg.norm(p[2] - p[1]), np.linalg.norm(p[0] - p[2]), np.linalg.norm(p[1] - p[0])]
        dist = np.minimum(np.minimum(w0 * abs(d) / el[0], w1 * abs(d) / el[1]), w2 * abs(d) / el[2])
        inner[y0:y1, x0:x1] += (dist > 0.6)
    return int((inner > 1).sum())


def unwrap(layer, margin):
    me.uv_layers.active = me.uv_layers[layer]
    for ang in (66, 55, 45, 35, 25):               # steeper folds of a rock can lap over themselves in one island: split finer until clean
        bpy.ops.object.select_all(action='DESELECT')
        ob.select_set(True); bpy.context.view_layer.objects.active = ob
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=math.radians(ang), island_margin=0.0, correct_aspect=True, scale_to_bounds=False)
        try:
            bpy.ops.uv.pack_islands(rotate=True, margin_method='FRACTION', margin=margin)
        except TypeError:
            bpy.ops.uv.pack_islands(rotate=True, margin=margin)
        bpy.ops.object.mode_set(mode='OBJECT')
        n = overlaps(layer)
        print('UNWRAP %s angle %d: overlapping texels %d' % (layer, ang, n))
        if n == 0:
            break
unwrap('UVMap', 0.004)
unwrap('LightmapUV', 0.01)
me.uv_layers.active = me.uv_layers['UVMap']
me.uv_layers['UVMap'].active_render = True

bimg = bpy.data.images.new('_bake_raw', 1024, 1024, alpha=False)
bmat = bpy.data.materials.new('_bake')
bmat.use_nodes = True
bn = bmat.node_tree.nodes.new('ShaderNodeTexImage')
bn.image = bimg
bmat.node_tree.nodes.active = bn
me.materials.clear()
me.materials.append(bmat)
scn = bpy.context.scene
scn.render.engine = 'CYCLES'
scn.cycles.samples = 4
scn.cycles.device = 'CPU'
bk = scn.render.bake
bk.use_selected_to_active = True
bk.cage_extrusion = 0.02
bk.max_ray_distance = 0.06
bk.margin = 8
bk.use_pass_direct = False
bk.use_pass_indirect = False
bk.use_pass_color = True
bpy.ops.object.select_all(action='DESELECT')
src.select_set(True); ob.select_set(True)
bpy.context.view_layer.objects.active = ob
bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'})
bimg.filepath_raw = OUT + '_work/_bake_raw.png'; bimg.file_format = 'PNG'; bimg.save()
bpy.data.objects.remove(src, do_unlink=True)

co = np.array([v.co for v in me.vertices])
kinds = [d.value for d in me.attributes['kind'].data]
print('BUILD tris %d (shell %d, small parts %d, pad %d) verts %d min %s max %s size %s' % (len(me.polygons), kinds.count(0), kinds.count(1), kinds.count(2), len(me.vertices),
      co.min(0).round(3), co.max(0).round(3), (co.max(0) - co.min(0)).round(3)))
np.save(OUT + '_work/_pad.npy', np.array([cx, cy, OLD_MIN[0] + ((mx0 + mx1) / 2 - mn[0]) * SX, OLD_MIN[1] + (-0.3 - mn[1]) * SY, best[0] * SZ, OLD_MIN[0] + (mx0 - mn[0]) * SX, OLD_MIN[0] + (mx1 - mn[0]) * SX]))
bpy.ops.wm.save_as_mainfile(filepath=OUT + '_work/wolfden_work.blend')
