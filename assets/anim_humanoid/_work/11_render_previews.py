"""Render preview contact sheets for the three animations, with the pistol / knife
placed in the right hand so the grip and the arc can actually be judged.

Run:  blender.exe -b _qc_anim.blend --factory-startup --python 11_render_previews.py
"""
import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from mathutils import Vector, Matrix
import acommon as A
from acommon import R_HAND, upd

OUT = 'E:/game-dev-team/assets/anim_humanoid/'
REND = OUT + 'renders/'
TMP = OUT + '_work/_frames/'
PISTOL = 'E:/game-dev-team/assets/pistol/SM_Pistol.fbx'
KNIFE = 'E:/game-dev-team/assets/knife/SM_Knife.fbx'
TILE = 460
os.makedirs(TMP, exist_ok=True)
os.makedirs(REND, exist_ok=True)

import addon_utils
addon_utils.enable('io_scene_fbx')

rig = A.get_rig()
meshes = [o for o in bpy.data.objects if o.type == 'MESH' and o.parent == rig]
print('character meshes:', [o.name for o in meshes])


# ------------------------------------------------------------ look

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

suns = []
for nm, energy, rot in (('KeyS', 3.4, (math.radians(52), 0, math.radians(-40))),
                        ('FillS', 1.5, (math.radians(66), 0, math.radians(150))),
                        ('RimS', 1.1, (math.radians(20), 0, math.radians(60)))):
    d = bpy.data.lights.new(nm, type='SUN')
    d.energy = energy
    o = bpy.data.objects.new(nm, d)
    sc.collection.objects.link(o)
    o.rotation_euler = rot
    suns.append(o)

# ground plane so the sweep height is readable against something
bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, 0))
ground = bpy.context.active_object
gm = bpy.data.materials.new('M_Ground')
gm.use_nodes = True
gm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.13, 0.14, 0.13, 1)
gm.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.95
ground.data.materials.append(gm)

cam_data = bpy.data.cameras.new('PrevCam')
cam_data.sensor_fit = 'HORIZONTAL'
cam_data.angle_x = math.radians(40.0)      # game camera FOV (PlayerCharacter.h)
cam = bpy.data.objects.new('PrevCam', cam_data)
sc.collection.objects.link(cam)
sc.camera = cam

TARGET = Vector((0.0, -0.25, 1.15))        # chest height, a bit ahead of the body


def place_cam(azimuth_deg, elevation_deg, dist, up_hint=None):
    """azimuth 0 = looking at the character's front (camera on -Y), positive turns
    the camera towards the character's left; elevation is degrees above horizon.

    The roll is built by hand rather than via to_track_quat: looking almost straight
    down makes 'keep screen-up near world +Z' degenerate, so the frame would come out
    rolled at random and nobody could tell which way the character faces.
    """
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


FWD_UP = (0, -1, 0)     # top view: character's forward points up the image
VIEWS = {
    'topdown': (180, 88, 4.6, FWD_UP),   # straight down: the only unambiguous read of the arc
    'game_back': (180, 60, 4.6, None),   # real game camera angle, character facing away
    'game_front': (0, 60, 4.6, None),    # real game camera angle, character facing the camera
    'side': (-90, 12, 4.6, None),        # from the character's right: arm reach, muzzle rise
    'front': (0, 12, 4.6, None),         # eye level: height of the swing, torso twist
}


# ------------------------------------------------------------ weapon in hand

def load_weapon(path, name):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    mesh = [o for o in new if o.type == 'MESH'][0]
    for o in new:
        if o is not mesh:
            bpy.data.objects.remove(o, do_unlink=True)
    mesh.name = name
    mesh.parent = None
    mat = vcol_material('M_Preview_' + name, mesh)
    mesh.data.materials.clear()
    mesh.data.materials.append(mat)
    return mesh


pistol = load_weapon(PISTOL, 'PreviewPistol')
knife = load_weapon(KNIFE, 'PreviewKnife')
print('pistol dims', tuple(round(d, 3) for d in pistol.dimensions))
print('knife dims', tuple(round(d, 3) for d in knife.dimensions))

GRIP_ALONG_HAND = 0.35   # palm sits roughly a third down the hand bone


def put_in_hand(weapon):
    """Weapon convention (both passports): origin = grip, +X = muzzle/tip, +Z = up.
    Line +X up with the hand bone and +Z with the hand's own up, so the wrist roll
    authored in the animation carries straight through to the weapon."""
    upd()
    pb = rig.pose.bones[R_HAND]
    M = rig.matrix_world @ pb.matrix
    head = M.translation.copy()
    xh, yh, zh = M.col[0].xyz.normalized(), M.col[1].xyz.normalized(), M.col[2].xyz.normalized()
    length = pb.bone.length
    wx, wz = yh, zh
    wy = wz.cross(wx)
    grip = head + yh * (length * GRIP_ALONG_HAND)
    weapon.matrix_world = Matrix(((wx.x, wy.x, wz.x, grip.x),
                                  (wx.y, wy.y, wz.y, grip.y),
                                  (wx.z, wy.z, wz.z, grip.z),
                                  (0, 0, 0, 1)))
    upd()


# ------------------------------------------------------------ render + montage

