"""Item icon render stand for the tile inventory UI (Build 1.2.1+).

Renders game item models to 512x512 PNG icons with transparent background:
uniform 3/4-top camera, uniform key+fill light, subject fills ~80% of frame.
Sources are the canonical asset .blend files (NOT FBX re-imports: FBX round
trip through Blender gives a false color snapshot - see modeler-3d context).

Headless run (Blender 5.1.2, ADR-021):
  E:/Programs/Blender/blender.exe -b --factory-startup \
      --python E:/game-dev-team/scripts/render-icons.py -- [--only a,b] [--list]

Output: E:/game-dev-team/assets/icons/512/<item>.png
Each render is verified in-place: file exists, 512x512, RGBA, transparent
corners, subject not touching frame borders, coverage printed (target ~0.80).

Adding future items: append to ITEMS below. 'blend' entries need the source
.blend path + object name (+ optional yaw so the item faces the camera).
"""
import bpy
import math
import os
import sys
import numpy as np
from mathutils import Vector, Matrix

OUT_DIR = 'E:/game-dev-team/assets/icons/512/'
RES = 512
FILL = 0.85                       # fraction of frame the subject should span
VIEW_DIR = Vector((0.8, 0.8, 0.7)).normalized()   # camera sits here (3/4 top)

# Torso pieces are authored in T-pose (2 m arm span) - as an icon that reads
# as a "glider" with a tiny jacket, so for the RENDER ONLY the arms are posed
# down at the shoulder joints (source assets untouched).
POSE_ARMS = {'armor_t1_torso', 'armor_t2_torso', 'armor_t3_torso'}
ARM_DOWN_DEG = 68     # from T-pose horizontal; hands end ~22 deg off vertical
SHOULDER_BONES = (('L_Shoulder', 1), ('R_Arm', -1))   # (bone, rotation sign)

# Head icons: the head dummy (skin/hair/brows) is part of the same mesh as
# the headgear, so "hide the head" = delete its faces on the RENDER COPY
# (Rinat review 08-02: a face in the icon reads as a severed head; assets
# untouched). T1/T3 heads are a dup of the base head (134 faces: 60 skin
# #C89A7A + 70 hair #4A3826 + 4 brows #2B2823) with gear appended after, so
# hair color is restricted to that prefix (the T1 cap reuses the same brown).
# T2 balaclava IS the repainted head - only the eye-slit skin goes.
DUMMY_PREFIX = 134
STRIP = {   # item -> [(hex, max_face_index or None), ...]
    'armor_t1_head': [('#C89A7A', None), ('#2B2823', None),
                      ('#4A3826', DUMMY_PREFIX)],
    'armor_t2_head': [('#7A4A32', None)],
    'armor_t3_head': [('#C89A7A', None), ('#2B2823', None),
                      ('#4A3826', DUMMY_PREFIX)],
}

A = 'E:/game-dev-team/assets/'
WW = A + 'armor_wearables/_work/wearables_work.blend'
WT = A + 'armor_wearables/_work/wearables_t2t3.blend'

# name -> (kind, source, object, yaw_deg)
# yaw turns the item so its front faces the camera quadrant (+X+Y):
# props author forward +Y (yaw 0), humanoid pieces author forward -Y (yaw 180).
ITEMS = {
    'knife':          ('blend', A + 'knife/SM_Knife.blend', 'SM_Knife', 0),
    # -45: side toward camera - readable profile (Rinat review 08-02)
    'pistol':         ('blend', A + 'pistol/SM_Pistol.blend', 'SM_Pistol', -45),
    'wolf_hide':      ('blend', A + 'hide_pickup/hide_pickup.blend',
                       'SM_HidePickup', 0),
    'money':          ('blend', A + 'money/money.blend', 'SM_Money', 0),
    'medkit':         ('blend', A + 'medkit/medkit.blend', 'SM_Medkit', 0),
    'canned_food':    ('blend', A + 'canned_food/canned_food.blend',
                       'SM_CannedFood', -45),   # label patch into camera
    'water':          ('blend', A + 'water/water.blend', 'SM_WaterBottle', 0),
    'ammo_9mm':       ('blend', A + 'ammo_9mm/ammo_9mm.blend',
                       'SM_Ammo9mm', 0),
    'laptop':         ('blend', A + 'laptop/laptop.blend', 'SM_Laptop', 0),
    'armor_t1_head':  ('blend', WW, 'SK_Armor_T1_Head', 180),
    'armor_t1_torso': ('blend', WW, 'SK_Armor_T1_Torso', 180),
    'armor_t1_legs':  ('blend', WW, 'SK_Armor_T1_Legs', 180),
    'armor_t2_head':  ('blend', WT, 'SK_Armor_T2_Head', 180),
    'armor_t2_torso': ('blend', WT, 'SK_Armor_T2_Torso', 180),
    'armor_t2_legs':  ('blend', WT, 'SK_Armor_T2_Legs', 180),
    'armor_t3_head':  ('blend', WT, 'SK_Armor_T3_Head', 180),
    'armor_t3_torso': ('blend', WT, 'SK_Armor_T3_Torso', 180),
    'armor_t3_legs':  ('blend', WT, 'SK_Armor_T3_Legs', 180),
}


