"""SM_UAZ452 from the Sketchfab UAZ-452 (YouRun, CC BY): add-on gear off (roof rack with the spare wheel, rear door ladder, front bull bar),
cabin and underbody parts off, body decimated, wheels / bumpers / steps / mirrors rebuilt as simple shapes, colour baked from the source.
Run: blender.exe -b --factory-startup --python uaz_10_build.py
"""
import bpy, bmesh, sys, math
import numpy as np
from mathutils import Vector, Matrix
sys.path.insert(0, 'E:/game-dev-team/assets/scientist_base/_work')
import sb

OUT = sb.ROOT + 'SM_UAZ452/'
LIMIT = 1293
TEX = 1024
SIZE = (1.94, 4.36, 2.06)          # body width (mirrors stick out), length, height - the real UAZ-452

sb.empty()
bpy.ops.import_scene.fbx(filepath=sb.SRCD + 'uaz-452-buhanka/source/unrar/UAZ_Buhanka.fbx')
src = sb.join_meshes([o for o in bpy.data.objects if o.type == 'MESH'], 'src')
dimg, dpx = sb.load_px(sb.SRCD + 'uaz-452-buhanka/textures/None_Diffuse.png')
oimg, opx = sb.load_px(sb.SRCD + 'uaz-452-buhanka/textures/None_Opacity.png')
H, W = dpx.shape[:2]

# ---- sort the connected parts of the source
bm = sb.bm_of(src); uvl = bm.loops.layers.uv.active
bmesh.ops.triangulate(bm, faces=bm.faces); bm.faces.ensure_lookup_table(); bm.faces.index_update()
kind_l = bm.faces.layers.int.new('kind')
K = dict(body=1, glass=2, wheel=3, bumper=4, step=5, mirror=6, detail=7, drop=0)
cnt = {k: [0, 0] for k in K}
wheels = []; boxes = []
for comp in sb.islands(bm):
    c = np.array([v.co[:] for v in {v for f in comp for v in f.verts}]); mn = c.min(0); mx = c.max(0); n = len(comp)
    ar = np.array([f.calc_area() for f in comp])
    uvc = np.array([np.mean([l[uvl].uv[:] for l in f.loops], 0) for f in comp]) % 1.0
    xi = np.clip((uvc[:, 0] * W).astype(int), 0, W - 1); yi = np.clip((uvc[:, 1] * H).astype(int), 0, H - 1)
    lum = float((dpx[yi, xi, :3].mean(1) * ar).sum() / ar.sum()); opa = float((opx[yi, xi, 0] * ar).sum() / ar.sum())
    ax = max(abs(mn[0]), abs(mx[0])); size = mx - mn
    if n == 704 and mx[2] < 1.4:
        k = 'wheel'; wheels.append((mn, mx))
    elif mx[2] > 2.75:
        k = 'drop'                                   # roof rack, its posts and bars, the spare wheel with straps, the roof board
    elif n > 100 and size[1] > 0.9 and size[2] > 1.3 or (n == 122 and size[1] > 3.5):
        k = 'body'                                   # the shell, the two front doors, the roof
    elif opa < 0.9 and n <= 10:
        k = 'glass'
    elif size[0] > 1.3 and size[2] < 0.16 and size[1] < 0.12 and mx[2] < 1.4:
        k = 'bumper'                                 # the two stock bumpers stay
    elif lum < 0.12 and (mn[1] < -2.12 or mn[1] > 2.0):
        k = 'drop'                                   # bull bar in front, ladder with its mounts on the rear doors
    elif n == 2 and size[1] < 0.001:
        k = 'drop'                                   # cabin partition
    elif size[1] > 1.5 and ax > 0.85 and mx[2] < 1.1:
        k = 'step'; boxes.append(('step', mn, mx))
    elif ax > 0.95 and n == 60:
        k = 'mirror'; boxes.append(('mirror', mn, mx))
    elif ax > 0.9 or (ax > 0.76 and n == 10):
        k = 'drop'                                   # mirror arms and their bolts (the mirror box reaches the door instead)
    elif mx[2] < 1.2 and ax < 0.81 and -1.5 < mn[1] and mx[1] < 2.0:
        k = 'drop'                                   # underbody: shaft, hubs, spring boxes
    elif ax < 0.74 and mn[1] > -2.05 and mx[1] < 2.03 and mn[2] > 1.3 and mx[2] < 2.53:
        k = 'drop'                                   # cabin: seats, wheel, visors, partition
    elif n == 2 and ax < 0.79 and size[2] > 0.4:
        k = 'drop'                                   # window posts behind the glass
    else:
        k = 'detail'                                 # lights, plates, handles, filler caps: painted onto the body by the bake
    for f in comp:
        f[kind_l] = K[k]
    cnt[k][0] += 1; cnt[k][1] += n
    if k in ('detail', 'bumper', 'step', 'mirror', 'glass') or (k == 'drop' and n >= 96):
        print('PART %-7s tris %4d min %s max %s lum %.2f opacity %.2f' % (k, n, mn.round(2), mx.round(2), lum, opa))
