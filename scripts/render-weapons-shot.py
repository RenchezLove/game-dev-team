"""One-off promo frame for the Telegram channel: knife + pistol, strict
orthographic profile, dark background (Rinat request 08-09).

Differs from the production icon stand (scripts/render-icons.py, DO NOT EDIT)
on purpose:
  * ORTHOGRAPHIC camera looking along +Y (Blender front view) - no perspective
    convergence, world +X reads to the right, world +Z is up;
  * ONE common scale for both items - they are placed side by side at their
    real authored size and the camera frames the pair, so the size relation
    between knife and pistol is the true one (the icon stand instead blows up
    every item to ~85% of its own frame);
  * opaque dark backdrop (icons are rendered on alpha).
Borrowed from the icon stand unchanged: append-from-source-.blend loading and
the key+fill sun scheme.

Headless run (Blender 5.1.2, ADR-021):
  E:/Programs/Blender/blender.exe -b --factory-startup \
      --python E:/game-dev-team/scripts/render-weapons-shot.py

Source .blend files are only appended from, never written.
Output: E:/game-dev-team/reports/renders/knife-pistol-profile*.png
"""
import bpy
import math
import os
import numpy as np
from mathutils import Vector, Matrix

OUT_DIR = 'E:/game-dev-team/reports/renders/'
A = 'E:/game-dev-team/assets/'
LEFT = (A + 'knife/SM_Knife.blend', 'SM_Knife')      # knife on the left
RIGHT = (A + 'pistol/SM_Pistol.blend', 'SM_Pistol')  # pistol on the right

# (name, width, height) - same shot, two aspects; wider one is the pick
VARIANTS = [('knife-pistol-profile', 1920, 900),
            ('knife-pistol-profile-16x9', 1920, 1080)]

FILL_X = 0.84        # pair spans this fraction of the frame width
FILL_Y = 0.72        # ...and never more than this fraction of its height
GAP_FRAC = 0.16      # air between the two items, fraction of their total length

BG_CORE = (0.0060, 0.0060, 0.0080)   # linear; soft glow right behind the pair
BG_EDGE = (0.0012, 0.0012, 0.0018)   # linear; near black at the frame corners

VIEW = Vector((0.0, 1.0, 0.0))       # camera looks this way (strict profile)
UP = Vector((0.0, 0.0, 1.0))
RIGHT_AX = Vector((1.0, 0.0, 0.0))
CAM_BACK = 4.0                       # ortho: distance is framing-neutral


def load_from_blend(path, obname):
    """Append the object from the canonical source .blend (never written).
    Parent/modifiers are stripped so the mesh sits at rest with identity
    transform - same helper as the icon stand."""
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


def vcol_material():
    mat = bpy.data.materials.get('M_Shot') or bpy.data.materials.new('M_Shot')
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


def world_bounds(ob):
    """(min, max) of the evaluated mesh in world space."""
    bpy.context.view_layer.update()
    deps = bpy.context.evaluated_depsgraph_get()
    oe = ob.evaluated_get(deps)
    tmp = oe.to_mesh()
    vs = [oe.matrix_world @ v.co for v in tmp.vertices]
    mn = Vector((min(v.x for v in vs), min(v.y for v in vs),
                 min(v.z for v in vs)))
    mx = Vector((max(v.x for v in vs), max(v.y for v in vs),
                 max(v.z for v in vs)))
    oe.to_mesh_clear()
    return mn, mx


def setup_scene(res_x, res_y):
    sc = bpy.context.scene
    try:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    except Exception:
        sc.render.engine = 'BLENDER_EEVEE'
    sc.render.resolution_x = res_x
    sc.render.resolution_y = res_y
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = True      # world lights but never shows;
    sc.render.image_settings.file_format = 'PNG'   # the backdrop plane below
    sc.render.image_settings.color_mode = 'RGB'    # is what fills the frame
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
    bg.inputs[0].default_value = (0.20, 0.20, 0.22, 1.0)   # ambient only
    bg.inputs[1].default_value = 0.55

    cd = bpy.data.cameras.new('ShotCam')
    cd.type = 'ORTHO'
    cam = bpy.data.objects.new('ShotCam', cd)
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.rotation_euler = (math.radians(90.0), 0.0, 0.0)   # -Z faces +Y, +Z up

    for name, energy, soft, aim in (
            ('Key', 3.0, 15, VIEW + 0.50 * RIGHT_AX - 0.60 * UP),
            ('Fill', 1.2, 60, VIEW - 0.50 * RIGHT_AX - 0.15 * UP)):
        d = bpy.data.lights.new(name, type='SUN')
        d.energy = energy
        d.angle = math.radians(soft)
        so = bpy.data.objects.new(name, d)
        sc.collection.objects.link(so)
        so.rotation_euler = aim.normalized().to_track_quat('-Z', 'Y').to_euler()
    return sc, cam


