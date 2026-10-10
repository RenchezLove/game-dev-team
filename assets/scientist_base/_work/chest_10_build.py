"""SM_StashChest from the Sketchfab "wooden chest" (nofaced3d, CC BY, 806 triangles): case, padlock and the two side handles rebuilt as boxes
(42 triangles); iron edging, rivets, hasp, handle shapes and wood are baked from the source into the colour texture.
Long side along X, the padlock looks to -Y, origin under the middle, 100 cm long.
Run: blender.exe -b --factory-startup --python chest_10_build.py
"""
import bpy, bmesh, sys, math, os
import numpy as np
from mathutils import Vector
sys.path.insert(0, 'E:/game-dev-team/assets/scientist_base/_work')
import sb
OUT = sb.ROOT + 'SM_StashChest/'; os.makedirs(OUT, exist_ok=True)
TEX = 512
LENGTH = 1.00
sb.empty()
src = sb.load_dae_simple(sb.SRCD + 'wooden-chest/source/unz/model/model.dae')[0]
simg = bpy.data.images.load(sb.SRCD + 'wooden-chest/textures/DefaultMaterial_albedo.jpeg')
sb.tex_material(src, 'src', simg); src.data.materials[0].use_backface_culling = False
c = sb.coords(src); mn, mx = c.min(0), c.max(0)
k = LENGTH / (mx[1] - mn[1])
print('SOURCE min %s max %s -> scale %.4f' % (mn.round(3), mx.round(3), k))
BX = (-0.505, 0.448)                                             # the case of the source (its biggest part), see _chest_parts.log
cxs = (BX[0] + BX[1]) / 2
def T(p):
    p = np.atleast_2d(np.asarray(p, float))
    return np.stack([p[:, 1] * k, -(p[:, 0] - cxs) * k, (p[:, 2] - mn[2]) * k], 1)      # lock side +X of the source -> -Y
sb.set_coords(src, T(c))
bm = bmesh.new()
def box(lo, hi, skip=()):
    a, b = T(lo)[0], T(hi)[0]; lo, hi = np.minimum(a, b), np.maximum(a, b)
    vs = [bm.verts.new((x, y, z)) for z in (lo[2], hi[2]) for y in (lo[1], hi[1]) for x in (lo[0], hi[0])]
    faces = {'bottom': (0, 1, 3, 2), 'top': (4, 5, 7, 6), 'ylo': (0, 1, 5, 4), 'yhi': (2, 3, 7, 6), 'xlo': (0, 2, 6, 4), 'xhi': (1, 3, 7, 5)}
    for n, q in faces.items():
        if n not in skip:
            bm.faces.new([vs[i] for i in q])
box((BX[0], -0.968, -0.509), (BX[1], 0.968, 0.509))                              # case
box((BX[1] - 0.01, -0.077, -0.083), (0.535, 0.077, 0.172))                       # padlock
box((-0.184, 0.960, -0.145), (0.143, 1.000, 0.105))                              # handle on one end
box((-0.184, -1.000, -0.145), (0.143, -0.960, 0.105))                            # handle on the other end
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bmesh.ops.triangulate(bm, faces=bm.faces)
me = bpy.data.meshes.new('SM_StashChest'); bm.to_mesh(me); bm.free()
low = bpy.data.objects.new('SM_StashChest', me); bpy.context.scene.collection.objects.link(low)
sb.flat(low); sb.fix_facing(low, tag='CHEST')
print('BUILD tris %d' % sb.tri_count(low))
sb.uv_clean(low, 'UVMap', 0.012, res=1024)
img = bpy.data.images.new('T_StashChest_D', TEX, TEX, alpha=False)
sb.tex_material(low, 'M_StashChest', img)
px = sb.bake_colour([src], low, img, cage=0.012, maxdist=0.06, margin=2).copy()
fid, bw = sb.raster(low.data, 'UVMap', TEX); m = fid >= 0
miss = m & (px[..., :3].max(2) < 0.01)
print('BAKE mean colour %s, texels the bake missed %d of %d' % (px[..., :3][m].mean(0).round(3), int(miss.sum()), int(m.sum())))
px[..., 3] = 1; px = sb.dilate(px, m & ~miss, 12)
img.pixels.foreach_set(px.astype(np.float32).ravel()); img.filepath_raw = OUT + 'T_StashChest_D.png'; img.file_format = 'PNG'; img.save()
ang, lov = sb.lightmap_uv(low); print('UV LightmapUV angle %d overlapping texels %d' % (ang, lov))
sb.store_facing(low)
c = sb.coords(low)
print('RESULT tris %d min %s max %s size %s (m)' % (sb.tri_count(low), c.min(0).round(4), c.max(0).round(4), np.ptp(c, 0).round(4)))
src.hide_render = True
bpy.ops.wm.save_as_mainfile(filepath=sb.WORK + 'chest_work.blend')
