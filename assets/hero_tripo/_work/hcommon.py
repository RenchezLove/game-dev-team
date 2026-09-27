"""Helpers for the Tripo hero -> RootAnim fit (landmarks measured by ray casts)."""
import bpy, bmesh, math
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

GLB = 'E:/ContrarySurvior/ContrarySurvivor/Saved/Tripo/hero.glb'
WEAR = 'E:/game-dev-team/assets/armor_wearables/_work/wearables_work.blend'


def bvh_of(objs):
    """World-space BVH over evaluated meshes of objs (welded copy)."""
    bm = bmesh.new()
    dg = bpy.context.evaluated_depsgraph_get()
    for ob in objs:
        me = ob.evaluated_get(dg).to_mesh()
        t = bmesh.new(); t.from_mesh(me); t.transform(ob.matrix_world)
        tmp = bpy.data.meshes.new('_t'); t.to_mesh(tmp); t.free()
        bm.from_mesh(tmp); bpy.data.meshes.remove(tmp)
        ob.evaluated_get(dg).to_mesh_clear()
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
    cos = [v.co.copy() for v in bm.verts]
    tree = BVHTree.FromBMesh(bm)
    bm.free()
    return tree, cos


def ray(tree, o, d):
    hit = tree.ray_cast(Vector(o), Vector(d).normalized(), 10.0)
    return hit[0]


def landmarks(objs, tag):
    tree, cos = bvh_of(objs)
    H = max(c.z for c in cos)
    zc = [c for c in cos if 0.55 * H < c.z < 0.70 * H]
    yc = sum(c.y for c in zc) / len(zc)
    L = {'H': H, 'yc': yc}
    L['crotch'] = ray(tree, (0, yc, 0.02), (0, 0, 1)).z
    L['side'] = ray(tree, (2, yc, 0.64 * H), (-1, 0, 0)).x
    L['armpit'] = ray(tree, (L['side'] + 0.03, yc, 0.64 * H), (0, 0, 1)).z
    p = ray(tree, (L['side'] - 0.02, yc, H + 1), (0, 0, -1))
    L['shtop'] = p.z
    tip = max(c.x for c in cos)
    L['tip'] = tip
    # arm slabs: centre z and thickness per 1 cm along +X
    slabs = []
    x = L['side'] + 0.02
    while x < tip - 0.005:
        up = ray(tree, (x, yc, L['armpit'] - 0.25), (0, 0, 1))
        dn = ray(tree, (x, yc, H + 1), (0, 0, -1))
        # arm may be off yc: sample a few y and take widest valid pair
        best = None
        for dy in (-0.04, -0.02, 0, 0.02, 0.04):
            up = ray(tree, (x, yc + dy, L['armpit'] - 0.25), (0, 0, 1))
            dn = ray(tree, (x, yc + dy, H + 1), (0, 0, -1))
            if up and dn and dn.z > up.z:
                t = dn.z - up.z
                if best is None or t > best[0]:
                    best = (t, (up.z + dn.z) / 2, yc + dy)
        if best:
            slabs.append((x, best[0], best[1], best[2]))
        x += 0.01
    L['slabs'] = slabs
    cand = [s for s in slabs if tip - 0.24 < s[0] < tip - 0.05]
    w = min(cand, key=lambda s: s[1])
    L['wrist'] = w[0]
    # leg centre x at shin (0.25H) and knee (0.5*crotch)
    for key, zz in (('shin', 0.12 * H), ('knee', 0.5 * L['crotch'])):
        a = ray(tree, (2, yc, zz), (-1, 0, 0)); b = ray(tree, (0.001, yc, zz), (1, 0, 0))
        L[key + '_cx'] = (a.x + b.x) / 2 if a and b else None
    print('LM %-6s H=%.3f yc=%.3f crotch=%.3f side=%.3f armpit=%.3f shtop=%.3f tip=%.3f wrist=%.3f shin_cx=%s knee_cx=%s' % (
        tag, H, yc, L['crotch'], L['side'], L['armpit'], L['shtop'], tip, L['wrist'],
        L['shin_cx'], L['knee_cx']))
    for s in slabs[::5]:
        print('   slab %s x=%.3f thick=%.3f zc=%.3f y=%.3f' % (tag, *s))
    return L


def pwl(x, pairs):
    """Piecewise-linear map through sorted (src,dst) pairs, linear extrapolation."""
    pairs = sorted(pairs)
    if x <= pairs[0][0]:
        (a, b), (c, d) = pairs[0], pairs[1]
    elif x >= pairs[-1][0]:
        (a, b), (c, d) = pairs[-2], pairs[-1]
    else:
        for (a, b), (c, d) in zip(pairs, pairs[1:]):
            if a <= x <= c:
                break
    return b + (x - a) * (d - b) / (c - a)
