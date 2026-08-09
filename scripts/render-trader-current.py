"""Presentation shot of the trader NPC that is CURRENTLY in the game, laid out
like the Tripo reference frame (PostNomber2/1.jpg): three copies of the same
figure in a row - front three-quarter, near-front, back three-quarter - full
body, on a dark grey vignette, no floor and no cast shadows.

Source of truth is the assembled work scene
    assets/npc_trader/_work/trader_work.blend
(SK_Trader_Head / _Torso / _Legs on the 21-bone RootAnim rig, built by
assets/npc_trader/10_build_trader.py). Geometry, vertex colours and the
M_Trader_Flat material are used AS THEY ARE - this frame must show the model
that ships, not a dressed-up version of it. The .blend is only read.

The rig rests in a T-pose, so the arms are posed down along the body first
(the existing renders_trader/ shots are T-pose or the deformation-test pose and
are useless for a presentation frame). The bend is split between the clavicle
and the upper arm so linear-blend skinning does not pinch the shoulder.

Framing is not eyeballed: the frame is rendered, the figures are located in the
result by edge energy, and camera distance + lens shift are corrected until the
group matches the reference proportions. The last pass is verified again.

Blender 5.1.2 has no Cycles - this is EEVEE Next. ADR-021 CLI:
  E:/Programs/Blender/blender.exe -b --factory-startup \
      --python E:/game-dev-team/scripts/render-trader-current.py -- [--stage pose]

Output: E:/game-dev-team/reports/renders/trader-current-3views.png
"""
import bpy
import math
import os
import sys
import numpy as np
from mathutils import Vector, Matrix

SRC = 'E:/game-dev-team/assets/npc_trader/_work/trader_work.blend'
OUT = 'E:/game-dev-team/reports/renders/trader-current-3views.png'
TMP = ('C:/Users/pgr40/AppData/Local/Temp/claude/E--game-dev-team/'
       'ab1333ef-9e44-437a-a14a-0db342c7a4f7/scratchpad/')
MODULES = ('SK_Trader_Head', 'SK_Trader_Torso', 'SK_Trader_Legs')

RES_X, RES_Y = 1416, 868
ASPECT = RES_X / float(RES_Y)
SAMPLES = 256

# Composition targets, measured off the reference frame (708x434):
#   group 41.5% of the width, 69.1% of the height, centre x 48.3%,
#   top margin 19.1%, bottom margin 11.8%.
TGT_H = 0.691                 # tallest figure top..lowest foot, share of height
TGT_CX = 0.483                # group centre, share of width
TGT_TOP = 0.185               # top margin, share of height

CAM_Z = 1.28                  # chest height of a 1.83 m figure - not a top-down
LENS = 105.0                  # long lens: no wide-angle spread on the outer two

# (x, y, yaw deg). Character faces -Y, camera sits at -Y, so world +X = screen
# right. y grows away from the camera: the row steps back to the right exactly
# like the reference, where the right figure measures ~13% shorter than the left
# one - at ~13 m that needs about 1.7 m of depth between the two ends.
# Sideways spacing is tight on purpose: the reference group measures 41.5% of
# the frame width against 69.1% of its height, i.e. the three figures just
# overlap rather than standing apart.
FIGURES = [
    (-0.56, -0.50, 44.0),     # front three-quarter, turned towards the centre
    (0.02, 0.20, -10.0),      # near-front
    (0.66, 1.15, 214.0),      # back three-quarter
]

# Arm rest pose is the T-pose; these are the wanted WORLD directions of each
# bone (character-left chain, mirrored in x for the right one). The right side
# names are what the source rig actually carries - 'Pelvis_009_R_002' is the
# misnamed right forearm, verified against the bone hierarchy in the .blend.
ARM_CHAIN = [
    # (left bone,     right bone,           direction (x, y, z), x mirrored)
    ('L_UpperArm', 'R_UpperArm', (0.977, -0.030, -0.210)),   # clavicle, tips down
    ('L_Shoulder', 'R_Arm', (0.225, -0.055, -0.972)),        # upper arm, hangs
    ('L_Arm', 'Pelvis_009_R_002', (0.165, -0.195, -0.967)),  # forearm, eased fwd
    ('L_Hand', 'R_Hand', (0.130, -0.175, -0.976)),           # hand follows
]
# a touch of life so the row does not read as three clones of a mannequin
EXTRA_POSE = {'C_Neck': (0.0, 0.0, 0.0)}

