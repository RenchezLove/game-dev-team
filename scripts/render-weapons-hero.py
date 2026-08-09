"""Hero shots of the knife + pistol for the Telegram channel (Rinat 08-09:
"add shadows, light and some haze, shoot it at an angle").

Scene, as opposed to the flat profile frame (scripts/render-weapons-shot.py):
  * long lens (100 mm) perspective camera, 3/4 from above - volume reads;
  * items LIE on a dark floor, so they get real soft cast shadows and a faint
    reflection instead of floating in the void;
  * key / rim / fill area lights + one spot that shows as a shaft in the haze;
  * world volume scatter = haze that eats the far floor and gives depth;
  * material upgrade: the vertex colour drives metalness (warm brown = grip
    wood, everything blue-ish = metal) - flat "everything is chalk" shading is
    half of why the pistol looked cheap.
Scale between the two items stays TRUE - they are placed at their authored
size, nothing is fitted per item.

Blender 5.1.2 has no Cycles (engine list is EEVEE only) - this is EEVEE Next
with ray tracing, soft shadows and volumetrics turned on. ADR-021 CLI:
  E:/Programs/Blender/blender.exe -b --factory-startup \
      --python E:/game-dev-team/scripts/render-weapons-hero.py -- [--only a,b]

The production icon stand (scripts/render-icons.py) is NOT touched, and the
source .blend files are only appended from, never written.
Output: E:/game-dev-team/reports/renders/weapons-hero-*.png
"""
import bpy
import bmesh
import math
import os
import sys
import numpy as np
from mathutils import Vector, Matrix

OUT_DIR = 'E:/game-dev-team/reports/renders/'
A = 'E:/game-dev-team/assets/'
RES_X, RES_Y = 1920, 1080
SAMPLES = 192

# (source .blend, object, yaw on the table in degrees, position x/y in metres)
LAYOUT = [
    (A + 'pistol/SM_Pistol.blend', 'SM_Pistol', -14.0, (0.105, 0.020)),
    (A + 'knife/SM_Knife.blend', 'SM_Knife', 8.0, (-0.125, -0.035)),
]

CHAMFER = 0.0004      # 4 mm/10 - render-only edge break for the A/B variant

VARIANTS = {
    # name: (lighting preset, render-time chamfer, view transform,
    #        camera azimuth from +X, elevation above the table, lens mm)
    # elevation matters more than anything here: an item lying on its side is
    # only readable from well above - at 30 deg the pistol squashed into a wedge
    'weapons-hero-studio':
        ('studio', False, 'Khronos PBR Neutral', -96.0, 54.0, 100.0),
    # same camera and same light as 'studio' - ONLY the geometry differs
    'weapons-hero-studio-chamfer':
        ('studio', True, 'Khronos PBR Neutral', -96.0, 54.0, 100.0),
    'weapons-hero-dramatic':
        ('dramatic', False, 'AgX', -80.0, 44.0, 85.0),
}


def sock(sockets, name, kind):
    """The Mix node carries several sockets with the SAME name (Float/Vector/
    Colour variants) - picking by name alone silently grabs the float one."""
    for s in sockets:
        if s.name == name and s.type == kind:
            return s
    raise KeyError('%s (%s) not among %s'
                   % (name, kind, [(s.name, s.type) for s in sockets]))


def load_from_blend(path, obname):
    """Append from the canonical source .blend (never written back)."""
    with bpy.data.libraries.load(path, link=False) as (src, dst):
        if obname not in src.objects:
            raise RuntimeError('%s not in %s' % (obname, path))
        dst.objects = [obname]
    ob = [o for o in dst.objects if o is not None][0]
    bpy.context.scene.collection.objects.link(ob)
    ob.parent = None
    for m in list(ob.modifiers):
        ob.modifiers.remove(m)
    ob.matrix_parent_inverse = Matrix.Identity(4)
    ob.matrix_basis = Matrix.Identity(4)
    ob.hide_render = ob.hide_viewport = False
    return ob


