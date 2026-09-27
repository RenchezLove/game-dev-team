import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
o = bpy.data.objects['Shell']; me = o.data
me.calc_loop_triangles()
tree = BVHTree.FromPolygons([v.co for v in me.vertices], [t.vertices[:] for t in me.loop_triangles])
img = [i for i in bpy.data.images if i.size[0] > 0][0]
W, H = img.size; px = np.array(img.pixels[:]).reshape(H, W, 4)
uvd = me.uv_layers[0].data
def col_at(orig, d):
    loc, nrm, ti, dist = tree.ray_cast(Vector(orig), Vector(d))
    if loc is None: return None, None
    t = me.loop_triangles[ti]
    from mathutils.geometry import barycentric_transform
    a, b, c = [me.vertices[i].co for i in t.vertices]
    ua, ub, uc = [uvd[l].uv.to_3d() for l in t.loops]
    uv = barycentric_transform(loc, a, b, c, ua, ub, uc)
    x = int(uv.x % 1 * W); y = int(uv.y % 1 * H)
    return loc, px[min(y, H-1), min(x, W-1), :3].mean()
def scan_y(z, x0=2.0):
    out = []
    for y in np.arange(-2.1, 2.1, 0.01):
        loc, l = col_at((x0, y, z), (-1, 0, 0))
        out.append((round(y, 2), None if l is None else round(l, 2), None if loc is None else round(loc.x, 3)))
    return out
def scan_z(y, x0=2.0):
    out = []
    for z in np.arange(0.2, 1.46, 0.01):
        loc, l = col_at((x0, y, z), (-1, 0, 0))
        out.append((round(z, 2), None if l is None else round(l, 2), None if loc is None else round(loc.x, 3)))
    return out
for z in ():
    s = scan_y(z); dark = [(y, l) for y, l, x in s if l is not None and l < 0.45]
    print('SCAN_Y z=%.2f dark:' % z, dark)
for y in ():
    s = scan_z(y)
    print('SCAN_Z y=%.2f:' % y, [(z, l, x) for z, l, x in s])
def trans(seq):
    out = []; prev = None
    for k, l, h in seq:
        c = None if l is None else ('D' if l < 0.3 else 'g' if l < 0.47 else 'P')
        if c != prev: out.append((k, c, h)); prev = c
    return out
def scan_top_y(x):
    r = []
    for y in np.arange(-2.1, 2.1, 0.01):
        loc, l = col_at((x, y, 3), (0, 0, -1)); r.append((round(y,2), l, None if loc is None else round(loc.z,3)))
    return r
def scan_top_x(y):
    r = []
    for x in np.arange(-0.85, 0.86, 0.01):
        loc, l = col_at((x, y, 3), (0, 0, -1)); r.append((round(x,2), l, None if loc is None else round(loc.z,3)))
    return r
#print('TOPY x=0', trans(scan_top_y(0.0)))
#print('TOPY x=0.4', trans(scan_top_y(0.4)))
for y in (1.5, 1.2, -1.7, 0.75, -1.2):
    pass # y=%.2f' % y, trans(scan_top_x(y)))
def rgb_at(orig, d):
    loc, nrm, ti, dist = tree.ray_cast(Vector(orig), Vector(d))
    if loc is None: return None
    t = me.loop_triangles[ti]
    from mathutils.geometry import barycentric_transform
    a, b, c = [me.vertices[i].co for i in t.vertices]
    ua, ub, uc = [uvd[l].uv.to_3d() for l in t.loops]
    uv = barycentric_transform(loc, a, b, c, ua, ub, uc)
    x = int(uv.x % 1 * W); y = int(uv.y % 1 * H)
    return px[min(y, H-1), min(x, W-1), :3]
print('BACK hue grid: B=blue paint N=neutral light n=neutral mid R=red O=orange D=dark')
for z in np.arange(0.95, 0.35, -0.025):
    row = ''
    for x in np.arange(-0.8, 0.81, 0.025):
        c = rgb_at((x, -3, z), (0, 1, 0))
        if c is None: row += ' '; continue
        r, g, b = c; l = c.mean()
        if l < 0.25: ch = 'D'
        elif r > g + 0.12 and r > b + 0.15: ch = 'R' if g < r * 0.6 else 'O'
        elif b - r > 0.05: ch = 'B'
        else: ch = 'N' if l > 0.6 else 'n'
        row += ch
    print('Z %.3f %s' % (z, row))