print('SORT (parts, triangles):', {k: tuple(v) for k, v in cnt.items()})
assert len(wheels) == 4 and cnt['bumper'][0] == 2 and cnt['body'][0] == 4 and len(boxes) == 4, (len(wheels), cnt, len(boxes))
bmesh.ops.delete(bm, geom=[f for f in bm.faces if f[kind_l] == 0], context='FACES')
bm.to_mesh(src.data); bm.free()

# ---- real size, nose to +Y, on the ground in the middle
co = sb.coords(src)
kk = np.zeros(len(src.data.polygons), np.int32); src.data.attributes['kind'].data.foreach_get('value', kk)
pv = np.zeros(len(src.data.loops), np.int32); src.data.loops.foreach_get('vertex_index', pv); pv = pv.reshape(-1, 3)
body_v = np.unique(pv[kk == 1]); len_v = np.unique(pv[(kk == 1) | (kk == 4)])
bmn, bmx = co[body_v].min(0), co[body_v].max(0)
zmin = co[:, 2].min()
sx = SIZE[0] / (bmx[0] - bmn[0]); sy = SIZE[1] / np.ptp(co[len_v][:, 1]); sz = SIZE[2] / (bmx[2] - zmin)
cx, cy = (bmn[0] + bmx[0]) / 2, (co[len_v][:, 1].min() + co[len_v][:, 1].max()) / 2
print('SCALE per axis x %.4f y %.4f z %.4f (source body %.3f x %.3f, ground to roof %.3f)' % (sx, sy, sz, bmx[0] - bmn[0], bmx[1] - bmn[1], bmx[2] - zmin))
def tf(p):
    p = np.atleast_2d(np.asarray(p, float))
    return np.stack([-(p[:, 0] - cx) * sx, -(p[:, 1] - cy) * sy, (p[:, 2] - zmin) * sz], 1)       # 180 deg about Z: nose -Y -> +Y