BG_CORE = '#414246'           # measured centre of the reference vignette
BG_MID = '#33353A'
BG_EDGE = '#26282C'
BG_CORNER = '#1F2023'         # measured corners of the reference vignette


def lin(hx):
    """'#RRGGBB' display sRGB -> linear, for shader inputs under the Standard
    view transform (which is what the QC stand and the game material use)."""
    hx = hx.lstrip('#')
    out = []
    for i in (0, 2, 4):
        c = int(hx[i:i + 2], 16) / 255.0
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return (out[0], out[1], out[2], 1.0)


# --------------------------------------------------------------- pose the rig

def aim_bone(rig, name, direction):
    """Rotate one pose bone so it points along `direction` in world space,
    keeping its head where the parent chain put it."""
    pb = rig.pose.bones[name]
    pb.rotation_mode = 'QUATERNION'
    bpy.context.view_layer.update()
    cur = (pb.tail - pb.head)
    if cur.length < 1e-6:
        raise RuntimeError('zero-length bone %s' % name)
    rot = cur.normalized().rotation_difference(Vector(direction).normalized())
    m = pb.matrix.copy()
    head = m.to_translation()
    pb.matrix = (Matrix.Translation(head)
                 @ rot.to_matrix().to_4x4() @ m.to_3x3().to_4x4())
    bpy.context.view_layer.update()


def pose_arms_down(rig):
    for lname, rname, d in ARM_CHAIN:                 # parents before children
        aim_bone(rig, lname, d)
        aim_bone(rig, rname, (-d[0], d[1], d[2]))
    for bn, eul in EXTRA_POSE.items():
        pb = rig.pose.bones[bn]
        pb.rotation_mode = 'XYZ'
        pb.rotation_euler = eul
    bpy.context.view_layer.update()
    print('--- posed bone directions (world) ---')
    bad = 0
    for lname, rname, d in ARM_CHAIN:
        for n in (lname, rname):
            pb = rig.pose.bones[n]
            v = (pb.tail - pb.head).normalized()
            down = -v.z
            print('  %-20s dir=(%6.3f,%6.3f,%6.3f)  downwardness=%.3f'
                  % (n, v.x, v.y, v.z, down))
            if lname != 'L_UpperArm' and down < 0.90:
                bad += 1
    if bad:
        raise RuntimeError('%d arm bones did not end up hanging down' % bad)


# ------------------------------------------------------- bake and lay out

def bake_figure(rig):
    """Freeze the posed, skinned modules into one static mesh object. The rig
    is at identity, so evaluated local coordinates are already world ones."""
    deps = bpy.context.evaluated_depsgraph_get()
    parts = []
    for n in MODULES:
        src = bpy.data.objects[n]
        me = bpy.data.meshes.new_from_object(src.evaluated_get(deps),
                                             depsgraph=deps)
        me.name = n + '_baked'
        ob = bpy.data.objects.new(n + '_baked', me)
        bpy.context.scene.collection.objects.link(ob)
        ob.matrix_world = Matrix.Identity(4)
        parts.append(ob)
        print('  baked %-18s verts=%d tris=%d mats=%s'
              % (n, len(me.vertices), sum(len(p.vertices) - 2 for p in me.polygons),
                 [m.name for m in me.materials]))
    bpy.ops.object.select_all(action='DESELECT')
    for ob in parts:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    fig = bpy.context.active_object
    fig.name = 'TraderBaked'
    return fig


def place_row(fig):
    """Three copies of the baked figure, rotated and stepped back in depth."""
    out = []
    for i, (x, y, yaw) in enumerate(FIGURES):
        ob = fig if i == 0 else fig.copy()
        if i:
            ob.data = fig.data           # one mesh, three users: same model
            bpy.context.scene.collection.objects.link(ob)
        ob.name = 'Trader_%d' % i
        ob.location = (x, y, 0.0)
        ob.rotation_euler = (0.0, 0.0, math.radians(yaw))
        out.append(ob)
    bpy.context.view_layer.update()
    return out


