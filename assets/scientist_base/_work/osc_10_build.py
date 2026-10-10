"""SM_Oscilloscope from the Sketchfab oscillograph (maxdragon, CC BY, 3774 triangles): rebuilt by hand from the measured parts of the source
(case, screen plate, tube bezel, 6 big and 4 small knobs, handle = 170 triangles), everything else (louvres, sockets, toggles, labels, the green
trace) is baked from the source into the colour texture.  Screen looks to -Y, origin under the middle, 30 cm high.
Run: blender.exe -b --factory-startup --python osc_10_build.py
"""
import bpy, bmesh, sys, math, os
import numpy as np
from mathutils import Vector
sys.path.insert(0, 'E:/game-dev-team/assets/scientist_base/_work')
import sb

OUT = sb.ROOT + 'SM_Oscilloscope/'; os.makedirs(OUT, exist_ok=True)
TEX = 512
HEIGHT = 0.30
sb.empty()                                                       # the source object is appended into a clean scene (its own file has an odd saved context)
with bpy.data.libraries.load(sb.SRCD + 'oscillograph/source/oscilloscope.blend', link=False) as (df, dt):
    dt.objects = ['oscilloscope']
src = dt.objects[0]; bpy.context.scene.collection.objects.link(src)
bpy.context.view_layer.update()
for md in list(src.modifiers):
    src.modifiers.remove(md)
simg = bpy.data.images.load(sb.SRCD + 'oscillograph/textures/oscilloscope_01.png')
sb.tex_material(src, 'src', simg); src.data.materials[0].use_backface_culling = False
c = sb.coords(src); mn, mx = c.min(0), c.max(0)
k = HEIGHT / (mx[2] - mn[2]); cx, cy = (mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2
print('SOURCE min %s max %s (cm) -> scale %.5f' % (mn.round(2), mx.round(2), k))
sb.set_coords(src, (c - np.array([cx, cy, mn[2]])) * k)
def S(x, y, z):
    return Vector(((x - cx) * k, (y - cy) * k, (z - mn[2]) * k))

# ---- parts of the source, measured (cm, source axes): see _osc_parts.log
bm = bmesh.new()
def box(lo, hi, skip=()):
    vs = [bm.verts.new(S(x, y, z)) for z in (lo[2], hi[2]) for y in (lo[1], hi[1]) for x in (lo[0], hi[0])]
    faces = {'bottom': (0, 1, 3, 2), 'top': (4, 5, 7, 6), 'front': (0, 1, 5, 4), 'back': (2, 3, 7, 6), 'left': (0, 2, 6, 4), 'right': (1, 3, 7, 5)}
    out = [bm.faces.new([vs[i] for i in q]) for n, q in faces.items() if n not in skip]
    return out
def knob(x, z, r, y_base, y_tip, n=4, a0=45):
    """prism along -Y with a cap at the tip"""
    ring = [[bm.verts.new(S(x + r * math.cos(math.radians(a0 + 360 * i / n)), y, z + r * math.sin(math.radians(a0 + 360 * i / n)))) for i in range(n)] for y in (y_base, y_tip)]
    for i in range(n):
        bm.faces.new((ring[0][i], ring[0][(i + 1) % n], ring[1][(i + 1) % n], ring[1][i]))
    bm.faces.new(ring[1])
box((-8.5, -15.2, 0.0), (8.5, 16.0, 25.3))                                         # case, closed on all six sides (it may be laid on any side), lowered onto the table instead of the four feet
box((-8.0, -16.5, 12.3), (4.0, -15.1, 24.3))                                        # screen plate
knob(-2.0, 18.3, 5.35 / math.cos(math.radians(22.5)) * 0.97, -16.4, -18.8, n=8, a0=22.5)   # tube bezel with the screen on its cap
for x in (-5.0, 0.0, 5.0):
    for z in (5.3, 9.3):
        knob(x, z, 1.2 * 1.25, -15.1, -17.2)                                      # six big knobs
for z in (13.8, 16.8, 19.8, 22.8):
    knob(6.0, z, 0.9 * 1.25, -15.1, -16.6)                                        # four small knobs
box((-1.4, -7.0, 27.0), (1.4, 7.0, 28.2))                                          # handle: bar and two legs
box((-1.4, -7.0, 25.2), (1.4, -5.6, 27.0), skip=('bottom', 'top'))
box((-1.4, 5.6, 25.2), (1.4, 7.0, 27.0), skip=('bottom', 'top'))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bmesh.ops.triangulate(bm, faces=bm.faces)
me = bpy.data.meshes.new('SM_Oscilloscope'); bm.to_mesh(me); bm.free()
low = bpy.data.objects.new('SM_Oscilloscope', me); bpy.context.scene.collection.objects.link(low)
sb.flat(low)
sb.fix_facing(low, tag='OSC')
print('BUILD tris %d' % sb.tri_count(low))
sb.uv_clean(low, 'UVMap', 0.012, res=1024)
img = bpy.data.images.new('T_Oscilloscope_D', TEX, TEX, alpha=False)
sb.tex_material(low, 'M_Oscilloscope', img)
px = sb.bake_colour([src], low, img, cage=0.021, maxdist=0.05, margin=2).copy()
fid, bw = sb.raster(low.data, 'UVMap', TEX); m = fid >= 0
miss = m & (px[..., :3].max(2) < 0.01)
print('BAKE mean colour %s, texels the bake missed %d of %d' % (px[..., :3][m].mean(0).round(3), int(miss.sum()), int(m.sum())))
px[..., 3] = 1
px = sb.dilate(px, m & ~miss, 12)
img.pixels.foreach_set(px.astype(np.float32).ravel()); img.filepath_raw = OUT + 'T_Oscilloscope_D.png'; img.file_format = 'PNG'; img.save()
ang, lov = sb.lightmap_uv(low)
print('UV LightmapUV angle %d overlapping texels %d' % (ang, lov))
sb.store_facing(low)
c = sb.coords(low)
print('RESULT tris %d min %s max %s size %s (m)' % (sb.tri_count(low), c.min(0).round(4), c.max(0).round(4), np.ptp(c, 0).round(4)))
src.hide_render = True
bpy.ops.wm.save_as_mainfile(filepath=sb.WORK + 'osc_work.blend')
