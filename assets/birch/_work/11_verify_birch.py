"""Round-trip проверка: реимпорт экспортированных FBX и замер по факту файла."""
import bpy, os
from mathutils import Vector

OUT = "E:/game-dev-team/assets/birch/"
FILES = ['SM_Tree_Birch_01.fbx', 'SM_Tree_Birch_01_LOD1.fbx', 'SM_Tree_Birch_01_LOD2.fbx']

bpy.ops.wm.read_factory_settings(use_empty=True)

for fn in FILES:
    p = OUT + fn
    print('=' * 72)
    print('FILE %s exists=%s size=%d' % (fn, os.path.exists(p),
                                         os.path.getsize(p) if os.path.exists(p) else 0))
    before = set(o.name for o in bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=p)
    new = [o for o in bpy.data.objects if o.name not in before and o.type == 'MESH']
    for o in sorted(new, key=lambda x: x.name):
        me = o.data
        me.calc_loop_triangles()
        pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
        xs = [v.x for v in pts]; ys = [v.y for v in pts]; zs = [v.z for v in pts]
        ngon = sum(1 for pl in me.polygons if len(pl.vertices) != 3)
        print('  obj=%-26s tris=%-5d verts=%-4d ngons=%d' % (o.name, len(me.loop_triangles), len(me.vertices), ngon))
        print('     loc=%s rot=%s scale=%s' % (
            tuple(round(c, 4) for c in o.location),
            tuple(round(r, 4) for r in o.rotation_euler),
            tuple(round(s, 4) for s in o.matrix_world.to_scale())))
        print('     bbox X[%.3f..%.3f] Y[%.3f..%.3f] Z[%.3f..%.3f] size=(%.3f, %.3f, %.3f)' % (
            min(xs), max(xs), min(ys), max(ys), min(zs), max(zs),
            max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)))
        print('     color_attrs=%s uv=%s materials=%s' % (
            [(a.name, a.domain, a.data_type) for a in me.color_attributes],
            [u.name for u in me.uv_layers], [m.name if m else None for m in me.materials]))
        # UV в пределах 0-1
        if me.uv_layers:
            us = [d.uv for d in me.uv_layers[0].data]
            print('     uv range U[%.3f..%.3f] V[%.3f..%.3f]' % (
                min(u.x for u in us), max(u.x for u in us),
                min(u.y for u in us), max(u.y for u in us)))
        # палитра: сколько уникальных цветов и их sRGB-хексы
        if me.color_attributes:
            ca = me.color_attributes[0]
            seen = {}
            for d in ca.data:
                c = tuple(round(x, 4) for x in d.color_srgb[:3])
                seen[c] = seen.get(c, 0) + 1
            print('     vcol uniq=%d:' % len(seen))
            for c, n in sorted(seen.items(), key=lambda kv: -kv[1]):
                print('        #%02X%02X%02X  углов=%d' % (
                    round(c[0] * 255), round(c[1] * 255), round(c[2] * 255), n))
        # незамкнутые рёбра
        cnt = {}
        for pl in me.polygons:
            vs = list(pl.vertices)
            for i in range(len(vs)):
                k = tuple(sorted((vs[i], vs[(i + 1) % len(vs)])))
                cnt[k] = cnt.get(k, 0) + 1
        print('     незамкнутых рёбер=%d' % sum(1 for v in cnt.values() if v < 2))
print('DONE')
