"""Export SM_WolfDenCave.fbx and verify the written file next to the old den FBX.
Run: blender.exe -b wolfden_work.blend --factory-startup --python 13_export_verify.py
"""
import bpy, bmesh, os, sys, math
import numpy as np
import addon_utils
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0, 'E:/game-dev-team/assets')
import propcommon as PC

OUT = 'E:/game-dev-team/assets/wolfden_tripo/'
FBX = OUT + 'SM_WolfDenCave.fbx'
OLD = 'E:/ForGameLead(Materials)/demo-assets/SM_WolfDenCave.fbx'
ob = bpy.data.objects['SM_WolfDenCave']
me = ob.data
tex = bpy.data.images.load(OUT + 'T_WolfDenTripo_D.png')
mat = bpy.data.materials.new('M_WolfDenTripo'); mat.use_nodes = True
tn = mat.node_tree.nodes.new('ShaderNodeTexImage'); tn.image = tex
mat.node_tree.links.new(tn.outputs['Color'], mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.9
me.materials.clear(); me.materials.append(mat)
for p in me.polygons:
    p.material_index = 0; p.use_smooth = False
addon_utils.enable('io_scene_fbx')
PC.export_one(ob, FBX)
print('FILE %s %.1f KB' % (FBX, os.path.getsize(FBX) / 1024))
bpy.ops.wm.save_as_mainfile(filepath=OUT + '_work/wolfden_work.blend')


def load(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    addon_utils.enable('io_scene_fbx')
    bpy.ops.import_scene.fbx(filepath=path)
    bpy.context.view_layer.update()
    return [o for o in bpy.data.objects if o.type == 'MESH'], [o.type for o in bpy.data.objects]


def overlaps(me, layer, res=2048):
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
    return int((inner > 1).sum()), float(uv.min()), float(uv.max())


def stats(tag, o):
    me = o.data; mw = o.matrix_world
    cs = np.array([mw @ v.co for v in me.vertices])
    loc, rot, scl = mw.decompose()
    print('%s tris=%d verts=%d min=%s max=%s size=%s origin=%s rot=%s scale=%s' % (tag, sum(len(p.vertices) - 2 for p in me.polygons), len(me.vertices),
          cs.min(0).round(3), cs.max(0).round(3), (cs.max(0) - cs.min(0)).round(3), tuple(round(a, 4) for a in loc), tuple(round(a, 4) for a in rot.to_euler()), tuple(round(a, 4) for a in scl)))
    print('%s materials=%s uv=%s vertex_colours=%s smooth_faces=%d' % (tag, [m.name for m in me.materials if m], [u.name for u in me.uv_layers], [c.name for c in me.color_attributes], sum(1 for p in me.polygons if p.use_smooth)))
    bm = bmesh.new(); bm.from_mesh(me); bm.transform(mw)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    tree = BVHTree.FromBMesh(bm)
    # mouth side: in the x-range of the mouth, how far a ray at wolf height gets when shot from the front (-Y) and from the back (+Y),
    # compared with the rock face just beside the mouth
    if me.color_attributes:                               # old den: the mouth is the darkest loose block (vertex colours)
        seen = set(); bestp = None
        cl = bm.loops.layers.color.active or bm.loops.layers.float_color.active
        for v in bm.verts:
            if v in seen:
                continue
            st = [v]; seen.add(v); c = []
            while st:
                q = st.pop(); c.append(q)
                for e in q.link_edges:
                    w = e.other_vert(q)
                    if w not in seen:
                        seen.add(w); st.append(w)
            lum = np.mean([sum(l[cl][:3]) for q in c for l in q.link_loops])
            co = np.array([q.co for q in c])
            if bestp is None or lum < bestp[0]:
                bestp = (lum, co)
        x0, x1 = bestp[1][:, 0].min() + 0.1, bestp[1][:, 0].max() - 0.1
    else:                                                 # new den: mouth span measured by the builder
        pc = np.load(OUT + '_work/_pad.npy'); x0, x1 = pc[5] + 0.1, pc[6] - 0.1
    def reach(xa, xb, ydir):
        ys = []
        for i in range(9):
            h = tree.ray_cast(Vector((xa + (xb - xa) * i / 8, -8.0 * ydir, 0.5)), Vector((0, ydir, 0)), 30.0)[0]
            if h is not None:
                ys.append(h.y)
        return float(np.median(ys)) if ys else float('nan')
    w = x1 - x0
    print('%s mouth test at height 0.5 m, mouth span x %.2f..%.2f: a ray from -Y stops at y %.2f in the span and at y %.2f / %.2f beside it; a ray from +Y stops at y %.2f in the span (box y %.2f..%.2f)' % (
        tag, x0, x1, reach(x0, x1, 1), reach(x0 - w, x0 - 0.15, 1), reach(x1 + 0.15, x1 + w, 1), reach(x0, x1, -1), cs[:, 1].min(), cs[:, 1].max()))
    # holes: can a ray from above / from the four sides at low height pass through without hitting anything inside the footprint
    low = cs[cs[:, 2] < 0.05]
    print('%s open edges (welded) %d; lowest z %.3f; verts on the ground %d' % (tag, sum(1 for e in bm.edges if len(e.link_faces) == 1), cs[:, 2].min(), len(low)))
    bm.free()
    return cs


ms, types = load(OLD)
old = stats('OLD', ms[0])
ms, types = load(FBX)
print('NEW objects in file: %s' % types)
new = stats('NEW', ms[0])
m2 = ms[0].data
for layer in [u.name for u in m2.uv_layers]:
    ov, lo, hi = overlaps(m2, layer)
    print('NEW uv %s range %.4f..%.4f overlapping texels at 2048: %d' % (layer, lo, hi, ov))
imgs = [bpy.path.abspath(n.image.filepath) for m in m2.materials if m and m.node_tree for n in m.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image]
print('NEW texture in material: %s' % [os.path.basename(i) for i in imgs])
# see-through test from the game camera side and from the mouth: rays through the model must end on the model, not on the far ground
bm = bmesh.new(); bm.from_mesh(m2); bm.transform(ms[0].matrix_world); bmesh.ops.triangulate(bm, faces=bm.faces[:])
tree = BVHTree.FromBMesh(bm)
thru = tot = 0
for ix in range(-10, 11):
    for iz in range(1, 12):
        o_ = Vector((0.15 + ix * 0.05, -6.0, iz * 0.1))
        h = tree.ray_cast(o_, Vector((0, 1, 0)), 30.0)
        tot += 1
        if h[0] is None:
            thru += 1
print('NEW rays shot into the mouth area from the front (x -0.35..0.65, z 0.1..1.1): %d of %d pass through the model without hitting anything' % (thru, tot))
down = 0; n = 0
for ix in range(-20, 21):
    for iy in range(-14, 15):
        o_ = Vector((ix * 0.1, iy * 0.1, 10)); h = tree.ray_cast(o_, Vector((0, 0, -1)), 30.0)[0]
        if h is not None:
            n += 1
print('NEW rays from above that hit the model: %d (footprint cells of 10 cm)' % n)
bm.free()
t1 = bpy.data.images.load(OUT + 'T_WolfDenTripo_D.png'); t2 = bpy.data.images.load(OUT + 'T_WolfDenTripo_Mask.png')
print('TEXTURES colour %dx%d, mask %dx%d channels=%d' % (t1.size[0], t1.size[1], t2.size[0], t2.size[1], t2.channels))
tris = sum(len(p.vertices) - 2 for p in m2.polygons)
ok = (len(ms) == 1 and tris <= 1000 and len(m2.materials) == 1 and [u.name for u in m2.uv_layers] == ['UVMap', 'LightmapUV']
      and np.abs(new.min(0)[:2] - old.min(0)[:2]).max() < 2e-3 and np.abs(new.max(0)[:2] - old.max(0)[:2]).max() < 2e-3 and abs(new.min(0)[2]) < 1e-4
      and all(overlaps(m2, u.name)[0] == 0 for u in m2.uv_layers) and thru == 0 and t1.size[0] == 1024 and t2.size[0] == 1024)
print('ROUNDTRIP', 'PASS' if ok else 'FAIL')
