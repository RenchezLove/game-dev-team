"""Ground the elder build constants against the REAL base bodies in master.blend
(rule C: read real geometry, don't hardcode zones from memory).
Dumps: BaseHead bounds + front(-Y)/bottom(-Z) extremes (beard/beanie fit),
L1_Torso arm x-profile + trunk band_of(z) (vest fit + rolled-sleeve elbow split),
L1_Legs shoe/belt zones (boots + belt band).
Run: blender.exe -b _work/master.blend --factory-startup --python 09_inspect_elder.py
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

# --- BaseHead: front (most -Y) and bottom (most -Z) extremes for beard/beanie ---
me = BH.data
front = sorted(me.vertices, key=lambda v: v.co.y)[:6]
bottom = sorted(me.vertices, key=lambda v: v.co.z)[:6]
print('\nBaseHead front(-Y):', [(round(v.co.x, 3), round(v.co.y, 3), round(v.co.z, 3)) for v in front])
print('BaseHead bottom(-Z):', [(round(v.co.x, 3), round(v.co.y, 3), round(v.co.z, 3)) for v in bottom])
# head halfwidth near ear height
ear = [v.co for v in me.vertices if 1.63 < v.co.z < 1.70]
print('BaseHead halfwidth@ear z1.63-1.70: maxAbsX=%.3f' % (max(abs(v.x) for v in ear) if ear else -1))

# --- L1_Torso: color-zone hexes + arm x-profile (elbow split) ---
def face_hex(m, p):
    return W.read_zone_hex(m, p.loop_indices[0])


mt = L1T.data
# unique hexes present
zones = {}
for p in mt.polygons:
    h = face_hex(mt, p)
    zones.setdefault(h, []).append(Vector(p.center))
print('\nL1_Torso zones (hex -> nfaces, x-range, z-range):')
for h, cs in sorted(zones.items(), key=lambda kv: -len(kv[1])):
    xs = [abs(c.x) for c in cs]; zs = [c.z for c in cs]
    print('  %s n=%3d |x|=[%.3f..%.3f] z=[%.3f..%.3f]' % (
        h, len(cs), min(xs), max(xs), min(zs), max(zs)))
# arm profile: for x bins, mean z (arm is roughly horizontal)
print('L1_Torso trunk band_of(z): (halfwidth_x, front_depth, back_depth)')
for z in (0.92, 1.00, 1.10, 1.20, 1.30, 1.40, 1.46, 1.50):
    vs = [v.co for v in mt.vertices if abs(v.co.z - z) < 0.045 and abs(v.co.x) < 0.30]
    if vs:
        a = max(abs(v.x) for v in vs); fb = max(-v.y for v in vs); bb = max(v.y for v in vs)
        print('  z=%.2f a=%.3f fb=%.3f bb=%.3f' % (z, a, fb, bb))
    else:
        print('  z=%.2f (no trunk verts)' % z)

# --- L1_Legs: shoe/belt/knee zones ---
ml = L1L.data
zl = {}
for p in ml.polygons:
    h = face_hex(ml, p)
    zl.setdefault(h, []).append(Vector(p.center))
print('\nL1_Legs zones (hex -> nfaces, |x|-range, z-range):')
for h, cs in sorted(zl.items(), key=lambda kv: -len(kv[1])):
    xs = [abs(c.x) for c in cs]; zs = [c.z for c in cs]
    print('  %s n=%3d |x|=[%.3f..%.3f] z=[%.3f..%.3f]' % (
        h, len(cs), min(xs), max(xs), min(zs), max(zs)))
print('\nINSPECT DONE')
