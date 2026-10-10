"""SM_WalkieTalkie: the hand radio the guard dropped while running from the wolves.  Built by hand from closed bodies (case, antenna base,
antenna, two knobs, talk button on the side); speaker grille, plate, screws and the wear are painted by rules into the colour texture.
The radio lies on its back: the face with the grille looks up (+Z), the antenna points to +Y, origin under the middle of the footprint.
Build frame = the lying radio: x across the case, y along the case (0 = bottom end), z through the case (0 = the back on the ground).
Run: blender.exe -b --factory-startup --python walkie_10_build.py
"""
import bpy, bmesh, sys, math, os
import numpy as np
from mathutils import Vector
sys.path.insert(0, 'E:/game-dev-team/assets/scientist_base/_work')
import sb
OUT = sb.ROOT + 'SM_WalkieTalkie/'; os.makedirs(OUT, exist_ok=True)
TEX = 256
TEX_ICON = 1024                                                  # the same paint at a higher resolution, only for the bag icon render
W, H, D = 0.066, 0.200, 0.036                                    # case: across, along, through
ANT_X, ANT_R, ANT_L = -0.019, 0.0062, 0.150                      # antenna: place across the case, half width, length above its base
BASE_R, BASE_L = 0.0095, 0.022
KNOB = ((0.004, 0.0085, 0.016, 2), (0.022, 0.0070, 0.011, 3))    # x, radius, height, part number
PTT = (0.105, 0.160, 0.008, 0.028, 0.004)                        # talk button on the -X side: y from, y to, z from, z to, how far it sticks out
sb.empty()
bm = bmesh.new(); part = bm.faces.layers.int.new('part')
def box(lo, hi, p):
    vs = [bm.verts.new((x, y, z)) for z in (lo[2], hi[2]) for y in (lo[1], hi[1]) for x in (lo[0], hi[0])]
    for q in ((0, 1, 3, 2), (4, 5, 7, 6), (0, 1, 5, 4), (2, 3, 7, 6), (0, 2, 6, 4), (1, 3, 7, 5)):
        bm.faces.new([vs[i] for i in q])[part] = p
def prism(x, z, r0, r1, y0, y1, n, p, a0=0.0):
    """Closed n-sided prism along Y (r0 at y0, r1 at y1)."""
    ring = [[bm.verts.new((x + r * math.cos(a0 + 2 * math.pi * i / n), y, z + r * math.sin(a0 + 2 * math.pi * i / n))) for i in range(n)] for r, y in ((r0, y0), (r1, y1))]
    for i in range(n):
        bm.faces.new((ring[0][i], ring[0][(i + 1) % n], ring[1][(i + 1) % n], ring[1][i]))[part] = p
    bm.faces.new(ring[0])[part] = p; bm.faces.new(ring[1])[part] = p
SINK = 0.004                                                     # every added body starts inside the case - no gap, no shared faces
box((-W / 2, 0, 0), (W / 2, H, D), 0)
prism(ANT_X, D / 2, BASE_R, BASE_R * 0.9, H - SINK, H + BASE_L, 6, 5, math.pi / 6)
prism(ANT_X, D / 2, ANT_R, ANT_R * 0.72, H + BASE_L - SINK, H + BASE_L + ANT_L, 5, 1, math.pi / 2)
for kx, kr, kh, kp in KNOB:
    prism(kx, D / 2, kr, kr * 0.92, H - SINK, H + kh, 6, kp, math.pi / 6)
box((-W / 2 - PTT[4], PTT[0], PTT[2]), (-W / 2 + SINK, PTT[1], PTT[3]), 4)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bmesh.ops.triangulate(bm, faces=bm.faces)
# every body has to be closed (each edge has exactly two faces) and to have a positive volume - the lesson of the shotgun
bm.normal_update()
for i, comp in enumerate(sb.islands(bm)):
    es = {e for f in comp for e in f.edges}
    openE = sum(1 for e in es if len(e.link_faces) != 2)
    vol = sum(f.verts[0].co.dot(f.verts[1].co.cross(f.verts[2].co)) for f in comp) / 6
    print('BODY %d part %d: %d triangles, edges with other than two faces %d, volume %.2f cm3 %s' % (i, comp[0][part], len(comp), openE, vol * 1e6, 'OK' if openE == 0 and vol > 0 else 'BAD'))
    assert openE == 0 and vol > 0