def clean_and_chamfer(ob, width):
    """Render-copy only: drop the zero-area faces the source mesh carries, then
    break every hard edge by `width`. This is what the game model does NOT
    have - the variant exists to show what the geometry is missing."""
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    n0 = len(bm.faces)
    bmesh.ops.dissolve_degenerate(bm, dist=1e-5, edges=bm.edges[:])
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    n1 = len(bm.faces)
    edges = [e for e in bm.edges if e.calc_face_angle(0.0) > math.radians(30)]
    bmesh.ops.bevel(bm, geom=edges + [v for v in bm.verts], offset=width,
                    segments=2, profile=0.5, affect='EDGES',
                    offset_type='OFFSET', clamp_overlap=True,
                    loop_slide=True, material=-1)
    n2 = len(bm.faces)
    bm.to_mesh(me)
    bm.free()
    me.update()
    print('  CHAMFER %s: %d faces -> %d after degenerate cleanup -> %d after '
          '%.1f mm edge break' % (ob.name, n0, n1, n2, width * 1000))


def weapon_material():
    """Vertex colour drives base colour AND metalness: hue tells grip (warm
    brown, hue ~0.05) from steel (everything blue-grey, hue ~0.6+)."""
    mat = bpy.data.materials.new('M_WeaponHero')
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    vc = nt.nodes.new('ShaderNodeVertexColor')
    vc.layer_name = 'Col'
    nt.links.new(vc.outputs['Color'], bsdf.inputs['Base Color'])

    hsv = nt.nodes.new('ShaderNodeSeparateColor')
    hsv.mode = 'HSV'
    nt.links.new(vc.outputs['Color'], hsv.inputs['Color'])
    is_metal = nt.nodes.new('ShaderNodeMath')       # hue > 0.30 -> steel
    is_metal.operation = 'GREATER_THAN'
    is_metal.inputs[1].default_value = 0.30
    nt.links.new(hsv.outputs['Red'], is_metal.inputs[0])
    metal_amt = nt.nodes.new('ShaderNodeMath')
    metal_amt.operation = 'MULTIPLY'
    metal_amt.inputs[1].default_value = 0.75        # not a full mirror: dark
    nt.links.new(is_metal.outputs[0], metal_amt.inputs[0])  # blued steel keeps
    nt.links.new(metal_amt.outputs[0], bsdf.inputs['Metallic'])  # some diffuse

    # roughness: steel 0.35, grip 0.62, plus a faint noise so it is not a
    # perfectly uniform surface
    noise = nt.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 220.0
    noise.inputs['Detail'].default_value = 2.0
    rough_mix = nt.nodes.new('ShaderNodeMix')
    rough_mix.data_type = 'FLOAT'
    sock(rough_mix.inputs, 'A', 'VALUE').default_value = 0.62
    sock(rough_mix.inputs, 'B', 'VALUE').default_value = 0.35
    nt.links.new(is_metal.outputs[0],
                 sock(rough_mix.inputs, 'Factor', 'VALUE'))
    jitter = nt.nodes.new('ShaderNodeMath')
    jitter.operation = 'MULTIPLY_ADD'
    jitter.inputs[1].default_value = 0.10
    jitter.inputs[2].default_value = -0.05
    nt.links.new(noise.outputs['Fac'], jitter.inputs[0])
    add = nt.nodes.new('ShaderNodeMath')
    add.operation = 'ADD'
    nt.links.new(sock(rough_mix.outputs, 'Result', 'VALUE'), add.inputs[0])
    nt.links.new(jitter.outputs[0], add.inputs[1])
    nt.links.new(add.outputs[0], bsdf.inputs['Roughness'])
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat


