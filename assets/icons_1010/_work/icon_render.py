"""Item icons for the bag and the shop in the manner of T_Item_Pistol.png (256 x 256, RGBA, object in three quarters, large, clear background,
contrast light, dark outline along the silhouette).  Cycles render at 1024 on a clear film, outline = widened silhouette, then 4 -> 1 reduction.
Run: blender.exe -b --factory-startup --python icon_render.py -- <shotgun|ammo|walkie>
"""
import bpy, bmesh, sys, math, os
import numpy as np
from mathutils import Vector, Matrix
sys.path.insert(0, 'E:/game-dev-team/assets/scientist_base/_work')
import sb
OUT = 'E:/game-dev-team/assets/icons_1010/'
TMP = OUT + '_work/'
SIZE, SS = 256, 4                                               # as T_Item_Pistol.png (measured: 256 x 256, 4 channels)
MARGIN = 11                                                      # clear pixels around the object in the sample
LINE = 2.25                                                      # outline width in pixels of the finished icon
LINE_COL = np.array([0.055, 0.04, 0.035])
mode = sb.args()[0]
sb.empty()
sc = bpy.context.scene
rig = bpy.data.objects.new('rig', None); sc.collection.objects.link(rig)


def lib_objects(path, names=None):
    with bpy.data.libraries.load(path, link=False) as (src, dst):
        dst.objects = [n for n in src.objects if names is None or n in names]
    return [o for o in dst.objects if o is not None]


def smooth(ob, deg=38):
    me = ob.data
    if 'custom_normal' in me.attributes:
        me.attributes.remove(me.attributes['custom_normal'])
    for p in me.polygons:
        p.use_smooth = True
    me.set_sharp_from_angle(angle=math.radians(deg))


def principled(name, colour, rough, metal=0.0):
    mat = bpy.data.materials.new(name); mat.use_nodes = True
    b = mat.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*colour, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    return mat, b


def noise_colour(mat, b, dark, light, map_scale, noise_scale, lo=0.35, hi=0.7):
    """Two tones mixed by noise in the frame of the rig (grain along the object, does not move with the camera turn)."""
    nt = mat.node_tree
    tc = nt.nodes.new('ShaderNodeTexCoord'); tc.object = rig
    mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = map_scale
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = noise_scale; nz.inputs['Detail'].default_value = 5
    rp = nt.nodes.new('ShaderNodeValToRGB'); rp.color_ramp.elements[0].position = lo; rp.color_ramp.elements[0].color = (*dark, 1)
    rp.color_ramp.elements[1].position = hi; rp.color_ramp.elements[1].color = (*light, 1)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], nz.inputs['Vector'])
    nt.links.new(nz.outputs['Fac'], rp.inputs['Fac']); nt.links.new(rp.outputs['Color'], b.inputs['Base Color'])


obs = []
if mode == 'shotgun':
    SRC = sb.SRCD + 'low-poly-toz-34/'
    for o in lib_objects(SRC + 'source/toz34.blend'):
        if o.type != 'MESH' or o.name in ('12/76', '1276') or 'extractor' in o.name:
            print('LEFT OUT', o.name, o.type); continue
        sc.collection.objects.link(o); obs.append(o)
    bpy.context.view_layer.update()                             # world matrices of the loaded parts are not there before this
    print('PARTS', [(o.name, sb.tri_count(o)) for o in obs], 'sum', sum(sb.tri_count(o) for o in obs))
    steel, bs = principled('steel', (0.10, 0.11, 0.135), 0.30, 0.85); noise_colour(steel, bs, (0.022, 0.025, 0.035), (0.10, 0.11, 0.14), (0.6, 2.5, 2.5), 3.0)
    dark, _ = principled('dark', (0.03, 0.03, 0.035), 0.4, 0.5)
    bright, _ = principled('bright', (0.55, 0.55, 0.57), 0.3, 0.9)
    wood, bw = principled('wood', (0.33, 0.14, 0.05), 0.38); noise_colour(wood, bw, (0.115, 0.040, 0.014), (0.36, 0.145, 0.045), (0.22, 3.5, 3.5), 3.2, 0.3, 0.72)
    chk, bc = principled('checker', (0.20, 0.08, 0.03), 0.6)
    nimg = bpy.data.images.load(SRC + 'textures/mesh2.png'); nimg.colorspace_settings.name = 'Non-Color'
    tn = chk.node_tree.nodes.new('ShaderNodeTexImage'); tn.image = nimg
    nm = chk.node_tree.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = 1.6
    chk.node_tree.links.new(tn.outputs['Color'], nm.inputs['Color']); chk.node_tree.links.new(nm.outputs['Normal'], bc.inputs['Normal'])
    swap = {'1b': steel, '2b': dark, '1w': bright, '1wo': wood, '1wo mesh1': chk}
    for o in obs:
        for s in o.material_slots:
            print('MATERIAL %-22s %-10s -> %s' % (o.name, s.material.name, swap[s.material.name].name)); s.material = swap[s.material.name]
        smooth(o)
    # muzzle is +X in the source: turn it a little to the camera, show the top, lay the gun along the diagonal of the frame
    BASE, YAW, PITCH, ROLL = Matrix(), -56.0, 24.0, -76.0; MARGIN = 3  # 10.10: Rinat - the icon looked small, so the gun is foreshortened (muzzle to the camera) and fills the frame
