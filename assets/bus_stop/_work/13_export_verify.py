"""Export SM_BusStop.fbx, SM_BusStopSign.fbx, SM_BusStopUrn.fbx (each with its origin at 0 and its UCX blocks) and verify the
written files by re-import: triangles (sum <= 800), bounds, origin, where every face looks, two UV sets without overlaps (and the
shared UVMap of the three files together), collision blocks (present, closed, convex), how deep the hero gets under the roof, textures.
Run: blender.exe -b busstop_work.blend --factory-startup --python 13_export_verify.py
"""
import bpy, bmesh, os, math
import numpy as np
import addon_utils

OUT = 'E:/game-dev-team/assets/bus_stop/'
NAMES = ['SM_BusStop', 'SM_BusStopSign', 'SM_BusStopUrn']
EXPECT_UCX = {'SM_BusStop': 3, 'SM_BusStopSign': 0, 'SM_BusStopUrn': 1}
LIMIT = 800
HERO_R = 0.40
PN = {1: 'roof', 2: 'roof underside', 3: 'roof edge', 4: 'back wall', 5: 'side walls', 6: 'posts', 7: 'beams', 8: 'rafters', 9: 'rails', 10: 'bench', 11: 'bench leg',
      12: 'timetable', 13: 'timetable back', 14: 'notices', 20: 'sign pole', 21: 'sign face', 22: 'sign back', 23: 'sign clamps', 30: 'urn outside', 31: 'urn inside', 32: 'urn rim', 33: 'urn bottom'}
tex = bpy.data.images.load(OUT + 'T_BusStop_D.png')
mat = bpy.data.materials['M_BusStop']
tn = mat.node_tree.nodes.new('ShaderNodeTexImage'); tn.image = tex
mat.node_tree.links.new(tn.outputs['Color'], mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.9
addon_utils.enable('io_scene_fbx')
REF = {}
PLACE = {}
for name in NAMES:
    ob = bpy.data.objects[name]; me = ob.data; T = len(me.polygons)
    # reference for the facing test: centre, part and the direction every triangle has to look (set by the builder from the shape, not from the winding)
    C = np.zeros(T * 3); me.polygons.foreach_get('center', C)
    Pp = np.zeros(T, np.int32); me.attributes['part'].data.foreach_get('value', Pp)
    Wn = np.zeros((T, 3))
    for i, a in enumerate(('wx', 'wy', 'wz')):
        t = np.zeros(T, np.float32); me.attributes[a].data.foreach_get('value', t); Wn[:, i] = t
    REF[name] = (C.reshape(-1, 3), Pp, Wn)
    group = [ob] + sorted([o for o in bpy.data.objects if o.name.startswith('UCX_%s_' % name)], key=lambda o: o.name)
    PLACE[name] = tuple(round(a, 3) for a in ob.location)
    keep = [o.location.copy() for o in group]
    bpy.ops.object.select_all(action='DESELECT')
    for o in group:
        o.location = (0, 0, 0); o.hide_render = False; o.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.export_scene.fbx(filepath=OUT + name + '.fbx', use_selection=True, object_types={'MESH'}, mesh_smooth_type='FACE', use_mesh_modifiers=True,
                             add_leaf_bones=False, bake_anim=False, path_mode='AUTO', colors_type='LINEAR')
    for o, l in zip(group, keep):
        o.location = l
    print('FILE %s.fbx %.1f KB, objects written: %s' % (name, os.path.getsize(OUT + name + '.fbx') / 1024, [o.name for o in group]))


def uvtris(me, layer):
    a = np.zeros(len(me.loops) * 2); me.uv_layers[layer].data.foreach_get('uv', a)
    return a.reshape(len(me.polygons), 3, 2)
def overlaps(uv, res=2048):
    inner = np.zeros((res, res), np.int16)
    for t in range(len(uv)):
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


def facing(tag, o, ref):
    """Unreal does not draw the back of a face: every face of the re-imported FBX must look where the builder meant it to
    (roof up, its underside down, block faces away from the middle of their block, plates and pictures at the viewer, urn inside inwards)."""
    RC, RP, RW = ref
    me = o.data; mw = o.matrix_world; n3 = mw.to_3x3()
    C = np.array([mw @ p.center for p in me.polygons]); N = np.array([(n3 @ p.normal).normalized() for p in me.polygons])
    d = np.linalg.norm(C[:, None, :] - RC[None, :, :], axis=2)
    j = d.argmin(1); part = RP[j]; dot = (N * RW[j]).sum(1)
    print('%s facing: %d faces matched to the work mesh, worst centre distance %.6f m' % (tag, len(C), d.min(1).max()))
    bad_total = 0 if d.min(1).max() < 1e-3 else 10 ** 6
    for p in sorted(set(part.tolist())):
        q = part == p; bad = int((dot[q] < 0.1).sum()); bad_total += bad
        up, dn = int((N[q][:, 2] > 0.5).sum()), int((N[q][:, 2] < -0.5).sum())
        print('%s facing %-15s faces %3d wrong %3d (of them look up %d, down %d, sideways %d)' % (tag, PN[p], q.sum(), bad, up, dn, q.sum() - up - dn))
    print('%s facing TOTAL wrong %d of %d' % (tag, bad_total, len(C)))
    return bad_total


def block(tag, o):
    """A collision block has to be closed and convex."""
    bm = bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); bm.normal_update()
    closed = all(len(e.link_faces) == 2 for e in bm.edges)
    vol = bm.calc_volume(signed=True)
    worst = max(max(f.normal.dot(v.co - f.verts[0].co) for v in bm.verts) for f in bm.faces)
    c = np.array([v.co[:] for v in bm.verts]); bm.free()
    ok = closed and vol > 0 and worst < 1e-4
    print('%s block %-22s min %s max %s closed %s convex %s volume %+.3f -> %s' % (tag, o.name, c.min(0).round(3), c.max(0).round(3), closed, worst < 1e-4, vol, 'ok' if ok else 'BAD'))
    return ok, c


