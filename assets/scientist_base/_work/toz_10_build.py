"""SM_Shotgun_TOZ34 from the Sketchfab low-poly TOZ-34 (DU1701, CC BY): parts joined, hidden extractors off, decimated to <= 700 triangles,
flat material colours baked into one texture (the checkering, a normal map in the source, is painted), 1.15 m long.
Axes and origin as our pistol in the game (weapons_tripo/SM_Pistol.fbx): muzzle to -Y, top to +Z, origin in the grip.
Run: blender.exe -b --factory-startup --python toz_10_build.py
"""
import bpy, bmesh, sys, math, os
import numpy as np
from mathutils import Vector
sys.path.insert(0, 'E:/game-dev-team/assets/scientist_base/_work')
import sb

OUT = sb.ROOT + 'SM_Shotgun_TOZ34/'
LIMIT = 700
TEX = 512
LENGTH = 1.15
os.makedirs(OUT, exist_ok=True)

# ---- how our pistol sits (measured, not remembered)
sb.empty()
bpy.ops.import_scene.fbx(filepath='E:/game-dev-team/assets/weapons_tripo/SM_Pistol.fbx')
po = [o for o in bpy.data.objects if o.type == 'MESH'][0]
pc = np.array([po.matrix_world @ v.co for v in po.data.vertices])
grip = pc[pc[:, 2] < pc[:, 2].min() + 0.04]; top = pc[pc[:, 2] > 0.0]
print('PISTOL in the game: min %s max %s (m); grip (lowest 4 cm) y %.3f..%.3f; upper part y %.3f..%.3f -> muzzle looks to %s, origin %.3f m from the rear end' % (
    pc.min(0).round(3), pc.max(0).round(3), grip[:, 1].min(), grip[:, 1].max(), top[:, 1].min(), top[:, 1].max(),
    '-Y' if abs(top[:, 1].min()) > abs(top[:, 1].max()) else '+Y', pc[:, 1].max()))

bpy.ops.wm.open_mainfile(filepath=sb.SRCD + 'low-poly-toz-34/source/toz34.blend', use_scripts=False)
for o in list(bpy.data.objects):
    if o.type != 'MESH':
        bpy.data.objects.remove(o, do_unlink=True)
shells = [o for o in bpy.data.objects if o.name in ('12/76', '1276')]
drop = [o for o in bpy.data.objects if 'extractor' in o.name]
for o in shells + drop:
    print('LEFT OUT %s (%d tris)' % (o.name, sb.tri_count(o)))
    bpy.data.objects.remove(o, do_unlink=True)
parts = [o for o in bpy.data.objects if o.type == 'MESH']
print('PARTS', [(o.name, sb.tri_count(o)) for o in parts], 'sum', sum(sb.tri_count(o) for o in parts))
# checkering of the grip and fore-end is a normal map in the source -> its own (darker) colour, the pattern is painted later
for mt in bpy.data.materials:
    b = mt.node_tree.nodes.get('Principled BSDF') if mt.node_tree else None
    if b:
        for l in list(b.inputs['Normal'].links):
            mt.node_tree.links.remove(l)
        c = b.inputs['Base Color'].default_value
        print('MATERIAL %-10s base colour (linear) %s' % (mt.name, tuple(round(a, 3) for a in c)))
        b.inputs['Metallic'].default_value = 0.0
CHK = bpy.data.materials['1wo mesh1'].node_tree.nodes['Principled BSDF'].inputs['Base Color']
CHK.default_value = (0.0, 1.0, 0.0, 1.0)                         # marker colour, replaced by the painted pattern
bpy.data.materials['1w'].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.42, 0.42, 0.44, 1)   # bare steel instead of pure white
bpy.data.materials['2b'].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.008, 0.008, 0.008, 1)   # not pure black: black = the bake missed
for o in parts:
    at = o.data.attributes.new('part', 'INT', 'FACE')
    at.data.foreach_set('value', np.full(len(o.data.polygons), 1 if o.name == 'toz34 barrels' else 0, np.int32))
