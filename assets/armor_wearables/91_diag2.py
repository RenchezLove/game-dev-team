"""Diag 2: evaluated vertex ranges + render with armature modifiers off."""
import bpy, sys
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W
from mathutils import Vector

bpy.ops.wm.open_mainfile(filepath=W.WORKDIR + '_work/wearables_work.blend')
sc, cam, suns = W.setup_render(res=500)
trio = [bpy.data.objects[n] for n in ('SK_Armor_T1_Head', 'SK_Armor_T1_Torso', 'SK_Armor_T1_Legs')]
for o in bpy.data.objects:
    if o.type == 'MESH':
        o.hide_render = o not in trio

rig = bpy.data.objects['RootAnim']
print('rig pose transforms (non-identity):')
for pb in rig.pose.bones:
    loc, rot, scale = pb.matrix_basis.decompose()
    if (loc.length > 1e-5 or abs(rot.angle) > 1e-4 or
            max(abs(scale.x - 1), abs(scale.y - 1), abs(scale.z - 1)) > 1e-4):
        print('  %-18s loc=%s rotang=%.2f scale=%s' % (
            pb.name, tuple(round(v, 3) for v in loc), rot.angle,
            tuple(round(v, 3) for v in scale)))

bpy.context.view_layer.update()
deps = bpy.context.evaluated_depsgraph_get()
for o in trio:
    oe = o.evaluated_get(deps)
    me = oe.to_mesh()
    zs = [ (oe.matrix_world @ v.co).z for v in me.vertices]
    xs = [ (oe.matrix_world @ v.co).x for v in me.vertices]
    print('EVAL %-22s verts=%d x=[%.3f..%.3f] z=[%.3f..%.3f]' % (
        o.name, len(me.vertices), min(xs), max(xs), min(zs), max(zs)))
    oe.to_mesh_clear()

# render trio with modifiers disabled
for o in trio:
    for m in o.modifiers:
        m.show_render = False
W.frame_and_shoot(trio, (0, -1, 0.12), W.WORKDIR + '_qc/diag_trio_nomod.png', suns=suns)
print('DIAG2 DONE')
