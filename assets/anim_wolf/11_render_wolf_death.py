"""Preview renders for Anim_Wolf_Death: fall montage from the front-side and
the game camera, plus the final corpse from 4 views.

Run:  blender.exe -b _work/_qc_wolf_death.blend --factory-startup --python 11_render_wolf_death.py
"""
import bpy, os, math
import numpy as np
from mathutils import Vector, Matrix

OUT = 'E:/game-dev-team/assets/anim_wolf/'
REND = OUT + 'renders/'
TMP = OUT + '_work/_frames/'
TILE = 460
NAME = 'Anim_Wolf_Death'
FPS = 30
os.makedirs(TMP, exist_ok=True)
os.makedirs(REND, exist_ok=True)

arm = bpy.data.objects['WolfRig']
mesh_obj = bpy.data.objects['SK_Wolf']
sc = bpy.context.scene


def upd():
    bpy.context.view_layer.update()


# vertex-color material so the wolf renders in its real colours
me = mesh_obj.data
mat = bpy.data.materials.new('M_PreviewWolf')
mat.use_nodes = True
nt = mat.node_tree
bsdf = nt.nodes['Principled BSDF']
vc = nt.nodes.new('ShaderNodeVertexColor')
vc.layer_name = me.color_attributes[0].name
nt.links.new(vc.outputs['Color'], bsdf.inputs['Base Color'])
bsdf.inputs['Roughness'].default_value = 0.8
me.materials.clear()
me.materials.append(mat)

try:
    sc.render.engine = 'BLENDER_EEVEE_NEXT'
except Exception:
    sc.render.engine = 'BLENDER_EEVEE'
sc.render.resolution_x = sc.render.resolution_y = TILE
sc.render.resolution_percentage = 100
sc.render.image_settings.file_format = 'PNG'
sc.view_settings.view_transform = 'Standard'
sc.render.use_stamp = True
sc.render.use_stamp_frame = True
sc.render.use_stamp_note = True
sc.render.stamp_font_size = 26
for f in ('use_stamp_date', 'use_stamp_time', 'use_stamp_render_time', 'use_stamp_scene',
          'use_stamp_camera', 'use_stamp_filename', 'use_stamp_lens', 'use_stamp_marker',
          'use_stamp_memory', 'use_stamp_hostname', 'use_stamp_frame_range'):
    if hasattr(sc.render, f):
        setattr(sc.render, f, False)

w = bpy.data.worlds.get('W') or bpy.data.worlds.new('W')
sc.world = w
w.use_nodes = True
bg = w.node_tree.nodes.get('Background')
bg.inputs[0].default_value = (0.18, 0.19, 0.22, 1.0)
bg.inputs[1].default_value = 0.75

for nm, energy, rot in (('KeyS', 3.4, (math.radians(52), 0, math.radians(-40))),
                        ('FillS', 1.5, (math.radians(66), 0, math.radians(150))),
                        ('RimS', 1.1, (math.radians(20), 0, math.radians(60)))):
    dl = bpy.data.lights.new(nm, type='SUN')
    dl.energy = energy
    o = bpy.data.objects.new(nm, dl)
    sc.collection.objects.link(o)
    o.rotation_euler = rot

bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
ground = bpy.context.active_object
gm = bpy.data.materials.new('M_Ground')
gm.use_nodes = True
gm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.13, 0.14, 0.13, 1)
gm.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.95
ground.data.materials.append(gm)

cam_data = bpy.data.cameras.new('PrevCam')
cam_data.sensor_fit = 'HORIZONTAL'
cam_data.angle_x = math.radians(40.0)
cam = bpy.data.objects.new('PrevCam', cam_data)
sc.collection.objects.link(cam)
sc.camera = cam

TARGET = Vector((0.0, 0.0, 0.35))


def place_cam(azimuth_deg, elevation_deg, dist, up_hint=None):
    a, e = math.radians(azimuth_deg), math.radians(elevation_deg)
    d = Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))
    loc = TARGET + d * dist
    look = (TARGET - loc).normalized()
    up = Vector(up_hint if up_hint is not None else (0, 0, 1))
    up = up - look * up.dot(look)
    up.normalize()
    zc = -look
    xc = up.cross(zc)
    cam.matrix_world = Matrix(((xc.x, up.x, zc.x, loc.x),
                               (xc.y, up.y, zc.y, loc.y),
                               (xc.z, up.z, zc.z, loc.z),
                               (0, 0, 0, 1)))


# wolf faces +Y and falls onto its right side (left flank tips towards +X)
VIEWS = {
    'topdown': (180, 88, 4.2, (0, 1, 0)),
    'game': (0, 60, 4.2, None),
    'nose_on': (180, 10, 4.2, None),     # looking at the nose from +Y
    'fall_side': (-90, 12, 4.2, None),   # from +X: the side it falls towards
    'left_side': (90, 12, 4.2, None),
}


def shoot(frame, view, tag):
    ad = arm.animation_data
    act = bpy.data.actions[NAME]
    if ad.action is not act:
        ad.action = act
        if act.slots and ad.action_slot is None:
            ad.action_slot = act.slots[0]
    sc.frame_set(frame)
    upd()
    place_cam(*VIEWS[view])
    sc.render.stamp_note_text = tag
    path = '%s%s_%s_f%02d.png' % (TMP, NAME, view, frame)
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    return path


def montage(paths, out, cols):
    imgs = []
    for p in paths:
        im = bpy.data.images.load(p)
        im.colorspace_settings.name = 'Non-Color'
        imgs.append(im)
    w_, h = imgs[0].size
    rows = (len(imgs) + cols - 1) // cols
    canvas = np.zeros((rows * h, cols * w_, 4), dtype=np.float32)
    canvas[:, :, 3] = 1.0
    for i, im in enumerate(imgs):
        px = np.array(im.pixels[:], dtype=np.float32).reshape(h, w_, 4)
        r, c = divmod(i, cols)
        canvas[(rows - 1 - r) * h:(rows - r) * h, c * w_:(c + 1) * w_] = px
    out_img = bpy.data.images.new('mtg', width=cols * w_, height=rows * h, alpha=True)
    out_img.colorspace_settings.name = 'Non-Color'
    out_img.pixels = canvas.ravel()
    out_img.filepath_raw = out
    out_img.file_format = 'PNG'
    out_img.save()
    for im in imgs:
        bpy.data.images.remove(im)
    bpy.data.images.remove(out_img)
    print('MONTAGE %s %dx%d exists=%s' % (out, cols * w_, rows * h, os.path.exists(out)))


FRAMES = [1, 4, 8, 13, 17, 20, 24, 32]

for view, outname in (('nose_on', 'wolf_death_front.png'),
                      ('game', 'wolf_death_gamecam.png')):
    paths = []
    for f in FRAMES:
        t = (f - 1) / float(FPS)
        paths.append(shoot(f, view, 'f%d  %.3fs' % (f, t)))
    montage(paths, REND + outname, 4)

paths = [shoot(32, v, 'final ' + v) for v in ('topdown', 'game', 'fall_side', 'nose_on')]
montage(paths, REND + 'wolf_death_final.png', 2)

print('RENDER_DONE')
