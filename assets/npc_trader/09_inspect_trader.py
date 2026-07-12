"""Ground the trader build constants against the REAL base bodies in master.blend
(rule C). Extra vs elder's 09: dump the 4 chest pocket-box islands of L1_Torso —
the trader (utility vest, kit "A") can KEEP them repainted as vest pouches
instead of dropping them; arm |x| profile for the wrist split (sweater sleeves
down to the wrists, only hands bare); thigh bands for cargo side pockets.
Run: blender.exe -b --factory-startup --python 09_inspect_trader.py
"""
import bpy, sys
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W
from mathutils import Vector

bpy.ops.wm.open_mainfile(filepath='E:/game-dev-team/assets/armor_wearables/_work/master.blend')
BH = bpy.data.objects['BaseHead']
L1T = bpy.data.objects['L1_Torso']
L1L = bpy.data.objects['L1_Legs']


def bounds(ob):
    me = ob.data
    xs = [v.co.x for v in me.vertices]; ys = [v.co.y for v in me.vertices]; zs = [v.co.z for v in me.vertices]
    print('%-9s verts=%d tris=%d x=[%.3f..%.3f] y=[%.3f..%.3f] z=[%.3f..%.3f]' % (
        ob.name, len(me.vertices), W.tri_count(ob),
        min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)))


for ob in (BH, L1T, L1L):
    bounds(ob)

# --- BaseHead: crown + halfwidths for the bandana dome, back of skull for knot ---
me = BH.data
zs = [v.co.z for v in me.vertices]
print('\nBaseHead crown zmax=%.3f' % max(zs))
for z in (1.60, 1.66, 1.70, 1.74, 1.78):
    band = [v.co for v in me.vertices if abs(v.co.z - z) < 0.02]
    if band:
        print('  z=%.2f |x|max=%.3f y=[%.3f..%.3f]' % (
            z, max(abs(v.x) for v in band), min(v.y for v in band), max(v.y for v in band)))

# --- L1_Torso: pocket-box islands (same detector as elder drop_front_boxes) ---
import bmesh


def islands(m):
    bm = bmesh.new(); bm.from_mesh(m)
    bm.faces.ensure_lookup_table()
    seen = set(); out = []
    for f in bm.faces:
        if f.index in seen:
            continue
        stack = [f]; comp = []
        while stack:
            g = stack.pop()
            if g.index in seen:
                continue
            seen.add(g.index); comp.append(g.index)
            for e in g.edges:
                for h in e.link_faces:
                    if h.index not in seen:
                        stack.append(h)
        out.append(comp)
    bm.free()
    return out


mt = L1T.data
print('\nL1_Torso islands (nfaces, bbox):')
for comp in islands(mt):
    vs = set()
    for fi in comp:
        vs.update(mt.polygons[fi].vertices)
    cos = [mt.vertices[i].co for i in vs]
    mn = Vector((min(c.x for c in cos), min(c.y for c in cos), min(c.z for c in cos)))
    mx = Vector((max(c.x for c in cos), max(c.y for c in cos), max(c.z for c in cos)))
    tag = 'BOX' if (3 <= len(comp) <= 80 and (mx - mn).length < 0.30 and mx.y < -0.02 and
                    0.95 < mn.z and mx.z < 1.45 and mn.x > -0.30 and mx.x < 0.30) else 'main'
    print('  %-4s n=%3d x=[%.3f..%.3f] y=[%.3f..%.3f] z=[%.3f..%.3f]' % (
        tag, len(comp), mn.x, mx.x, mn.y, mx.y, mn.z, mx.z))

# arm |x| profile -> wrist split (hand verts): mean z + count per |x| bin
print('\nL1_Torso arm |x| bins (n verts, z-range, y-range):')
for x0 in (0.50, 0.60, 0.70, 0.80, 0.85, 0.90, 0.95):
    vs = [v.co for v in mt.vertices if x0 < abs(v.co.x) < x0 + 0.05]
    if vs:
        print('  |x|=%.2f-%.2f n=%3d z=[%.3f..%.3f] y=[%.3f..%.3f]' % (
            x0, x0 + 0.05, len(vs), min(v.z for v in vs), max(v.z for v in vs),
            min(v.y for v in vs), max(v.y for v in vs)))

# trunk band + collar zone (repaint checks)
print('\nL1_Torso trunk band_of(z): (halfwidth_x, front_depth, back_depth)')
for z in (0.92, 1.00, 1.10, 1.20, 1.30, 1.40, 1.46, 1.50):
    vs = [v.co for v in mt.vertices if abs(v.co.z - z) < 0.045 and abs(v.co.x) < 0.30]
    if vs:
        a = max(abs(v.x) for v in vs); fb = max(-v.y for v in vs); bb = max(v.y for v in vs)
        print('  z=%.2f a=%.3f fb=%.3f bb=%.3f' % (z, a, fb, bb))

# --- L1_Legs: shoe hex + thigh bands for cargo pockets ---
def face_hex(m, p):
    return W.read_zone_hex(m, p.loop_indices[0])


ml = L1L.data
zl = {}
for p in ml.polygons:
    h = face_hex(ml, p)
    zl.setdefault(h, []).append(Vector(p.center))
print('\nL1_Legs zones (hex -> nfaces, |x|-range, z-range):')
for h, cs in sorted(zl.items(), key=lambda kv: -len(kv[1])):
    xs = [abs(c.x) for c in cs]; zsr = [c.z for c in cs]
    print('  %s n=%3d |x|=[%.3f..%.3f] z=[%.3f..%.3f]' % (
        h, len(cs), min(xs), max(xs), min(zsr), max(zsr)))
print('\nL1_Legs thigh bands (outer-x per leg, front/back y):')
for z in (0.45, 0.55, 0.62, 0.70, 0.78):
    for sgn, lab in ((1, 'R(+x)'), (-1, 'L(-x)')):
        vs = [v.co for v in ml.vertices if abs(v.co.z - z) < 0.04 and v.co.x * sgn > 0.02]
        if vs:
            print('  z=%.2f %s xin=%.3f xout=%.3f y=[%.3f..%.3f]' % (
                z, lab, min(v.x * sgn for v in vs), max(v.x * sgn for v in vs),
                min(v.y for v in vs), max(v.y for v in vs)))
print('\nINSPECT DONE')
