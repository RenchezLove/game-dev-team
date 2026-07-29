"""Import a reference FBX and dump its bind (rest) pose + animation, so we can prove
what the UE skeleton actually holds instead of trusting memory."""
import bpy, sys, os, addon_utils
addon_utils.enable('io_scene_fbx')
bpy.ops.wm.read_homefile(use_factory_startup=True)
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

path = sys.argv[-1]
bpy.ops.import_scene.fbx(filepath=path)
print('=== IMPORTED', os.path.basename(path))
for o in bpy.context.scene.objects:
    print('  obj %-28s type=%-9s parent=%-14s loc=%s rot=%s scale=%s' % (
        o.name, o.type, o.parent.name if o.parent else '-',
        tuple(round(c, 4) for c in o.location),
        tuple(round(c, 4) for c in o.rotation_euler),
        tuple(round(c, 4) for c in o.scale)))

arms = [o for o in bpy.context.scene.objects if o.type == 'ARMATURE']
for ao in arms:
    mw = ao.matrix_world
    print('--- REST (bind) pose, world coords, armature %s bones=%d ---' % (ao.name, len(ao.data.bones)))
    for b in ao.data.bones:
        h = mw @ b.head_local
        t = mw @ b.tail_local
        print('  %-20s parent=%-20s head=(%7.4f,%7.4f,%7.4f) tail=(%7.4f,%7.4f,%7.4f)' % (
            b.name, b.parent.name if b.parent else '-', h.x, h.y, h.z, t.x, t.y, t.z))
    ad = ao.animation_data
    act = ad.action if ad else None
    print('--- action:', act.name if act else None, 'scene range', bpy.context.scene.frame_start, bpy.context.scene.frame_end)
    if act:
        bones = sorted({fc.data_path.split('"')[1] for fc in act.fcurves if '"' in fc.data_path})
        print('  animated bones (%d): %s' % (len(bones), bones))
        chans = {}
        for fc in act.fcurves:
            if '"' not in fc.data_path:
                continue
            bn = fc.data_path.split('"')[1]
            ch = fc.data_path.rsplit('.', 1)[-1]
            chans.setdefault(bn, set()).add(ch)
        for bn in bones:
            print('    %-20s channels=%s' % (bn, sorted(chans[bn])))
        # per-bone world travel of tail over the take
        sc = bpy.context.scene
        prev = {}
        travel = {}
        for f in range(int(sc.frame_start), int(sc.frame_end) + 1):
            sc.frame_set(f)
            dg = bpy.context.evaluated_depsgraph_get()
            ae = ao.evaluated_get(dg)
            for pb in ae.pose.bones:
                w = (ae.matrix_world @ pb.tail).copy()
                if pb.name in prev:
                    travel[pb.name] = travel.get(pb.name, 0.0) + (w - prev[pb.name]).length
                prev[pb.name] = w
        for k in sorted(travel, key=lambda x: -travel[x]):
            print('    travel %-20s %.4f' % (k, travel[k]))
print('=== FBX_INSPECT_DONE')
