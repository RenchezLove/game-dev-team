"""Build two small loot pickup props (Rinat chooses one):
  SM_LootSack     - drawstring cloth sack (grey-brown fabric, amber tie = loot accent)
  SM_LootBackpack - small backpack (dark fabric + leather flap, amber buckles)
Budget <=200 tris each (tiny ground pickup, top-down camera far away).
Vertex colors = approved 16-color palette (GDD), raw sRGB bytes in 'Col'
(CORNER/BYTE_COLOR), FBX export colors_type='LINEAR' (project convention).
Conventions: meters, origin = base center Z=0, forward +Y, flat shade,
one material per asset, Smart UV 0-1, FBX MESH-only FACE smoothing.

Headless:
  E:/Programs/Blender/blender.exe -b --factory-startup --python 10_build_loot_bags.py
Self-verifies via FBX round-trip into fresh factory scenes (tris, dims,
origin, manifold, normals, color census vs palette, UV range).
"""
import bpy, bmesh, math, addon_utils
from mathutils import Vector, Matrix

OUT = 'E:/game-dev-team/assets/loot_bag/'

HEX = dict(
    DryEarth='#7D6A4E', Timber='#8A5A32', AmberLoot='#E0A32E',
    FadedSage='#9AA08C', ColdSteel='#5A6470', PanelDark='#1B2018',
    Magenta='#FF00FF')

# part ids kept in face.material_index during build, reset to 0 before export
(P_BODY, P_KNOT, P_TIE, P_FLAP, P_POCKET, P_STRAP,
 P_BUCK_A, P_BUCK_D, P_HANDLE) = range(9)


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


def lathe(bm, profile, n, part, ang0=0.0):
    """profile = [(r,z), ...]; r==0 entries are poles (fan caps)."""
    entries = []
    for r, z in profile:
        if r == 0.0:
            entries.append(('pole', bm.verts.new((0.0, 0.0, z))))
        else:
            ring = []
            for k in range(n):
                a = ang0 + 2.0 * math.pi * k / n
                ring.append(bm.verts.new((r * math.cos(a), r * math.sin(a), z)))
            entries.append(('ring', ring))
    for i in range(len(entries) - 1):
        ka, va = entries[i]
        kb, vb = entries[i + 1]
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
    """Bent solid slab. path = [(y,z),...] outer skin; thickness th offset
    along 2D normal (tz,-ty)*sign. Spans x0..x1 in X."""
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
        faces.append((A[i], B[i], B[i + 1], A[i + 1]))      # outer
        faces.append((D[i + 1], C[i + 1], C[i], D[i]))      # inner
        faces.append((A[i + 1], D[i + 1], D[i], A[i]))      # side x0
        faces.append((B[i], C[i], C[i + 1], B[i + 1]))      # side x1
    faces.append((A[0], B[0], C[0], D[0]))                  # cap start
    faces.append((D[m - 1], C[m - 1], B[m - 1], A[m - 1]))  # cap end
    for idx in faces:
        f = bm.faces.new(idx)
        f.material_index = part


def build_sack():
    bm = bmesh.new()
    profile = [(0.0, 0.0), (0.13, 0.0), (0.175, 0.055), (0.185, 0.13),
               (0.145, 0.21), (0.09, 0.26), (0.078, 0.30),
               (0.115, 0.345), (0.055, 0.40), (0.0, 0.415)]
    lathe(bm, profile, 8, P_BODY, math.radians(22.5))
    # knot at front (+Y) of the neck
    box(bm, (-0.034, 0.06, 0.255), (0.034, 0.105, 0.305), P_KNOT)
    # two tie ends draping down the front shoulder of the bag
    tie_path = [(0.095, 0.272), (0.148, 0.222), (0.168, 0.178)]
    slab(bm, tie_path, -0.056, -0.028, 0.012, 1, P_TIE)
    slab(bm, tie_path, 0.028, 0.056, 0.012, 1, P_TIE)
    return bm


