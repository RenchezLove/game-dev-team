import bpy
print('FPS', bpy.context.scene.render.fps, bpy.context.scene.render.fps_base)
for o in bpy.data.objects:
    print('OBJ', o.name, o.type, 'parent=', o.parent.name if o.parent else None)
for a in bpy.data.actions:
    print('ACTION', a.name, 'range=', tuple(a.frame_range))
arm = bpy.data.objects['WolfRig']
for b in arm.data.bones:
    print('BONE %-14s parent=%-12s head=(%.3f,%.3f,%.3f) tail=(%.3f,%.3f,%.3f)' % (
        b.name, b.parent.name if b.parent else '-', *b.head_local, *b.tail_local))
me = bpy.data.objects['SK_Wolf'].data
xs=[v.co.x for v in me.vertices]; ys=[v.co.y for v in me.vertices]; zs=[v.co.z for v in me.vertices]
print('MESH bbox X[%.3f,%.3f] Y[%.3f,%.3f] Z[%.3f,%.3f] verts=%d' % (min(xs),max(xs),min(ys),max(ys),min(zs),max(zs),len(me.vertices)))
print('VCOL', [(ca.name, ca.domain, ca.data_type) for ca in me.color_attributes])
for pb in arm.pose.bones[:3]:
    print('POSEBONE', pb.name, pb.rotation_mode)