def floor_material():
    """Dark concrete: without colour variation the floor reads as a blank grey
    sheet, which is half of why the first attempt looked like a backdrop."""
    mat = bpy.data.materials.new('M_Floor')
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Metallic'].default_value = 0.0

    grain = nt.nodes.new('ShaderNodeTexNoise')     # fine speckle
    grain.inputs['Scale'].default_value = 90.0
    grain.inputs['Detail'].default_value = 6.0
    blotch = nt.nodes.new('ShaderNodeTexNoise')    # large patchiness
    blotch.inputs['Scale'].default_value = 3.5
    blotch.inputs['Detail'].default_value = 3.0

    col = nt.nodes.new('ShaderNodeMix')
    col.data_type = 'RGBA'
    sock(col.inputs, 'A', 'RGBA').default_value = (0.0085, 0.0090, 0.0110, 1.0)
    sock(col.inputs, 'B', 'RGBA').default_value = (0.0290, 0.0280, 0.0300, 1.0)
    nt.links.new(blotch.outputs['Fac'], sock(col.inputs, 'Factor', 'VALUE'))
    nt.links.new(sock(col.outputs, 'Result', 'RGBA'),
                 bsdf.inputs['Base Color'])

    r = nt.nodes.new('ShaderNodeMapRange')
    r.inputs['To Min'].default_value = 0.30
    r.inputs['To Max'].default_value = 0.62
    nt.links.new(grain.outputs['Fac'], r.inputs['Value'])
    nt.links.new(r.outputs['Result'], bsdf.inputs['Roughness'])
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat


def setup_world(haze):
    sc = bpy.context.scene
    w = bpy.data.worlds.new('W')
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputWorld')
    bg = nt.nodes.new('ShaderNodeBackground')
    bg.inputs['Color'].default_value = (0.0030, 0.0035, 0.0055, 1.0)
    bg.inputs['Strength'].default_value = 1.0
    nt.links.new(bg.outputs['Background'], out.inputs['Surface'])
    vs = nt.nodes.new('ShaderNodeVolumeScatter')
    vs.inputs['Color'].default_value = (0.55, 0.62, 0.75, 1.0)
    vs.inputs['Density'].default_value = haze
    vs.inputs['Anisotropy'].default_value = 0.45
    nt.links.new(vs.outputs['Volume'], out.inputs['Volume'])


def add_area(name, loc, target, energy, size, color, spread=180.0):
    d = bpy.data.lights.new(name, type='AREA')
    d.energy = energy
    d.size = size
    d.color = color
    d.spread = math.radians(spread)
    d.use_shadow = True
    ob = bpy.data.objects.new(name, d)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat(
        '-Z', 'Y').to_euler()
    return ob


def add_spot(name, loc, target, energy, color, cone, blend=0.55):
    d = bpy.data.lights.new(name, type='SPOT')
    d.energy = energy
    d.color = color
    d.spot_size = math.radians(cone)
    d.spot_blend = blend
    d.shadow_soft_size = 0.05
    d.use_shadow = True
    ob = bpy.data.objects.new(name, d)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat(
        '-Z', 'Y').to_euler()
    return ob


def light_rig(preset, c):
    """c = centre of the pair on the table. Distances are in metres, watts are
    small on purpose: the lights sit ~1 m away and the floor is meant to fall
    off into darkness rather than turn into a white studio backdrop."""
    if preset == 'studio':
        add_area('Key', (c.x - 0.50, c.y - 0.42, c.z + 0.62), c,
                 16.0, 0.70, (1.00, 0.97, 0.92))
        add_area('Rim', (c.x + 0.78, c.y + 0.72, c.z + 0.36), c,
                 18.0, 0.28, (1.00, 0.74, 0.48))
        add_area('Fill', (c.x + 0.35, c.y - 0.80, c.z + 0.28), c,
                 3.0, 1.40, (0.62, 0.74, 1.00))
        add_spot('Shaft', (c.x - 1.05, c.y + 1.10, c.z + 1.05),
                 (c.x + 0.05, c.y + 0.10, c.z), 26.0,
                 (1.00, 0.90, 0.74), 50.0, blend=0.70)
    else:                                   # dramatic: low key, strong backlight
        add_area('Key', (c.x - 0.62, c.y - 0.34, c.z + 0.46), c,
                 12.0, 0.55, (0.92, 0.95, 1.00))
        add_area('Rim', (c.x + 0.48, c.y + 0.62, c.z + 0.22), c,
                 46.0, 0.22, (1.00, 0.68, 0.38))
        add_area('Fill', (c.x + 0.10, c.y - 0.95, c.z + 0.24), c,
                 2.0, 1.60, (0.55, 0.68, 1.00))
        add_spot('Shaft', (c.x - 1.35, c.y + 1.20, c.z + 1.00),
                 (c.x + 0.40, c.y - 0.20, c.z), 120.0,
                 (1.00, 0.84, 0.60), 30.0, blend=0.35)


