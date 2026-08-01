"""Build SM_HidePickup - small rolled-up animal hide tied with twine.
Wolf loot pickup (a backpack on a wolf corpse looks silly - decision from
game-lead). Grey-brown fur outside, pale hide underside at the cut edge and
the roll ends, straw-coloured twine bands + knot + two hanging tails.
Budget 100-300 tris (ground pickup, top-down camera 30 m away).

Vertex colors = approved 16-color palette (GDD), raw sRGB in 'Col'
(CORNER/BYTE_COLOR), FBX export colors_type='LINEAR' (project convention).
Conventions: meters, origin = base center Z=0, forward +Y, flat shade,
one material, Smart UV 0-1, FBX MESH-only FACE smoothing.

Headless:
  E:/Programs/Blender/blender.exe -b --factory-startup --python 10_build_hide_pickup.py
Self-verifies via FBX round-trip into a fresh factory scene.
"""
import bpy, bmesh, math, addon_utils
from mathutils import Vector, Matrix

OUT = 'E:/game-dev-team/assets/hide_pickup/'

HEX = dict(
    DryEarth='#7D6A4E',   # grey-brown fur (main)
    StoneGrey='#6E6A60',  # grey fur mottling
    Straw='#CAA54E',      # twine bands / knot / tails
    PaleHide='#E7E4D8',   # hide underside: roll ends + outer wrap edge
    Magenta='#FF00FF')

P_FUR, P_TIE, P_CAP, P_EDGE = range(4)


def hexv(hx):
    hx = hx.lstrip('#')
    return (int(hx[0:2], 16) / 255.0, int(hx[2:4], 16) / 255.0,
            int(hx[4:6], 16) / 255.0, 1.0)