elif mode == 'ammo':
    o = lib_objects(sb.SRCD + 'low-poly-toz-34/source/toz34.blend', ('12/76',))[0]
    me = o.data; mw = o.matrix_basis.copy()
    me.transform(mw)
    if mw.determinant() < 0:
        me.flip_normals()
    names = [s.material.name for s in o.material_slots]
    co = np.array([v.co[:] for v in me.vertices]); mn, mx = co.min(0), co.max(0); ax = int(np.argmax(mx - mn))
    cb = np.array([p.center[ax] for p in me.polygons if names[p.material_index] == 'blt']).mean()
    brass_low = cb < (mn[ax] + mx[ax]) / 2
    print('SHELL source %d tris, size %s, long axis %s, brass at the %s end, materials %s' % (sb.tri_count(o), (mx - mn).round(3), 'XYZ'[ax], 'low' if brass_low else 'high', names))
    # standing shell: axis +Z, brass head on the ground, centred
    e = [Vector((0, 0, 0)) for _ in range(3)]; other = [i for i in range(3) if i != ax]
    T = Matrix.Identity(4)
    sgn = 1.0 if brass_low else -1.0
    rows = np.zeros((3, 3)); rows[2, ax] = sgn; rows[0, other[0]] = 1.0; rows[1, other[1]] = 1.0
    if np.linalg.det(rows) < 0:
        rows[1] *= -1
    R = Matrix(rows.tolist()).to_4x4()
    me.transform(R)
    co = np.array([v.co[:] for v in me.vertices]); mn, mx = co.min(0), co.max(0)
    me.transform(Matrix.Translation((-(mn[0] + mx[0]) / 2, -(mn[1] + mx[1]) / 2, -mn[2])))
    d = float(mx[0] - mn[0]); L = float(mx[2] - mn[2]); r = d / 2
    print('SHELL standing: diameter %.3f length %.3f (source units)' % (d, L))
    red, br = principled('hull', (0.72, 0.05, 0.035), 0.42); noise_colour(red, br, (0.50, 0.025, 0.02), (0.86, 0.085, 0.05), (2.0, 2.0, 0.5), 6.0, 0.25, 0.75)
    brass, bb = principled('brass', (0.90, 0.62, 0.22), 0.28, 0.9); noise_colour(brass, bb, (0.62, 0.38, 0.10), (1.0, 0.74, 0.30), (3.0, 3.0, 3.0), 5.0, 0.3, 0.75)
    for s in o.material_slots:
        s.material = red if s.material.name == '2r' else brass
    smooth(o, 50)
    place = [Matrix.Translation((-0.52 * d, 0.30 * d, 0)) @ Matrix.Rotation(math.radians(20), 4, 'Z'),
             Matrix.Translation((0.60 * d, 0.62 * d, 0)) @ Matrix.Rotation(math.radians(140), 4, 'Z'),
             # the third one lies in front: axis level, brass head to the left and a little to the camera
             Matrix.Translation((0.50 * d, -0.95 * d, r)) @ Matrix.Rotation(math.radians(-22), 4, 'Z') @ Matrix.Rotation(math.radians(-90), 4, 'Y') @ Matrix.Translation((0, 0, -L / 2))]
    for i, M in enumerate(place):
        c = bpy.data.objects.new('shell%d' % i, me); sc.collection.objects.link(c); c.matrix_world = M; obs.append(c)
    bpy.data.objects.remove(o)
    BASE, YAW, PITCH, ROLL = Matrix(), 0.0, 30.0, 0.0
elif mode == 'walkie':
    o = lib_objects(sb.WORK + 'walkie_work.blend', ('SM_WalkieTalkie',))[0]
    sc.collection.objects.link(o); obs.append(o)
    img = bpy.data.images.load(sb.WORK + '_walkie_icon_D.png')
    mat = sb.tex_material(o, 'icon', img); mat.use_backface_culling = False
    mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.5
    print('WALKIE %d tris, texture %dx%d' % (sb.tri_count(o), *img.size))
    # the model lies on its back with the antenna to +Y: stand it up (face to the camera), turn to three quarters, lean along the diagonal
    BASE, YAW, PITCH, ROLL = Matrix.Rotation(math.radians(90), 4, 'X'), -32.0, 14.0, -44.0
for o in obs:
    mwo = o.matrix_world.copy(); o.parent = rig; o.matrix_parent_inverse = Matrix(); o.matrix_basis = mwo
rig.matrix_world = Matrix.Rotation(math.radians(ROLL), 4, 'Y') @ Matrix.Rotation(math.radians(PITCH), 4, 'X') @ Matrix.Rotation(math.radians(YAW), 4, 'Z') @ BASE
bpy.context.view_layer.update()