def setup_render(view_transform, haze):
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
    sc.eevee.fast_gi_method = 'GLOBAL_ILLUMINATION'
    sc.eevee.use_volumetric_shadows = True
    sc.eevee.volumetric_samples = 128
    sc.eevee.volumetric_shadow_samples = 32
    sc.eevee.volumetric_start = 0.05
    sc.eevee.volumetric_end = 12.0
    sc.view_settings.view_transform = view_transform
    setup_world(haze)
    return sc


def lay_on_table(ob, yaw_deg, xy):
    """Thin axis Y becomes world up, then spin on the table and drop the lowest
    vertex onto z = 0 so the item really rests on the floor. -90 (not +90) so
    the pistol grip, which is authored downwards, ends up pointing towards the
    camera instead of away from it."""
    ob.rotation_euler = (math.radians(-90.0), 0.0, math.radians(yaw_deg))
    bpy.context.view_layer.update()
    vs = [ob.matrix_world @ v.co for v in ob.data.vertices]
    ctr = Vector(((min(v.x for v in vs) + max(v.x for v in vs)) * 0.5,
                  (min(v.y for v in vs) + max(v.y for v in vs)) * 0.5, 0.0))
    ob.location = (ob.location.x + xy[0] - ctr.x,
                   ob.location.y + xy[1] - ctr.y,
                   -min(v.z for v in vs))
    bpy.context.view_layer.update()


def world_verts(obs):
    deps = bpy.context.evaluated_depsgraph_get()
    out = []
    for ob in obs:
        oe = ob.evaluated_get(deps)
        me = oe.to_mesh()
        out += [oe.matrix_world @ v.co for v in me.vertices]
        oe.to_mesh_clear()
    return out


def frame_camera(cam, verts, fill, drop, az, el):
    """Pull the camera back along its axis until every vertex sits inside
    `fill` of the frame; `drop` pushes the pair below the centre line."""
    fwd = Vector((math.cos(math.radians(az)) * math.cos(math.radians(el)),
                  math.sin(math.radians(az)) * math.cos(math.radians(el)),
                  math.sin(math.radians(el))))    # camera sits along +fwd
    view = -fwd
    right = view.cross(Vector((0, 0, 1))).normalized()
    up = right.cross(view).normalized()
    mn = Vector((min(v.x for v in verts), min(v.y for v in verts),
                 min(v.z for v in verts)))
    mx = Vector((max(v.x for v in verts), max(v.y for v in verts),
                 max(v.z for v in verts)))
    C = (mn + mx) * 0.5
    half_w = math.tan(cam.data.angle * 0.5)
    half_h = half_w * RES_Y / float(RES_X)
    t = 0.0
    for v in verts:
        p = v - C
        x, y, z = p.dot(right), p.dot(up), p.dot(fwd)
        t = max(t, z + abs(x) / (half_w * fill), z + abs(y) / (half_h * fill))
    cam.location = C + fwd * t + up * (drop * t * half_h)
    cam.rotation_euler = view.to_track_quat('-Z', 'Y').to_euler()
    cam.data.clip_start = max(0.01, t * 0.02)
    cam.data.clip_end = t + 60.0
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = t
    cam.data.dof.aperture_fstop = 8.0
    return C, t


