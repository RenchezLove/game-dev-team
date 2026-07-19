"""Builder: SM_Tree_Birch_01 (берёза для леса ContrarySurvivor).

Ориентир по габаритам/стилю — SM_Tree_01 (112 трис, 1.14x1.20x1.96 м),
источник E:/ForGameLead(Materials)/phase3-assets/SM_Tree_01.fbx.

Ветер (ADR-039 п.2): M_WindTrees берёт маску качания из ВЫСОТЫ меша
(LocalPosition Z, нормировка по ObjectLocalBounds Min/Max), НЕ из покраски вершин.
Значит от меша требуется только: пивот в основании, zmin=0, вертикальная
протяжённость. Vertex color целиком уходит в BaseColor (текстур у материала нет).

Конвенции проекта: метры, origin в центре основания Z=0, forward +Y,
vcol 'Col' CORNER/BYTE, пишем color_srgb, экспорт FBX colors_type='LINEAR',
1 материал, flat shade, нормали наружу, Smart-UV 0-1.
"""
import bpy, bmesh, math, os, random, sys
from mathutils import Matrix, Vector

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from crown_approved import CLUMPS_BAKED   # крона, принятая лидом, зафиксирована данными

OUT = "E:/game-dev-team/assets/birch/"
WORK = OUT + "_work/"

# ---- палитра (sRGB-хексы из context/concept-artist/tmp/cs-palette.html) ----
def hx(h):
    h = h.lstrip('#')
    return (int(h[0:2], 16) / 255.0, int(h[2:4], 16) / 255.0, int(h[4:6], 16) / 255.0, 1.0)

BARK_WHITE = hx('E7E4D8')   # кора берёзы (палитра: ink / выцвет-светлый)
BARK_DARK  = hx('1B2018')   # чёрточки на коре (палитра: панель)
BARK_ROOT  = hx('3A4233')   # огрубевшая кора у комля (палитра: line)
LEAF_LIGHT = hx('5C7A3E')   # листва берёзы (палитра: подсвет травы)
LEAF_DARK  = hx('3F5A31')   # затенённые пряди (палитра: трава/поля)
COLL_GREY  = hx('6E6A60')   # UCX, в рендер не идёт

SIDES = 5

# ---- ПРОФИЛЬ ствола: (z, радиус, смещение x, смещение y) ----
# Форма НЕ меняется: новые кольца сажаются ровно на эту ломаную (линейная
# интерполяция между её узлами), поэтому силуэт остаётся прежним.
# S-изгиб: x идёт 0 -> -0.024 -> +0.055, наклон по y монотонный 0 -> 0.245.
PROFILE = [
    (0.00, 0.105,  0.000, 0.000),
    (0.22, 0.088, -0.010, 0.010),
    (0.52, 0.077, -0.023, 0.032),
    (0.59, 0.075, -0.024, 0.038),
    (0.95, 0.065, -0.014, 0.080),
    (1.02, 0.063, -0.010, 0.090),
    (1.42, 0.050,  0.018, 0.155),
    (1.49, 0.048,  0.024, 0.168),
    (1.95, 0.030,  0.055, 0.245),
]


def prof(z):
    """Радиус и смещения на высоте z по ломаной PROFILE."""
    if z <= PROFILE[0][0]:
        return PROFILE[0][1:]
    for a, b in zip(PROFILE, PROFILE[1:]):
        if z <= b[0]:
            t = (z - a[0]) / (b[0] - a[0])
            return tuple(a[i] + (b[i] - a[i]) * t for i in (1, 2, 3))
    return PROFILE[-1][1:]


# Кольца. Крона начинается на z≈1.03, выше ствол не виден — чёрточки туда не ставим.
# Пояски разной толщины и на разной высоте, кверху тоньше: 5.0, 4.5, 4.0, 3.5, 3.0 см.
RING_Z = [0.00, 0.22,
          0.33, 0.38,      # поясок 1 — 5.0 см
          0.52, 0.565,     # поясок 2 — 4.5 см
          0.70, 0.74,      # поясок 3 — 4.0 см
          0.86, 0.895,     # поясок 4 — 3.5 см
          0.97, 1.00,      # поясок 5 — 3.0 см
          1.95]
TRUNK_RINGS = [(z,) + prof(z) for z in RING_Z]

# чёрточки: сегмент -> какие грани красим тёмным. Грани вразнобой, чтобы
# отметины не выстраивались в вертикальный столбик и в ровные пояски.
MARKS = {2: (0, 2), 4: (4,), 6: (1, 3), 8: (0,), 10: (2, 4)}
# комель: тёмная кора не сплошным кольцом (иначе читается «сапогом»), а 3 грани из 5
ROOT_SEG = 0
ROOT_SIDES_DEFAULT = (0, 1, 3)