# ---- camera: orthographic, from -Y; the object fills the frame up to the margin of the sample
P = np.concatenate([np.array([o.matrix_world @ v.co for v in o.data.vertices]) for o in obs])
mn, mx = P.min(0), P.max(0); span = max(mx[0] - mn[0], mx[2] - mn[2]); R = float(np.linalg.norm(mx - mn))
cd = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', cd); sc.collection.objects.link(cam); sc.camera = cam
cd.type = 'ORTHO'; cd.ortho_scale = span * SIZE / (SIZE - 2 * (MARGIN + LINE + 0.5)); cd.clip_start = R * 0.01; cd.clip_end = R * 10
cam.location = ((mn[0] + mx[0]) / 2, mn[1] - R * 2, (mn[2] + mx[2]) / 2); cam.rotation_euler = (math.radians(90), 0, 0)
print('FRAME object %.3f x %.3f in the picture plane, ortho scale %.3f' % (mx[0] - mn[0], mx[2] - mn[2], cd.ortho_scale))
def sun(name, travel, energy, colour=(1, 1, 1), angle=6.0):
    l = bpy.data.lights.new(name, 'SUN'); l.energy = energy; l.color = colour; l.angle = math.radians(angle)
    ob = bpy.data.objects.new(name, l); sc.collection.objects.link(ob)
    ob.rotation_euler = Vector(travel).normalized().to_track_quat('-Z', 'Y').to_euler()
KEY, FILL, RIM, AMB = {'shotgun': (6.0, 2.2, 5.0, 1.3), 'ammo': (2.6, 0.8, 2.4, 0.45), 'walkie': (4.4, 1.4, 3.0, 1.15)}[mode]
sun('key', (0.55, 0.62, -0.56), KEY, (1.0, 0.97, 0.92))         # from the upper left, from the camera side
sun('fill', (-0.75, 0.55, -0.10), FILL, (0.85, 0.92, 1.0), 20)
sun('rim', (-0.35, -0.70, -0.62), RIM, (1.0, 0.95, 0.88))        # from behind and above: a light edge on the top
w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs[0].default_value = (0.75, 0.78, 0.85, 1); w.node_tree.nodes['Background'].inputs[1].default_value = AMB
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 96; sc.cycles.use_denoising = True
sc.render.film_transparent = True; sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'
sc.render.resolution_x = sc.render.resolution_y = SIZE * SS; sc.render.resolution_percentage = 100
sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGBA'; sc.render.image_settings.color_depth = '8'
raw = TMP + '_raw_%s.png' % mode
sc.render.filepath = raw
bpy.ops.render.render(write_still=True)

# ---- outline and reduction
im = bpy.data.images.load(raw, check_existing=False); im.alpha_mode = 'CHANNEL_PACKED'
px = np.array(im.pixels[:], dtype=np.float32).reshape(SIZE * SS, SIZE * SS, 4)
a = px[..., 3]; rgb = px[..., :3]
CON, SAT = {'shotgun': (1.12, 1.15), 'ammo': (1.18, 1.10), 'walkie': (1.15, 1.25)}[mode]
g = rgb.mean(2, keepdims=True); rgb = np.clip(((g + (rgb - g) * SAT) - 0.5) * CON + 0.5, 0, 1)
rad = LINE * SS; k = int(math.ceil(rad)); wide = a.copy(); H = a.shape[0]
pad = np.pad(a, k)
for dy in range(-k, k + 1):
    for dx in range(-k, k + 1):
        if (dx or dy) and dx * dx + dy * dy <= rad * rad:
            wide = np.maximum(wide, pad[k + dy:k + dy + H, k + dx:k + dx + H])
pm = rgb * a[..., None] + LINE_COL * (wide - a)[..., None]
pm = pm.reshape(SIZE, SS, SIZE, SS, 3).mean((1, 3)); oa = wide.reshape(SIZE, SS, SIZE, SS).mean((1, 3))
out = np.zeros((SIZE, SIZE, 4), np.float32)
out[..., :3] = np.where(oa[..., None] > 1e-4, pm / np.maximum(oa, 1e-4)[..., None], LINE_COL)
out[..., 3] = oa
name = {'shotgun': 'T_Item_Shotgun', 'ammo': 'T_Item_Ammo12g', 'walkie': 'T_Item_WalkieTalkie'}[mode]
res = bpy.data.images.new(name, SIZE, SIZE, alpha=True); res.alpha_mode = 'CHANNEL_PACKED'
res.pixels.foreach_set(out.ravel()); res.filepath_raw = OUT + name + '.png'; res.file_format = 'PNG'
sc.render.image_settings.color_mode = 'RGBA'
res.save()
ys, xs = np.where(oa > 0.5); op = oa > 0.9; lum = (out[..., :3] * [0.2126, 0.7152, 0.0722]).sum(2)
print('ICON %s.png %dx%d | covered share %.3f | box x %d..%d y %d..%d | brightness mean %.3f, tenth part darker than %.3f, tenth part lighter than %.3f | %.1f KB' % (
    name, SIZE, SIZE, op.mean(), xs.min(), xs.max(), ys.min(), ys.max(), lum[op].mean(), np.percentile(lum[op], 10), np.percentile(lum[op], 90), os.path.getsize(OUT + name + '.png') / 1024))