src = sb.join_meshes(parts, 'src')
# ---- turn: muzzle +X of the source -> -Y, scale to the real length
c = sb.coords(src); mn, mx = c.min(0), c.max(0)
k = LENGTH / (mx[0] - mn[0])
print('SOURCE size %s -> scale %.5f' % ((mx - mn).round(3), k))
c2 = np.stack([c[:, 1] * k * 1.5, -c[:, 0] * k, c[:, 2] * k], 1)       # the source is too flat (2.9 cm): one and a half times thicker
sb.set_coords(src, c2)
bm = sb.bm_of(src); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(src.data); bm.free()
sb.fix_facing(src, ground=False, tag='SOURCE')
# ---- origin: the grip (wrist of the stock right behind the trigger guard, where the right hand holds)
c = sb.coords(src)
me = src.data
mi = np.zeros(len(me.polygons), np.int32); me.polygons.foreach_get('material_index', mi)
names = [m.name for m in me.materials]
ls = np.zeros(len(me.polygons), np.int32); me.polygons.foreach_get('loop_start', ls); lt = np.zeros(len(me.polygons), np.int32); me.polygons.foreach_get('loop_total', lt)
lv = np.zeros(len(me.loops), np.int32); me.loops.foreach_get('vertex_index', lv)
def verts_of(matnames):
    idx = [names.index(n) for n in matnames if n in names]
    out = set()
    for p in np.nonzero(np.isin(mi, idx))[0]:
        out.update(lv[ls[p]:ls[p] + lt[p]].tolist())
    return c[sorted(out)]
chk = verts_of(['1wo mesh1'])
rear_chk = chk[chk[:, 1] > np.median(chk[:, 1])] if np.ptp(chk[:, 1]) > 0.2 else chk     # checkering exists on the fore-end and on the grip
gy = float(rear_chk[:, 1].mean())
ring = c[abs(c[:, 1] - gy) < 0.03]
gz = float((ring[:, 2].min() + ring[:, 2].max()) / 2); gx = float((ring[:, 0].min() + ring[:, 0].max()) / 2)
print('GRIP checkering y %.3f..%.3f z %.3f..%.3f -> origin at (%.4f, %.4f, %.4f) of the turned source' % (rear_chk[:, 1].min(), rear_chk[:, 1].max(), rear_chk[:, 2].min(), rear_chk[:, 2].max(), gx, gy, gz))
sb.set_coords(src, c - np.array([gx, gy, gz]))

# ---- low mesh (2026-10-09, after Rinat saw holes and one-sided strips in Unreal): every part is its own CLOSED solid.
# All islands of the source are closed; each is decimated on its own (a closed island stays closed), nothing "hidden" is cut away,
# the barrels with the ventilated rib are replaced by two closed 6-sided tubes and a closed rib, the tiny pins and sights are dropped.
work = src.copy(); work.data = src.data.copy(); work.name = 'work'; bpy.context.scene.collection.objects.link(work)
bm = sb.bm_of(work); pl_ = bm.faces.layers.int['part']
for pv_ in (0, 1):                                               # weld inside each source object only (the receiver must not fuse with the barrels)
    bmesh.ops.remove_doubles(bm, verts=list({v for f in bm.faces if f[pl_] == pv_ for v in f.verts}), dist=1e-5)
bmesh.ops.triangulate(bm, faces=bm.faces)
bm.faces.ensure_lookup_table(); bm.faces.index_update()
mnames = [m_.name for m_ in work.data.materials]
il = bm.faces.layers.int.new('isl'); bm.faces.ensure_lookup_table(); bm.faces.index_update(); isl = sb.islands(bm)
PLAN = []; barrel = None; TRIG = []; BND = {}
for i, comp in enumerate(isl):
    for f in comp:
        f[il] = i
    cc = np.array([v.co[:] for f in comp for v in f.verts]); n = len(comp); mats = {mnames[f.material_index] for f in comp}
    op = sum(1 for e in {e for f in comp for e in f.edges} if len(e.link_faces) != 2)
    wood = bool(mats & {'1wo', '1wo mesh1'}); ylen = np.ptp(cc[:, 1])
    if not wood and ylen > 0.5:
        kind, tgt = 'barrels', 0; barrel = cc
    elif n <= 28:
        kind, tgt = 'pin or sight (dropped)', 0
    elif wood and ylen > 0.35:
        kind, tgt = 'stock', 218
    elif wood:
        kind, tgt = 'fore-end', 130
    elif n == 158:
        kind, tgt = 'receiver', 124
    elif n == 140:
        kind, tgt = 'trigger guard', 92
    elif n in (52, 76):
        kind, tgt = 'trigger', -1; TRIG.append((cc.min(0), cc.max(0)))
    else:
        kind, tgt = 'lock lever', 40
    PLAN.append((i, kind, tgt, n, op)); BND[kind] = (cc.min(0), cc.max(0))
    print('ISLAND %-22s tris %4d, edges without exactly two faces %d, y %.3f..%.3f z %.3f..%.3f -> %s' % (kind, n, op, cc[:, 1].min(), cc[:, 1].max(), cc[:, 2].min(), cc[:, 2].max(), ('%d tris' % tgt) if tgt > 0 else ('a closed box, 12 tris' if tgt < 0 else 'not taken')))