# ---- крона: (центр, радиус, масштаб, seed, цвет) ----
CLUMPS = [
    ((0.02,  0.16, 1.62), 0.40, (1.15, 1.10, 1.22), 21, LEAF_LIGHT),
    ((-0.26, 0.04, 1.44), 0.28, (1.10, 1.10, 1.18), 22, LEAF_DARK),
    ((0.25,  0.30, 1.54), 0.27, (1.10, 1.10, 1.18), 23, LEAF_LIGHT),
    ((0.02,  0.19, 1.88), 0.26, (1.00, 1.00, 0.95), 24, LEAF_LIGHT),
    ((-0.07, -0.14, 1.34), 0.23, (1.05, 1.05, 1.15), 25, LEAF_DARK),
]
JITTER = 0.045


def trunk(bm, rings, colmap, sides=SIDES, marks=None, root_seg=ROOT_SEG, root_sides=None):
    marks = marks or {}
    ROOT_SIDES = ROOT_SIDES_DEFAULT if root_sides is None else root_sides
    loops = []
    for (z, r, dx, dy) in rings:
        ring = []
        for i in range(sides):
            a = 2.0 * math.pi * i / sides
            ring.append(bm.verts.new((dx + r * math.cos(a), dy + r * math.sin(a), z)))
        loops.append(ring)
    for s in range(len(loops) - 1):
        lo, hi = loops[s], loops[s + 1]
        for i in range(sides):
            j = (i + 1) % sides
            f = bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
            if s == root_seg:
                colmap[f] = BARK_ROOT if i in ROOT_SIDES else BARK_WHITE
            elif s in marks and i in marks[s]:
                colmap[f] = BARK_DARK
            else:
                colmap[f] = BARK_WHITE
    colmap[bm.faces.new(list(reversed(loops[0])))] = BARK_ROOT
    colmap[bm.faces.new(loops[-1])] = BARK_WHITE


def clump(bm, idx, colmap):
    """Комок кроны из зафиксированных данных (crown_approved.py).

    Процедурная генерация УБРАНА намеренно: дрожание вершин применялось при
    обходе множества bmesh-вершин, порядок которого зависит от числа вершин
    ствола, поэтому крона молча менялась при каждой правке ствола (замерено до
    0.103 м на вершину). Крону принял лид — она зафиксирована и не пересчитывается.
    """
    verts, faces, hexcol = CLUMPS_BAKED[idx]
    col = hx(hexcol)
    vs = [bm.verts.new(v) for v in verts]
    for f in faces:
        colmap[bm.faces.new([vs[i] for i in f])] = col


def prism(bm, radius, z0, z1, colmap, color, sides=6, off=(0.01, 0.06)):
    lo, hi = [], []
    for i in range(sides):
        a = 2.0 * math.pi * i / sides
        x, y = off[0] + radius * math.cos(a), off[1] + radius * math.sin(a)
        lo.append(bm.verts.new((x, y, z0)))
        hi.append(bm.verts.new((x, y, z1)))
    for i in range(sides):
        j = (i + 1) % sides
        colmap[bm.faces.new((lo[i], lo[j], hi[j], hi[i]))] = color
    colmap[bm.faces.new(list(reversed(lo)))] = color
    colmap[bm.faces.new(hi)] = color


def signed_volume(me):
    tot = 0.0
    me.calc_loop_triangles()
    for t in me.loop_triangles:
        a, b, c = (me.vertices[i].co for i in t.vertices)
        tot += a.dot(b.cross(c)) / 6.0
    return tot


def finish(name, bm, colmap, mat_name='M_Birch', do_uv=True):
    """bmesh -> объект: нормали наружу, flat, vcol 'Col', UV, триангуляция."""
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    # remove_doubles/recalc могли пересобрать грани — восстановим цвет по «родителю»
    colors = {}
    for f in bm.faces:
        colors[f.index if f.index >= 0 else id(f)] = None
    me = bpy.data.meshes.new(name)
    # цвет снимаем ДО записи в меш: ключ — центр грани (устойчив к пересборке)
    fcol = {}
    for f, c in colmap.items():
        if f.is_valid:
            fcol[tuple(round(x, 5) for x in f.calc_center_median())] = c
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)

    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shade_flat()

    ca = me.color_attributes.new(name='Col', type='BYTE_COLOR', domain='CORNER')
    miss = 0
    for p in me.polygons:
        key = tuple(round(x, 5) for x in p.center)
        c = fcol.get(key)
        if c is None:  # ключ не совпал -> ближайший центр
            best, bd = None, 1e9
            for k, v in fcol.items():
                d = (Vector(k) - p.center).length
                if d < bd:
                    best, bd = v, d
            c = best
            if bd > 1e-3:
                miss += 1
        for li in p.loop_indices:
            ca.data[li].color_srgb = c
    if miss:
        print('  WARN: %d граней покрашены по ближайшему центру' % miss)

    if do_uv:
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.02)
        bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
    bpy.ops.object.mode_set(mode='OBJECT')

    mat = bpy.data.materials.get(mat_name)
    if mat is None:
        mat = bpy.data.materials.new(mat_name)
        mat.use_nodes = True
        nt = mat.node_tree
        bsdf = nt.nodes['Principled BSDF']
        bsdf.inputs['Roughness'].default_value = 0.8
        attr = nt.nodes.new('ShaderNodeVertexColor')
        attr.layer_name = 'Col'
        nt.links.new(attr.outputs['Color'], bsdf.inputs['Base Color'])
    me.materials.append(mat)

    ob.select_set(False)
    return ob


