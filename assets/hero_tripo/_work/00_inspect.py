import bpy, sys
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='E:/game-dev-team/assets/armor_wearables/_work/wearables_work.blend')
rig = bpy.data.objects['RootAnim']
print('RIG mw', [list(r) for r in rig.matrix_world])
for b in rig.data.bones:
    print('BONE %-18s parent=%-18s head=(%.3f,%.3f,%.3f) tail=(%.3f,%.3f,%.3f)' % (
        b.name, b.parent.name if b.parent else '-', *b.head_local, *b.tail_local))
for ob in bpy.data.objects:
    if ob.type == 'MESH':
        me = ob.data
        zs = [v.co.z for v in me.vertices]; xs=[v.co.x for v in me.vertices]
        print('MESH %-22s tris=%d v=%d parent=%s mats=%s z=[%.3f..%.3f] x=[%.3f..%.3f] act=%s' % (
            ob.name, sum(len(p.vertices)-2 for p in me.polygons), len(me.vertices),
            ob.parent.name if ob.parent else '-', [m.name for m in me.materials if m],
            min(zs), max(zs), min(xs), max(xs), rig.animation_data.action.name if rig.animation_data and rig.animation_data.action else None))
# glb
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath='E:/ContrarySurvior/ContrarySurvivor/Saved/Tripo/hero.glb')
bpy.context.view_layer.update()
for ob in bpy.data.objects:
    print('GLB OBJ', ob.name, ob.type, ob.parent.name if ob.parent else '-', tuple(ob.matrix_world.to_scale()))
    if ob.type == 'MESH':
        me = ob.data
        cos = [ob.matrix_world @ v.co for v in me.vertices]
        mn = Vector((min(c.x for c in cos), min(c.y for c in cos), min(c.z for c in cos)))
        mx = Vector((max(c.x for c in cos), max(c.y for c in cos), max(c.z for c in cos)))
        print('  tris=%d verts=%d bbox=%s..%s uv=%s col=%s mats=%s' % (
            sum(len(p.vertices)-2 for p in me.polygons), len(me.vertices), tuple(round(a,3) for a in mn), tuple(round(a,3) for a in mx),
            [u.name for u in me.uv_layers], [c.name for c in me.color_attributes], [m.name for m in me.materials]))
        # x-extent per z slice
        for z in [i*0.05 for i in range(0, 40)]:
            sl = [c for c in cos if z <= c.z - mn.z < z+0.05]
            if sl:
                print('   slice dz=%.2f n=%d x=[%.3f..%.3f] y=[%.3f..%.3f]' % (z, len(sl), min(c.x for c in sl), max(c.x for c in sl), min(c.y for c in sl), max(c.y for c in sl)))
for im in bpy.data.images:
    print('IMG', im.name, tuple(im.size), im.packed_file is not None)
