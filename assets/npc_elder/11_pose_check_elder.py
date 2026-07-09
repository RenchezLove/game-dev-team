"""Deformation check for the elder: load _work/elder_work.blend, render the
assembled set at rest + in a bent pose (elbows/shoulder/knee/neck) — the x100
lesson: if the rig bones were baked wrong the added hat/beard/vest/boots would
explode off the body when posed. Also a wireframe pass. Output: renders_elder/.
Run: blender.exe -b --factory-startup --python 11_pose_check_elder.py
"""
import bpy, sys, os, math
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W

HERE = 'E:/game-dev-team/assets/npc_elder/'
OUT = HERE + 'renders_elder/'
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=HERE + '_work/elder_work.blend')
sc, cam, suns = W.setup_render(res=860)
rig = bpy.data.objects['RootAnim']
SET = [bpy.data.objects[n] for n in ('SK_Elder_Head', 'SK_Elder_Torso', 'SK_Elder_Legs')]


def show_only(objs):
    for o in bpy.data.objects:
        if o.type == 'MESH':
            o.hide_render = o not in objs


VIEWS = {'front': (0, -1, 0.12), 'tq': (0.7, -1, 0.55), 'side': (1, 0, 0.12),
         'top': (0, -0.001, 1), 'back': (0, 1, 0.12)}

# ---- lit per module + assembled (rest pose) ----
for ob in SET:
    show_only([ob])
    for vn, vd in VIEWS.items():
        W.frame_and_shoot([ob], vd, OUT + '%s_%s.png' % (ob.name, vn), suns=suns)
show_only(SET)
for vn, vd in VIEWS.items():
    W.frame_and_shoot(SET, vd, OUT + 'Elder_assembled_%s.png' % vn, suns=suns)

# ---- posed: bend joints (same pose as the wearables batches) ----
POSE = {
    'L_Shoulder': (0, 0, math.radians(40)),
    'L_Arm': (0, 0, math.radians(45)),
    'R_Arm': (0, 0, math.radians(-35)),
    'C_Neck': (math.radians(18), 0, math.radians(14)),
    'L_Thigh': (math.radians(-35), 0, 0),
    'L_Claf': (math.radians(30), 0, 0),
    'R_Thigh': (math.radians(15), 0, 0),
}
for bn, eul in POSE.items():
    pb = rig.pose.bones[bn]
    pb.rotation_mode = 'XYZ'
    pb.rotation_euler = eul
bpy.context.view_layer.update()
show_only(SET)
for vn in ('front', 'tq', 'side'):
    W.frame_and_shoot(SET, VIEWS[vn], OUT + 'Elder_pose_%s.png' % vn, suns=suns)
for pb in rig.pose.bones:
    pb.rotation_euler = (0, 0, 0)
    pb.location = (0, 0, 0)
bpy.context.view_layer.update()

# ---- wireframe pass (tq + top per module) ----
wm = bpy.data.materials.new('WIRE')
wm.use_nodes = True
nt = wm.node_tree
nt.nodes.clear()
o = nt.nodes.new('ShaderNodeOutputMaterial')
b = nt.nodes.new('ShaderNodeBsdfPrincipled')
b.inputs['Base Color'].default_value = (0.05, 0.05, 0.06, 1.0)
nt.links.new(b.outputs['BSDF'], o.inputs['Surface'])
sc.world.node_tree.nodes['Background'].inputs[0].default_value = (0.85, 0.85, 0.87, 1.0)
sc.world.node_tree.nodes['Background'].inputs[1].default_value = 1.0
for ob in SET:
    ob.data.materials.clear()
    ob.data.materials.append(wm)
    md = ob.modifiers.new('w', 'WIREFRAME')
    md.thickness = 0.004
    md.use_replace = True
for ob in SET:
    show_only([ob])
    for vn in ('tq', 'top'):
        W.frame_and_shoot([ob], VIEWS[vn], OUT + '%s_wire_%s.png' % (ob.name, vn), suns=None)
print('POSE+WIRE RENDERS DONE ->', OUT)
