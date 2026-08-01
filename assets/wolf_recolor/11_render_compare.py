"""Before/after renders: old brown SK_Wolf (phase3-assets) vs new grey SK_Wolf
(assets/wolf_recolor). Both stand side by side, brown LEFT, grey RIGHT.

Colour display note (project lesson): the FBX holds raw linear numbers; on
re-import Blender puts them in .color_srgb. To render the INTENDED colour the
raw value must be copied into .color (the linear view). Done via a 'ColView'
attribute per mesh.

Run:  blender.exe -b --factory-startup --python 11_render_compare.py
"""
import bpy, os, math, addon_utils
from mathutils import Vector, Matrix

OUT = 'E:/game-dev-team/assets/wolf_recolor/'
REND = OUT + 'renders/'
OLD_FBX = 'E:/ForGameLead(Materials)/phase3-assets/SK_Wolf.fbx'
NEW_FBX = OUT + 'SK_Wolf.fbx'
os.makedirs(REND, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
addon_utils.enable('io_scene_fbx')
sc = bpy.context.scene


def load(fbx, tag, x):
    """Show the BIND mesh only: the FBX armature import mangles the pose
    (first compare render came out with two smeared overlapping wolves), so
    the armature modifier and the rig are dropped - colours live on the mesh."""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=fbx)
    new = [o for o in bpy.data.objects if o not in before]
    mesh = [o for o in new if o.type == 'MESH'][0]
    for md in list(mesh.modifiers):
        mesh.modifiers.remove(md)
    mesh.parent = None
    mesh.matrix_world = Matrix.Translation((x, 0.0, 0.0))
    for o in new:
        if o is not mesh:
            bpy.data.objects.remove(o, do_unlink=True)
    me = mesh.data
    src = me.color_attributes[0]
    view = me.color_attributes.new('ColView', 'FLOAT_COLOR', 'CORNER')
    for i, d in enumerate(src.data):
        view.data[i].color = tuple(d.color_srgb)   # raw -> linear view = intended
    mat = bpy.data.materials.new('M_' + tag)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes['Principled BSDF']
    vc = nt.nodes.new('ShaderNodeVertexColor')
    vc.layer_name = 'ColView'
    nt.links.new(vc.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.8
    me.materials.clear()
    me.materials.append(mat)
    print('LOADED', tag, fbx)
    return mesh


old_mesh = load(OLD_FBX, 'old_brown', 0.0)
new_mesh = load(NEW_FBX, 'new_grey', 0.0)

try:
    sc.render.engine = 'BLENDER_EEVEE_NEXT'
except Exception:
    sc.render.engine = 'BLENDER_EEVEE'
sc.render.resolution_x = 1400
sc.render.resolution_y = 900
sc.render.image_settings.file_format = 'PNG'
sc.view_settings.view_transform = 'Standard'
sc.render.use_stamp = True
sc.render.use_stamp_note = True
sc.render.stamp_font_size = 26
for f in ('use_stamp_date', 'use_stamp_time', 'use_stamp_render_time', 'use_stamp_scene',
          'use_stamp_camera', 'use_stamp_filename', 'use_stamp_lens', 'use_stamp_marker',
          'use_stamp_memory', 'use_stamp_hostname', 'use_stamp_frame_range',
          'use_stamp_frame'):
    if hasattr(sc.render, f):
        setattr(sc.render, f, False)

w = bpy.data.worlds.new('W')
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

bpy.ops.mesh.primitive_plane_add(size=14, location=(0, 0, 0))
ground = bpy.context.active_object
gm = bpy.data.materials.new('M_Ground')
gm.use_nodes = True
gm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.13, 0.14, 0.13, 1)
gm.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.95
ground.data.materials.append(gm)

cam_data = bpy.data.cameras.new('Cam')
cam_data.sensor_fit = 'HORIZONTAL'
cam_data.angle_x = math.radians(40.0)
cam = bpy.data.objects.new('Cam', cam_data)
sc.collection.objects.link(cam)
sc.camera = cam
TARGET = Vector((0.0, 0.0, 0.5))


def place_cam(azimuth_deg, elevation_deg, dist):
    a, e = math.radians(azimuth_deg), math.radians(elevation_deg)
    d = Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))
    loc = TARGET + d * dist
    look = (TARGET - loc).normalized()
    up = Vector((0, 0, 1))
    up = up - look * up.dot(look)
    up.normalize()
    zc = -look
    xc = up.cross(zc)
    cam.matrix_world = Matrix(((xc.x, up.x, zc.x, loc.x),
                               (xc.y, up.y, zc.y, loc.y),
                               (xc.z, up.z, zc.z, loc.z),
                               (0, 0, 0, 1)))


# each wolf shot separately in the SAME view, then glued side by side with a
# label on every tile - no left/right ambiguity from camera azimuth
import numpy as np

sc.render.resolution_x = sc.render.resolution_y = 800
TMP = OUT + '_work/_frames/'
os.makedirs(TMP, exist_ok=True)


def montage(paths, out):
    imgs = []
    for p in paths:
        im = bpy.data.images.load(p)
        im.colorspace_settings.name = 'Non-Color'
        imgs.append(im)
    w_, h = imgs[0].size
    canvas = np.zeros((h, len(imgs) * w_, 4), dtype=np.float32)
    canvas[:, :, 3] = 1.0
    for i, im in enumerate(imgs):
        px = np.array(im.pixels[:], dtype=np.float32).reshape(h, w_, 4)
        canvas[:, i * w_:(i + 1) * w_] = px
    out_img = bpy.data.images.new('mtg', width=len(imgs) * w_, height=h, alpha=True)
    out_img.colorspace_settings.name = 'Non-Color'
    out_img.pixels = canvas.ravel()
    out_img.filepath_raw = out
    out_img.file_format = 'PNG'
    out_img.save()
    for im in imgs:
        bpy.data.images.remove(im)
    bpy.data.images.remove(out_img)
    print('RENDER', out)


SHOTS = (('front34', (30, 18, 3.6)),
         ('side', (-90, 12, 3.6)),
         ('game', (180, 60, 3.8)))
for name, prm in SHOTS:
    place_cam(*prm)
    tiles = []
    for mesh, label in ((old_mesh, 'СТАРЫЙ коричневый'), (new_mesh, 'НОВЫЙ серый')):
        old_mesh.hide_render = mesh is not old_mesh
        new_mesh.hide_render = mesh is not new_mesh
        sc.render.stamp_note_text = label + ' — ' + name
        p = TMP + 'cmp_%s_%s.png' % (name, 'old' if mesh is old_mesh else 'new')
        sc.render.filepath = p
        bpy.ops.render.render(write_still=True)
        tiles.append(p)
    montage(tiles, REND + 'wolf_compare_%s.png' % name)
print('COMPARE_DONE')