def build_pack():
    bm = bmesh.new()
    # tapered body box
    bx, by, tx, ty, h = 0.13, 0.07, 0.1105, 0.056, 0.30
    vs = [bm.verts.new(v) for v in (
        (-bx, -by, 0), (bx, -by, 0), (bx, by, 0), (-bx, by, 0),
        (-tx, -ty, h), (tx, -ty, h), (tx, ty, h), (-tx, ty, h))]
    for idx in ((0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4),
                (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        f = bm.faces.new([vs[i] for i in idx])
        f.material_index = P_BODY
    # leather flap over the top, hanging down the front (+Y)
    slab(bm, [(-0.06, 0.295), (0.0, 0.325), (0.058, 0.315),
              (0.085, 0.24), (0.082, 0.155)], -0.12, 0.12, 0.022, 1, P_FLAP)
    # front pocket
    box(bm, (-0.085, 0.055, 0.025), (0.085, 0.115, 0.125), P_POCKET)
    # shoulder straps on the back (-Y), bowed outward
    strap_path = [(-0.055, 0.285), (-0.105, 0.16), (-0.065, 0.02)]
    slab(bm, strap_path, -0.085, -0.045, 0.016, -1, P_STRAP)
    slab(bm, strap_path, 0.045, 0.085, 0.016, -1, P_STRAP)
    # buckle straps on flap front: dark strap + slightly proud amber buckle
    for sx in (-1, 1):
        box(bm, (sx * 0.063 - (0.026 if sx < 0 else 0), 0.075, 0.15)
            if False else
            (min(sx * 0.063, sx * 0.037), 0.075, 0.15),
            (max(sx * 0.063, sx * 0.037), 0.106, 0.195), P_BUCK_A)
        box(bm, (min(sx * 0.063, sx * 0.037), 0.075, 0.185),
            (max(sx * 0.063, sx * 0.037), 0.100, 0.26), P_BUCK_D)
    # top carry handle
    box(bm, (-0.045, -0.048, 0.295), (0.045, -0.018, 0.328), P_HANDLE)
    return bm


def paint_sack(me):
    def rule(p):
        pid = p.material_index
        if pid in (P_KNOT, P_TIE):
            return HEX['AmberLoot']
        z = p.center.z
        if z < 0.06:
            return HEX['Timber']       # dirty base
        if z < 0.265:
            return HEX['DryEarth']     # cloth body
        if z < 0.307:
            return HEX['AmberLoot']    # tie band
        return HEX['FadedSage']        # puff above the tie
    _paint(me, rule)


def paint_pack(me):
    def rule(p):
        pid = p.material_index
        if pid == P_BODY:
            return HEX['ColdSteel']
        if pid in (P_FLAP, P_POCKET):
            return HEX['Timber']
        if pid == P_BUCK_A:
            return HEX['AmberLoot']
        return HEX['PanelDark']        # straps, handle, dark buckle straps
    _paint(me, rule)


def _paint(me, rule):
    keep = None
    for ca in list(me.color_attributes):
        me.color_attributes.remove(ca)
    ca = me.color_attributes.new('Col', 'BYTE_COLOR', 'CORNER')
    mag = hexv(HEX['Magenta'])
    for d in ca.data:
        d.color_srgb = mag
    for p in me.polygons:
        c = hexv(rule(p))
        for li in p.loop_indices:
            ca.data[li].color_srgb = c
    me.update()


def make_mat(name):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    b.inputs['Metallic'].default_value = 0.0
    b.inputs['Roughness'].default_value = 0.75
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
    # origin: base center Z=0 (bbox XY center to 0, min Z to 0)
    xs = [v.co.x for v in me.vertices]
    ys = [v.co.y for v in me.vertices]
    zs = [v.co.z for v in me.vertices]
    off = Vector(((min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0, min(zs)))
    me.transform(Matrix.Translation(-off))
    for p in me.polygons:
        p.use_smooth = False
    painter(me)
    # reset part ids -> single material slot 0
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
    # Smart UV 0-1
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
    'SM_LootSack': {HEX['Timber'], HEX['DryEarth'], HEX['AmberLoot'],
                    HEX['FadedSage']},
    'SM_LootBackpack': {HEX['ColdSteel'], HEX['Timber'], HEX['AmberLoot'],
                        HEX['PanelDark']},
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
    # color census (stored sRGB bytes reconstructed via color_srgb)
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

    def near(hx):
        r, g, b = (int(hx[i:i + 2], 16) for i in (1, 3, 5))
        for e in exp:
            er, eg, eb = (int(e[i:i + 2], 16) for i in (1, 3, 5))
            if abs(r - er) <= 3 and abs(g - eg) <= 3 and abs(b - eb) <= 3:
                return True
        return False
    bad = {h: n for h, n in census.items() if not near(h)}
    magenta = census.get(HEX['Magenta'], 0)
    print('VERIFY %s palette_check=%s off_palette=%s magenta_faces=%d'
          % (name, 'PASS' if not bad else 'FAIL', bad, magenta))
    uvl = me.uv_layers.active
    us = [d.uv[0] for d in uvl.data]
    vs = [d.uv[1] for d in uvl.data]
    print('VERIFY %s uv_u=[%.3f..%.3f] uv_v=[%.3f..%.3f] materials=%s'
          % (name, min(us), max(us), min(vs), max(vs),
             [m.name for m in me.materials]))
    budget = 'PASS' if tris <= 200 else 'FAIL'
    print('VERIFY %s tri_budget<=200: %s (%d)' % (name, budget, tris))


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    addon_utils.enable('io_scene_fbx')
    sack = finalize(build_sack(), 'SM_LootSack', paint_sack, 'M_LootSack')
    pack = finalize(build_pack(), 'SM_LootBackpack', paint_pack,
                    'M_LootBackpack')
    bpy.ops.wm.save_as_mainfile(filepath=OUT + 'loot_bag.blend')
    print('SAVED', OUT + 'loot_bag.blend')
    export_one(sack, OUT + 'SM_LootSack.fbx')
    export_one(pack, OUT + 'SM_LootBackpack.fbx')
    verify(OUT + 'SM_LootSack.fbx', 'SM_LootSack')
    verify(OUT + 'SM_LootBackpack.fbx', 'SM_LootBackpack')
    print('DONE')


main()
