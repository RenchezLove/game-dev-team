"""Shared helpers for armor/wearables batch (T0+T1).
Pipeline: import UE-handoff FBX (cm scale artifacts) -> normalize to meters,
single 21-bone RootAnim rig (from SK_Cloth_L1, T-pose bind), author geometry
in meters, vertex colors written as RAW sRGB bytes (matches existing L1/bandit
content: stored byte == palette hex), export FBX MESH+ARMATURE (FACE smoothing).
"""
import bpy, bmesh, math, os, addon_utils
from mathutils import Vector, Matrix, kdtree

HANDOFF = 'E:/game-dev-team/assets/_handoff/humanoid-export/'
WORKDIR = 'E:/game-dev-team/assets/armor_wearables/'

BASE_BONES_21 = [
    'C_Root', 'C_Spine01', 'L_UpperArm', 'L_Shoulder', 'L_Arm', 'L_Hand',
    'R_UpperArm', 'R_Arm', 'Pelvis_009_R_002', 'R_Hand', 'C_Spine02',
    'C_Head', 'C_Neck', 'L_Pelvis', 'L_Thigh', 'L_Claf', 'L_Foot',
    'R_Pelvis', 'R_Thigh', 'R_Claf', 'R_Foot']


def fresh():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    addon_utils.enable('io_scene_fbx')


def import_fbx(path):
    """Import one FBX, return (meshes, armatures) of the newly added objects."""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    return ([o for o in new if o.type == 'MESH'],
            [o for o in new if o.type == 'ARMATURE'],
            [o for o in new if o.type not in ('MESH', 'ARMATURE')])


def bake_world(ob):
    """Bake world transform into mesh data; object ends at identity, no parent."""
    bpy.context.view_layer.update()          # avoid stale matrix_world
    mw = ob.matrix_world.copy()
    ob.data.transform(mw)
    ob.parent = None
    ob.matrix_basis = Matrix.Identity(4)
    ob.matrix_parent_inverse = Matrix.Identity(4)
    ob.data.update()


def apply_armature_transform(arm):
    """Bake the FULL WORLD transform into bone data and detach the armature.
    (ops.transform_apply bakes only the local basis; the FBX import parents
    the armature under a 0.01-scale empty, so deleting the empty afterwards
    left bones x100 — invisible at rest, meshes explode on any pose.)"""
    if arm.animation_data:
        arm.animation_data.action = None
    bpy.context.view_layer.update()
    M = arm.matrix_world.copy()
    bpy.ops.object.select_all(action='DESELECT')
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')
    for eb in arm.data.edit_bones:
        eb.transform(M)
    bpy.ops.object.mode_set(mode='OBJECT')
    arm.parent = None
    arm.matrix_basis = Matrix.Identity(4)
    arm.matrix_parent_inverse = Matrix.Identity(4)
    bpy.context.view_layer.update()
    zref = arm.data.bones.get('C_Neck')
    if zref:
        print('  armature %s applied: C_Neck local z=%.3f (expect ~1.461)' % (
            arm.name, zref.matrix_local.translation.z))


def rebind(ob, rig):
    """Point mesh armature modifier + parent at rig (bind = rig rest pose).
    Explicit identity matrices — no matrix_world setter magic (a stale parent
    transform once smuggled a x100 basis onto the torso)."""
    ob.parent = rig
    ob.matrix_parent_inverse = Matrix.Identity(4)
    ob.matrix_basis = Matrix.Identity(4)
    mods = [m for m in ob.modifiers if m.type == 'ARMATURE']
    if not mods:
        mods = [ob.modifiers.new('Armature', 'ARMATURE')]
    for m in mods:
        m.object = rig


def assert_identity(ob):
    bpy.context.view_layer.update()
    _, _, sc = ob.matrix_world.decompose()
    ok = max(abs(sc.x - 1), abs(sc.y - 1), abs(sc.z - 1)) < 1e-4
    print('XFORM %-22s world_scale=(%.3f,%.3f,%.3f) %s' % (
        ob.name, sc.x, sc.y, sc.z, 'OK' if ok else '!!! NOT IDENTITY'))
    return ok


def hexv(hx):
    """'#RRGGBB' -> (r,g,b,1.0) raw 0..1 (written as-is into BYTE_COLOR)."""
    hx = hx.lstrip('#')
    return (int(hx[0:2], 16) / 255.0, int(hx[2:4], 16) / 255.0,
            int(hx[4:6], 16) / 255.0, 1.0)


def ensure_col(me):
    """Single CORNER/BYTE_COLOR attribute named 'Col' (rename import leftovers)."""
    keep = None
    for ca in list(me.color_attributes):
        if keep is None and ca.domain == 'CORNER' and ca.data_type == 'BYTE_COLOR':
            keep = ca
        elif ca.name != 'Col':
            me.color_attributes.remove(ca)
    if keep is None:
        keep = me.color_attributes.new('Col', 'BYTE_COLOR', 'CORNER')
    keep.name = 'Col'
    return keep


def paint_by_rule(ob, rule, default=None):
    """rule(face_center Vector, poly, me) -> '#hex' or None (keep current).
    Writes raw sRGB via color_srgb. default: hex for None results."""
    me = ob.data
    ca = ensure_col(me)
    for p in me.polygons:
        hx = rule(Vector(p.center), p, me)
        if hx is None:
            hx = default
        if hx is None:
            continue
        c = hexv(hx)
        for li in p.loop_indices:
            ca.data[li].color_srgb = c
    me.update()