def box(bm, mn, mx, part):
    x0, y0, z0 = mn
    x1, y1, z1 = mx
    vs = [bm.verts.new(v) for v in (
        (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
        (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1))]
    for idx in ((0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4),
                (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        f = bm.faces.new([vs[i] for i in idx])
        f.material_index = part


def lathe_spans(bm, profile, n, span_parts, ang0=0.0, jit=None):
    """Like loot-bag lathe(), but each span between profile rows gets its own
    part id from span_parts (len == len(profile)-1). Needed because the twine
    bands / end caps are painted by part id, not by position (positions shift
    when finalize() recenters the origin)."""
    entries = []
    for r, z in profile:
        if r == 0.0:
            entries.append(('pole', bm.verts.new((0.0, 0.0, z))))
        else:
            ring = []
            for k in range(n):
                a = ang0 + 2.0 * math.pi * k / n
                rk = r * (jit[k] if jit else 1.0)
                ring.append(bm.verts.new((rk * math.cos(a),
                                          rk * math.sin(a), z)))
            entries.append(('ring', ring))
    for i in range(len(entries) - 1):
        ka, va = entries[i]
        kb, vb = entries[i + 1]
        part = span_parts[i]
        if ka == 'pole' and kb == 'ring':
            for k in range(n):
                f = bm.faces.new((va, vb[k], vb[(k + 1) % n]))
                f.material_index = part
        elif ka == 'ring' and kb == 'ring':
            for k in range(n):
                f = bm.faces.new((va[k], va[(k + 1) % n],
                                  vb[(k + 1) % n], vb[k]))
                f.material_index = part
        elif ka == 'ring' and kb == 'pole':
            for k in range(n):
                f = bm.faces.new((va[(k + 1) % n], va[k], vb))
                f.material_index = part


def slab(bm, path, x0, x1, th, sign, part):
    """Bent solid slab, same as loot-bag builder. path = [(y,z),...]."""
    m = len(path)
    P, Q = [], []
    for i in range(m):
        a = path[max(i - 1, 0)]
        b = path[min(i + 1, m - 1)]
        t = Vector((b[0] - a[0], b[1] - a[1]))
        t.normalize()
        nrm = Vector((t.y, -t.x)) * th * sign
        P.append(Vector((path[i][0], path[i][1])))
        Q.append(P[i] + nrm)
    A = [bm.verts.new((x0, p.x, p.y)) for p in P]
    B = [bm.verts.new((x1, p.x, p.y)) for p in P]
    C = [bm.verts.new((x1, q.x, q.y)) for q in Q]
    D = [bm.verts.new((x0, q.x, q.y)) for q in Q]
    faces = []
    for i in range(m - 1):
        faces.append((A[i], B[i], B[i + 1], A[i + 1]))
        faces.append((D[i + 1], C[i + 1], C[i], D[i]))
        faces.append((A[i + 1], D[i + 1], D[i], A[i]))
        faces.append((B[i], C[i], C[i + 1], B[i + 1]))
    faces.append((A[0], B[0], C[0], D[0]))
    faces.append((D[m - 1], C[m - 1], B[m - 1], A[m - 1]))
    for idx in faces:
        f = bm.faces.new(idx)
        f.material_index = part


def build_roll():
    """Roll lies with its axis along X. Built vertically (lathe axis Z),
    then rotated (x,y,z)->(z,y,-x) so profile z becomes world X.
    ang0=22.5 deg puts two verts at equal lowest height -> flat resting face.
    jit[0]==jit[7] keeps that face flat despite the irregular outline."""
    bm = bmesh.new()
    profile = [(0.0, -0.225), (0.058, -0.210), (0.088, -0.165),
               (0.096, -0.132), (0.096, -0.100), (0.090, -0.040),
               (0.092, 0.040), (0.095, 0.100), (0.095, 0.132),
               (0.086, 0.170), (0.056, 0.210), (0.0, 0.225)]
    spans = (P_CAP, P_FUR, P_FUR, P_TIE, P_FUR, P_FUR,
             P_FUR, P_TIE, P_FUR, P_FUR, P_CAP)
    jit = (1.00, 0.95, 1.05, 0.97, 1.03, 0.94, 1.06, 1.00)
    lathe_spans(bm, profile, 8, spans, math.radians(22.5), jit=jit)
    # lay the roll down + settle-squash (wider than tall). Only lathe verts
    # exist at this point, so the loop touches nothing else.
    for v in bm.verts:
        x, y, z = v.co
        v.co = Vector((z, y * 1.04, -x * 0.93))
    # NO wrap-edge lip: tried twice (9 cm and 3.5 cm arc) - a pale strip on
    # top always reads as a white label, not a hide edge. The pale roll ends
    # plus twine bands carry the "rolled bundle" read on their own.
    # twine knot on top of band 1 + two short elbowed tails down the front
    # (+Y), bending back toward the surface so they do not float as planks
    box(bm, (-0.130, -0.021, 0.086), (-0.102, 0.021, 0.112), P_TIE)
    slab(bm, [(0.090, 0.045), (0.104, 0.010), (0.100, -0.038)],
         -0.126, -0.108, 0.010, -1, P_TIE)
    slab(bm, [(0.088, 0.043), (0.112, 0.000), (0.115, -0.052)],
         -0.104, -0.088, 0.010, -1, P_TIE)
    return bm


def paint_roll(me):
    """Fur = DryEarth with deterministic StoneGrey mottling (index-based, no
    randomness - birch lesson: build must be deterministic)."""
    for ca in list(me.color_attributes):
        me.color_attributes.remove(ca)
    ca = me.color_attributes.new('Col', 'BYTE_COLOR', 'CORNER')
    mag = hexv(HEX['Magenta'])
    for d in ca.data:
        d.color_srgb = mag
    for p in me.polygons:
        pid = p.material_index
        if pid == P_TIE:
            c = HEX['Straw']
        elif pid in (P_CAP, P_EDGE):
            c = HEX['PaleHide']
        else:
            c = HEX['StoneGrey'] if (p.index * 5) % 7 < 2 else HEX['DryEarth']
        cv = hexv(c)
        for li in p.loop_indices:
            ca.data[li].color_srgb = cv
    me.update()


def make_mat(name):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    b.inputs['Metallic'].default_value = 0.0
    b.inputs['Roughness'].default_value = 0.8
    vc = nt.nodes.new('ShaderNodeVertexColor')
    vc.layer_name = 'Col'
    nt.links.new(vc.outputs['Color'], b.inputs['Base Color'])
    nt.links.new(b.outputs['BSDF'], out.inputs['Surface'])
    return mat


def finalize(bm, name, painter, mat_name):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    vol = bm.calc_volume(signed=True)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    xs = [v.co.x for v in me.vertices]
    ys = [v.co.y for v in me.vertices]
    zs = [v.co.z for v in me.vertices]
    off = Vector(((min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0, min(zs)))
    me.transform(Matrix.Translation(-off))
    for p in me.polygons:
        p.use_smooth = False
    painter(me)
    bm2 = bmesh.new()
    bm2.from_mesh(me)
    nb = sum(1 for e in bm2.edges if len(e.link_faces) != 2)
    centers = set()
    dup = 0
    for f in bm2.faces:
        f.material_index = 0
        key = tuple(round(c, 5) for c in f.calc_center_median())
        if key in centers:
            dup += 1
        centers.add(key)
    bm2.to_mesh(me)
    bm2.free()
    me.update()
    me.materials.clear()
    me.materials.append(make_mat(mat_name))
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')
    tris = sum(len(p.vertices) - 2 for p in me.polygons)
    d = ob.dimensions
    print('BUILD %-16s tris=%d verts=%d dims=(%.3f,%.3f,%.3f) signed_vol=%+.5f '
          'nonmanifold_edges=%d dup_faces=%d'
          % (name, tris, len(me.vertices), d.x, d.y, d.z, vol, nb, dup))
    return ob


def export_one(ob, path):
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.export_scene.fbx(
        filepath=path, use_selection=True, object_types={'MESH'},
        mesh_smooth_type='FACE', use_mesh_modifiers=True,
        add_leaf_bones=False, bake_anim=False, path_mode='AUTO',
        colors_type='LINEAR')
    print('EXPORTED', path)


EXPECT = {
    'SM_HidePickup': {HEX['DryEarth'], HEX['StoneGrey'], HEX['Straw'],
                      HEX['PaleHide']},
}


def verify(path, name):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    addon_utils.enable('io_scene_fbx')
    bpy.ops.import_scene.fbx(filepath=path)
    meshes = [o for o in bpy.data.objects if o.type == 'MESH']
    print('VERIFY %s imported_meshes=%d' % (name, len(meshes)))
    ob = meshes[0]
    me = ob.data
    mw = ob.matrix_world
    loc, rot, sc = mw.decompose()
    tris = sum(len(p.vertices) - 2 for p in me.polygons)
    cor = [mw @ v.co for v in me.vertices]
    mn = Vector((min(c.x for c in cor), min(c.y for c in cor), min(c.z for c in cor)))
    mx = Vector((max(c.x for c in cor), max(c.y for c in cor), max(c.z for c in cor)))
    dim = mx - mn
    print('VERIFY %s tris=%d verts=%d dims_m=(%.3f,%.3f,%.3f)'
          % (name, tris, len(me.vertices), dim.x, dim.y, dim.z))
    print('VERIFY %s origin=(%.4f,%.4f,%.4f) scale=(%.3f,%.3f,%.3f) '
          'bbox_z=[%.4f..%.4f] xy_center=(%.4f,%.4f)'
          % (name, loc.x, loc.y, loc.z, sc.x, sc.y, sc.z, mn.z, mx.z,
             (mn.x + mx.x) / 2, (mn.y + mx.y) / 2))
    ca = me.color_attributes[0]
    census = {}
    for p in me.polygons:
        c = ca.data[p.loop_indices[0]].color_srgb
        hx = '#%02X%02X%02X' % (round(c[0] * 255), round(c[1] * 255),
                                round(c[2] * 255))
        census[hx] = census.get(hx, 0) + 1
    print('VERIFY %s vcol_attr=%s/%s/%s census=%s'
          % (name, ca.name, ca.domain, ca.data_type, sorted(census.items())))
    exp = EXPECT[name]

    def s2l_byte(b):
        c = b / 255.0
        c = c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
        return round(c * 255)

    def rgb(hx):
        return tuple(int(hx[i:i + 2], 16) for i in (1, 3, 5))

    def match(hx):
        got = rgb(hx)
        for e in exp:
            er, eg, eb = rgb(e)
            lin = (s2l_byte(er), s2l_byte(eg), s2l_byte(eb))
            if all(abs(g - x) <= 3 for g, x in zip(got, lin)):
                return 'LINEAR', e
            if all(abs(g - x) <= 3 for g, x in zip(got, (er, eg, eb))):
                return 'SRGB', e
        return None, None
    mapping = {h: match(h) for h in census}
    print('VERIFY %s color_mapping=%s' % (name, sorted(
        (h, n, mapping[h][1], mapping[h][0]) for h, n in census.items())))
    bad = {h: n for h, n in census.items() if mapping[h][0] is None}
    magenta = census.get(HEX['Magenta'], 0)
    print('VERIFY %s palette_check=%s off_palette=%s magenta_faces=%d'
          % (name, 'PASS' if not bad else 'FAIL', bad, magenta))
    uvl = me.uv_layers.active
    us = [d.uv[0] for d in uvl.data]
    vs = [d.uv[1] for d in uvl.data]
    print('VERIFY %s uv_u=[%.3f..%.3f] uv_v=[%.3f..%.3f] materials=%s'
          % (name, min(us), max(us), min(vs), max(vs),
             [m.name for m in me.materials]))
    budget = 'PASS' if 100 <= tris <= 300 else 'FAIL'
    print('VERIFY %s tri_budget_100_300: %s (%d)' % (name, budget, tris))


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    addon_utils.enable('io_scene_fbx')
    roll = finalize(build_roll(), 'SM_HidePickup', paint_roll, 'M_HidePickup')
    bpy.ops.wm.save_as_mainfile(filepath=OUT + 'hide_pickup.blend')
    print('SAVED', OUT + 'hide_pickup.blend')
    export_one(roll, OUT + 'SM_HidePickup.fbx')
    verify(OUT + 'SM_HidePickup.fbx', 'SM_HidePickup')
    print('DONE')


main()
