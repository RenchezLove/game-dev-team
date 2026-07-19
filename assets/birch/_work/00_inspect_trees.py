import bpy, sys, os
from mathutils import Vector

SRC = "E:/ForGameLead(Materials)/phase3-assets"
names = ["SM_Tree_01","SM_Tree_02","SM_Tree_03"]

bpy.ops.wm.read_factory_settings(use_empty=True)

for n in names:
    p = os.path.join(SRC, n + ".fbx")
    if not os.path.exists(p):
        print("MISSING", p); continue
    before = set(o.name for o in bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=p)
    new = [o for o in bpy.data.objects if o.name not in before and o.type=='MESH']
    print("="*70)
    print("FILE:", n, " objects:", [o.name for o in new])
    for o in new:
        me = o.data
        me.calc_loop_triangles()
        # world-space bbox
        pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
        xs=[v.x for v in pts]; ys=[v.y for v in pts]; zs=[v.z for v in pts]
        print("  obj=%s verts=%d tris=%d polys=%d" % (o.name, len(me.vertices), len(me.loop_triangles), len(me.polygons)))
        print("  matrix scale=%s loc=%s" % (tuple(round(s,4) for s in o.matrix_world.to_scale()), tuple(round(c,4) for c in o.matrix_world.translation)))
        print("  bbox_world X[%.3f..%.3f] Y[%.3f..%.3f] Z[%.3f..%.3f]  size=(%.3f, %.3f, %.3f)" % (
            min(xs),max(xs),min(ys),max(ys),min(zs),max(zs), max(xs)-min(xs), max(ys)-min(ys), max(zs)-min(zs)))
        print("  color_attrs:", [(a.name, a.domain, a.data_type) for a in me.color_attributes])
        print("  uv_layers:", [u.name for u in me.uv_layers])
        print("  materials:", [ (m.name if m else None) for m in me.materials ])
        # sample vertex colors: cluster unique colours
        if me.color_attributes:
            ca = me.color_attributes[0]
            seen = {}
            for d in ca.data:
                c = tuple(round(x,3) for x in (d.color[0],d.color[1],d.color[2]))
                seen[c] = seen.get(c,0)+1
            top = sorted(seen.items(), key=lambda kv:-kv[1])[:8]
            print("  vcol unique=%d top:" % len(seen))
            for c,cnt in top:
                print("     %s x%d" % (c,cnt))
        # per-material / loose part count
        print("  poly-size histogram:", {k: sum(1 for pl in me.polygons if len(pl.vertices)==k) for k in set(len(pl.vertices) for pl in me.polygons)})
print("DONE")