def build(preset, chamfer, view_transform, az, el, lens):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    haze = 0.004 if preset == 'studio' else 0.010
    sc = setup_render(view_transform, haze)

    mat = weapon_material()
    obs = []
    for path, name, yaw, xy in LAYOUT:
        ob = load_from_blend(path, name)
        if chamfer:
            clean_and_chamfer(ob, CHAMFER)
        ob.data.materials.clear()
        ob.data.materials.append(mat)
        lay_on_table(ob, yaw, xy)
        obs.append(ob)

    bpy.ops.mesh.primitive_plane_add(size=40.0, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = 'Floor'
    floor.data.materials.clear()
    floor.data.materials.append(floor_material())

    cd = bpy.data.cameras.new('HeroCam')
    cd.lens = lens                      # long lens: no wide-angle distortion
    cd.sensor_width = 36.0
    cam = bpy.data.objects.new('HeroCam', cd)
    sc.collection.objects.link(cam)
    sc.camera = cam
    verts = world_verts(obs)
    C, t = frame_camera(cam, verts, 0.80, 0.02, az, el)
    light_rig(preset, C)
    return sc, cam, obs, verts, C, t


def check_inside(cam, verts):
    """Analytic proof that nothing is cropped: project every vertex."""
    m = cam.matrix_world
    fwd = (m.to_quaternion() @ Vector((0, 0, -1))).normalized()
    right = (m.to_quaternion() @ Vector((1, 0, 0))).normalized()
    up = (m.to_quaternion() @ Vector((0, 1, 0))).normalized()
    half_w = math.tan(cam.data.angle * 0.5)
    half_h = half_w * RES_Y / float(RES_X)
    xs, ys = [], []
    for v in verts:
        p = v - cam.location
        d = p.dot(fwd)
        xs.append((p.dot(right) / d / half_w * 0.5 + 0.5) * RES_X)
        ys.append((0.5 - p.dot(up) / d / half_h * 0.5) * RES_Y)
    return (min(xs), RES_X - max(xs), min(ys), RES_Y - max(ys))


def verify(path, cam, verts):
    if not os.path.isfile(path):
        return False, 'file missing'
    img = bpy.data.images.load(path)
    try:
        w, h = img.size
        if (w, h) != (RES_X, RES_Y):
            return False, 'size %dx%d' % (w, h)
        buf = np.empty(w * h * img.channels, dtype=np.float32)
        img.pixels.foreach_get(buf)
        a = buf.reshape(h, w, img.channels)
        if img.channels == 4 and a[:, :, 3].min() < 0.999:
            return False, 'not opaque'
        lum = a[:, :, :3].max(axis=2)   # stored sRGB scale, not linear
        info = ('tone %.0f..%.0f/255, mean %.0f, blown %.2f%%'
                % (lum.min() * 255, lum.max() * 255, lum.mean() * 255,
                   100.0 * (lum > 0.99).mean()))
    finally:
        bpy.data.images.remove(img)
    l, r, t, b = check_inside(cam, verts)
    if min(l, r, t, b) < 8:
        return False, 'cropped (margins %.0f/%.0f/%.0f/%.0f px)' % (l, r, t, b)
    return True, ('%s; free margins left %.0f right %.0f top %.0f bottom %.0f px'
                  % (info, l, r, t, b))


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    names = list(VARIANTS)
    if '--only' in argv:
        names = argv[argv.index('--only') + 1].split(',')
    os.makedirs(OUT_DIR, exist_ok=True)
    bad = 0
    for name in names:
        preset, chamfer, vt, az, el, lens = VARIANTS[name]
        sc, cam, obs, verts, C, t = build(preset, chamfer, vt, az, el, lens)
        print('%s: preset=%s chamfer=%s view=%s, camera %.2f m from the pair '
              '(lens %.0f mm, azimuth %.0f deg, elevation %.0f deg)'
              % (name, preset, chamfer, vt, t, cam.data.lens, az, el))
        path = OUT_DIR + name + '.png'
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
        ok, info = verify(path, cam, verts)
        bad += 0 if ok else 1
        print('HERO %-30s %s %s' % (name, 'PASS' if ok else 'FAIL', info))
        print('  ->', path)
        print('-' * 70)
    print('SUMMARY', 'ALL PASS' if not bad else '%d FAILED' % bad)
    if bad:
        sys.exit(1)


main()
