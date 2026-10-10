"""Export one model from its work blend to FBX and check the written file by importing it back into an empty scene:
triangles, size, origin, where every face looks (against the directions stored by the builder), UV sets, textures.
Run: blender.exe -b <work.blend> --factory-startup --python 91_export.py -- <object> <out dir> <tri min> <tri max> <texture max> <flags> <texture png> [...]
flags: letters g = lowest point on the ground (z 0), c = origin in the middle of the footprint, l = has LightmapUV; '-' for none
"""
import bpy, sys, os
import numpy as np
sys.path.insert(0, 'E:/game-dev-team/assets/scientist_base/_work')
import sb
a = sb.args()
name, out, lo, hi, tmax, flags = a[0], a[1], int(a[2]), int(a[3]), int(a[4]), a[5]
texs = a[6:]
ob = bpy.data.objects[name]
ref = sb.ref_of(ob)
for at in ('wx', 'wy', 'wz'):
    pass
exp = ob.copy(); exp.data = ob.data.copy(); bpy.context.scene.collection.objects.link(exp)
ob.name = name + '_work'; exp.name = name; exp.data.name = name
for at in ('wx', 'wy', 'wz'):
    exp.data.attributes.remove(exp.data.attributes[at])
sb.export_fbx([exp], out + name + '.fbx')
ok, res = sb.roundtrip(out + name + '.fbx', name, ref, hi, texs, tmax, uv_expect=('UVMap', 'LightmapUV') if 'l' in flags else ('UVMap',),
                       origin_ground='g' in flags, centred='c' in flags, lo=lo)
mn, mx = res['mn'] * 100, res['mx'] * 100
print('%s SUMMARY tris %d | size cm %.1f x %.1f x %.1f | min cm (%.1f, %.1f, %.1f) max cm (%.1f, %.1f, %.1f) | %s' % (
    name, res['tris'], *(mx - mn), *mn, *mx, 'PASS' if ok else 'FAIL'))
