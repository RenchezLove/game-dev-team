"""SM_PersonalChest: our own crate (lowpoly_market/SM_Crate_01.fbx, in the game SM_BanditCrate) as a separate model with its own texture -
army green paint worn off on the edges and boards, the wood shows through. Geometry is the same 336 triangles, 74 cm, origin under the middle.
Run: blender.exe -b --factory-startup --python crate_10_build.py
"""
import bpy, bmesh, sys, math, os
import numpy as np
from mathutils import Vector
sys.path.insert(0, 'E:/game-dev-team/assets/scientist_base/_work')
import sb

OUT = sb.ROOT + 'SM_PersonalChest/'
TEX = 512
SIZE = 0.74
WOOD = np.array([0.60, 0.44, 0.29])          # the wood of our crate (palette 0.69 0.49 0.33), a little weathered
WOOD_DARK = np.array([0.36, 0.25, 0.16])
GREEN = np.array([0.285, 0.335, 0.185])      # army protective green
GREEN_DARK = np.array([0.20, 0.245, 0.135])
os.makedirs(OUT, exist_ok=True)

sb.empty()
bpy.ops.import_scene.fbx(filepath='E:/game-dev-team/assets/lowpoly_market/SM_Crate_01.fbx')
ob = sb.join_meshes([o for o in bpy.data.objects if o.type == 'MESH'], 'SM_PersonalChest')
bm = sb.bm_of(ob); bm.normal_update()
c = np.array([v.co[:] for v in bm.verts]); mn, mx = c.min(0), c.max(0)
k = SIZE / (mx - mn).max()
for v in bm.verts:
    v.co = Vector(((v.co.x - (mn[0] + mx[0]) / 2) * k, (v.co.y - (mn[1] + mx[1]) / 2) * k, (v.co.z - mn[2]) * k))
bm.normal_update()
pid = bm.faces.layers.int.new('pid')
POLY = []                                    # per source polygon: kind, grain direction, wear edges
comps = sb.islands(bm)
for comp in comps:
    kind = {48: 0, 17: 1, 6: 2}.get(len(comp), 0)            # 0 frame boards, 1 plank panel, 2 diagonal brace
    for f in comp:
        e = max(f.edges, key=lambda e: e.calc_length())
        g = (e.verts[1].co - e.verts[0].co).normalized()
        segs = []
        for e in f.edges:
            lf = e.link_faces
            if len(lf) == 2 and lf[0].normal.dot(lf[1].normal) > 0.99:
                continue                                      # the same board goes on behind this edge
            convex = True
            if len(lf) == 2:
                o = lf[1] if lf[0] is f else lf[0]
                convex = (o.calc_center_median() - f.calc_center_median()).dot(f.normal) < 1e-6   # outer corner wears, inner corner collects dirt
            segs.append((np.array(e.verts[0].co[:]), np.array(e.verts[1].co[:]), convex))
        f[pid] = len(POLY); POLY.append((kind, np.array(g[:]), segs, np.array(f.normal[:]), np.array(f.calc_center_median()[:])))
print('SOURCE polygons %d (frame %d, panel %d, brace %d), scale %.3f' % (len(POLY), *[sum(1 for p in POLY if p[0] == i) for i in range(3)], k))
bmesh.ops.triangulate(bm, faces=bm.faces)
bm.to_mesh(ob.data); bm.free()
sb.clear_uv(ob.data); sb.flat(ob)
sb.fix_facing(ob, tag='CRATE')
sb.uv_clean(ob, 'UVMap', 0.012, res=TEX)
me = ob.data; T = len(me.polygons)
pidv = np.zeros(T, np.int32); me.attributes['pid'].data.foreach_get('value', pidv)
co = sb.coords(ob); pv = np.zeros(T * 3, np.int32); me.loops.foreach_get('vertex_index', pv); pv = pv.reshape(-1, 3)
fid, bw = sb.raster(me, 'UVMap', TEX)
m = fid >= 0; f = np.clip(fid, 0, None)
P = (co[pv[f]] * bw[..., None]).sum(2)
PI = pidv[f]


def vnoise(p, freq, seed):
    """value noise in 3D, 0..1"""
    q = p * freq; i = np.floor(q).astype(np.int64); t = q - i; t = t * t * (3 - 2 * t)
    def h(a, b, c_):
        n = (a * 73856093) ^ (b * 19349663) ^ (c_ * 83492791) ^ (seed * 2654435761)
        n = (n ^ (n >> 13)) * 1274126177
        return ((n ^ (n >> 16)) & 0xFFFF) / 65535.0
    out = 0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (t[..., 0] if dx else 1 - t[..., 0]) * (t[..., 1] if dy else 1 - t[..., 1]) * (t[..., 2] if dz else 1 - t[..., 2])
                out = out + w * h(i[..., 0] + dx, i[..., 1] + dy, i[..., 2] + dz)
    return out


def fbm(p, freq, seed, octs=4):
    s = 0; a = 0.5; tot = 0
    for o in range(octs):
        s = s + a * vnoise(p, freq * 2 ** o, seed + o); tot += a; a *= 0.5
    return s / tot