def read_zone_hex(me, li):
    ca = me.color_attributes['Col'] if 'Col' in me.color_attributes else me.color_attributes[0]
    c = ca.data[li].color_srgb
    return '#%02X%02X%02X' % (round(c[0] * 255), round(c[1] * 255), round(c[2] * 255))


def transfer_weights(ob, src_obs, only_new_from=0):
    """Weights for verts >= only_new_from copied from nearest vert of src_obs
    (KDTree over all source verts, world space; both at identity so local ok)."""
    entries = []
    for so in src_obs:
        gn = [g.name for g in so.vertex_groups]
        for v in so.data.vertices:
            w = {gn[g.group]: g.weight for g in v.groups if g.weight > 1e-4}
            entries.append((so.matrix_world @ v.co, w))
    kd = kdtree.KDTree(len(entries))
    for i, (co, _) in enumerate(entries):
        kd.insert(co, i)
    kd.balance()
    mw = ob.matrix_world
    for v in ob.data.vertices:
        if v.index < only_new_from:
            continue
        _, i, _ = kd.find(mw @ v.co)
        w = entries[i][1]
        for gname, wt in w.items():
            vg = ob.vertex_groups.get(gname) or ob.vertex_groups.new(name=gname)
            vg.add([v.index], wt, 'REPLACE')


def finalize_mesh(ob, mat_name='M_Clothes_Flat'):
    """Flat shade, recalc normals, triangulate, single material, smart UV."""
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = False
    me.update()
    mat = bpy.data.materials.get(mat_name) or bpy.data.materials.new(mat_name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    b.inputs['Metallic'].default_value = 0.0
    b.inputs['Roughness'].default_value = 0.7
    vc = nt.nodes.new('ShaderNodeVertexColor')
    vc.layer_name = 'Col'
    nt.links.new(vc.outputs['Color'], b.inputs['Base Color'])
    nt.links.new(b.outputs['BSDF'], out.inputs['Surface'])
    me.materials.clear()
    me.materials.append(mat)
    # UV: keep existing if present, else smart project
    if not me.uv_layers:
        bpy.ops.object.select_all(action='DESELECT')
        ob.select_set(True)
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.02)
        bpy.ops.object.mode_set(mode='OBJECT')


def smart_uv(ob):
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')


def tri_count(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)


def export_skeletal(ob, rig, path):
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    rig.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.export_scene.fbx(
        filepath=path, use_selection=True,
        object_types={'MESH', 'ARMATURE'}, mesh_smooth_type='FACE',
        use_mesh_modifiers=False, add_leaf_bones=False, bake_anim=False,
        path_mode='AUTO',
        # ONLY 'LINEAR': default 'SRGB' dumps stored bytes into the FBX as-is
        # and UE re-encodes on import -> double sRGB, washed-out grey (07-06)
        colors_type='LINEAR')


# ---------------- QC rendering ----------------

def setup_render(res=760):
    sc = bpy.context.scene
    try:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    except Exception:
        sc.render.engine = 'BLENDER_EEVEE'
    sc.render.resolution_x = res
    sc.render.resolution_y = res
    try:
        sc.view_settings.view_transform = 'Standard'
    except Exception:
        pass
    w = bpy.data.worlds.get('W') or bpy.data.worlds.new('W')
    sc.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes.get('Background') or w.node_tree.nodes.new('ShaderNodeBackground')
    bg.inputs[0].default_value = (0.20, 0.20, 0.22, 1.0)
    bg.inputs[1].default_value = 0.55
    cam = bpy.data.objects.get('QCCam')
    if not cam:
        cd = bpy.data.cameras.new('QCCam')
        cam = bpy.data.objects.new('QCCam', cd)
        sc.collection.objects.link(cam)
    sc.camera = cam
    cam.data.type = 'ORTHO'
    suns = []
    for name, e in (('KeyS', 3.2), ('FillS', 1.3), ('TopS', 1.1)):
        o = bpy.data.objects.get(name)
        if not o:
            d = bpy.data.lights.new(name, type='SUN')
            d.energy = e
            o = bpy.data.objects.new(name, d)
            sc.collection.objects.link(o)
        suns.append(o)
    return sc, cam, suns


def frame_and_shoot(objs, view_dir, out_path, margin=1.12, suns=None):
    """Ortho camera along view_dir onto bbox of objs, key/fill/top sun aimed."""
    sc = bpy.context.scene
    cam = sc.camera
    bpy.context.view_layer.update()
    cor = []
    for ob in objs:
        for c in ob.bound_box:
            cor.append(ob.matrix_world @ Vector(c))
    mn = Vector((min(c.x for c in cor), min(c.y for c in cor), min(c.z for c in cor)))
    mx = Vector((max(c.x for c in cor), max(c.y for c in cor), max(c.z for c in cor)))
    center = (mn + mx) * 0.5
    diag = (mx - mn).length
    vd = Vector(view_dir).normalized()
    cam.location = center + vd * diag * 4
    fwd = (center - cam.location).normalized()
    cam.rotation_euler = fwd.to_track_quat('-Z', 'Y').to_euler()
    cam.data.ortho_scale = diag * margin
    cam.data.clip_start = 0.01
    cam.data.clip_end = diag * 20
    if suns:
        zup = Vector((0, 0, 1))
        right = fwd.cross(zup)
        right = right.normalized() if right.length > 1e-5 else Vector((1, 0, 0))
        up = right.cross(fwd).normalized()
        aims = (fwd + 0.55 * right - 0.55 * up,
                fwd - 0.5 * right + 0.35 * up,
                fwd - 0.9 * up + 0.1 * right)
        for s, t in zip(suns, aims):
            s.rotation_euler = t.normalized().to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = out_path
    bpy.ops.render.render(write_still=True)
    print('RENDER', out_path)
