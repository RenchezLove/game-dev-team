import bpy, bmesh, math
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath='E:/ContrarySurvior/ContrarySurvivor/Saved/Tripo/wolfden/wolfden.glb')
ob = [o for o in bpy.context.selected_objects if o.type == 'MESH'][0]
bpy.context.view_layer.update()
me = ob.data
me.transform(Matrix.Rotation(math.radians(-90), 4, 'Z') @ ob.matrix_world)
me.transform(Matrix.Translation((0, 0, -min(v.co.z for v in me.vertices))))
bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
# keep the biggest part only
seen = set(); parts = []
for v in bm.verts:
    if v in seen: continue
    st = [v]; seen.add(v); c = []
    while st:
        a = st.pop(); c.append(a)
        for e in a.link_edges:
            b = e.other_vert(a)
            if b not in seen: seen.add(b); st.append(b)
    parts.append(c)
parts.sort(key=lambda c: -len(c))
for c in parts[1:]:
    bmesh.ops.delete(bm, geom=c, context='VERTS')
tree = BVHTree.FromBMesh(bm)
print('DEPTH map from the front (-Y looking +Y): rows z from 0.80 down to 0.04, columns x -0.70..0.70 step 0.05; value = hit y*10 (deeper = bigger), . = no hit')
for iz in range(20, 0, -1):
    z = iz * 0.04
    row = ''
    for ix in range(-14, 15):
        h = tree.ray_cast(Vector((ix * 0.05, -3, z)), Vector((0, 1, 0)), 6.0)[0]
        row += ' .. ' if h is None else '%+3.0f ' % (h.y * 10)
    print('D z=%.2f %s' % (z, row))