def strip_faces(ob, rules):
    """Delete faces by vcol hex (optionally only below a face index) on the
    loaded copy; the source .blend is never written. Prints the count as
    proof that only the expected dummy faces went away."""
    import bmesh
    me = ob.data
    ca = me.color_attributes[0]
    kill = set()
    for hx, max_idx in rules:
        want = tuple(int(hx.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
        for p in me.polygons:
            if max_idx is not None and p.index >= max_idx:
                continue
            c = ca.data[p.loop_indices[0]].color_srgb
            got = tuple(round(v * 255) for v in c[:3])
            if all(abs(g - w) <= 3 for g, w in zip(got, want)):
                kill.add(p.index)
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.faces.ensure_lookup_table()
    bmesh.ops.delete(bm, geom=[bm.faces[i] for i in sorted(kill)],
                     context='FACES')
    bm.to_mesh(me)
    bm.free()
    me.update()
    print('STRIP %s removed=%d left=%d' % (ob.name, len(kill),
                                           len(me.polygons)))


# ---------------- stand ----------------

def load_from_blend(path, obname, keep_rig=False):
    """Append object; returns (mesh_ob, rig_or_None). Without keep_rig the
    parent armature link and modifiers are stripped (mesh = rest pose)."""
    with bpy.data.libraries.load(path, link=False) as (src, dst):
        if obname not in src.objects:
            raise RuntimeError('%s not in %s' % (obname, path))
        dst.objects = [obname]
    ob = [o for o in dst.objects if o is not None][0]
    bpy.context.scene.collection.objects.link(ob)
    rig = None
    if keep_rig and ob.parent and ob.parent.type == 'ARMATURE':
        rig = ob.parent                    # came along as append dependency
        bpy.context.scene.collection.objects.link(rig)
        rig.hide_render = rig.hide_viewport = False
    else:
        ob.parent = None
        for m in list(ob.modifiers):
            ob.modifiers.remove(m)
        ob.matrix_parent_inverse = Matrix.Identity(4)
        ob.matrix_basis = Matrix.Identity(4)
    ob.hide_render = ob.hide_viewport = False
    return ob, rig


def pose_arms_down(rig):
    """Rotate upper-arm pose bones about world Y at the shoulder joint so the
    T-pose arms hang down (icon presentation only, nothing is saved)."""
    for bname, sign in SHOULDER_BONES:
        pb = rig.pose.bones.get(bname)
        if pb is None:
            raise RuntimeError('bone %s missing in %s' % (bname, rig.name))
        bpy.context.view_layer.update()
        M = pb.matrix.copy()
        pivot = M.translation.copy()
        R = Matrix.Rotation(math.radians(sign * ARM_DOWN_DEG), 4, 'Y')
        pb.matrix = (Matrix.Translation(pivot) @ R
                     @ Matrix.Translation(-pivot) @ M)
    bpy.context.view_layer.update()


def icon_material():
    mat = bpy.data.materials.get('M_Icon') or bpy.data.materials.new('M_Icon')
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
    return mat


def setup_stand():
    sc = bpy.context.scene
    try:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    except Exception:
        sc.render.engine = 'BLENDER_EEVEE'
    sc.render.resolution_x = sc.render.resolution_y = RES
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGBA'
    sc.render.image_settings.color_depth = '8'
    try:
        sc.view_settings.view_transform = 'Standard'
    except Exception:
        pass
    w = bpy.data.worlds.get('W') or bpy.data.worlds.new('W')
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes.get('Background') or nt.nodes.new('ShaderNodeBackground')
    o = nt.nodes.get('World Output') or nt.nodes.new('ShaderNodeOutputWorld')
    nt.links.new(bg.outputs['Background'], o.inputs['Surface'])
    bg.inputs[0].default_value = (0.20, 0.20, 0.22, 1.0)   # soft ambient only
    bg.inputs[1].default_value = 0.55                      # (bg itself is alpha 0)
    cd = bpy.data.cameras.new('IconCam')
    cd.lens = 50.0
    cd.type = 'PERSP'
    cam = bpy.data.objects.new('IconCam', cd)
    sc.collection.objects.link(cam)
    sc.camera = cam
    fwd = -VIEW_DIR
    cam.rotation_euler = fwd.to_track_quat('-Z', 'Y').to_euler()
    right = fwd.cross(Vector((0, 0, 1))).normalized()
    up = right.cross(fwd).normalized()
    suns = []
    for name, energy, soft, aim in (
            ('Key', 3.0, 15, fwd + 0.50 * right - 0.60 * up),
            ('Fill', 1.2, 60, fwd - 0.50 * right - 0.15 * up)):
        d = bpy.data.lights.new(name, type='SUN')
        d.energy = energy
        d.angle = math.radians(soft)
        so = bpy.data.objects.new(name, d)
        sc.collection.objects.link(so)
        so.rotation_euler = aim.normalized().to_track_quat('-Z', 'Y').to_euler()
        suns.append(so)
    return sc, cam


def frame_camera(cam, ob):
    """Place cam back along VIEW_DIR so the subject spans FILL of the frame.
    Uses the EVALUATED mesh (armature pose applied), not rest-pose data."""
    bpy.context.view_layer.update()
    deps = bpy.context.evaluated_depsgraph_get()
    oe = ob.evaluated_get(deps)
    tmp = oe.to_mesh()
    verts = [oe.matrix_world @ v.co for v in tmp.vertices]
    mn = Vector((min(v.x for v in verts), min(v.y for v in verts),
                 min(v.z for v in verts)))
    mx = Vector((max(v.x for v in verts), max(v.y for v in verts),
                 max(v.z for v in verts)))
    C = (mn + mx) * 0.5
    fwd = -VIEW_DIR
    right = fwd.cross(Vector((0, 0, 1))).normalized()
    up = right.cross(fwd).normalized()
    tan_h = math.tan(cam.data.angle / 2.0) * FILL
    t = 0.0
    for v in verts:
        p = v - C
        x, y, z = p.dot(right), p.dot(up), p.dot(VIEW_DIR)
        t = max(t, z + abs(x) / tan_h, z + abs(y) / tan_h)
    oe.to_mesh_clear()
    cam.location = C + VIEW_DIR * t
    cam.data.clip_start = max(0.001, t * 0.01)
    cam.data.clip_end = t * 20 + 10
    return t


def render_icon(name):
    kind, source, obname, yaw = ITEMS[name]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc, cam = setup_stand()
    rig = None
    if kind == 'builder':
        ob = globals()[source]()
    else:
        ob, rig = load_from_blend(source, obname, keep_rig=name in POSE_ARMS)
    if rig is not None:
        # mesh is parented to the rig - yaw the rig only (else double turn)
        rig.rotation_euler = (0, 0, math.radians(yaw))
        pose_arms_down(rig)
    else:
        ob.rotation_euler = (0, 0, math.radians(yaw))
    if name in STRIP:
        strip_faces(ob, STRIP[name])
    mat = icon_material()
    ob.data.materials.clear()
    ob.data.materials.append(mat)
    frame_camera(cam, ob)
    path = OUT_DIR + name + '.png'
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    return path


# ---------------- verification ----------------

def verify_png(path):
    """size / RGBA / transparent corners / borders clear / coverage."""
    if not os.path.isfile(path):
        return False, 'missing file'
    img = bpy.data.images.load(path)
    try:
        w, h = img.size
        if (w, h) != (RES, RES):
            return False, 'size %dx%d' % (w, h)
        if img.channels != 4:
            return False, 'channels=%d' % img.channels
        px = np.empty(w * h * 4, dtype=np.float32)
        img.pixels.foreach_get(px)
        alpha = px.reshape(h, w, 4)[:, :, 3]
        cov = alpha > 0.01
        if not cov.any():
            return False, 'fully transparent'
        for cy, cx in ((0, 0), (0, w - 1), (h - 1, 0), (h - 1, w - 1)):
            if alpha[cy, cx] > 0.001:
                return False, 'corner not transparent'
        ys, xs = np.nonzero(cov)
        top, bot = ys.min(), ys.max()
        left, right = xs.min(), xs.max()
        margin = min(top, left, h - 1 - bot, w - 1 - right)
        if margin < 2:
            return False, 'subject touches border (margin %dpx)' % margin
        coverage = max(bot - top + 1, right - left + 1) / float(RES)
        return True, 'coverage %.2f margin %dpx' % (coverage, margin)
    finally:
        bpy.data.images.remove(img)


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    if '--list' in argv:
        for n in ITEMS:
            print('ITEM', n)
        return
    names = list(ITEMS)
    if '--only' in argv:
        names = argv[argv.index('--only') + 1].split(',')
    os.makedirs(OUT_DIR, exist_ok=True)
    results = []
    for n in names:
        path = render_icon(n)
        ok, info = verify_png(path)
        results.append((n, ok, info, path))
        print('ICON %-16s %s %s' % (n, 'PASS' if ok else 'FAIL', info))
    print('-' * 60)
    bad = [r for r in results if not r[1]]
    for n, ok, info, path in results:
        print('%-4s %-16s %s' % ('PASS' if ok else 'FAIL', n, path))
    print('SUMMARY %d/%d PASS' % (len(results) - len(bad), len(results)))
    if bad:
        sys.exit(1)


main()