def report(ob, label):
    me = ob.data
    me.calc_loop_triangles()
    d = ob.dimensions
    zmin = min((ob.matrix_world @ v.co).z for v in me.vertices)
    loose = sum(1 for e in me.edges if len(
        [p for p in me.polygons if e.key[0] in p.vertices and e.key[1] in p.vertices]) < 2)
    print('  %-28s tris=%-5d verts=%-5d dim=(%.3f, %.3f, %.3f) zmin=%.4f vol=%+.5f uv=%s vcol=%s'
          % (label, len(me.loop_triangles), len(me.vertices), d.x, d.y, d.z,
             zmin, signed_volume(me),
             [u.name for u in me.uv_layers], [a.name for a in me.color_attributes]))
    return len(me.loop_triangles)


def build_lod0():
    bm = bmesh.new(); cm = {}
    trunk(bm, TRUNK_RINGS, cm, marks=MARKS)
    for idx in range(len(CLUMPS_BAKED)):
        clump(bm, idx, cm)
    return finish('SM_Tree_Birch_01', bm, cm)


def build_lod1():
    # короткий комель отдельным кольцом, иначе тёмная кора растягивается на пол-ствола
    rings = [(0.00, 0.105, 0.000, 0.000), (0.22, 0.088, -0.010, 0.010),
             (0.50, 0.078, -0.022, 0.030), (0.98, 0.064, -0.012, 0.085),
             (1.45, 0.049, 0.020, 0.160), (1.95, 0.030, 0.055, 0.245)]
    bm = bmesh.new(); cm = {}
    trunk(bm, rings, cm, marks={})
    for idx in (0, 2, 3):
        clump(bm, idx, cm)
    return finish('SM_Tree_Birch_01_LOD1', bm, cm)


def build_lod2():
    rings = [(0.00, 0.105, 0.000, 0.000), (0.98, 0.064, -0.012, 0.085),
             (1.95, 0.030, 0.055, 0.245)]
    bm = bmesh.new(); cm = {}
    # на LOD2 сегменты длинные: тёмный комель занял бы пол-ствола -> ствол целиком белый
    trunk(bm, rings, cm, sides=4, marks={}, root_sides=())
    for idx in (0, 3):
        clump(bm, idx, cm)
    return finish('SM_Tree_Birch_01_LOD2', bm, cm)


def build_ucx():
    bm = bmesh.new(); cm = {}
    # радиус 0.17 — с запасом на наклон ствола, иначе комель торчит наружу хулла
    prism(bm, 0.17, 0.0, 2.00, cm, COLL_GREY, sides=6)
    return finish('UCX_SM_Tree_Birch_01_01', bm, cm, mat_name='M_Birch', do_uv=False)


def export(objs, path):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.export_scene.fbx(
        filepath=path, use_selection=True, object_types={'MESH'},
        mesh_smooth_type='FACE', use_mesh_modifiers=True, add_leaf_bones=False,
        bake_anim=False, colors_type='LINEAR',
        apply_scale_options='FBX_SCALE_NONE', global_scale=1.0,
        axis_forward='-Z', axis_up='Y', path_mode='COPY', embed_textures=False)
    print('  EXPORT %s exists=%s size=%d' % (path, os.path.exists(path),
                                             os.path.getsize(path) if os.path.exists(path) else 0))


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    print('=== СБОРКА БЕРЁЗЫ ===')
    lod0 = build_lod0(); t0 = report(lod0, 'LOD0 (крона+ствол)')
    lod1 = build_lod1(); t1 = report(lod1, 'LOD1')
    lod2 = build_lod2(); t2 = report(lod2, 'LOD2')
    ucx = build_ucx();   tc = report(ucx, 'UCX (коллизия)')
    print('  ИТОГО рендер-трисов LOD0=%d LOD1=%d LOD2=%d, коллизия=%d' % (t0, t1, t2, tc))

    print('=== ЭКСПОРТ ===')
    export([lod0, ucx], OUT + 'SM_Tree_Birch_01.fbx')
    export([lod1], OUT + 'SM_Tree_Birch_01_LOD1.fbx')
    export([lod2], OUT + 'SM_Tree_Birch_01_LOD2.fbx')

    bpy.ops.wm.save_as_mainfile(filepath=WORK + '_qc_birch.blend')
    print('  BLEND', os.path.exists(WORK + '_qc_birch.blend'))
    print('DONE')


main()
