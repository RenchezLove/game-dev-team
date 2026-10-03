"""Export SK_Wolf.fbx (mesh + WolfRig, same exporter settings as the old wolf) and verify the written
file against the old SK_Wolf.fbx and the four animation FBX: bones, hierarchy, rest pose, sizes.
Run: blender.exe -b --factory-startup --python 13_export_verify.py
"""
import bpy, os, math
import addon_utils
from mathutils import Matrix

OUT = 'E:/game-dev-team/assets/wolf_tripo/'
FBX = OUT + 'SK_Wolf.fbx'
OLD = 'E:/game-dev-team/assets/wolf_recolor/SK_Wolf.fbx'
ANIMS = {'Idle': 'E:/ForGameLead(Materials)/phase3-assets/Anim_Wolf_Idle.fbx', 'Run': 'E:/ForGameLead(Materials)/phase3-assets/Anim_Wolf_Run.fbx',
         'Bite': 'E:/ForGameLead(Materials)/phase3-assets/Anim_Wolf_Bite.fbx', 'Death': 'E:/game-dev-team/assets/anim_wolf/Anim_Wolf_Death.fbx'}
bpy.ops.wm.open_mainfile(filepath=OUT + '_work/wolf_work.blend')
addon_utils.enable('io_scene_fbx')
from io_scene_fbx import parse_fbx
rig = bpy.data.objects['WolfRig']; wolf = bpy.data.objects['SK_Wolf']
rig.animation_data.action = None
for tr in list(rig.animation_data.nla_tracks):
    rig.animation_data.nla_tracks.remove(tr)
for pb in rig.pose.bones:
    pb.matrix_basis = Matrix.Identity(4)
bpy.ops.object.select_all(action='DESELECT')
wolf.select_set(True); rig.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.export_scene.fbx(filepath=FBX, use_selection=True, object_types={'MESH', 'ARMATURE'}, mesh_smooth_type='FACE',
                         add_leaf_bones=False, bake_anim=False, use_mesh_modifiers=True, path_mode='AUTO')
print('EXPORTED %s %.1f KB' % (FBX, os.path.getsize(FBX) / 1024))


def settings(path):
    root, ver = parse_fbx.parse(path)
    out = {'version': ver}
    for ch in root.elems:
        if ch.id == b'GlobalSettings':
            for sub in ch.elems:
                if sub.id == b'Properties70':
                    for p in sub.elems:
                        if p.props[0] in (b'UpAxis', b'FrontAxis', b'CoordAxis', b'UnitScaleFactor'):
                            out[p.props[0].decode()] = p.props[-1]
    return out


def snap(path, static=True):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    addon_utils.enable('io_scene_fbx')
    bpy.ops.import_scene.fbx(filepath=path)
    bpy.context.view_layer.update()
    arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
    ms = [o for o in bpy.data.objects if o.type == 'MESH']
    aw = arm.matrix_world
    bones = {b.name: (aw @ b.matrix_local, b.parent.name if b.parent else None, (aw @ b.head_local.to_4d()).to_3d(), (aw @ b.tail_local.to_4d()).to_3d()) for b in arm.data.bones}
    d = dict(arm=arm.name, bones=bones, order=[b.name for b in arm.data.bones], nmesh=len(ms), meshname=[m.name for m in ms])
    if ms:
        ob = ms[0]; me = ob.data; me.calc_loop_triangles()
        co = [ob.matrix_world @ v.co for v in me.vertices]
        gn = {g.index: g.name for g in ob.vertex_groups}
        d.update(tris=len(me.loop_triangles), verts=len(me.vertices), co=co,
                 unweighted=sum(1 for v in me.vertices if not any(g.weight > 1e-4 for g in v.groups)),
                 maxinf=max(sum(1 for g in v.groups if g.weight > 1e-4) for v in me.vertices),
                 used=sorted({gn[g.group] for v in me.vertices for g in v.groups if g.weight > 1e-4}),
                 uv=[u.name for u in me.uv_layers], mats=[m.name for m in me.materials if m], cols=[c.name for c in me.color_attributes],
                 imgs=[os.path.basename(bpy.path.abspath(n.image.filepath)) for m in me.materials if m and m.node_tree for n in m.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image],
                 smooth=sum(1 for p in me.polygons if p.use_smooth),
                 scale=tuple(round(a, 4) for a in ob.matrix_world.to_scale()))
    return d


def box(co):
    return ' '.join('%s %.3f..%.3f' % (n, min(c[i] for c in co), max(c[i] for c in co)) for i, n in enumerate('xyz'))


print('SETTINGS new %s' % settings(FBX))
print('SETTINGS old %s' % settings(OLD))
new = snap(FBX); old = snap(OLD)
print('NEW armature=%s meshes=%d %s tris=%d verts=%d unweighted=%d max_influences=%d uv=%s mats=%s vertex_colours=%s tex=%s smooth_faces=%d mesh_scale=%s' % (
    new['arm'], new['nmesh'], new['meshname'], new['tris'], new['verts'], new['unweighted'], new['maxinf'], new['uv'], new['mats'], new['cols'], new['imgs'], new['smooth'], new['scale']))
print('OLD armature=%s meshes=%d %s tris=%d verts=%d uv=%s mats=%s vertex_colours=%s' % (old['arm'], old['nmesh'], old['meshname'], old['tris'], old['verts'], old['uv'], old['mats'], old['cols']))
print('SIZE new %s' % box(new['co']))
print('SIZE old %s' % box(old['co']))
print('SKIN new mesh uses bones: %s (%d of %d)' % (new['used'], len(new['used']), len(new['bones'])))


def compare(tag, a, b):
    same_names = sorted(a['bones']) == sorted(b['bones'])
    same_order = a['order'] == b['order']
    par = same_names and all(a['bones'][k][1] == b['bones'][k][1] for k in a['bones'])
    dm = max(abs(a['bones'][k][0][r][c] - b['bones'][k][0][r][c]) for k in a['bones'] for r in range(4) for c in range(4)) if same_names else -1
    dh = max(max((a['bones'][k][2] - b['bones'][k][2]).length, (a['bones'][k][3] - b['bones'][k][3]).length) for k in a['bones']) if same_names else -1
    ok = same_names and same_order and par and 0 <= dm < 1e-4 and dh < 1e-4
    print('SKELETON new vs %-10s bones %d/%d names_equal=%s order_equal=%s parents_equal=%s rest_matrix_max_delta=%.6f joint_position_max_delta=%.6f m -> %s' % (
        tag, len(a['bones']), len(b['bones']), same_names, same_order, par, dm, dh, 'PASS' if ok else 'FAIL'))
    return ok


ok = compare('old SK', new, old)
for tag, p in ANIMS.items():
    a = snap(p)
    # animation files are imported at their first frame; rest data of the bones is still the bind pose
    ok = compare('Anim ' + tag, new, a) and ok
print('BONES', new['order'])
tex = bpy.data.images.load(OUT + 'T_WolfTripo_D.png')
print('TEXTURE %dx%d channels=%d %.1f KB' % (tex.size[0], tex.size[1], tex.channels, os.path.getsize(OUT + 'T_WolfTripo_D.png') / 1024))
ok = (ok and new['nmesh'] == 1 and new['meshname'] == ['SK_Wolf'] and new['arm'] == old['arm'] and new['tris'] <= 1000 and new['unweighted'] == 0 and new['maxinf'] <= 4
      and len(new['mats']) == 1 and new['uv'] == ['UVMap'] and tex.size[0] <= 1024 and settings(FBX) == settings(OLD))
print('ROUNDTRIP %s' % ('ALL PASS' if ok else 'HAS FAILURES'))
