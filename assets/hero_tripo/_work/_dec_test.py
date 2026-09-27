import bpy, bmesh, sys, math
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables'); sys.path.insert(0, 'E:/game-dev-team/assets/hero_tripo/_work')
import wcommon as W, hcommon as H
from mathutils import Matrix
OUT = 'E:/game-dev-team/assets/hero_tripo/_work/_look/'
def load():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=H.GLB)
    ob = [o for o in bpy.context.selected_objects if o.type == 'MESH'][0]
    bpy.context.view_layer.update()
    ob.data.transform(Matrix.Rotation(math.radians(-90), 4, 'Z') @ ob.matrix_world); ob.matrix_world = Matrix.Identity(4)
    bm = bmesh.new(); bm.from_mesh(ob.data); bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4); bm.to_mesh(ob.data); bm.free()
    return ob
def seam_verts(ob):
    bm = bmesh.new(); bm.from_mesh(ob.data); uv = bm.loops.layers.uv.active; s = set()
    for e in bm.edges:
        if len(e.link_loops) != 2: s.update(v.index for v in e.verts); continue
        l1, l2 = e.link_loops
        a1, b1 = l1[uv].uv, l1.link_loop_next[uv].uv
        a2, b2 = l2.link_loop_next[uv].uv, l2[uv].uv
        if (a1 - a2).length > 1e-4 or (b1 - b2).length > 1e-4: s.update(v.index for v in e.verts)
    bm.free(); return s
for tag, mode in (('plain', None), ('vg', False), ('vginv', True)):
    ob = load()
    md = ob.modifiers.new('D', 'DECIMATE'); md.ratio = 800 / 2549; md.use_collapse_triangulate = True
    if mode is not None:
        s = seam_verts(ob); vg = ob.vertex_groups.new(name='seam')
        vg.add(list(s), 1.0, 'REPLACE'); md.vertex_group = 'seam'; md.invert_vertex_group = mode; md.vertex_group_factor = 10.0
        print('SEAMVERTS', len(s), 'of', len(ob.data.vertices))
    bpy.context.view_layer.objects.active = ob; bpy.ops.object.modifier_apply(modifier='D')
    print('DEC', tag, W.tri_count(ob))
    sc, cam, suns = W.setup_render(600)
    W.frame_and_shoot([ob], (0, -1, 0.1), OUT + 'dec_%s.png' % tag, suns=suns)