assert barrel is not None
bm.to_mesh(work.data); bm.free()
pieces = []
for i, kind, tgt, n, op in PLAN:
    if tgt <= 0:
        continue
    o = work.copy(); o.data = work.data.copy(); o.name = 'isl%d' % i; bpy.context.scene.collection.objects.link(o)
    b = sb.bm_of(o); l_ = b.faces.layers.int['isl']; bmesh.ops.delete(b, geom=[f for f in b.faces if f[l_] != i], context='FACES')
    bmesh.ops.recalc_face_normals(b, faces=b.faces); b.to_mesh(o.data); b.free()
    o, a0, a1 = sb.decimate_to(o, tgt, weld=0)
    b = sb.bm_of(o); bad = sum(1 for e in b.edges if len(e.link_faces) != 2); vol = b.calc_volume(signed=True); b.free()
    print('PIECE %-14s %4d -> %3d tris, edges without exactly two faces %d, signed volume %+.6f' % (kind, a0, a1, bad, vol))
    pieces.append(o)
# barrels: measured at the muzzle of the source (the tubes have points only at their ends)
y0, y1 = float(barrel[:, 1].min()), float(barrel[:, 1].max())
mz = barrel[barrel[:, 1] < y0 + 0.02]
rx = float(np.abs(mz[:, 0]).max()); rz = rx / 1.5; zlo = float(mz[:, 2].min()); ribh = 0.004
print('BARRELS y %.3f..%.3f, tube radius %.4f (x %.4f), lowest point z %.4f' % (y0, y1, rz, rx, zlo))
bm = bmesh.new()
for zc in (zlo + rz, zlo + 3 * rz):
    ring = [[bm.verts.new((rx * math.cos(math.radians(30 + 60 * k_)), y, zc + rz * math.sin(math.radians(30 + 60 * k_)))) for k_ in range(6)] for y in (y1, y0)]
    for k_ in range(6):
        bm.faces.new((ring[0][k_], ring[0][(k_ + 1) % 6], ring[1][(k_ + 1) % 6], ring[1][k_]))
    bm.faces.new(ring[0]); bm.faces.new(ring[1])
wr = rx * 0.42; zt = zlo + 4 * rz - 0.003
vs = [bm.verts.new((x_, y, z)) for z in (zt, zt + ribh + 0.003) for y in (y0 + 0.004, y1) for x_ in (-wr, wr)]
for q in ((0, 1, 3, 2), (4, 5, 7, 6), (0, 1, 5, 4), (2, 3, 7, 6), (0, 2, 6, 4), (1, 3, 7, 5)):
    bm.faces.new([vs[i_] for i_ in q])
# the breech block of the source barrels filled the space between the fore-end and the receiver under the tubes: a closed dark block there
fe, rc = BND['fore-end'], BND['receiver']
TRIG.append((np.array([-(rx - 0.002), fe[1][1] - 0.07, max(fe[0][2], rc[0][2]) + 0.006]), np.array([rx - 0.002, rc[0][1] + 0.05, zlo + rz])))
print('FILLER block between fore-end and receiver: y %.3f..%.3f z %.3f..%.3f' % (TRIG[-1][0][1], TRIG[-1][1][1], TRIG[-1][0][2], TRIG[-1][1][2]))
for lo_, hi_ in TRIG:                                            # the two triggers: closed blades (boxes leaning as the source blades do not matter at this size)
    vs = [bm.verts.new((x_, y, z)) for z in (lo_[2], hi_[2]) for y in (lo_[1], hi_[1]) for x_ in (lo_[0], hi_[0])]
    for q in ((0, 1, 3, 2), (4, 5, 7, 6), (0, 1, 5, 4), (2, 3, 7, 6), (0, 2, 6, 4), (1, 3, 7, 5)):
        bm.faces.new([vs[i_] for i_ in q])
bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bmesh.ops.triangulate(bm, faces=bm.faces)
tme = bpy.data.meshes.new('tubes'); bm.to_mesh(tme); bm.free()
tubes = bpy.data.objects.new('tubes', tme); bpy.context.scene.collection.objects.link(tubes)
for o in pieces:
    for a in list(o.data.attributes):
        if a.name in ('isl', 'part'):
            o.data.attributes.remove(a)
    sb.clear_uv(o.data); o.data.materials.clear()