def hide_source():
    for o in bpy.data.objects:
        if o.type in ('MESH', 'ARMATURE') and not o.name.startswith('Trader_'):
            o.hide_render = True
            o.hide_viewport = True


# ------------------------------------------------------------ stage dressing

def backdrop_material():
    """Screen-space elliptical vignette: bright core down the middle falling to
    near-black at the left/right edges and the corners, which is what the
    reference frame measures as. Emission only, so no light and no shadow of the
    figures ever lands on it."""
    mat = bpy.data.materials.new('M_TraderBackdrop')
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    em = nt.nodes.new('ShaderNodeEmission')
    em.inputs['Strength'].default_value = 1.0

    tc = nt.nodes.new('ShaderNodeTexCoord')          # Window = screen space
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(tc.outputs['Window'], sep.inputs['Vector'])
    comb = nt.nodes.new('ShaderNodeCombineXYZ')
    # (x - 0.47) * aspect, (y - 0.42) * 0.345 -> ellipse, wide and slow in y
    for src, dst, off, scale in ((sep.outputs['X'], 'X', 0.47, ASPECT / 0.816),
                                 (sep.outputs['Y'], 'Y', 0.42, 0.345 / 0.5)):
        sub = nt.nodes.new('ShaderNodeMath')
        sub.operation = 'SUBTRACT'
        sub.inputs[1].default_value = off
        nt.links.new(src, sub.inputs[0])
        mul = nt.nodes.new('ShaderNodeMath')
        mul.operation = 'MULTIPLY'
        mul.inputs[1].default_value = scale
        nt.links.new(sub.outputs[0], mul.inputs[0])
        nt.links.new(mul.outputs[0], comb.inputs[dst])
    ln = nt.nodes.new('ShaderNodeVectorMath')
    ln.operation = 'LENGTH'
    nt.links.new(comb.outputs['Vector'], ln.inputs[0])

    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.interpolation = 'EASE'
    e = ramp.color_ramp.elements
    e[0].position, e[0].color = 0.00, lin(BG_CORE)
    e[1].position, e[1].color = 0.62, lin(BG_MID)
    for pos, hx in ((0.86, BG_EDGE), (1.20, BG_CORNER)):
        el = e.new(pos)
        el.color = lin(hx)
    nt.links.new(ln.outputs['Value'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], em.inputs['Color'])
    nt.links.new(em.outputs['Emission'], out.inputs['Surface'])
    return mat


BACKDROP_GAP = 7.0            # metres BEHIND the row, not behind the camera


def place_backdrop(cam):
    """Big camera-facing card well behind the row (the row straddles y=0, so the
    card sits at camera distance + BACKDROP_GAP). Emission is dim (~0.05 linear)
    at 16+ m, so it lights nothing measurably."""
    p = bpy.data.objects.get('Backdrop')
    if p is None:
        bpy.ops.mesh.primitive_plane_add(size=1.0)
        p = bpy.context.active_object
        p.name = 'Backdrop'
        p.data.materials.clear()
        p.data.materials.append(backdrop_material())
        p.visible_shadow = False
    dist = abs(cam.location.y) + BACKDROP_GAP
    half_w = math.tan(cam.data.angle * 0.5) * dist
    p.scale = (half_w * 4.0, half_w * 4.0, 1.0)
    q = cam.matrix_world.to_quaternion()
    p.rotation_euler = q.to_euler()                  # plane normal -> camera
    p.location = cam.location + (q @ Vector((0, 0, -1))) * dist
    bpy.context.view_layer.update()
    return p


def add_sun(name, azimuth, elevation, energy, angle_deg, color):
    """azimuth 0 = straight in front of the row (from -Y), positive = towards
    screen right; elevation is degrees above the horizon."""
    d = bpy.data.lights.new(name, type='SUN')
    d.energy = energy
    d.angle = math.radians(angle_deg)
    d.color = color
    d.use_shadow = True
    ob = bpy.data.objects.new(name, d)
    bpy.context.scene.collection.objects.link(ob)
    a, e = math.radians(azimuth), math.radians(elevation)
    # direction the light travels: from the lamp towards the row
    v = Vector((math.sin(a) * math.cos(e), math.cos(a) * math.cos(e),
                -math.sin(e)))
    ob.rotation_euler = v.to_track_quat('-Z', 'Y').to_euler()
    return ob