ok_all = True; total = 0; shared = []
for name in NAMES:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    addon_utils.enable('io_scene_fbx')
    bpy.ops.import_scene.fbx(filepath=OUT + name + '.fbx')
    bpy.context.view_layer.update()
    tag = name
    print('%s objects in file: %s' % (tag, sorted((o.name, o.type) for o in bpy.data.objects)))
    main = [o for o in bpy.data.objects if o.type == 'MESH' and o.name == name]
    ucx = sorted([o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith('UCX_%s_' % name)], key=lambda o: o.name)
    o = main[0]; me = o.data; mw = o.matrix_world
    cs = np.array([mw @ v.co for v in me.vertices])
    loc, rot, scl = mw.decompose()
    tris = sum(len(p.vertices) - 2 for p in me.polygons); total += tris
    print('%s tris=%d verts=%d min=%s max=%s size=%s origin=%s rot=%s scale=%s' % (tag, tris, len(me.vertices), cs.min(0).round(3), cs.max(0).round(3), (cs.max(0) - cs.min(0)).round(3),
          tuple(round(a, 4) for a in loc), tuple(round(a, 4) for a in rot.to_euler()), tuple(round(a, 4) for a in scl)))
    print('%s materials=%s uv=%s smooth_faces=%d place by the shelter (Blender axes, m)=%s' % (tag, [m.name for m in me.materials if m], [u.name for u in me.uv_layers], sum(1 for p in me.polygons if p.use_smooth), PLACE[name]))
    wrong = facing(tag, o, REF[name])
    ovs = []
    for layer in [u.name for u in me.uv_layers]:
        uv = uvtris(me, layer); ov = overlaps(uv); ovs.append(ov)
        print('%s uv %s range %.4f..%.4f overlapping texels at 2048: %d' % (tag, layer, uv.min(), uv.max(), ov))
    shared.append(uvtris(me, 'UVMap'))
    bl = [block(tag, u) for u in ucx]
    print('%s collision blocks: %d (expected %d)' % (tag, len(ucx), EXPECT_UCX[name]))
    if name == 'SM_BusStop':
        roof_front = cs[:, 1].min(); stop = min(c[:, 1].min() for okb, c in bl if c[:, 0].min() < -1 and c[:, 0].max() > 1)
        bench = REF[name][0][REF[name][1] == 10][:, 1].min()
        free = stop - roof_front
        print('%s open side looks -Y: roof edge at y %.3f, the wide block stops the hero at y %.3f -> free strip under the roof %.2f m; a capsule of radius %.2f keeps its centre at y <= %.3f (%s the roof edge)' % (
            tag, roof_front, stop, free, HERO_R, stop - HERO_R, 'outside' if stop - HERO_R <= roof_front + 1e-6 else 'INSIDE'))
        sidex = max(c[:, 0].max() for okb, c in bl); wallx = cs[cs[:, 2] < 0.5][:, 0].max()
        print('%s blocks reach x +-%.3f, walls and posts reach x +-%.3f; back of the blocks y %.3f, back of the walls and posts y %.3f' % (tag, sidex, wallx, max(c[:, 1].max() for okb, c in bl), cs[cs[:, 2] < 2.0][:, 1].max()))
        ok_all &= free <= 0.40 + 1e-6 and abs(cs[:, 0].min() + cs[:, 0].max()) < 2e-3 and abs(cs[:, 1].min() + cs[:, 1].max()) < 2e-3
    ok = (len(main) == 1 and len(me.materials) == 1 and [u.name for u in me.uv_layers] == ['UVMap', 'LightmapUV'] and abs(cs[:, 2].min()) < 1e-4
          and max(abs(a) for a in loc) < 1e-5 and wrong == 0 and sum(ovs) == 0 and len(ucx) == EXPECT_UCX[name] and all(b[0] for b in bl))
    print('%s file check: %s' % (tag, 'ok' if ok else 'FAILED'))
    ok_all &= ok
sh = overlaps(np.concatenate(shared))
print('ALL shared UVMap of the three files together: overlapping texels at 2048: %d' % sh)
t1 = bpy.data.images.load(OUT + 'T_BusStop_D.png'); t2 = bpy.data.images.load(OUT + 'T_BusStop_Mask.png')
t2.alpha_mode = 'CHANNEL_PACKED'; t2.colorspace_settings.name = 'Non-Color'
K = np.array(t2.pixels[:], dtype=np.float32).reshape(t2.size[1], t2.size[0], t2.channels)
print('TEXTURES colour %dx%d, mask %dx%d channels=%d; mask texels set: R %d G %d B %d A %d, in two channels at once %d' % (t1.size[0], t1.size[1], t2.size[0], t2.size[1], t2.channels,
      *[int((K[..., i] > 0.5).sum()) for i in range(4)], int(((K > 0.5).sum(-1) > 1).sum())))
print('ALL triangles of the three files: %d of at most %d' % (total, LIMIT))
ok_all &= total <= LIMIT and sh == 0 and t1.size[0] == 1024 and t2.size[0] == 1024 and t2.channels == 4 and ((K > 0.5).sum(-1) > 1).sum() == 0
print('ROUNDTRIP', 'PASS' if ok_all else 'FAIL')