bpy.data.objects.remove(work, do_unlink=True)
low = sb.join_meshes(pieces + [tubes], 'SM_Shotgun_TOZ34')
bm = sb.bm_of(low); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bad = sum(1 for e in bm.edges if len(e.link_faces) != 2)
vols = []
for comp in sb.islands(bm):
    t = bmesh.new(); vm = {}
    for f in comp:
        t.faces.new([vm.setdefault(v, t.verts.new(v.co)) for v in f.verts])
    vols.append(t.calc_volume(signed=True)); t.free()
bm.to_mesh(low.data); bm.free()
n1 = sb.tri_count(low)
print('CLOSED CHECK: %d triangles (limit %d), %d closed solids, edges without exactly two faces %d, solids turned inside out %d' % (n1, LIMIT, len(vols), bad, sum(1 for v in vols if v <= 0)))
assert n1 <= LIMIT and bad == 0 and all(v > 0 for v in vols)
sb.clear_uv(low.data); sb.flat(low)
ang_, ov_ = sb.uv_clean(low, 'UVMap', 0.012, res=1024)
if ov_:
    # slivers left by the decimation overlap in any island layout: give every triangle its own place (the colours are flat, seams do not show)
    sb.only(low); bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.lightmap_pack(PREF_CONTEXT='ALL_FACES', PREF_PACK_IN_ONE=True, PREF_NEW_UVLAYER=False, PREF_BOX_DIV=24, PREF_MARGIN_DIV=0.25)
    bpy.ops.object.mode_set(mode='OBJECT')
    print('UV UVMap repacked face by face, overlapping texels at %d: %d' % (1024, sb.overlaps(sb.uvtris(low.data, 'UVMap'), 1024)))
img = bpy.data.images.new('T_Shotgun_TOZ34_D', TEX, TEX, alpha=False)
sb.tex_material(low, 'M_Shotgun_TOZ34', img)
px = sb.bake_colour([src], low, img, cage=0.004, maxdist=0.02, margin=2).copy()
me = low.data; T = len(me.polygons)
co = sb.coords(low); pv = np.zeros(T * 3, np.int32); me.loops.foreach_get('vertex_index', pv); pv = pv.reshape(-1, 3)
fid, bw = sb.raster(me, 'UVMap', TEX); m = fid >= 0; f = np.clip(fid, 0, None)
P = (co[pv[f]] * bw[..., None]).sum(2)
rgb = px[..., :3].astype(np.float64)
is_chk = m & (rgb[..., 1] > 0.6) & (rgb[..., 0] < 0.4) & (rgb[..., 2] < 0.4)
wood = m & ~is_chk & (rgb[..., 0] > rgb[..., 2] * 1.4) & (rgb[..., 0] > 0.15)
wcol = rgb[wood].mean(0) if wood.any() else np.array([0.33, 0.21, 0.15])
print('BAKE wood colour %s (texels %d), checkering texels %d, black texels inside faces %d' % (wcol.round(3), wood.sum(), is_chk.sum(), int((rgb[m].max(1) < 0.01).sum())))
# wood: grain streaks along the gun (Y)
ph = np.sin(P[..., 2] * 230 + np.sin(P[..., 1] * 7) * 2.5 + P[..., 0] * 90) * 0.5 + 0.5
rgb[wood] = rgb[wood] * (0.95 + 0.11 * ph[wood][:, None])
# checkering: crossed fine lines, darker than the wood
d1 = np.mod((P[..., 1] + P[..., 2]) / 0.006, 1.0); d2 = np.mod((P[..., 1] - P[..., 2]) / 0.006, 1.0)
line = (d1 < 0.34) | (d2 < 0.34)
rgb[is_chk] = np.where(line[is_chk][:, None], wcol[None] * 0.52, wcol[None] * 0.86)
px[..., :3] = np.clip(rgb, 0, 1); px[..., 3] = 1
miss = m & (px[..., :3].max(2) < 0.01)
print('BAKE texels the bake missed: %d -> filled from their neighbours' % int(miss.sum()))
px = sb.dilate(px, m & ~miss, 12)
img.pixels.foreach_set(px.astype(np.float32).ravel()); img.filepath_raw = OUT + 'T_Shotgun_TOZ34_D.png'; img.file_format = 'PNG'; img.save()
sb.store_facing(low)
c = sb.coords(low)
print('RESULT tris %d min %s max %s size %s (m); muzzle end y %.4f, butt end y %.4f' % (sb.tri_count(low), c.min(0).round(4), c.max(0).round(4), np.ptp(c, 0).round(4), c[:, 1].min(), c[:, 1].max()))
src.hide_render = True
bpy.ops.wm.save_as_mainfile(filepath=sb.WORK + 'toz_work.blend')
