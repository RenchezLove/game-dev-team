"""Export the 3 hero slots (mesh + 21-bone RootAnim) + round-trip verify against
the current T0 FBX and the UE handoff skeleton (names + rest matrices).
Run: blender.exe -b --factory-startup --python 13_export_verify.py
"""
import bpy, sys, os
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W
from mathutils import Matrix
OUTDIR = 'E:/game-dev-team/assets/hero_tripo/'
NAMES = ['SK_Cloth_T0_Head', 'SK_Cloth_T0_Torso', 'SK_Cloth_T0_Legs']
bpy.ops.wm.open_mainfile(filepath=OUTDIR + '_work/hero_work.blend')
W.fresh.__globals__['addon_utils'].enable('io_scene_fbx')
rig = bpy.data.objects['RootAnim']
for pb in rig.pose.bones:
    pb.matrix_basis = Matrix.Identity(4)
for n in NAMES:
    p = OUTDIR + n + '.fbx'
    W.export_skeletal(bpy.data.objects[n], rig, p)
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
    mats = [m.name for m in me.materials if m]
    imgs = [n.image.filepath for m in me.materials if m and m.use_nodes
            for n in m.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image]
    zs = [v.co.z for v in me.vertices]
    return bones, dict(tris=len(me.loop_triangles), verts=len(me.vertices),
                       unweighted=sum(1 for v in me.vertices if not v.groups),
                       uv=[u.name for u in me.uv_layers], mats=mats, imgs=imgs,
                       z=(min(zs), max(zs)))


refs = {'handoff': snap(W.HANDOFF + 'SK_Cloth_L1_Torso.fbx')[0],
        'old_T0': snap('E:/game-dev-team/assets/armor_wearables/SK_Cloth_T0_Torso.fbx')[0]}
ok_all = True
total = 0
for n in NAMES:
    bones, i = snap(OUTDIR + n + '.fbx')
    total += i['tris']
    line = []
    ok = len(bones) == 21 and i['unweighted'] == 0 and i['uv'] and len(i['mats']) == 1
    for rn, rb in refs.items():
        same = sorted(bones) == sorted(rb)
        d = max(abs(bones[b][r][c] - rb[b][r][c]) for b in bones for r in range(4) for c in range(4)) if same else -1
        ok = ok and same and 0 <= d < 1e-3
        line.append('%s:names=%s rest_maxdelta=%.5f' % (rn, same, d))
    ok_all = ok_all and ok
    print('VERIFY %-18s bones=%d %s tris=%d verts=%d unweighted=%d uv=%s mats=%s tex=%s z=[%.3f..%.3f] -> %s' % (
        n, len(bones), ' '.join(line), i['tris'], i['verts'], i['unweighted'], i['uv'], i['mats'],
        i['imgs'], i['z'][0], i['z'][1], 'PASS' if ok else 'FAIL'))
    print('BONES', n, sorted(bones))
print('TOTAL tris %d' % total)
print('ROUNDTRIP %s' % ('ALL PASS' if ok_all else 'HAS FAILURES'))