def shoot(action_name, frame, view, weapon, tag):
    ad = rig.animation_data
    act = bpy.data.actions[action_name]
    if ad.action is not act:
        ad.action = act
        if act.slots and ad.action_slot is None:
            ad.action_slot = act.slots[0]
    sc.frame_set(frame)
    upd()
    pistol.hide_render = weapon is not pistol
    knife.hide_render = weapon is not knife
    if weapon:
        put_in_hand(weapon)
    place_cam(*VIEWS[view])
    sc.render.stamp_note_text = tag
    path = '%s%s_%s_f%02d.png' % (TMP, action_name, view, frame)
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    return path


def montage(paths, out, cols):
    imgs = []
    for p in paths:
        im = bpy.data.images.load(p)
        im.colorspace_settings.name = 'Non-Color'
        imgs.append(im)
    w, h = imgs[0].size
    rows = (len(imgs) + cols - 1) // cols
    canvas = np.zeros((rows * h, cols * w, 4), dtype=np.float32)
    canvas[:, :, 3] = 1.0
    for i, im in enumerate(imgs):
        px = np.array(im.pixels[:], dtype=np.float32).reshape(h, w, 4)
        r, c = divmod(i, cols)
        canvas[(rows - 1 - r) * h:(rows - r) * h, c * w:(c + 1) * w] = px   # blender images are bottom-up
    out_img = bpy.data.images.new('mtg', width=cols * w, height=rows * h, alpha=True)
    out_img.colorspace_settings.name = 'Non-Color'
    out_img.pixels = canvas.ravel()
    out_img.filepath_raw = out
    out_img.file_format = 'PNG'
    out_img.save()
    for im in imgs:
        bpy.data.images.remove(im)
    bpy.data.images.remove(out_img)
    print('MONTAGE %s %dx%d  exists=%s' % (out, cols * w, rows * h, os.path.exists(out)))


SLASH_FRAMES = [1, 4, 7, 9, 11, 12, 14, 16, 18, 21]
FIRE_FRAMES = [1, 2, 3, 4, 6, 9]

JOBS = [
    # action, frames, views, weapon, columns, output
    ('Anim_AimPistol_Humanoid', [1], ['topdown', 'game_back', 'game_front', 'side'],
     'pistol', 2, 'aim_pistol_views.png'),
    ('Anim_FirePistol_Humanoid', FIRE_FRAMES, ['side'], 'pistol', 3, 'fire_pistol_side.png'),
    ('Anim_FirePistol_Humanoid', FIRE_FRAMES, ['game_back'], 'pistol', 3, 'fire_pistol_gamecam.png'),
    ('Anim_MeleeSlash_Humanoid', SLASH_FRAMES, ['topdown'], 'knife', 5, 'melee_slash_topdown.png'),
    ('Anim_MeleeSlash_Humanoid', SLASH_FRAMES, ['game_back'], 'knife', 5, 'melee_slash_gamecam.png'),
    ('Anim_MeleeSlash_Humanoid', SLASH_FRAMES, ['front'], 'knife', 5, 'melee_slash_front.png'),
]

WEAP = {'pistol': pistol, 'knife': knife, None: None}

for action, frames, views, wname, cols, outname in JOBS:
    weapon = WEAP[wname]
    paths = []
    if len(views) > 1:
        for v in views:
            paths.append(shoot(action, frames[0], v, weapon, v))
    else:
        for f in frames:
            t = (f - 1) / float(A.FPS)
            paths.append(shoot(action, f, views[0], weapon, 'f%d  %.3fs' % (f, t)))
    montage(paths, REND + outname, cols)


# ------------------------------------------------------------ swept arc in one frame

def arc_sheet(action_name, body_frame, ghost_frames, out, views, res=900):
    """One image showing where the blade passes: body held at one frame, a ghost of
    the weapon dropped at every sampled frame of the swing."""
    ad = rig.animation_data
    act = bpy.data.actions[action_name]
    ad.action = act
    if act.slots and ad.action_slot is None:
        ad.action_slot = act.slots[0]
    ghosts = []
    for f in ghost_frames:
        sc.frame_set(f)
        upd()
        g = knife.copy()
        g.data = knife.data.copy()
        sc.collection.objects.link(g)
        put_in_hand(g)
        ghosts.append(g)
    sc.frame_set(body_frame)
    upd()
    knife.hide_render = False
    pistol.hide_render = True
    put_in_hand(knife)
    sc.render.resolution_x = sc.render.resolution_y = res
    paths = []
    for v in views:
        place_cam(*VIEWS[v])
        sc.render.stamp_note_text = 'arc of frames %s, body at f%d' % (
            ','.join(str(f) for f in ghost_frames), body_frame)
        p = '%sarc_%s.png' % (TMP, v)
        sc.render.filepath = p
        bpy.ops.render.render(write_still=True)
        paths.append(p)
    for g in ghosts:
        bpy.data.objects.remove(g, do_unlink=True)
    sc.render.resolution_x = sc.render.resolution_y = TILE
    montage(paths, out, len(views))


arc_sheet('Anim_MeleeSlash_Humanoid', 12, [7, 9, 10, 11, 12, 13, 14, 15, 16],
          REND + 'melee_slash_arc.png', ['topdown', 'game_back'])

print('RENDER_DONE')
