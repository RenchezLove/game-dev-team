"""Export SM_BanditShed.fbx and verify the written file next to the old shed FBX.
Run: blender.exe -b banditshed_work.blend --factory-startup --python 13_export_verify.py
"""
import bpy, bmesh, os, sys, math
import numpy as np
import addon_utils
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0, 'E:/game-dev-team/assets')
import propcommon as PC

OUT = 'E:/game-dev-team/assets/banditshed_tripo/'
FBX = OUT + 'SM_BanditShed.fbx'
OLD = 'E:/ForGameLead(Materials)/demo-assets/SM_BanditShed.fbx'
ob = bpy.data.objects['SM_BanditShed']
me = ob.data
tex = bpy.data.images.load(OUT + 'T_BanditShedTripo_D.png')
mat = me.materials[0]
tn = mat.node_tree.nodes.new('ShaderNodeTexImage'); tn.image = tex
mat.node_tree.links.new(tn.outputs['Color'], mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.9
# reference for the facing test: centre and part of every triangle of the work mesh (the FBX keeps no part numbers)
_T = len(me.polygons)
REF_C = np.zeros(_T * 3); me.polygons.foreach_get('center', REF_C); REF_C = REF_C.reshape(-1, 3)
REF_P = np.zeros(_T, np.int32); me.attributes['part'].data.foreach_get('value', REF_P)
PN = {1: 'walls', 2: 'gables', 3: 'doorway', 4: 'door', 5: 'step', 6: 'rag over the door', 7: 'window boards', 8: 'tin patches', 9: 'sheathing', 10: 'soffit',
      11: 'slate', 12: 'tin roof sheet', 13: 'ridge', 14: 'bottom', 15: 'roof rag'}
addon_utils.enable('io_scene_fbx')
PC.export_one(ob, FBX)
print('FILE %s %.1f KB' % (FBX, os.path.getsize(FBX) / 1024))
bpy.ops.wm.save_as_mainfile(filepath=OUT + '_work/banditshed_work.blend')


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
    bm = bmesh.new(); bm.from_mesh(me); bm.transform(mw); bmesh.ops.triangulate(bm, faces=bm.faces[:])
    tree = BVHTree.FromBMesh(bm)
    def stop(x, z, ydir):
        h = tree.ray_cast(Vector((x, -8.0 * ydir, z)), Vector((0, ydir, 0)), 30.0)[0]
        return float('nan') if h is None else h.y
    print('%s door test, rays along Y at height 1.3 m: in the door opening (x 0.43) a ray from -Y stops at y %.2f, beside the door (x -1.6 / 1.0) at y %.2f / %.2f; from +Y at x 0.43 it stops at y %.2f' % (
        tag, stop(0.43, 1.3, 1), stop(-1.6, 1.3, 1), stop(1.0, 1.3, 1), stop(0.43, 1.3, -1)))
    # ridge direction: the highest part of the roof
    top = cs[cs[:, 2] > cs[:, 2].max() - 0.35]
    print('%s roof top (highest 35 cm): x %.2f..%.2f y %.2f..%.2f' % (tag, top[:, 0].min(), top[:, 0].max(), top[:, 1].min(), top[:, 1].max()))
    # bottom of the walls: rays straight up from under the ground inside the wall line must hit a face at z 0
    hit = tot = 0
    for ix in range(-11, 12):
        for iy in range(-6, 7):
            tot += 1
            h = tree.ray_cast(Vector((ix * 0.2, iy * 0.2, -1.0)), Vector((0, 0, 1)), 5.0)[0]
            if h is not None and abs(h.z) < 1e-3:
                hit += 1
    print('%s bottom: %d of %d rays from below (x +-2.2, y +-1.2) meet a face at z 0' % (tag, hit, tot))
    bm.free()
    return cs


def facing(tag, o):
    """Unreal does not draw the back of a face: every face of the re-imported FBX must look where it is seen from.
    Roof sheets, ridge, roof rag, sheathing: up.  Soffit, bottom: down.  Walls, gables, tin patches: away from the middle
    of the shed along the wall normal.  Rag over the door, window boards: towards -Y (they hang on the front wall).
    Door, step (closed boxes): away from their own middle.  Doorway (a niche): towards its own middle."""
    me = o.data; mw = o.matrix_world; n3 = mw.to_3x3()
    C = np.array([mw @ p.center for p in me.polygons]); N = np.array([(n3 @ p.normal).normalized() for p in me.polygons])
    d = np.linalg.norm(C[:, None, :] - REF_C[None, :, :], axis=2)
    part = REF_P[d.argmin(1)]
    print('%s facing: %d faces matched to the work mesh, worst centre distance %.6f m' % (tag, len(C), d.min(1).max()))
    bad_total = 0 if d.min(1).max() < 1e-3 else 10 ** 6
    for p in sorted(set(part.tolist())):
        q = part == p; c, n = C[q], N[q]
        if p in (9, 11, 12, 13, 15):
            good = n[:, 2] > 0.05; rule = 'up'
        elif p in (10, 14):
            good = n[:, 2] < -0.05; rule = 'down'
        elif p in (1, 2, 8):
            ax = np.abs(n[:, :2]).argmax(1); i = np.arange(len(n))
            good = n[i, ax] * c[i, ax] > 0; rule = 'away from the middle of the shed'
        elif p in (6, 7):
            good = n[:, 1] < -0.05; rule = 'towards -Y'
        elif p in (4, 5):
            good = ((c - c.mean(0)) * n).sum(1) > 0; rule = 'away from the middle of the box'
        else:
            good = ((c.mean(0) - c) * n).sum(1) > 0; rule = 'into the niche'
        bad = int((~good).sum()); bad_total += bad
        extra = ''
        if p in (11, 12, 13, 15):
            fr = c[:, 1] < 0
            extra = ' | door slope (y < 0): %d of %d wrong, back slope: %d of %d wrong' % ((~good & fr).sum(), fr.sum(), (~good & ~fr).sum(), (~fr).sum())
        print('%s facing %-17s must look %-32s faces %3d wrong %3d%s' % (tag, PN[p], rule + ':', q.sum(), bad, extra))
    print('%s facing TOTAL wrong %d of %d' % (tag, bad_total, len(C)))
    return bad_total


if os.path.exists(FBX + '.before'):                          # the file as it was before this export (kept by hand for a before / after record)
    ms, types = load(FBX + '.before')
    facing('BEFORE', ms[0])
ms, types = load(OLD)
old = stats('OLD', ms[0])
ms, types = load(FBX)
print('NEW objects in file: %s' % types)
new = stats('NEW', ms[0])
m2 = ms[0].data
wrong = facing('NEW', ms[0])
ovs = []
for layer in [u.name for u in m2.uv_layers]:
    ov, lo, hi = overlaps(m2, layer); ovs.append(ov)
    print('NEW uv %s range %.4f..%.4f overlapping texels at 2048: %d' % (layer, lo, hi, ov))
print('NEW texture in material: %s' % [os.path.basename(bpy.path.abspath(n.image.filepath)) for m in m2.materials if m and m.node_tree for n in m.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image])
t1 = bpy.data.images.load(OUT + 'T_BanditShedTripo_D.png'); t2 = bpy.data.images.load(OUT + 'T_BanditShedTripo_Mask.png')
print('TEXTURES colour %dx%d, mask %dx%d channels=%d' % (t1.size[0], t1.size[1], t2.size[0], t2.size[1], t2.channels))
tris = sum(len(p.vertices) - 2 for p in m2.polygons)
ok = (len(ms) == 1 and tris <= 352 and len(m2.materials) == 1 and [u.name for u in m2.uv_layers] == ['UVMap', 'LightmapUV']
      and np.abs(new.min(0)[:2] - old.min(0)[:2]).max() < 2e-3 and np.abs(new.max(0)[:2] - old.max(0)[:2]).max() < 2e-3 and abs(new.min(0)[2]) < 1e-4
      and wrong == 0 and sum(ovs) == 0 and t1.size[0] == 1024 and t2.size[0] == 1024 and t2.channels == 4)
print('ROUNDTRIP', 'PASS' if ok else 'FAIL')