px = np.zeros((TEX, TEX, 4), np.float32); px[..., 3] = 1
rgb = np.zeros((TEX, TEX, 3))
cover_stat = []
for i, (kind, g, segs, nrm, cen) in enumerate(POLY):
    sel = m & (PI == i)
    if not sel.any():
        continue
    p = P[sel]
    # board coordinates: along the grain / across it / through the board
    across = np.cross(nrm, g); across /= max(np.linalg.norm(across), 1e-9)
    u = p @ g; v = p @ across; w = p @ nrm
    pg = np.stack([u * 0.10, v, w + i * 0.37], 1)             # stretched along the grain (every board has its own pattern)
    grain = fbm(pg, 60.0, 5, 3)                               # fine grain lines
    streak = fbm(pg, 14.0, 9, 3)                              # broad streaks along the board
    blotch = fbm(p + i * 0.11, 9.0, 21, 3)                    # round stains and chips, not stretched
    wood = WOOD[None] * (0.80 + 0.36 * streak[:, None]) * (0.90 + 0.22 * grain[:, None])
    wood = wood * (1 - 0.35 * (grain[:, None] > 0.66)) + WOOD_DARK[None] * 0.35 * (grain[:, None] > 0.66)
    # distance to the worn (outer) edges and to the inner corners of the board
    d_out = np.full(len(p), 1.0); d_in = np.full(len(p), 1.0)
    for a, b, convex in segs:
        ab = b - a; tt = np.clip(((p - a) @ ab) / (ab @ ab), 0, 1)
        d = np.linalg.norm(p - (a + tt[:, None] * ab), axis=1)
        if convex:
            d_out = np.minimum(d_out, d)
        else:
            d_in = np.minimum(d_in, d)
    # where the paint is gone: always a little on the outer edges, in scratches along the grain, in round chips
    edge = np.clip(1 - d_out / 0.030, 0, 1)                   # 3 cm band
    wear = 0.52 * edge ** 1.3 + 0.60 * (streak - 0.42) + 0.75 * (blotch - 0.50) + 0.30 * (grain - 0.5)
    wear += {0: 0.02, 1: -0.04, 2: 0.04}[kind]                # frame and braces are rubbed more than the sunk panels
    thr = 0.30
    gone = np.clip((wear - thr) / 0.16 + 0.5, 0, 1)           # 0 paint, 1 bare wood, soft border
    gone = gone * gone * (3 - 2 * gone)
    paint = GREEN[None] * (0.86 + 0.26 * fbm(p + 3.1, 5.0, 33, 3)[:, None])
    paint = paint * (1 - 0.22 * (grain[:, None] > 0.70))      # the grain is felt through the thin paint
    # thin paint next to the bare places lets the wood shine through
    thin = np.clip((wear - (thr - 0.22)) / 0.22, 0, 1) * 0.38
    paint = paint * (1 - thin[:, None]) + wood * thin[:, None]
    col = paint * (1 - gone[:, None]) + wood * gone[:, None]
    # shade: sunk panels darker, dirt in the inner corners and at the ground
    shade = {0: 1.0, 1: 0.86, 2: 0.96}[kind] * (1 - 0.30 * np.clip(1 - d_in / 0.035, 0, 1) ** 1.5)
    shade = shade * (0.80 + 0.20 * np.clip(p[:, 2] / 0.22, 0, 1))
    rgb[sel] = np.clip(col * shade[:, None], 0, 1)
    cover_stat.append((kind, gone.mean(), sel.sum()))
px[..., :3] = rgb
for kname, kk in (('frame', 0), ('panels', 1), ('braces', 2)):
    s = [(g_, n) for kd, g_, n in cover_stat if kd == kk]
    print('PAINT %-6s bare wood share %.1f%% of its texels' % (kname, 100 * sum(g_ * n for g_, n in s) / max(sum(n for g_, n in s), 1)))
tot = sum(g_ * n for kd, g_, n in cover_stat) / sum(n for kd, g_, n in cover_stat)
print('PAINT whole crate: bare wood %.1f%%, paint %.1f%%; mean colour %s' % (100 * tot, 100 - 100 * tot, rgb[m].mean(0).round(3)))
px = sb.dilate(px, m, 6)
img = sb.save_png(px, OUT + 'T_PersonalChest_D.png', 'T_PersonalChest_D')
sb.tex_material(ob, 'M_PersonalChest', img)
me.attributes.remove(me.attributes['pid'])
ang, lov = sb.lightmap_uv(ob)
print('UV LightmapUV angle %d overlapping texels %d' % (ang, lov))
sb.store_facing(ob)
co = sb.coords(ob)
print('RESULT tris %d min %s max %s size %s' % (sb.tri_count(ob), co.min(0).round(4), co.max(0).round(4), np.ptp(co, 0).round(4)))
bpy.ops.wm.save_as_mainfile(filepath=sb.WORK + 'crate_work.blend')
