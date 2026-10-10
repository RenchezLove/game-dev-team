"""SM_ShotgunShell: a 12-gauge shell for the TOZ-34, built by hand as a 4-sided prism (12 triangles), 7 cm long, lying on its side along Y
(as the cartridges of our 9 mm ammo), brass head at -Y. Colours follow the two shells of the Sketchfab TOZ-34 file (DU1701): red hull, brass head.
Run: blender.exe -b --factory-startup --python shell_10_build.py
"""
import bpy, bmesh, sys, math, os
import numpy as np
from mathutils import Vector
sys.path.insert(0, 'E:/game-dev-team/assets/scientist_base/_work')
import sb
OUT = sb.ROOT + 'SM_ShotgunShell/'; os.makedirs(OUT, exist_ok=True)
TEX = 128
L = 0.070; W = 0.0205                                            # length, width across the flats
sb.empty()
bm = bmesh.new()
h = W / 2
ring = [[bm.verts.new((x, y, z)) for x, z in ((-h, 0.0), (h, 0.0), (h, W), (-h, W))] for y in (-L / 2, L / 2)]
for k in range(4):
    bm.faces.new((ring[0][k], ring[0][(k + 1) % 4], ring[1][(k + 1) % 4], ring[1][k]))
bm.faces.new(ring[0]); bm.faces.new(ring[1])
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bmesh.ops.triangulate(bm, faces=bm.faces)
me = bpy.data.meshes.new('SM_ShotgunShell'); bm.to_mesh(me); bm.free()
ob = bpy.data.objects.new('SM_ShotgunShell', me); bpy.context.scene.collection.objects.link(ob)
sb.flat(ob)
sb.fix_facing(ob, ground=False, tag='SHELL')
sb.uv_clean(ob, 'UVMap', 0.04, res=TEX)
T = len(me.polygons)
co = sb.coords(ob); pv = np.zeros(T * 3, np.int32); me.loops.foreach_get('vertex_index', pv); pv = pv.reshape(-1, 3)
nr = np.zeros(T * 3); me.polygons.foreach_get('normal', nr); nr = nr.reshape(-1, 3)
fid, bw = sb.raster(me, 'UVMap', TEX); m = fid >= 0; f = np.clip(fid, 0, None)
P = (co[pv[f]] * bw[..., None]).sum(2); N = nr[f]
RED = np.array([0.66, 0.10, 0.08]); BRASS = np.array([0.74, 0.56, 0.22]); DARK = np.array([0.36, 0.26, 0.10])
rgb = np.zeros((TEX, TEX, 3))
y = P[..., 1]; r = np.hypot(P[..., 0], P[..., 2] - h)
side = m & (abs(N[..., 1]) < 0.5)
head_len = 0.016
rgb[side] = np.where((y[side] < -L / 2 + head_len)[:, None], BRASS[None], RED[None])
rim = side & (y < -L / 2 + 0.003); rgb[rim] = BRASS * 0.78
edge = side & (abs(y - (-L / 2 + head_len)) < 0.0012); rgb[edge] = DARK
crimp = side & (y > L / 2 - 0.006); rgb[crimp] = RED * 0.80
# a lighter band along every flat - reads as a round hull
band = side & ((abs(P[..., 0]) < h * 0.35) | (abs(P[..., 2] - h) < h * 0.35)); rgb[band] = np.clip(rgb[band] * 1.14, 0, 1)
back = m & (N[..., 1] < -0.5)
rgb[back] = BRASS * 0.92; rgb[back & (r < 0.0042)] = np.array([0.80, 0.74, 0.62]); rgb[back & (abs(r - 0.0048) < 0.0007)] = DARK
front = m & (N[..., 1] > 0.5)
ang = np.arctan2(P[..., 2] - h, P[..., 0])
rgb[front] = RED * 0.86; star = front & (np.abs(np.sin(ang * 3)) < 0.22) & (r < h * 0.95); rgb[star] = RED * 0.50
px = np.zeros((TEX, TEX, 4), np.float32); px[..., :3] = rgb; px[..., 3] = 1
px = sb.dilate(px, m, 8)
img = sb.save_png(px, OUT + 'T_ShotgunShell_D.png', 'T_ShotgunShell_D')
sb.tex_material(ob, 'M_ShotgunShell', img)
sb.store_facing(ob)
c = sb.coords(ob)
print('RESULT tris %d min %s max %s size %s (m)' % (sb.tri_count(ob), c.min(0).round(4), c.max(0).round(4), np.ptp(c, 0).round(4)))
bpy.ops.wm.save_as_mainfile(filepath=sb.WORK + 'shell_work.blend')
