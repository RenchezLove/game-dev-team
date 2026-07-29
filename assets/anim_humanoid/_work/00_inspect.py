"""Inspect the humanoid rig: real bone coordinates (names are shifted on the right arm),
existing actions, mesh slots. Read-only: never saves the source blend."""
import bpy, sys, os
from mathutils import Vector

print('=== FILE', bpy.data.filepath)
print('--- objects ---')
for o in bpy.data.objects:
    print('  %-28s type=%-9s parent=%-12s loc=%s rot=%s scale=%s' % (
        o.name, o.type, o.parent.name if o.parent else '-',
        tuple(round(c, 4) for c in o.location),
        tuple(round(c, 4) for c in o.rotation_euler),
        tuple(round(c, 4) for c in o.scale)))

arms = [o for o in bpy.data.objects if o.type == 'ARMATURE']
for ao in arms:
    print('--- armature object %s (data %s) bones=%d ---' % (ao.name, ao.data.name, len(ao.data.bones)))
    mw = ao.matrix_world
    for b in ao.data.bones:
        h = mw @ b.head_local
        t = mw @ b.tail_local
        print('  %-20s parent=%-20s head=(%7.4f,%7.4f,%7.4f) tail=(%7.4f,%7.4f,%7.4f) len=%.4f' % (
            b.name, b.parent.name if b.parent else '-', h.x, h.y, h.z, t.x, t.y, t.z, b.length))

print('--- actions ---')
for a in bpy.data.actions:
    fr = a.frame_range
    paths = sorted({fc.data_path.split('"')[1] for fc in a.fcurves if '"' in fc.data_path})
    print('  %-24s range=(%.1f,%.1f) fcurves=%d bones=%s' % (a.name, fr[0], fr[1], len(a.fcurves), paths))

print('--- meshes ---')
for o in bpy.data.objects:
    if o.type != 'MESH':
        continue
    me = o.data
    vg = [g.name for g in o.vertex_groups]
    print('  %-24s verts=%-6d polys=%-6d vgroups=%d mods=%s' % (
        o.name, len(me.vertices), len(me.polygons), len(vg),
        [(m.type, getattr(m, 'object', None).name if getattr(m, 'object', None) else '') for m in o.modifiers]))
    print('     colattrs=%s uv=%s' % ([(c.name, c.domain, c.data_type) for c in me.color_attributes],
                                      [u.name for u in me.uv_layers]))
print('=== INSPECT_DONE')
