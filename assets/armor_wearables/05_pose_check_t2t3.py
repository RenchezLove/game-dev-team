"""Deformation + mix check for the T2/T3 batch + final renders.
Loads _work/wearables_t2t3.blend, renders into renders/:
  <item>_{front,tq,side,top}.png (lit) + <item>_wire_{tq,top}.png
  T2_assembled_*, T3_assembled_*
  MIX_T2torsoT3legs_*, MIX_T3torsoT2legs_*   (cross-tier slot mix)
  T2_pose_*, T3_pose_*, MIX_*_pose_*         (bent joints — the x100 lesson)
Run: blender.exe -b --factory-startup --python 05_pose_check_t2t3.py
"""
import bpy, sys, os, math
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W

OUT = W.WORKDIR + 'renders/'
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=W.WORKDIR + '_work/wearables_t2t3.blend')
sc, cam, suns = W.setup_render(res=820)
rig = bpy.data.objects['RootAnim']

T2 = [bpy.data.objects[n] for n in ('SK_Armor_T2_Head', 'SK_Armor_T2_Torso', 'SK_Armor_T2_Legs')]
T3 = [bpy.data.objects[n] for n in ('SK_Armor_T3_Head', 'SK_Armor_T3_Torso', 'SK_Armor_T3_Legs')]
MIX_A = [T2[0], T2[1], T3[2]]     # T2 torso + T3 legs
MIX_B = [T3[0], T3[1], T2[2]]     # T3 torso + T2 legs


def show_only(objs):
    for o in bpy.data.objects:
        if o.type == 'MESH':
            o.hide_render = o not in objs


VIEWS = {'front': (0, -1, 0.12), 'tq': (0.7, -1, 0.55), 'side': (1, 0, 0.12),
         'top': (0, -0.001, 1)}

# ---- lit per item ----
for ob in T2 + T3:
    show_only([ob])
    for vn, vd in VIEWS.items():
        W.frame_and_shoot([ob], vd, OUT + '%s_%s.png' % (ob.name, vn), suns=suns)

# ---- assembled sets + cross-tier mixes ----
SETS = (('T2_assembled', T2), ('T3_assembled', T3),
        ('MIX_T2torsoT3legs', MIX_A), ('MIX_T3torsoT2legs', MIX_B))
for label, trio in SETS:
    show_only(trio)
    for vn, vd in VIEWS.items():
        W.frame_and_shoot(trio, vd, OUT + '%s_%s.png' % (label, vn), suns=suns)

# ---- pose: bend elbows/shoulder/knee/neck (same pose as batch 1) ----
POSE = {
    'L_Shoulder': (0, 0, math.radians(40)),    # left arm forward-down
    'L_Arm': (0, 0, math.radians(45)),         # left elbow bend
    'R_Arm': (0, 0, math.radians(-35)),        # right elbow
    'C_Neck': (math.radians(18), 0, math.radians(14)),
    'L_Thigh': (math.radians(-35), 0, 0),      # step
    'L_Claf': (math.radians(30), 0, 0),        # knee bend
    'R_Thigh': (math.radians(15), 0, 0),
}
for bn, eul in POSE.items():
    pb = rig.pose.bones[bn]
    pb.rotation_mode = 'XYZ'
    pb.rotation_euler = eul
bpy.context.view_layer.update()
for label, trio in (('T2_pose', T2), ('T3_pose', T3),
                    ('MIX_T2torsoT3legs_pose', MIX_A),
                    ('MIX_T3torsoT2legs_pose', MIX_B)):
    show_only(trio)
    for vn in ('front', 'tq', 'side'):
        W.frame_and_shoot(trio, VIEWS[vn], OUT + '%s_%s.png' % (label, vn), suns=suns)
# reset pose
for pb in rig.pose.bones:
    pb.rotation_euler = (0, 0, 0)
    pb.location = (0, 0, 0)
bpy.context.view_layer.update()

# ---- wireframe pass ----
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
for ob in T2 + T3:
    ob.data.materials.clear()
    ob.data.materials.append(wm)
    md = ob.modifiers.new('w', 'WIREFRAME')
    md.thickness = 0.004
    md.use_replace = True
for ob in T2 + T3:
    show_only([ob])
    for vn in ('tq', 'top'):
        W.frame_and_shoot([ob], VIEWS[vn], OUT + '%s_wire_%s.png' % (ob.name, vn), suns=None)
print('RENDERS DONE ->', OUT)