def add_backdrop(center, width, height):
    """Emission-only plane behind the pair: dark, with a soft radial falloff so
    the near-black parts of the pistol still separate from the background."""
    bpy.ops.mesh.primitive_plane_add(size=2.0, location=(0, 0, 0))
    pl = bpy.context.active_object
    pl.name = 'Backdrop'
    pl.rotation_euler = (math.radians(90.0), 0.0, 0.0)   # face -Y (the camera)
    # local X/Y are the plane's own axes (local Y becomes world Z after the
    # rotation); 0.75 of the frame size = 1.5x overscan on every side
    pl.scale = (width * 0.75, height * 0.75, 1.0)
    pl.location = (center.x, center.y + 1.5, center.z)
    mat = bpy.data.materials.new('M_Backdrop')
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    em = nt.nodes.new('ShaderNodeEmission')
    em.inputs['Strength'].default_value = 1.0
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.30
    ramp.color_ramp.elements[0].color = BG_EDGE + (1.0,)
    ramp.color_ramp.elements[1].position = 1.0
    ramp.color_ramp.elements[1].color = BG_CORE + (1.0,)
    grad = nt.nodes.new('ShaderNodeTexGradient')
    grad.gradient_type = 'SPHERICAL'
    mapn = nt.nodes.new('ShaderNodeMapping')
    mapn.inputs['Location'].default_value = (-0.5, -0.5, -0.5)
    tc = nt.nodes.new('ShaderNodeTexCoord')
    nt.links.new(tc.outputs['Generated'], mapn.inputs['Vector'])
    nt.links.new(mapn.outputs['Vector'], grad.inputs['Vector'])
    nt.links.new(grad.outputs['Color'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], em.inputs['Color'])
    nt.links.new(em.outputs['Emission'], out.inputs['Surface'])
    pl.data.materials.clear()
    pl.data.materials.append(mat)
    return pl


