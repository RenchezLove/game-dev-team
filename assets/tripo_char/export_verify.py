"""Export the 3 slots of a Tripo character (mesh + 21-bone RootAnim) and verify the written FBX against the T0 hero FBX
(skeleton, sizes, cut rings, hands) and the UE handoff skeleton.
Run: blender.exe -b --factory-startup --python export_verify.py -- <id>
"""
import bpy, bmesh, sys, os, math
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0, 'E:/game-dev-team/assets/tripo_char')
import configs
C = configs.CFG[sys.argv[sys.argv.index('--') + 1]]
OUTDIR = C['outdir']
HERO = 'E:/game-dev-team/assets/hero_tripo/'
SL = ('Head', 'Torso', 'Legs')
bpy.ops.wm.open_mainfile(filepath=OUTDIR + '_work/' + C['id'] + '_work.blend')
W.fresh.__globals__['addon_utils'].enable('io_scene_fbx')
rig = bpy.data.objects['RootAnim']
for pb in rig.pose.bones:
    pb.matrix_basis = Matrix.Identity(4)
for s in SL:
    p = OUTDIR + C['prefix'] + '%s.fbx' % s
    W.export_skeletal(bpy.data.objects[C['prefix'] + s], rig, p)
    print('EXPORTED %s %.1f KB' % (p, os.path.getsize(p) / 1024))


def snap(path):
    W.fresh()
    meshes, arms, _ = W.import_fbx(path)
    a = arms[0]
    for ob in meshes:
        W.bake_world(ob)
    W.apply_armature_transform(a)
    bones = {b.name: b.matrix_local.copy() for b in a.data.bones}
    ob = meshes[0]; me = ob.data; me.calc_loop_triangles()
    gn = {g.index: g.name for g in ob.vertex_groups}
    co = [v.co.copy() for v in me.vertices]
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
    bnd = [v.co.copy() for v in bm.verts if any(len(e.link_faces) == 1 for e in v.link_edges)]
    tris = [[v.co.copy() for v in f.verts] for f in bm.faces]
    bm.free()
    return dict(bones=bones, n_obj=(len(meshes), len(arms)), tris=len(me.loop_triangles), verts=len(me.vertices),
                unweighted=sum(1 for v in me.vertices if not any(g.weight > 1e-4 for g in v.groups)),
                maxinf=max(sum(1 for g in v.groups if g.weight > 1e-4) for v in me.vertices),
                used=sorted({gn[g.group] for v in me.vertices for g in v.groups if g.weight > 1e-4}),
                uv=[u.name for u in me.uv_layers], mats=[m.name for m in me.materials if m],
                imgs=[bpy.path.abspath(n.image.filepath) for m in me.materials if m and m.node_tree
                      for n in m.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image],
                co=co, bnd=bnd, faces=tris, smooth=sum(1 for p in me.polygons if p.use_smooth))


def box(co):
    return tuple((min(c[i] for c in co), max(c[i] for c in co)) for i in range(3))


handoff = snap(W.HANDOFF + 'SK_Cloth_L1_Torso.fbx')['bones']
T0 = {s: snap(HERO + 'SK_Cloth_T0_%s.fbx' % s) for s in SL}
T1 = {s: snap(OUTDIR + C['prefix'] + '%s.fbx' % s) for s in SL}
bm = bmesh.new()
for s in SL:
    for f in T0[s]['faces']:
        bm.faces.new([bm.verts.new(c) for c in f])
t0tree = BVHTree.FromBMesh(bm); bm.free()

