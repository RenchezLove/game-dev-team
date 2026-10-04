"""Export SM_Tent.fbx and verify the written file (re-import) next to the old tent FBX: triangles, bounds inside the old
footprint, origin, two UV sets without overlaps, where every face looks, textures.
Run: blender.exe -b tent_work.blend --factory-startup --python 13_export_verify.py
"""
import bpy, os, sys, math
import numpy as np
import addon_utils
sys.path.insert(0, 'E:/game-dev-team/assets')
import propcommon as PC

OUT = 'E:/game-dev-team/assets/tent_survival/'
FBX = OUT + 'SM_Tent.fbx'
OLD = 'E:/ForGameLead(Materials)/demo-assets/SM_Tent.fbx'
LIMIT = 116                                                   # triangles of the old SM_Tent
ob = bpy.data.objects['SM_Tent']
me = ob.data
# reference for the facing test: centre, part and group of every triangle of the work mesh (the FBX keeps no part numbers)
_T = len(me.polygons)
REF_C = np.zeros(_T * 3); me.polygons.foreach_get('center', REF_C); REF_C = REF_C.reshape(-1, 3)
REF_P = np.zeros(_T, np.int32); me.attributes['part'].data.foreach_get('value', REF_P)
REF_G = np.zeros(_T, np.int32); me.attributes['grp'].data.foreach_get('value', REF_G)
AX = np.load(OUT + '_work/_grp.npz')['AX']                    # pole axes: bottom xyz, top xyz per group
PN = {1: 'tarp', 2: 'tarp underside', 3: 'pole sides', 4: 'pole ends'}
tex = bpy.data.images.load(OUT + 'T_TentSurvival_D.png')
mat = me.materials[0]
tn = mat.node_tree.nodes.new('ShaderNodeTexImage'); tn.image = tex
mat.node_tree.links.new(tn.outputs['Color'], mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.9
addon_utils.enable('io_scene_fbx')
PC.export_one(ob, FBX)
print('FILE %s %.1f KB' % (FBX, os.path.getsize(FBX) / 1024))
bpy.ops.wm.save_as_mainfile(filepath=OUT + '_work/tent_work.blend')


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
    top = cs[cs[:, 2] > cs[:, 2].max() - 0.15]
    print('%s ridge (highest 15 cm): x %.2f..%.2f y %.2f..%.2f -> the long side runs along %s' % (tag, top[:, 0].min(), top[:, 0].max(), top[:, 1].min(), top[:, 1].max(),
          'Y' if np.ptp(top[:, 1]) > np.ptp(top[:, 0]) else 'X'))
    return cs


def facing(tag, o):
    """Unreal does not draw the back of a face: every face of the re-imported FBX must look where it is seen from.
    Tarp: up.  Underside of the tarp: down.  Pole sides: away from the axis of their pole.  Pole ends: away from the middle of their pole."""
    me = o.data; mw = o.matrix_world; n3 = mw.to_3x3()
    C = np.array([mw @ p.center for p in me.polygons]); N = np.array([(n3 @ p.normal).normalized() for p in me.polygons])
    d = np.linalg.norm(C[:, None, :] - REF_C[None, :, :], axis=2)
    part = REF_P[d.argmin(1)]; grp = REF_G[d.argmin(1)]
    print('%s facing: %d faces matched to the work mesh, worst centre distance %.6f m' % (tag, len(C), d.min(1).max()))
    bad_total = 0 if d.min(1).max() < 1e-3 else 10 ** 6
    a, b = AX[grp][:, :3], AX[grp][:, 3:]
    for p in sorted(set(part.tolist())):
        q = part == p; c, n = C[q], N[q]
        if p == 1:
            good = n[:, 2] > 0.05; rule = 'up'
        elif p == 2:
            good = n[:, 2] < -0.05; rule = 'down'
        elif p == 3:
            ax = b[q] - a[q]; t = ((c - a[q]) * ax).sum(1) / (ax * ax).sum(1)
            good = ((c - (a[q] + ax * t[:, None])) * n).sum(1) > 0; rule = 'away from the axis of the pole'
        else:
            good = ((c - (a[q] + b[q]) / 2) * n).sum(1) > 0; rule = 'away from the middle of the pole'
        bad = int((~good).sum()); bad_total += bad
        print('%s facing %-15s must look %-33s faces %3d wrong %3d' % (tag, PN[p], rule + ':', q.sum(), bad))
    print('%s facing TOTAL wrong %d of %d' % (tag, bad_total, len(C)))
    return bad_total


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
t1 = bpy.data.images.load(OUT + 'T_TentSurvival_D.png'); t2 = bpy.data.images.load(OUT + 'T_TentSurvival_Mask.png')
t2.alpha_mode = 'CHANNEL_PACKED'; t2.colorspace_settings.name = 'Non-Color'
K = np.array(t2.pixels[:], dtype=np.float32).reshape(t2.size[1], t2.size[0], t2.channels)
print('TEXTURES colour %dx%d, mask %dx%d channels=%d; mask texels set: R %d G %d B %d A %d, in two channels at once %d' % (t1.size[0], t1.size[1], t2.size[0], t2.size[1], t2.channels,
      *[int((K[..., i] > 0.5).sum()) for i in range(4)], int(((K > 0.5).sum(-1) > 1).sum())))
tris = sum(len(p.vertices) - 2 for p in m2.polygons)
inside = bool((new.min(0)[:2] >= old.min(0)[:2] - 1e-3).all() and (new.max(0)[:2] <= old.max(0)[:2] + 1e-3).all())
print('NEW footprint inside the old one: %s (new x %.3f..%.3f y %.3f..%.3f, old x %.3f..%.3f y %.3f..%.3f); triangles %d of at most %d' % (
    inside, new.min(0)[0], new.max(0)[0], new.min(0)[1], new.max(0)[1], old.min(0)[0], old.max(0)[0], old.min(0)[1], old.max(0)[1], tris, LIMIT))
ok = (len(ms) == 1 and tris <= LIMIT and len(m2.materials) == 1 and [u.name for u in m2.uv_layers] == ['UVMap', 'LightmapUV']
      and inside and abs(new.min(0)[2]) < 1e-4 and np.ptp(new[:, 1]) > np.ptp(new[:, 0])
      and wrong == 0 and sum(ovs) == 0 and t1.size[0] == 512 and t2.size[0] == 512 and t2.channels == 4
      and (K[..., 2] > 0.5).sum() == 0 and (K[..., 3] > 0.5).sum() == 0 and ((K > 0.5).sum(-1) > 1).sum() == 0)
print('ROUNDTRIP', 'PASS' if ok else 'FAIL')