def build(res_x, res_y):
    """Load both items at their real size, lay them out, frame the pair."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc, cam = setup_scene(res_x, res_y)
    mat = vcol_material()

    items = []
    for path, obname in (LEFT, RIGHT):
        ob = load_from_blend(path, obname)
        ob.rotation_euler = (0.0, 0.0, 0.0)   # authored forward +X, up +Z
        ob.data.materials.clear()
        ob.data.materials.append(mat)
        mn, mx = world_bounds(ob)
        items.append([ob, mn, mx])

    dims = [(mx - mn) for _, mn, mx in items]
    total_len = dims[0].x + dims[1].x
    gap = GAP_FRAC * total_len

    # left item ends at -gap/2, right item starts at +gap/2; both centred on z=0
    starts = [-gap * 0.5 - dims[0].x, gap * 0.5]
    for (ob, mn, mx), x0 in zip(items, starts):
        ob.location = (x0 - mn.x,
                       -(mn.y + mx.y) * 0.5,
                       -(mn.z + mx.z) * 0.5)

    bpy.context.view_layer.update()
    bounds = [world_bounds(ob) for ob, _, _ in items]
    x0 = min(b[0].x for b in bounds)
    x1 = max(b[1].x for b in bounds)
    z0 = min(b[0].z for b in bounds)
    z1 = max(b[1].z for b in bounds)
    cx, cz = (x0 + x1) * 0.5, (z0 + z1) * 0.5

    span_x, span_z = x1 - x0, z1 - z0
    ortho = max(span_x / FILL_X, (span_z / FILL_Y) * (res_x / float(res_y)))
    cam.data.ortho_scale = ortho
    cam.location = (cx, -CAM_BACK, cz)
    cam.data.clip_start = 0.01
    cam.data.clip_end = CAM_BACK + 10.0

    frame_h = ortho * res_y / float(res_x)
    add_backdrop(Vector((cx, 0.0, cz)), ortho, frame_h)
    return sc, cam, items, bounds, (ortho, cx, cz, gap)


def px(world_x, world_z, ortho, cx, cz, res_x, res_y):
    ppm = res_x / ortho                       # pixels per metre, both axes
    return ((world_x - cx) * ppm + res_x * 0.5,
            res_y * 0.5 - (world_z - cz) * ppm)


def verify(path, res_x, res_y, geom, ortho, cx, cz):
    """Read the written file back: real size, opaque, background dark, subject
    clear of every border, and every mesh vertex inside the frame with margin
    (the analytic part is shading-independent).

    NB on units: bpy image.pixels hands back the STORED 8-bit values / 255
    (sRGB-encoded here), not scene-linear - thresholds below are in that same
    stored scale, cross-checked against System.Drawing byte reads."""
    if not os.path.isfile(path):
        return False, 'file missing'
    BG_MAX = 0.11        # 28/255 - measured background tops out at 21/255
    img = bpy.data.images.load(path)
    try:
        w, h = img.size
        if (w, h) != (res_x, res_y):
            return False, 'size %dx%d' % (w, h)
        buf = np.empty(w * h * img.channels, dtype=np.float32)
        img.pixels.foreach_get(buf)
        a = buf.reshape(h, w, img.channels)     # row 0 = bottom of the image
        if img.channels == 4 and a[:, :, 3].min() < 0.999:
            return False, ('background not opaque (alpha min %.3f)'
                           % a[:, :, 3].min())
        lum = a[:, :, :3].max(axis=2)
        border = max(lum[0, :].max(), lum[h - 1, :].max(),
                     lum[:, 0].max(), lum[:, w - 1].max())
        if border > BG_MAX:
            return False, ('subject touches the border (%.0f/255)'
                           % (border * 255))
        lit = lum > BG_MAX
        if not lit.any():
            return False, 'nothing rendered'
        ys, xs = np.nonzero(lit)
        print('  background %.0f..%.0f/255, subject pixels %.0f..%.0f/255'
              % (lum[~lit].min() * 255, lum[~lit].max() * 255,
                 lum[lit].min() * 255, lum[lit].max() * 255))
        print('  subject pixel bbox x[%d..%d] y[%d..%d] in %dx%d - free '
              'margins left %d, right %d, bottom %d, top %d px'
              % (xs.min(), xs.max(), ys.min(), ys.max(), w, h,
                 xs.min(), w - 1 - xs.max(), ys.min(), h - 1 - ys.max()))
    finally:
        bpy.data.images.remove(img)

    margins = []
    for (mn, mx) in geom:
        pxs = [px(x, z, ortho, cx, cz, res_x, res_y)
               for x in (mn.x, mx.x) for z in (mn.z, mx.z)]
        margins.append(min(min(p[0] for p in pxs),
                           min(p[1] for p in pxs),
                           res_x - max(p[0] for p in pxs),
                           res_y - max(p[1] for p in pxs)))
    m = min(margins)
    if m < 8:
        return False, 'geometry margin only %.1f px' % m
    gap_px = (px(geom[1][0].x, 0, ortho, cx, cz, res_x, res_y)[0]
              - px(geom[0][1].x, 0, ortho, cx, cz, res_x, res_y)[0])
    if gap_px < 20:
        return False, 'items nearly touch (%.1f px)' % gap_px
    return True, 'margin %.0f px, gap between items %.0f px' % (m, gap_px)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    ok_all = True
    for name, res_x, res_y in VARIANTS:
        sc, cam, items, bounds, (ortho, cx, cz, gap) = build(res_x, res_y)
        for (ob, _, _), (mn, mx) in zip(items, bounds):
            d = mx - mn
            print('MODEL %-12s length(X) %.4f m  height(Z) %.4f m  '
                  'thickness(Y) %.4f m  tris %d'
                  % (ob.name, d.x, d.z, d.y, len(ob.data.loop_triangles)
                     or len(ob.data.polygons)))
        lk = (bounds[0][1] - bounds[0][0]).x
        lp = (bounds[1][1] - bounds[1][0]).x
        print('SCALE knife %.4f m vs pistol %.4f m -> pistol/knife = %.3f'
              % (lk, lp, lp / lk))
        print('FRAME %dx%d ortho_scale %.4f m (frame height %.4f m), '
              'gap %.4f m, camera ORTHO at (%.3f, %.1f, %.3f)'
              % (res_x, res_y, ortho, ortho * res_y / float(res_x), gap,
                 cx, -CAM_BACK, cz))
        path = OUT_DIR + name + '.png'
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
        ok, info = verify(path, res_x, res_y, bounds, ortho, cx, cz)
        ok_all = ok_all and ok
        print('SHOT %-28s %s %s' % (name, 'PASS' if ok else 'FAIL', info))
        print('  ->', path)
        print('-' * 60)
    print('SUMMARY', 'ALL PASS' if ok_all else 'FAILURES PRESENT')


main()