sb.set_coords(src, tf(co))
flatmat = bpy.data.materials.new('src'); flatmat.use_nodes = True
tn = flatmat.node_tree.nodes.new('ShaderNodeTexImage'); tn.image = dimg
flatmat.node_tree.links.new(tn.outputs['Color'], flatmat.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
src.data.materials.clear(); src.data.materials.append(flatmat)
for p in src.data.polygons:
    p.material_index = 0

# ---- low mesh: decimated shell + glass
low = src.copy(); low.data = src.data.copy(); low.name = 'shell'; bpy.context.scene.collection.objects.link(low)
bm = sb.bm_of(low); kl = bm.faces.layers.int['kind']
bmesh.ops.delete(bm, geom=[f for f in bm.faces if f[kl] not in (1, 2, 4)], context='FACES')
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
bm.normal_update()
# the floor of the shell is never seen from above: off (the wheel arches stay)
zfloor = min(v.co.z for f in bm.faces if f[kl] == 1 for v in f.verts)
floor = [f for f in bm.faces if f[kl] == 1 and f.normal.z < -0.9 and f.calc_center_median().z < zfloor + 0.12]
print('SHELL floor faces removed %d (lowest shell point %.3f)' % (len(floor), zfloor))
bmesh.ops.delete(bm, geom=floor, context='FACES')
n_fixed = sum(1 for f in bm.faces if f[kl] in (2, 4))
bm.to_mesh(low.data); bm.free()
# split: the shell is decimated, glass and bumpers are kept as they are
def split(ob, kinds, name):
    o = ob.copy(); o.data = ob.data.copy(); o.name = name; bpy.context.scene.collection.objects.link(o)
    b = sb.bm_of(o); l = b.faces.layers.int['kind']
    bmesh.ops.delete(b, geom=[f for f in b.faces if f[l] not in kinds], context='FACES'); b.to_mesh(o.data); b.free()
    return o
fixed = split(low, (2, 4), 'fixed'); shell = split(low, (1,), 'shell_d')
bpy.data.objects.remove(low, do_unlink=True)

# ---- rebuilt parts: wheels (10 sides, outer cap only), steps and mirrors (boxes)
bm = bmesh.new(); tagl = bm.faces.layers.int.new('tag')
NS = 10
for mn, mx in wheels:
    a, b = tf(mn)[0], tf(mx)[0]; lo = np.minimum(a, b); hi = np.maximum(a, b)
    cyv = (lo[1] + hi[1]) / 2; czv = (lo[2] + hi[2]) / 2; ry = (hi[1] - lo[1]) / 2; rz = (hi[2] - lo[2]) / 2
    xs = (lo[0], hi[0]) if lo[0] > 0 else (hi[0], lo[0])          # (inner, outer)
    ring = [[bm.verts.new((x, cyv + ry * math.cos(2 * math.pi * (k + 0.5) / NS), czv + rz * math.sin(2 * math.pi * (k + 0.5) / NS))) for k in range(NS)] for x in xs]
    for k in range(NS):
        bm.faces.new((ring[0][k], ring[0][(k + 1) % NS], ring[1][(k + 1) % NS], ring[1][k]))
    bm.faces.new(ring[1])
for kind, mn, mx in boxes:
    a, b = tf(mn)[0], tf(mx)[0]; lo = np.minimum(a, b); hi = np.maximum(a, b)
    vs = [bm.verts.new((x, y, z)) for z in (lo[2], hi[2]) for y in (lo[1], hi[1]) for x in (lo[0], hi[0])]
    for q in ((0, 1, 3, 2), (4, 5, 7, 6), (0, 1, 5, 4), (2, 3, 7, 6), (0, 2, 6, 4), (1, 3, 7, 5)):
        f = bm.faces.new([vs[i] for i in q]); f[tagl] = 1 if kind == 'mirror' else 0
    if kind == 'mirror':                                          # a thin arm from the door to the mirror (4 sides, no caps)
        sgn = 1.0 if lo[0] > 0 else -1.0
        xa, xb = sgn * 0.74, (lo[0] if sgn > 0 else hi[0]); ym = (lo[1] + hi[1]) / 2; zm = lo[2] + 0.25 * (hi[2] - lo[2]); h = 0.016
        r = [[bm.verts.new((x, ym + dy, zm + dz)) for dy, dz in ((-h, -h), (h, -h), (h, h), (-h, h))] for x in (xa, xb)]
        for k in range(4):
            f = bm.faces.new((r[0][k], r[0][(k + 1) % 4], r[1][(k + 1) % 4], r[1][k])); f[tagl] = 1
bmesh.ops.triangulate(bm, faces=bm.faces)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
me = bpy.data.meshes.new('rebuilt'); bm.to_mesh(me); bm.free()
reb = bpy.data.objects.new('rebuilt', me); bpy.context.scene.collection.objects.link(reb)
n_reb = sb.tri_count(reb); n_fix = sb.tri_count(fixed)
shell, n0, n1 = sb.decimate_to(shell, LIMIT - n_reb - n_fix, weld=0)
print('BUDGET rebuilt parts %d + glass and bumpers %d + shell %d (was %d) = %d of %d' % (n_reb, n_fix, n1, n0, n_reb + n_fix + n1, LIMIT))
for o in (shell, fixed, reb):
    sb.clear_uv(o.data)
    for a in list(o.data.attributes):
        if a.name == 'kind':
            o.data.attributes.remove(a)
low = sb.join_meshes([shell, fixed, reb], 'SM_UAZ452')
sb.flat(low)
sb.fix_facing(low, tag='UAZ')

# ---- UV, bake, light map UV
sb.uv_clean(low, 'UVMap', 0.012)
ov = sb.overlaps(sb.uvtris(low.data, 'UVMap'))
print('UV UVMap overlapping texels at 1024: %d' % ov)
img = bpy.data.images.new('T_UAZ452_D', TEX, TEX, alpha=False)
sb.tex_material(low, 'M_UAZ452', img)
px = sb.bake_colour([src], low, img, cage=0.03, maxdist=0.14, margin=8)
print('BAKE black texels (rgb<0.02) %.1f%%, mean colour %s' % (100 * (px[..., :3].max(2) < 0.02).mean(), px[..., :3].reshape(-1, 3).mean(0).round(3)))
import os
os.makedirs(OUT, exist_ok=True)
# mirrors and their arms: plain dark housing, pale glass on the side that looks back (the bake gives them random texels)
tg = np.zeros(len(low.data.polygons), np.int32); low.data.attributes['tag'].data.foreach_get('value', tg)
nr = np.zeros(len(low.data.polygons) * 3); low.data.polygons.foreach_get('normal', nr); nr = nr.reshape(-1, 3)
fid, bw = sb.raster(low.data, 'UVMap', TEX)
col = np.where((nr[:, 1] < -0.9)[:, None], np.array([[0.36, 0.41, 0.45]]), np.array([[0.09, 0.09, 0.09]]))
m = (fid >= 0) & (tg[np.clip(fid, 0, None)] == 1)
px[m, :3] = col[fid[m]]
for _ in range(5):                                               # and the margin around those islands
    for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        sm = np.roll(m, (dy, dx), (0, 1)); new = sm & ~m & (fid < 0)
        px[new] = np.roll(px, (dy, dx), (0, 1))[new]; m = m | new
print('MIRRORS repainted texels %d (faces %d)' % (int(m.sum()), int((tg == 1).sum())))
low.data.attributes.remove(low.data.attributes['tag'])
img.pixels.foreach_set(px.ravel())
img.filepath_raw = OUT + 'T_UAZ452_D.png'; img.file_format = 'PNG'; img.save()
ang, lov = sb.lightmap_uv(low)
print('UV LightmapUV angle %d overlapping texels %d' % (ang, lov))
sb.store_facing(low)
src.hide_render = True
c = sb.coords(low)
print('RESULT tris %d min %s max %s size %s' % (sb.tri_count(low), c.min(0).round(3), c.max(0).round(3), np.ptp(c, 0).round(3)))
bpy.ops.wm.save_as_mainfile(filepath=sb.WORK + 'uaz_work.blend')