def light_rig():
    """Soft and broad: the outfit is nearly all dark grey, so the frame lives or
    dies on (a) enough fill that the near-black sleeves keep their shape and
    (b) two back rims that cut the silhouette off a background of almost the
    same value as the bandana."""
    add_sun('Key', -32.0, 36.0, 2.9, 14.0, (1.00, 0.98, 0.95))
    add_sun('Fill', 44.0, 16.0, 1.55, 30.0, (0.86, 0.90, 1.00))
    add_sun('Bounce', 8.0, -22.0, 0.85, 40.0, (0.90, 0.92, 1.00))
    add_sun('RimL', -152.0, 30.0, 1.70, 10.0, (0.98, 0.96, 1.00))
    add_sun('RimR', 156.0, 26.0, 1.45, 10.0, (1.00, 0.97, 0.92))


def setup_scene():
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_EEVEE'
    sc.render.resolution_x, sc.render.resolution_y = RES_X, RES_Y
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGB'
    sc.render.image_settings.color_depth = '8'
    sc.eevee.taa_render_samples = SAMPLES
    sc.eevee.use_shadows = True
    sc.eevee.shadow_ray_count = 4
    sc.eevee.shadow_step_count = 8
    sc.eevee.use_raytracing = True
    sc.eevee.ray_tracing_method = 'SCREEN'
    sc.eevee.use_fast_gi = True
    sc.view_settings.view_transform = 'Standard'
    sc.view_settings.look = 'None'
    w = bpy.data.worlds.new('W')
    sc.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes['Background']
    # ambient floor: the sweater is genuinely near-black (#33302B), so without
    # this the sleeves lose their form instead of just reading dark
    bg.inputs[0].default_value = (0.055, 0.059, 0.072, 1.0)
    bg.inputs[1].default_value = 1.0
    return sc


