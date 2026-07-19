"""QC renders for the two loot pickup variants (SM_LootSack / SM_LootBackpack).

Lit multi-angle shots + wireframe + a true gameplay-scale frame that copies the
real player camera from PlayerCharacter.h (perspective, FOV 40, arm 3000 uu =
30 m, boom pitch -60 deg), with a 1.8 m human-height box for scale reference.

Headless:
  E:/Programs/Blender/blender.exe -b E:/game-dev-team/assets/loot_bag/loot_bag.blend \
      --factory-startup --python 11_render_loot_bags.py
"""
import bpy, sys, math
from mathutils import Vector

sys.path.append('E:/game-dev-team/assets/armor_wearables')
import wcommon as W

OUT = 'E:/game-dev-team/assets/loot_bag/renders/'
NAMES = ('SM_LootSack', 'SM_LootBackpack')

# game camera facts (Source/ContrarySurvivor/Characters/PlayerCharacter.h)
GAME_PITCH = 60.0        # CameraBoomRotation pitch -60
GAME_FOV = 40.0          # CameraFieldOfView
GAME_DIST = 30.0         # CameraArmLength 3000 uu = 30 m

g = math.radians(GAME_PITCH)
VIEWS = {
    'front': (0, 1, 0),
    'back': (0, -1, 0),
    'side': (1, 0, 0),
    'tq': (0.8, 0.8, 0.55),
    'top': (0, 0, 1),
    # camera placed at the game boom pitch, looking at the prop from the front
    'game': (0.0, math.cos(g), math.sin(g)),
}
LIT = ('front', 'back', 'side', 'tq', 'top', 'game')
WIRE = ('tq', 'top', 'game')

objs = {n: bpy.data.objects[n] for n in NAMES}
sc, cam, suns = W.setup_render(res=900)


def show_only(keep):
    for ob in bpy.data.objects:
        if ob.type == 'MESH':
            ob.hide_render = ob not in keep


# ---------------- lit per-variant shots ----------------
for n in NAMES:
    ob = objs[n]
    show_only([ob])
    for vn in LIT:
        W.frame_and_shoot([ob], VIEWS[vn], OUT + '%s_%s.png' % (n, vn),
                          suns=suns)

# ---------------- side-by-side comparison (close up) ----------------
objs['SM_LootSack'].location = (-0.28, 0, 0)
objs['SM_LootBackpack'].location = (0.28, 0, 0)
bpy.context.view_layer.update()
pair = [objs[n] for n in NAMES]
show_only(pair)
for vn in ('front', 'tq', 'top', 'game'):
    W.frame_and_shoot(pair, VIEWS[vn], OUT + 'LootPair_%s.png' % vn, suns=suns)

# ---------------- true gameplay-scale frame ----------------
# ground plane + 1.8 m human-height reference box, real camera params
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = 'QC_Ground'
gm = bpy.data.materials.new('QC_GroundMat')
gm.use_nodes = True
gbsdf = gm.node_tree.nodes['Principled BSDF']
gbsdf.inputs['Base Color'].default_value = (0.16, 0.13, 0.09, 1.0)
gbsdf.inputs['Roughness'].default_value = 0.95
ground.data.materials.append(gm)

bpy.ops.mesh.primitive_cube_add(size=1, location=(-1.6, 0, 0.9))
man = bpy.context.active_object
man.name = 'QC_HumanRef_1m8'
man.scale = (0.45, 0.25, 1.8)
mm = bpy.data.materials.new('QC_HumanMat')
mm.use_nodes = True
mbsdf = mm.node_tree.nodes['Principled BSDF']
mbsdf.inputs['Base Color'].default_value = (0.35, 0.35, 0.38, 1.0)
mbsdf.inputs['Roughness'].default_value = 0.9
man.data.materials.append(mm)

objs['SM_LootSack'].location = (0.0, 0, 0)
objs['SM_LootBackpack'].location = (0.9, 0, 0)
bpy.context.view_layer.update()
show_only(pair + [ground, man])

sc.render.resolution_x = 1920
sc.render.resolution_y = 1080
cam.data.type = 'PERSP'
cam.data.angle_x = math.radians(GAME_FOV)
cam.data.clip_start = 0.1
cam.data.clip_end = 300.0

target = Vector((0.45, 0.0, 0.2))
vd = Vector((0.0, math.cos(g), math.sin(g))).normalized()
cam.location = target + vd * GAME_DIST
fwd = (target - cam.location).normalized()
cam.rotation_euler = fwd.to_track_quat('-Z', 'Y').to_euler()

zup = Vector((0, 0, 1))
right = fwd.cross(zup).normalized()
up = right.cross(fwd).normalized()
for s, t in zip(suns, (fwd + 0.55 * right - 0.55 * up,
                       fwd - 0.5 * right + 0.35 * up,
                       fwd - 0.9 * up + 0.1 * right)):
    s.rotation_euler = t.normalized().to_track_quat('-Z', 'Y').to_euler()

half_w = GAME_DIST * math.tan(math.radians(GAME_FOV) / 2.0)
print('GAMEPLAY cam_loc=(%.2f,%.2f,%.2f) dist=%.1fm fov=%.0f visible_width=%.1fm'
      % (cam.location.x, cam.location.y, cam.location.z, GAME_DIST, GAME_FOV,
         half_w * 2))
sc.render.filepath = OUT + 'LootPair_gameplay_scale.png'
bpy.ops.render.render(write_still=True)
print('RENDER', sc.render.filepath)

# zoomed gameplay angle (same pitch, tighter lens) so shapes are legible
cam.data.angle_x = math.radians(6.0)
sc.render.filepath = OUT + 'LootPair_gameplay_zoom.png'
bpy.ops.render.render(write_still=True)
print('RENDER', sc.render.filepath)

# ---------------- wireframe pass (destructive: replaces materials) ----------
sc.render.resolution_x = 900
sc.render.resolution_y = 900
cam.data.type = 'ORTHO'
ground.hide_render = True
man.hide_render = True
objs['SM_LootSack'].location = (0, 0, 0)
objs['SM_LootBackpack'].location = (0, 0, 0)
bpy.context.view_layer.update()

wm = bpy.data.materials.new('WIRE')
wm.use_nodes = True
nt = wm.node_tree
nt.nodes.clear()
o = nt.nodes.new('ShaderNodeOutputMaterial')
b = nt.nodes.new('ShaderNodeBsdfPrincipled')
b.inputs['Base Color'].default_value = (0.05, 0.05, 0.06, 1.0)
nt.links.new(b.outputs['BSDF'], o.inputs['Surface'])
bg = sc.world.node_tree.nodes['Background']
bg.inputs[0].default_value = (0.85, 0.85, 0.87, 1.0)
bg.inputs[1].default_value = 1.0
for n in NAMES:
    ob = objs[n]
    ob.data.materials.clear()
    ob.data.materials.append(wm)
    md = ob.modifiers.new('w', 'WIREFRAME')
    md.thickness = 0.0035
    md.use_replace = True
for n in NAMES:
    ob = objs[n]
    show_only([ob])
    for vn in WIRE:
        W.frame_and_shoot([ob], VIEWS[vn], OUT + '%s_wire_%s.png' % (n, vn),
                          suns=None)

for n in NAMES:
    me = objs[n].data
    tris = sum(len(p.vertices) - 2 for p in me.polygons)
    print('RECHECK %s source_tris=%d (wireframe modifier not applied to data)'
          % (n, tris))
print('RENDERS DONE ->', OUT)