me = bpy.data.meshes.new('SM_WalkieTalkie'); bm.to_mesh(me); bm.free()
ob = bpy.data.objects.new('SM_WalkieTalkie', me); bpy.context.scene.collection.objects.link(ob)
sb.flat(ob)
print('BUILD tris %d' % sb.tri_count(ob))
sb.uv_clean(ob, 'UVMap', 0.02, res=1024)

# ---- paint by rules: world point of every texel -> colour
def vnoise(P, scale, seed):
    """Value noise 0..1 of points P (..., 3)."""
    q = P * scale; i = np.floor(q).astype(np.int64); f = q - i; f = f * f * (3 - 2 * f)
    def h(ix, iy, iz):
        n = (ix * 73856093) ^ (iy * 19349663) ^ (iz * 83492791) ^ (seed * 2654435761)
        n = (n ^ (n >> 13)) * 1274126177
        return ((n ^ (n >> 16)) & 0xFFFF) / 65535.0
    out = 0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (f[..., 0] if dx else 1 - f[..., 0]) * (f[..., 1] if dy else 1 - f[..., 1]) * (f[..., 2] if dz else 1 - f[..., 2])
                out = out + w * h(i[..., 0] + dx, i[..., 1] + dy, i[..., 2] + dz)
    return out
GREEN = np.array([0.30, 0.35, 0.21]); GREEN_D = np.array([0.20, 0.24, 0.15]); BLACK = np.array([0.075, 0.075, 0.08]); RUBBER = np.array([0.12, 0.12, 0.125])
STEEL = np.array([0.62, 0.61, 0.57]); PLATE = np.array([0.70, 0.67, 0.55]); RED = np.array([0.80, 0.13, 0.08]); RUST = np.array([0.40, 0.22, 0.10]); DIRT = np.array([0.24, 0.20, 0.14])
def paint(res):
    T = len(me.polygons)
    co = sb.coords(ob); pv = np.zeros(T * 3, np.int32); me.loops.foreach_get('vertex_index', pv); pv = pv.reshape(-1, 3)
    nr = np.zeros(T * 3); me.polygons.foreach_get('normal', nr); nr = nr.reshape(-1, 3)
    pt = np.zeros(T, np.int32); me.attributes['part'].data.foreach_get('value', pt)
    fid, bw = sb.raster(me, 'UVMap', res); m = fid >= 0; f = np.clip(fid, 0, None)
    P = (co[pv[f]] * bw[..., None]).sum(2); N = nr[f]; K = pt[f]
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    rgb = np.zeros((res, res, 3))
    body = m & (K == 0)
    rgb[body] = GREEN
    front = body & (N[..., 2] > 0.5); back = body & (N[..., 2] < -0.5); side = body & (abs(N[..., 0]) > 0.5); top = body & (N[..., 1] > 0.5); bot = body & (N[..., 1] < -0.5)
    # face: black upper panel with a red lamp, a tin plate with two lines of stamped text, the speaker grille, microphone holes, four screws
    rgb[front & (y > 0.168)] = BLACK
    rgb[front & (abs(y - 0.168) < 0.0012)] = GREEN_D * 0.7
    rgb[front & (np.hypot(x - 0.020, y - 0.184) < 0.0042)] = RED
    rgb[front & (np.hypot(x - 0.0205, y - 0.1848) < 0.0015)] = np.array([1.0, 0.62, 0.50])
    rgb[front & (abs(x + 0.008) < 0.014) & (abs(y - 0.184) < 0.0055)] = np.array([0.13, 0.15, 0.13])          # dial window
    rgb[front & (abs(x + 0.008) < 0.012) & (abs(y - 0.184) < 0.0010)] = np.array([0.72, 0.70, 0.52])
    pl = front & (abs(x) < 0.022) & (abs(y - 0.146) < 0.011)
    rgb[pl] = PLATE
    rgb[pl & ((abs(y - 0.150) < 0.0017) | (abs(y - 0.142) < 0.0014)) & (abs(x) < 0.017) & (np.sin(x * 2600) > -0.55)] = BLACK * 1.6
    rgb[front & (abs(abs(x) - 0.0225) < 0.0009) & (abs(y - 0.146) < 0.0115)] = GREEN_D * 0.6
    gr = front & (abs(x) < 0.025) & (y > 0.040) & (y < 0.122)
    rgb[gr] = GREEN_D
    rgb[gr & (np.mod(y - 0.040, 0.0091) < 0.0052) & (abs(x) < 0.0225)] = BLACK * 0.55                        # nine slots
    rgb[front & ((abs(abs(x) - 0.0255) < 0.0009) & (y > 0.039) & (y < 0.123) | (abs(x) < 0.026) & ((abs(y - 0.039) < 0.0009) | (abs(y - 0.123) < 0.0009)))] = GREEN_D * 0.55
    for mx_ in (-0.008, 0.0, 0.008):
        rgb[front & (np.hypot(x - mx_, y - 0.022) < 0.0021)] = BLACK * 0.5
    for sx in (-1, 1):
        for sy in (0.010, 0.160):
            r = np.hypot(x - sx * 0.026, y - sy)
            rgb[front & (r < 0.0036)] = STEEL * 0.75; rgb[front & (r < 0.0036) & (abs(x - sx * 0.026 - (y - sy)) < 0.0009)] = BLACK
    # back: battery cover (a seam and a latch), a black belt clip painted flat
    rgb[back & (abs(y - 0.095) < 0.0012)] = GREEN_D * 0.55
    rgb[back & (abs(x) < 0.009) & (y > 0.078) & (y < 0.093)] = GREEN_D
    rgb[back & (abs(x) < 0.012) & (y > 0.110) & (y < 0.185)] = BLACK
    rgb[back & (abs(x) < 0.008) & (y > 0.176) & (y < 0.182)] = STEEL * 0.6
    # sides: ribs of the grip in the lower half, a seam along the middle
    rgb[side & (y < 0.090) & (y > 0.015) & (np.mod(y, 0.0075) < 0.0032)] = GREEN_D
    rgb[side & (abs(z - D / 2) < 0.0010)] = GREEN_D * 0.6
    rgb[top] = BLACK * 1.2
    rgb[bot & (abs(x) < 0.020) & (abs(z - D / 2) < 0.009)] = GREEN_D                                       # charging contacts
    for cx_ in (-0.010, 0.010):
        rgb[bot & (np.hypot(x - cx_, z - D / 2) < 0.0040)] = PLATE
    # wear of the case: bare metal along the edges, scratches, rust spots, dirt towards the bottom end
    ex = W / 2 - abs(x); ey = np.minimum(y, H - y); ez = np.minimum(z, D - z)
    d3 = np.sort(np.stack([ex, ey, ez], -1), -1)
    edge = d3[..., 1]                                                # distance to the nearest edge of the case
    n1 = vnoise(P, 260.0, 1); n2 = vnoise(P, 90.0, 2); n3 = vnoise(P, 45.0, 3)
    wear = body & (edge < 0.0015 + 0.0050 * n2 * n2) & (n1 > 0.22)
    rgb[wear] = STEEL * (0.80 + 0.25 * n1[wear])[:, None]
    corner = body & (d3[..., 2] < 0.004 + 0.008 * n2)
    rgb[corner] = STEEL * (0.80 + 0.2 * n1[corner])[:, None]
    scr = body & ~wear & (vnoise(P * np.array([1.0, 0.12, 1.0]), 900.0, 4) > 0.93) & (n3 > 0.50)
    rgb[scr] = rgb[scr] * 0.45 + STEEL * 0.55
    rs = np.clip((n3 - 0.66) / 0.14, 0, 1) * np.clip((vnoise(P, 400.0, 5) - 0.25) * 2, 0, 1)
    sel = body & (rs > 0)
    rgb[sel] = rgb[sel] * (1 - 0.75 * rs[sel])[:, None] + RUST * (0.75 * rs[sel])[:, None]
    dk = np.clip(1 - y / 0.060, 0, 1) * (0.25 + 0.55 * n2)
    rgb[body] = rgb[body] * (1 - dk[body])[:, None] + DIRT * dk[body][:, None]
    rgb[body] *= (0.88 + 0.24 * vnoise(P, 140.0, 6)[body])[:, None]
    # antenna base (steel nut with a dark thread), rubber antenna with a worn tip, knobs (ribbed side, light pointer on the end), talk button
    sel = m & (K == 5); rgb[sel] = STEEL * 0.62; rgb[sel & (np.mod(y - H, 0.0055) < 0.0018)] = STEEL * 0.34
    sel = m & (K == 1); rgb[sel] = RUBBER
    rgb[sel & (np.mod(y, 0.012) < 0.0022)] = RUBBER * 0.55
    rgb[sel & (y > H + BASE_L + ANT_L - 0.012)] = RUBBER * 1.9
    rgb[sel & (n2 > 0.80)] = RUBBER * 2.3
    for kx, kr, kh, kp in KNOB:
        sel = m & (K == kp); rgb[sel] = BLACK * 1.35
        ang = np.arctan2(z - D / 2, x - kx)
        rgb[sel & (abs(N[..., 1]) < 0.5) & (np.sin(ang * 12) > 0.15)] = BLACK * 0.6
        end = sel & (N[..., 1] > 0.5)
        rgb[end] = BLACK * 1.9; rgb[end & (abs(x - kx) < kr * 0.16) & (z > D / 2)] = np.array([0.85, 0.83, 0.75])
        rgb[sel & (abs(N[..., 1]) < 0.5) & (y > H + kh - 0.0022)] = STEEL * 0.55
    sel = m & (K == 4); rgb[sel] = RUBBER * 1.25
    rgb[sel & (N[..., 0] < -0.5) & (np.mod(y - PTT[0], 0.0072) < 0.0026)] = RUBBER * 0.6
    rgb[sel & (N[..., 0] < -0.5) & ((y - PTT[0] < 0.002) | (PTT[1] - y < 0.002))] = np.array([0.55, 0.30, 0.08])
    px = np.zeros((res, res, 4), np.float32); px[..., :3] = np.clip(rgb, 0, 1); px[..., 3] = 1
    return sb.dilate(px, m, 6 if res <= 256 else 16), m
px, m = paint(TEX)
print('PAINT %d: painted texels %d of %d (%.1f %%), mean colour %s' % (TEX, int(m.sum()), TEX * TEX, 100.0 * m.mean(), px[..., :3][m].mean(0).round(3)))
img = sb.save_png(px, OUT + 'T_WalkieTalkie_D.png', 'T_WalkieTalkie_D')
pxi, mi_ = paint(TEX_ICON)
sb.save_png(pxi, sb.WORK + '_walkie_icon_D.png', '_walkie_icon_D')
sb.tex_material(ob, 'M_WalkieTalkie', img)
sb.fix_facing(ob, tag='WALKIE')
sb.place(ob)
me.attributes.remove(me.attributes['part'])
sb.store_facing(ob)
c = sb.coords(ob)
print('RESULT tris %d min %s max %s size %s (m)' % (sb.tri_count(ob), c.min(0).round(4), c.max(0).round(4), np.ptp(c, 0).round(4)))
bpy.ops.wm.save_as_mainfile(filepath=sb.WORK + 'walkie_work.blend')