def make_camera(sc, dist):
    cd = bpy.data.cameras.new('TraderCam')
    cd.lens = LENS
    cd.sensor_width = 36.0
    cam = bpy.data.objects.new('TraderCam', cd)
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.location = (0.0, -dist, CAM_Z)
    # dead level: verticals stay vertical, framing is done with lens shift
    cam.rotation_euler = Vector((0, 1, 0)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    return cam


# ------------------------------------------------------ measure and verify

def silhouette(sc, cam, tag='cal'):
    """Exact figure bounding box: one cheap pass with a transparent film and
    the backdrop hidden, read straight off the alpha channel. Edge detection on
    the beauty frame is only a sanity check - dark boots on a dark vignette are
    exactly where it would go blind."""
    bd = bpy.data.objects.get('Backdrop')
    keep = (sc.render.film_transparent, sc.render.image_settings.color_mode,
            sc.eevee.taa_render_samples, sc.render.filepath,
            bd.hide_render if bd else None)
    sc.render.film_transparent = True
    sc.render.image_settings.color_mode = 'RGBA'
    sc.eevee.taa_render_samples = 4
    if bd:
        bd.hide_render = True
    path = TMP + 'alpha_%s.png' % tag
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    (sc.render.film_transparent, sc.render.image_settings.color_mode,
     sc.eevee.taa_render_samples, sc.render.filepath) = keep[:4]
    if bd:
        bd.hide_render = keep[4]

    img = bpy.data.images.load(path)
    try:
        w, h = img.size
        buf = np.empty(w * h * img.channels, dtype=np.float32)
        img.pixels.foreach_get(buf)
        alpha = buf.reshape(h, w, img.channels)[::-1, :, 3]
    finally:
        bpy.data.images.remove(img)
    mask = alpha > 0.5
    xs = np.nonzero(mask.any(axis=0))[0]
    ys = np.nonzero(mask.any(axis=1))[0]
    if not len(xs) or not len(ys):
        raise RuntimeError('nothing visible in the silhouette pass')
    return {'x0': xs.min() / w, 'x1': (xs.max() + 1) / w,
            'y0': ys.min() / h, 'y1': (ys.max() + 1) / h,
            'cx': 0.5 * (xs.min() + xs.max() + 1) / w,
            'wfrac': (xs.max() + 1 - xs.min()) / float(w),
            'hfrac': (ys.max() + 1 - ys.min()) / float(h)}


def solve_framing(sc, cam, dist):
    """Put the row where the reference puts it. Camera distance sets the size;
    lens shift slides the frame without tilting, so verticals stay vertical.
    The response to shift_x / shift_y is MEASURED, not assumed - Blender's sign
    convention is not something to take from memory."""
    def setcam(d):
        cam.location = (0.0, -d, CAM_Z)
        bpy.context.view_layer.update()
        place_backdrop(cam)

    for i in range(7):                      # projected size ~ 1 / distance
        b = silhouette(sc, cam, 'd%d' % i)
        print('    size pass %d: dist=%.3f -> group height %.1f%% (target %.1f%%)'
              % (i, dist, 100 * b['hfrac'], 100 * TGT_H))
        if abs(b['hfrac'] - TGT_H) < 0.003:
            break
        dist *= b['hfrac'] / TGT_H
        setcam(dist)

    b0 = silhouette(sc, cam, 'p0')
    probe = 0.05
    cam.data.shift_x = probe
    bx = silhouette(sc, cam, 'px')
    cam.data.shift_x = 0.0
    cam.data.shift_y = probe
    by = silhouette(sc, cam, 'py')
    cam.data.shift_y = 0.0
    kx = (bx['cx'] - b0['cx']) / probe
    ky = (by['y0'] - b0['y0']) / probe
    print('    shift response: d(centre x)/d(shift_x)=%+.3f  '
          'd(top margin)/d(shift_y)=%+.3f' % (kx, ky))
    if abs(kx) < 0.1 or abs(ky) < 0.1:
        raise RuntimeError('lens shift does not move the frame as expected')

    for i in range(4):
        b = silhouette(sc, cam, 's%d' % i)
        dx, dy = TGT_CX - b['cx'], TGT_TOP - b['y0']
        print('    place pass %d: centre x=%.1f%% top=%.1f%% (targets %.1f%% / '
              '%.1f%%)' % (i, 100 * b['cx'], 100 * b['y0'],
                           100 * TGT_CX, 100 * TGT_TOP))
        if abs(dx) < 0.003 and abs(dy) < 0.003:
            break
        cam.data.shift_x += dx / kx
        cam.data.shift_y += dy / ky
        bpy.context.view_layer.update()
    return dist, silhouette(sc, cam, 'final')


def measure(path):
    """Locate the figures in a rendered frame by local edge energy (the
    backdrop is smooth, the model is faceted), return their bounding box as
    fractions of the frame."""
    img = bpy.data.images.load(path)
    try:
        w, h = img.size
        buf = np.empty(w * h * img.channels, dtype=np.float32)
        img.pixels.foreach_get(buf)
        a = buf.reshape(h, w, img.channels)[::-1, :, :3]      # top-down, sRGB
        alpha_ok = (img.channels < 4
                    or buf.reshape(h, w, img.channels)[:, :, 3].min() > 0.999)
    finally:
        bpy.data.images.remove(img)
    g = a.mean(axis=2) * 255.0
    ed = np.zeros_like(g)
    ed[:, 1:-1] += np.abs(g[:, 2:] - g[:, :-2])
    ed[1:-1, :] += np.abs(g[2:, :] - g[:-2, :])
    mask = ed > 12.0
    xs = np.nonzero(mask.sum(axis=0) >= 3)[0]
    ys = np.nonzero(mask.sum(axis=1) >= 3)[0]
    if not len(xs) or not len(ys):
        raise RuntimeError('no figures found in %s' % path)
    tone = g[mask]
    return {
        'w': w, 'h': h, 'opaque': alpha_ok,
        'x0': xs.min() / w, 'x1': xs.max() / w,
        'y0': ys.min() / h, 'y1': ys.max() / h,
        'cx': 0.5 * (xs.min() + xs.max()) / w,
        'hfrac': (ys.max() - ys.min()) / float(h),
        'wfrac': (xs.max() - xs.min()) / float(w),
        'fig_min': tone.min(), 'fig_max': tone.max(), 'fig_mean': tone.mean(),
        'frame_min': g.min(), 'frame_max': g.max(),
    }


def report(tag, m):
    print('  %-9s group  w=%.1f%% h=%.1f%%  centre x=%.1f%%  margins '
          'top=%.1f%% bottom=%.1f%% left=%.1f%% right=%.1f%%'
          % (tag, 100 * m['wfrac'], 100 * m['hfrac'], 100 * m['cx'],
             100 * m['y0'], 100 * (1 - m['y1']), 100 * m['x0'],
             100 * (1 - m['x1'])))
    print('  %-9s figure tone %.0f..%.0f (mean %.0f) of 255; whole frame '
          '%.0f..%.0f; opaque=%s'
          % ('', m['fig_min'], m['fig_max'], m['fig_mean'],
             m['frame_min'], m['frame_max'], m['opaque']))


# ------------------------------------------------------------------- stages

def build():
    bpy.ops.wm.open_mainfile(filepath=SRC)
    rig = bpy.data.objects['RootAnim']
    for n in MODULES:                      # the build script leaves QC hides on
        bpy.data.objects[n].hide_render = False
        bpy.data.objects[n].hide_viewport = False
    pose_arms_down(rig)
    fig = bake_figure(rig)
    row = place_row(fig)
    hide_source()
    for ob in row:
        ob.hide_render = ob.hide_viewport = False
    sc = setup_scene()
    light_rig()
    return sc, row


def stage_pose():
    """Cheap isolating test: one posed figure, flat front and three-quarter, no
    stage dressing - is the pose itself right before the composition is built?"""
    sc, row = build()
    for ob in row[1:]:
        ob.hide_render = True
    row[0].location = (0, 0, 0)
    sc.render.resolution_x = sc.render.resolution_y = 700
    cam = make_camera(sc, 6.0)
    for name, yaw in (('front', 0.0), ('tq', 35.0), ('side', 90.0)):
        row[0].rotation_euler = (0, 0, math.radians(yaw))
        cam.location = (0, -6.0, 0.95)
        cam.data.lens = 60.0
        cam.data.shift_y = 0.045
        bpy.context.view_layer.update()
        sc.render.filepath = TMP + 'pose_%s.png' % name
        bpy.ops.render.render(write_still=True)
        print('POSE CHECK ->', sc.render.filepath)


def stage_full():
    sc, row = build()
    dist = 9.5
    cam = make_camera(sc, dist)
    place_backdrop(cam)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)

    print('--- framing ---')
    dist, sil = solve_framing(sc, cam, dist)
    print('  camera %.2f m from the row, lens %.0f mm at %.2f m height, '
          'shift=(%.4f, %.4f)' % (dist, LENS, CAM_Z, cam.data.shift_x,
                                  cam.data.shift_y))
    print('  silhouette: group w=%.1f%% h=%.1f%% centre x=%.1f%%  margins '
          'top=%.1f%% bottom=%.1f%% left=%.1f%% right=%.1f%%'
          % (100 * sil['wfrac'], 100 * sil['hfrac'], 100 * sil['cx'],
             100 * sil['y0'], 100 * (1 - sil['y1']), 100 * sil['x0'],
             100 * (1 - sil['x1'])))

    sc.render.filepath = OUT
    bpy.ops.render.render(write_still=True)
    if not os.path.isfile(OUT):
        raise RuntimeError('render did not write %s' % OUT)
    m = measure(OUT)
    print('--- FINAL %s ---' % OUT)
    report('final', m)
    size = os.path.getsize(OUT)
    print('  file %d bytes, %dx%d' % (size, m['w'], m['h']))
    ok = (m['w'], m['h']) == (RES_X, RES_Y) and m['opaque']
    # nothing cropped, measured on the exact silhouette, not on edge energy
    ok = ok and min(sil['y0'], 1 - sil['y1'], sil['x0'], 1 - sil['x1']) > 0.03
    print('CHECK', 'PASS' if ok else 'FAIL')
    if not ok:
        sys.exit(1)


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    if '--stage' in argv and argv[argv.index('--stage') + 1] == 'pose':
        stage_pose()
    else:
        stage_full()


main()
