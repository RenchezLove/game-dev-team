"""Diagnose vanishing meshes in multi-object renders."""
import bpy, sys
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W

bpy.ops.wm.open_mainfile(filepath=W.WORKDIR + '_work/wearables_work.blend')
sc, cam, suns = W.setup_render(res=500)
trio = [bpy.data.objects[n] for n in ('SK_Armor_T1_Head', 'SK_Armor_T1_Torso', 'SK_Armor_T1_Legs')]

for o in bpy.data.objects:
    if o.type == 'MESH':
        o.hide_render = o not in trio
bpy.context.view_layer.update()
deps = bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
    if o.type != 'MESH':
        continue
    oe = o.evaluated_get(deps)
    print('OBJ %-22s hide_render=%s hide_viewport=%s visible_get=%s evalpolys=%d mats=%s' % (
        o.name, o.hide_render, o.hide_viewport,
        o.visible_get() if not o.hide_viewport else 'n/a',
        len(oe.data.polygons) if oe.data else -1,
        [m.name if m else None for m in o.data.materials]))
W.frame_and_shoot(trio, (0, -1, 0.12), W.WORKDIR + '_qc/diag_trio_hide.png', suns=suns)

# alternative: no hiding at all, everything visible
for o in bpy.data.objects:
    if o.type == 'MESH':
        o.hide_render = False
W.frame_and_shoot(trio, (0, -1, 0.12), W.WORKDIR + '_qc/diag_all_visible.png', suns=suns)
print('DIAG DONE')
