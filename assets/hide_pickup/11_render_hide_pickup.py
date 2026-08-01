"""QC renders for SM_HidePickup (rolled hide, wolf loot pickup).
Lit multi-angle + wireframe + true gameplay-scale frame (real player camera
from PlayerCharacter.h) with a 1.8 m human-height reference box.

Headless:
  E:/Programs/Blender/blender.exe -b E:/game-dev-team/assets/hide_pickup/hide_pickup.blend \
      --factory-startup --python 11_render_hide_pickup.py
"""
import bpy, sys, math
from mathutils import Vector

sys.path.append('E:/game-dev-team/assets/armor_wearables')
import wcommon as W

OUT = 'E:/game-dev-team/assets/hide_pickup/renders/'
NAME = 'SM_HidePickup'

GAME_PITCH = 60.0
GAME_FOV = 40.0
GAME_DIST = 30.0

g = math.radians(GAME_PITCH)
VIEWS = {
    'front': (0, 1, 0),
    'back': (0, -1, 0),
    'side': (1, 0, 0),
    'tq': (0.8, 0.8, 0.55),
    'top': (0, 0, 1),
    'game': (0.0, math.cos(g), math.sin(g)),
}
LIT = ('front', 'back', 'side', 'tq', 'top', 'game')
WIRE = ('tq', 'top', 'game')

ob = bpy.data.objects[NAME]
sc, cam, suns = W.setup_render(res=900)


def show_only(keep):
    for o in bpy.data.objects:
        if o.type == 'MESH':
            o.hide_render = o not in keep


show_only([ob])
for vn in LIT:
    W.frame_and_shoot([ob], VIEWS[vn], OUT + '%s_%s.png' % (NAME, vn),
                      suns=suns)

# ---------------- true gameplay-scale frame ----------------
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

ob.location = (0.0, 0, 0)
bpy.context.view_layer.update()
show_only([ob, ground, man])

sc.render.resolution_x = 1920
sc.render.resolution_y = 1080
cam.data.type = 'PERSP'
cam.data.angle_x = math.radians(GAME_FOV)
cam.data.clip_start = 0.1
cam.data.clip_end = 300.0

target = Vector((0.0, 0.0, 0.2))
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

sc.render.filepath = OUT + 'HidePickup_gameplay_scale.png'
bpy.ops.render.render(write_still=True)
print('RENDER', sc.render.filepath)

cam.data.angle_x = math.radians(6.0)
sc.render.filepath = OUT + 'HidePickup_gameplay_zoom.png'
bpy.ops.render.render(write_still=True)
print('RENDER', sc.render.filepath)

# ---------------- wireframe pass (destructive) ----------------
sc.render.resolution_x = 900
sc.render.resolution_y = 900
cam.data.type = 'ORTHO'
ground.hide_render = True
man.hide_render = True
ob.location = (0, 0, 0)
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
ob.data.materials.clear()
ob.data.materials.append(wm)
md = ob.modifiers.new('w', 'WIREFRAME')
md.thickness = 0.0035
md.use_replace = True
show_only([ob])
for vn in WIRE:
    W.frame_and_shoot([ob], VIEWS[vn], OUT + '%s_wire_%s.png' % (NAME, vn),
                      suns=None)

tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
print('RECHECK %s source_tris=%d' % (NAME, tris))
print('RENDERS DONE ->', OUT)
