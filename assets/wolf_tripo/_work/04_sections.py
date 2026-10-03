"""Cross-sections of the Tripo wolf (turned to +Y, feet on Z0): centres and sizes of the closed
outlines at each height (left side, x>0), plus vertical sections across the trunk / neck / tail.
Run: blender.exe -b --factory-startup --python 04_sections.py
"""
import bpy, bmesh, math
from mathutils import Matrix, Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath='E:/ContrarySurvior/ContrarySurvivor/Saved/Tripo/wolf/wolf.glb')
tr = [o for o in bpy.context.selected_objects if o.type == 'MESH'][0]
bpy.context.view_layer.update()
tr.data.transform(Matrix.Rotation(math.radians(90), 4, 'Z') @ tr.matrix_world); tr.matrix_world = Matrix.Identity(4)
zmin = min(v.co.z for v in tr.data.vertices)
tr.data.transform(Matrix.Translation((0, 0, -zmin)))
base = bmesh.new(); base.from_mesh(tr.data)
bmesh.ops.remove_doubles(base, verts=base.verts[:], dist=1e-4)


def section(co, no):
    bm = base.copy()
    r = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=co, plane_no=no)
    es = [e for e in r['geom_cut'] if isinstance(e, bmesh.types.BMEdge)]
    vs = {}
    for e in es:
        for v in e.verts:
            vs.setdefault(v, []).append(e)
    seen = set(); comps = []
    for v in vs:
        if v in seen:
            continue
        st = [v]; seen.add(v); c = []
        while st:
            a = st.pop(); c.append(a.co.copy())
            for e in vs[a]:
                b = e.other_vert(a)
                if b not in seen:
                    seen.add(b); st.append(b)
        comps.append(c)
    bm.free()
    return comps


print('HORIZONTAL sections (outlines with centre x>0.02): z | centre (x,y) size (dx,dy)')
for i in range(1, 17):
    z = i * 0.05
    out = []
    for c in section((0, 0, z), (0, 0, 1)):
        mn = Vector((min(p.x for p in c), min(p.y for p in c))); mx = Vector((max(p.x for p in c), max(p.y for p in c)))
        ce = (mn + mx) / 2
        if ce.x > 0.02 or (mx.x - mn.x) > 0.2:
            out.append('c(%.3f,%+.3f) size(%.3f,%.3f)' % (ce.x, ce.y, mx.x - mn.x, mx.y - mn.y))
    print('SEC z=%.2f  %s' % (z, ' | '.join(sorted(out, key=lambda s: s[10:]))))
print('VERTICAL sections across the body: y | centre z, z range, x half-width')
for i in range(-21, 22):
    y = i * 0.05
    for c in section((0, y, 0), (0, 1, 0)):
        zs = [p.z for p in c]; xs = [p.x for p in c]
        if max(xs) - min(xs) > 0.03 and abs((max(xs) + min(xs)) / 2) < 0.05:
            print('CROSS y=%+.2f z %.3f..%.3f (centre %.3f) x half %.3f' % (y, min(zs), max(zs), (min(zs) + max(zs)) / 2, (max(xs) - min(xs)) / 2))
