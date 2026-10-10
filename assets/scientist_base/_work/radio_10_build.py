"""SM_Radio from the Sketchfab "Gauja" retro radio receiver (Vitalii.Sandula, CC BY, 1578 triangles): rebuilt by hand from the measured parts
(case, tuning dial, its centre knob, band switch, side socket = 70 triangles); grille lines, scale digits, the slot with the thumb wheels on top
and the wear are baked from the source into the colour texture.  The dial looks to -Y, origin under the middle, 25 cm wide.
Run: blender.exe -b --factory-startup --python radio_10_build.py
"""
import bpy, bmesh, sys, math, os
import numpy as np
from mathutils import Vector
sys.path.insert(0, 'E:/game-dev-team/assets/scientist_base/_work')
import sb
OUT = sb.ROOT + 'SM_Radio/'; os.makedirs(OUT, exist_ok=True)
TEX = 512
WIDTH = 0.25
sb.empty()
bpy.ops.import_scene.fbx(filepath=sb.SRCD + 'gauja-retro-radio-receiver-low-poly/source/unz/audio receiver1.fbx')
simg = bpy.data.images.load(sb.SRCD + 'gauja-retro-radio-receiver-low-poly/textures/_BaseColor.png')
B = {}
for o in [o for o in bpy.data.objects if o.type == 'MESH']:
    c = np.array([o.matrix_world @ v.co for v in o.data.vertices]); B[o.name] = (c.min(0), c.max(0))
    print('SOURCE %-13s tris %4d min %s max %s' % (o.name, sb.tri_count(o), c.min(0).round(3), c.max(0).round(3)))
src = sb.join_meshes([o for o in bpy.data.objects if o.type == 'MESH'], 'src')
sb.tex_material(src, 'src', simg); src.data.materials[0].use_backface_culling = False
src.data.uv_layers[0].active_render = True
c = sb.coords(src); mn, mx = c.min(0), c.max(0)
k = WIDTH / (mx[0] - mn[0]); cx, cy = (mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2
print('SOURCE all min %s max %s -> scale %.5f' % (mn.round(3), mx.round(3), k))
def S(x, y, z):
    return Vector((-(x - cx) * k, -(y - cy) * k, (z - mn[2]) * k))          # half a turn about Z: the dial of the source looks to +Y
sb.set_coords(src, np.stack([-(c[:, 0] - cx) * k, -(c[:, 1] - cy) * k, (c[:, 2] - mn[2]) * k], 1))
bm = bmesh.new()
def box(lo, hi, skip=()):
    vs = [bm.verts.new(S(x, y, z)) for z in (lo[2], hi[2]) for y in (lo[1], hi[1]) for x in (lo[0], hi[0])]
    faces = {'bottom': (0, 1, 3, 2), 'top': (4, 5, 7, 6), 'ylo': (0, 1, 5, 4), 'yhi': (2, 3, 7, 6), 'xlo': (0, 2, 6, 4), 'xhi': (1, 3, 7, 5)}
    for n, q in faces.items():
        if n not in skip:
            bm.faces.new([vs[i] for i in q])
def disc(name, n, a0, grow=1.0):
    lo, hi = B[name]; x = (lo[0] + hi[0]) / 2; z = (lo[2] + hi[2]) / 2; r = (hi[0] - lo[0]) / 2 / math.cos(math.pi / n) * grow
    ring = [[bm.verts.new(S(x + r * math.cos(math.radians(a0 + 360 * i / n)), y, z + r * math.sin(math.radians(a0 + 360 * i / n)))) for i in range(n)] for y in (B['Cube.009'][1][1] - 0.02, hi[1])]
    for i in range(n):
        bm.faces.new((ring[0][i], ring[0][(i + 1) % n], ring[1][(i + 1) % n], ring[1][i]))
    bm.faces.new(ring[1])
box(B['Cube.009'][0], B['Cube.009'][1])                                      # case
disc('Cylinder.013', 8, 22.5, 0.985)                                         # tuning dial
disc('Cylinder.014', 6, 0, 0.97)                                             # its centre knob
lo, hi = B['Cube.011']; box((lo[0], B['Cube.009'][1][1] - 0.02, lo[2]), hi, skip=('ylo',))      # band switch
lo, hi = B['Plane.002']; box(lo, (max(hi[0], B['Cube.009'][1][0] + 0.03), hi[1], hi[2]), skip=('xlo',))   # side socket
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bmesh.ops.triangulate(bm, faces=bm.faces)
me = bpy.data.meshes.new('SM_Radio'); bm.to_mesh(me); bm.free()
low = bpy.data.objects.new('SM_Radio', me); bpy.context.scene.collection.objects.link(low)
sb.flat(low)
sb.fix_facing(low, tag='RADIO')
print('BUILD tris %d' % sb.tri_count(low))
sb.uv_clean(low, 'UVMap', 0.012, res=1024)
img = bpy.data.images.new('T_Radio_D', TEX, TEX, alpha=False)
sb.tex_material(low, 'M_Radio', img)
px = sb.bake_colour([src], low, img, cage=0.006, maxdist=0.03, margin=2).copy()
fid, bw = sb.raster(low.data, 'UVMap', TEX); m = fid >= 0
miss = m & (px[..., :3].max(2) < 0.01)
print('BAKE mean colour %s, texels the bake missed %d of %d' % (px[..., :3][m].mean(0).round(3), int(miss.sum()), int(m.sum())))
px[..., 3] = 1
px = sb.dilate(px, m & ~miss, 12)
img.pixels.foreach_set(px.astype(np.float32).ravel()); img.filepath_raw = OUT + 'T_Radio_D.png'; img.file_format = 'PNG'; img.save()
ang, lov = sb.lightmap_uv(low)
print('UV LightmapUV angle %d overlapping texels %d' % (ang, lov))
sb.store_facing(low)
c = sb.coords(low)
print('RESULT tris %d min %s max %s size %s (m)' % (sb.tri_count(low), c.min(0).round(4), c.max(0).round(4), np.ptp(c, 0).round(4)))
src.hide_render = True
bpy.ops.wm.save_as_mainfile(filepath=sb.WORK + 'radio_work.blend')
