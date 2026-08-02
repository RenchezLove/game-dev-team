"""Shared helpers for small static prop builders (assets/<id>/10_build_*.py).
Extracted from the accepted hide_pickup builder (2026-08-01) so each new prop
builder stays short; skeletal assets keep using armor_wearables/wcommon.py.

Conventions (context/_shared.md + asset-contract.md): meters, origin = bbox
center at Z=0, forward +Y, flat shade, 1 material, vcol 'Col' CORNER/BYTE
written via color_srgb, Smart UV 0-1, FBX MESH-only FACE smoothing with
colors_type='LINEAR' (default 'SRGB' double-encodes in UE - proven 07-06).
Painters pre-fill magenta; any face left magenta is caught by verify().
"""
import bpy
import bmesh
import math
import addon_utils
from mathutils import Vector, Matrix

MAGENTA = '#FF00FF'


def hexv(hx):
    hx = hx.lstrip('#')
    return (int(hx[0:2], 16) / 255.0, int(hx[2:4], 16) / 255.0,
            int(hx[4:6], 16) / 255.0, 1.0)


def box(bm, mn, mx, part):
    """Closed axis-aligned box, all faces tagged with part id."""
    x0, y0, z0 = mn
    x1, y1, z1 = mx
    vs = [bm.verts.new(v) for v in (
        (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
        (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1))]
    out = []
    for idx in ((0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4),
                (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        f = bm.faces.new([vs[i] for i in idx])
        f.material_index = part
        out.append(f)
    return vs, out


def lathe_spans(bm, profile, n, span_parts, ang0=0.0, jit=None):
    """Solid of revolution around Z. profile = [(radius, z), ...], r == 0 is
    a pole vertex. Each span between profile rows gets its own part id."""
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


def paint_parts(me, part_hex, default=None):
    """Fill 'Col' magenta, then color every polygon by its material_index via
    part_hex: {part_id: '#hex' or callable(poly, me) -> '#hex'}."""
    for ca in list(me.color_attributes):
        me.color_attributes.remove(ca)
    ca = me.color_attributes.new('Col', 'BYTE_COLOR', 'CORNER')
    mag = hexv(MAGENTA)
    for d in ca.data:
        d.color_srgb = mag
    for p in me.polygons:
        rule = part_hex.get(p.material_index, default)
        hx = rule(p, me) if callable(rule) else rule
        if hx is None:
            continue
        cv = hexv(hx)
        for li in p.loop_indices:
            ca.data[li].color_srgb = cv
    me.update()


def finalize(bm, name, painter, mat_name):
    """Recalc normals, triangulate, recenter origin to bbox-center/Z=0,
    flat shade, paint, collapse to 1 material, Smart UV. Returns object."""
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    vol = bm.calc_volume(signed=True)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    xs = [v.co.x for v in me.vertices]
    ys = [v.co.y for v in me.vertices]
    zs = [v.co.z for v in me.vertices]
    off = Vector(((min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0,
                  min(zs)))
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
    print('BUILD %-16s tris=%d verts=%d dims=(%.3f,%.3f,%.3f) '
          'signed_vol=%+.5f nonmanifold_edges=%d dup_faces=%d'
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


def verify(path, name, expect_hexes, budget):
    """FBX round-trip into a fresh factory scene; prints VERIFY lines:
    tris/verts/dims/origin/vcol census vs expected palette/UV/budget."""
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
    mn = Vector((min(c.x for c in cor), min(c.y for c in cor),
                 min(c.z for c in cor)))
    mx = Vector((max(c.x for c in cor), max(c.y for c in cor),
                 max(c.z for c in cor)))
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

    def s2l_byte(b):
        c = b / 255.0
        c = c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
        return round(c * 255)

    def rgb(hx):
        return tuple(int(hx[i:i + 2], 16) for i in (1, 3, 5))

    def match(hx):
        got = rgb(hx)
        for e in expect_hexes:
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
    magenta = census.get(MAGENTA, 0)
    print('VERIFY %s palette_check=%s off_palette=%s magenta_faces=%d'
          % (name, 'PASS' if not bad else 'FAIL', bad, magenta))
    uvl = me.uv_layers.active
    us = [d.uv[0] for d in uvl.data]
    vs = [d.uv[1] for d in uvl.data]
    print('VERIFY %s uv_u=[%.3f..%.3f] uv_v=[%.3f..%.3f] materials=%s'
          % (name, min(us), max(us), min(vs), max(vs),
             [m.name for m in me.materials]))
    lo, hi = budget
    ok = 'PASS' if lo <= tris <= hi else 'FAIL'
    print('VERIFY %s tri_budget_%d_%d: %s (%d)' % (name, lo, hi, ok, tris))


def fresh():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    addon_utils.enable('io_scene_fbx')
