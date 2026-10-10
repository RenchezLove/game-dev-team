"""Shared by the preview and the export of the UAZ kit: split the work mesh 'kit' into its parts with the origin of each on its mounting point."""
import bpy, bmesh, json, math, sys
import numpy as np
from mathutils import Vector
sys.path.insert(0, 'E:/game-dev-team/assets/scientist_base/_work')
import sb
META = json.load(open(sb.WORK + '_uazkit_meta.json'))
PARTS = META['parts']
def pivot(n):
    if n in META['hinge']:
        return Vector(META['hinge'][n])
    if n == 'Wheel':
        return Vector(META['wheels'][0])
    return Vector((0, 0, 0))
def split():
    kit = bpy.data.objects['kit']; out = {}
    for i, n in enumerate(PARTS):
        o = kit.copy(); o.data = kit.data.copy(); o.name = 'SM_UAZ452_' + n; o.data.name = o.name; bpy.context.scene.collection.objects.link(o)
        b = sb.bm_of(o); pl = b.faces.layers.int['pid']
        bmesh.ops.delete(b, geom=[f for f in b.faces if f[pl] != i], context='FACES')
        p = pivot(n)
        for v in b.verts:
            v.co -= p
        b.to_mesh(o.data); b.free()
        o.data.attributes.remove(o.data.attributes['pid'])
        sb.store_facing(o)
        o.location = p; out[n] = o
    kit.hide_render = True
    bpy.context.view_layer.update()
    return out
def ue(p):
    return (round(p[0] * 100, 1), round(-p[1] * 100, 1), round(p[2] * 100, 1))
