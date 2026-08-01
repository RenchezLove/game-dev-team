"""Preview renders for Anim_Death_Humanoid: montage of the fall from the side
and from the real game camera angle, plus the final corpse pose from 4 views.

Run:  blender.exe -b _qc_death.blend --factory-startup --python 21_render_death.py
"""
import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from mathutils import Vector, Matrix
import acommon as A
from acommon import upd

OUT = 'E:/game-dev-team/assets/anim_humanoid/'
REND = OUT + 'renders/'
TMP = OUT + '_work/_frames/'
TILE = 460
NAME = 'Anim_Death_Humanoid'
os.makedirs(TMP, exist_ok=True)
os.makedirs(REND, exist_ok=True)

rig = A.get_rig()
meshes = [o for o in bpy.data.objects if o.type == 'MESH' and o.parent == rig]
print('character meshes:', [o.name for o in meshes])


def vcol_material(name, obj):
    layer = obj.data.color_attributes[0].name if obj.data.color_attributes else 'Col'
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        nt = mat.node_tree
        bsdf = nt.nodes['Principled BSDF']
        vc = nt.nodes.new('ShaderNodeVertexColor')
        vc.layer_name = layer
        nt.links.new(vc.outputs['Color'], bsdf.inputs['Base Color'])
        bsdf.inputs['Roughness'].default_value = 0.65
        bsdf.inputs['Metallic'].default_value = 0.0
    return mat


for ob in meshes:
    mat = vcol_material('M_PreviewBody_' + ob.name, ob)
    ob.data.materials.clear()
    ob.data.materials.append(mat)

sc = bpy.context.scene
try:
    sc.render.engine = 'BLENDER_EEVEE_NEXT'
except Exception:
    sc.render.engine = 'BLENDER_EEVEE'
sc.render.resolution_x = sc.render.resolution_y = TILE
sc.render.resolution_percentage = 100
sc.render.image_settings.file_format = 'PNG'
sc.view_settings.view_transform = 'Standard'
sc.render.film_transparent = False
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
    d = bpy.data.lights.new(nm, type='SUN')
    d.energy = energy
    o = bpy.data.objects.new(nm, d)
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

# body travels backward (+Y) and ends lying: aim between stand and corpse
TARGET = Vector((0.0, 0.25, 0.55))


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


FWD_UP = (0, -1, 0)
VIEWS = {
    'topdown': (180, 88, 5.2, FWD_UP),
    'game_back': (180, 60, 5.2, None),
    'game_front': (0, 60, 5.2, None),
    'side': (-90, 10, 5.2, None),
    'front': (0, 10, 5.2, None),
}


def shoot(frame, view, tag):
    ad = rig.animation_data
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
    print('MONTAGE %s %dx%d  exists=%s' % (out, cols * w_, rows * h, os.path.exists(out)))


FRAMES = [1, 4, 6, 9, 14, 17, 19, 22, 26, 34]

for view, outname in (('side', 'death_humanoid_side.png'),
                      ('game_back', 'death_humanoid_gamecam.png')):
    paths = []
    for f in FRAMES:
        t = (f - 1) / float(A.FPS)
        paths.append(shoot(f, view, 'f%d  %.3fs' % (f, t)))
    montage(paths, REND + outname, 5)

paths = [shoot(34, v, 'final ' + v) for v in ('topdown', 'game_back', 'side', 'front')]
montage(paths, REND + 'death_humanoid_final.png', 2)

print('RENDER_DONE')