ok_all = True
for s in SL:
    a, b = T1[s], T0[s]
    names = sorted(a['bones']) == sorted(b['bones']) == sorted(handoff)
    d0 = max(abs(a['bones'][k][r][c] - b['bones'][k][r][c]) for k in a['bones'] for r in range(4) for c in range(4)) if names else -1
    dh = max(abs(a['bones'][k][r][c] - handoff[k][r][c]) for k in a['bones'] for r in range(4) for c in range(4)) if names else -1
    ok = (names and d0 < 1e-3 and dh < 1e-3 and len(a['bones']) == 21 and a['unweighted'] == 0 and a['maxinf'] <= 4
          and a['uv'] == ['UVMap'] and len(a['mats']) == 1 and a['n_obj'] == (1, 1) and a['smooth'] == 0)
    ok_all = ok_all and ok
    print('VERIFY %-5s objects(mesh,armature)=%s bones=%d names_equal_T0_and_handoff=%s rest_delta_vs_T0=%.5f vs_handoff=%.5f tris=%d (T0 %d) verts=%d unweighted=%d max_influences=%d uv=%s mats=%s tex=%s -> %s' % (
        s, a['n_obj'], len(a['bones']), names, d0, dh, a['tris'], b['tris'], a['verts'], a['unweighted'], a['maxinf'], a['uv'], a['mats'],
        [os.path.basename(i) for i in a['imgs']], 'PASS' if ok else 'FAIL'))
    print('  skin bones used: %s' % a['used'])
    ba, bb = box(a['co']), box(b['co'])
    print('  SIZE T1 x[%.3f..%.3f] y[%.3f..%.3f] z[%.3f..%.3f] | T0 x[%.3f..%.3f] y[%.3f..%.3f] z[%.3f..%.3f]' % (
        *ba[0], *ba[1], *ba[2], *bb[0], *bb[1], *bb[2]))
    for tag, part in (('T1', a), ('T0', b)):
        lv = {}
        for c in part['bnd']:
            lv.setdefault(round(c.z, 3), []).append(c)
        for z, cs in sorted(lv.items()):
            if len(cs) < 6:
                continue
            ds = [(t0tree.find_nearest(c)[0] - c).length for c in cs]
            rs = [math.hypot(c.x, c.y) for c in cs]
            print('  CUT %s %s open edge at z=%.3f: %d verts, radius %.3f..%.3f, distance to the T0 surface max %.4f mean %.4f m' % (
                tag, s, z, len(cs), min(rs), max(rs), max(ds), sum(ds) / len(ds)))
print('BONES', sorted(T1['Torso']['bones']))
print('TOTAL tris T1 %d | T0 %d' % (sum(T1[s]['tris'] for s in SL), sum(T0[s]['tris'] for s in SL)))
for tag, P in (('T1', T1), ('T0', T0)):
    co = [c for s in SL for c in P[s]['co']]
    b = box(co)
    print('WHOLE %s height %.3f (z %.3f..%.3f) span x %.3f..%.3f depth y %.3f..%.3f' % (tag, b[2][1] - b[2][0], *b[2], *b[0], *b[1]))
for tag, part in (('T1', T1['Torso']), ('T0', T0['Torso'])):
    for side, sg in (('left', 1), ('right', -1)):
        h = [c for c in part['co'] if c.x * sg > 0.898]            # beyond the wrist joint (L_Hand head x 0.898)
        print('HAND %s %s: tip |x|=%.3f, length past the wrist joint %.3f, thickness z %.3f, width y %.3f' % (
            tag, side, max(abs(c.x) for c in h), max(abs(c.x) for c in h) - 0.898, max(c.z for c in h) - min(c.z for c in h), max(c.y for c in h) - min(c.y for c in h)))
print('SLOTS T1 head lowest z %.3f, legs highest z %.3f, torso z %.3f..%.3f' % (min(c.z for c in T1['Head']['co']), max(c.z for c in T1['Legs']['co']),
      min(c.z for c in T1['Torso']['co']), max(c.z for c in T1['Torso']['co'])))
for tag, part in (('T1', T1['Legs']), ('T0', T0['Legs'])):
    top = [c for c in part['co'] if c.z > 0.87]
    print('LEGS %s above z 0.87: max |x| %.3f, max radius %.3f' % (tag, max(abs(c.x) for c in top), max(math.hypot(c.x, c.y) for c in top)))
tex = bpy.data.images.load(OUTDIR + C['tex'])
print('TEXTURE %s %dx%d channels=%d %.1f KB' % (tex.filepath, tex.size[0], tex.size[1], tex.channels, os.path.getsize(OUTDIR + C['tex']) / 1024))
tot = sum(T1[s]['tris'] for s in SL)
print('ROUNDTRIP %s' % ('ALL PASS' if ok_all and 1400 <= tot <= 1600 and tex.size[0] <= 1024 else 'HAS FAILURES'))
