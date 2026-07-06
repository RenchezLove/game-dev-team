"""Diag 3: object transform internals for trio + rig."""
import bpy, sys
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W

bpy.ops.wm.open_mainfile(filepath=W.WORKDIR + '_work/wearables_work.blend')
deps = bpy.context.evaluated_depsgraph_get()


def dump(o):
    oe = o.evaluated_get(deps)
    print('== %s parent=%s parent_type=%s parent_bone=%r' % (
        o.name, o.parent.name if o.parent else None, o.parent_type, o.parent_bone))
    print('   constraints=%s' % [(c.type, getattr(c, "target", None)) for c in o.constraints])
    print('   delta loc=%s scale=%s' % (tuple(o.delta_location), tuple(o.delta_scale)))
    for tag, M in (('basis', o.matrix_basis), ('parent_inv', o.matrix_parent_inverse),
                   ('world', o.matrix_world), ('world_EVAL', oe.matrix_world)):
        loc, rot, sc = M.decompose()
        print('   %-10s loc=(%.3f,%.3f,%.3f) scale=(%.3f,%.3f,%.3f)' % (
            tag, loc.x, loc.y, loc.z, sc.x, sc.y, sc.z))


for n in ('RootAnim', 'SK_Armor_T1_Head', 'SK_Armor_T1_Torso', 'SK_Armor_T1_Legs',
          'L1_Torso'):
    dump(bpy.data.objects[n])
print('DIAG3 DONE')
