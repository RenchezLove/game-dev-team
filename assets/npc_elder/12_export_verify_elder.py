"""Export the 3 elder FBX (mesh + 21-bone RootAnim) + round-trip verify.
Same checks as the wearables batches (06_export_verify_t2t3.py):
  - rest pose before export; colors_type='LINEAR'
  - bone count == 21, names identical to handoff SK_Cloth_L1_Torso.fbx
  - full 21-bone rest matrices match handoff (maxdelta)
  - tris / verts / vcol 'Col' / UV / unweighted verts
Run: blender.exe -b --factory-startup --python 12_export_verify_elder.py
"""
import bpy, sys, os
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W

HERE = 'E:/game-dev-team/assets/npc_elder/'
NAMES = ['SK_Elder_Head', 'SK_Elder_Torso', 'SK_Elder_Legs']

# ---- export ----
bpy.ops.wm.open_mainfile(filepath=HERE + '_work/elder_work.blend')
rig = bpy.data.objects['RootAnim']
for pb in rig.pose.bones:                      # rest pose before export
    pb.rotation_mode = 'XYZ'
    pb.rotation_euler = (0, 0, 0)
    pb.location = (0, 0, 0)
    pb.scale = (1, 1, 1)
for n in NAMES:
    ob = bpy.data.objects[n]
    path = HERE + n + '.fbx'
    W.export_skeletal(ob, rig, path)
    print('EXPORTED %s (%.1f KB)' % (path, os.path.getsize(path) / 1024))


def rig_snapshot(fbx_path):
    W.fresh()
    meshes, arms, rest = W.import_fbx(fbx_path)
    a = arms[0]
    for ob in meshes:
        W.bake_world(ob)
    W.apply_armature_transform(a)
    bones = {b.name: b.matrix_local.copy() for b in a.data.bones}
    info = []
    for ob in meshes:
        me = ob.data
        me.calc_loop_triangles()
        info.append({
            'tris': len(me.loop_triangles), 'verts': len(me.vertices),
            'vcol': [(c.name, c.domain, c.data_type) for c in me.color_attributes],
            'uv': [u.name for u in me.uv_layers],
            'unweighted': sum(1 for v in me.vertices if not v.groups),
            'vgroups': len(ob.vertex_groups),
            'zmin': min(v.co.z for v in me.vertices),
            'zmax': max(v.co.z for v in me.vertices),
        })
    return bones, info


ref_bones, _ = rig_snapshot(W.HANDOFF + 'SK_Cloth_L1_Torso.fbx')
print('\nREFERENCE bones=%d' % len(ref_bones))

ok_all = True
for n in NAMES:
    bones, info = rig_snapshot(HERE + n + '.fbx')
    same_names = sorted(bones) == sorted(ref_bones)
    maxd = 0.0
    if same_names:
        for bn in bones:
            d = max(abs(bones[bn][i][j] - ref_bones[bn][i][j])
                    for i in range(4) for j in range(4))
            maxd = max(maxd, d)
    i = info[0]
    ok = (same_names and maxd < 1e-3 and i['unweighted'] == 0 and i['vcol']
          and i['uv'])
    ok_all = ok_all and ok
    print('VERIFY %-20s bones=%d names_match=%s rest_maxdelta=%.5f tris=%d '
          'verts=%d vgroups=%d unweighted=%d vcol=%s uv=%s z=[%.3f..%.3f] -> %s' % (
              n, len(bones), same_names, maxd, i['tris'], i['verts'],
              i['vgroups'], i['unweighted'], i['vcol'], i['uv'],
              i['zmin'], i['zmax'], 'PASS' if ok else 'FAIL'))
print('\nROUNDTRIP %s' % ('ALL PASS' if ok_all else 'HAS FAILURES'))
