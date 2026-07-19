"""Перекраска SM_Tree_01 под берёзу. ТОЛЬКО цвет вершин, геометрия не трогается.

Про кодировку цвета (иначе цвет «уплывает» на каждом круге импорт-экспорт):
в FBX лежит linear = s2l(задуманный sRGB). Blender на импорте кладёт это сырое
число в .color_srgb, то есть .color становится s2l(V) — на единицу кодирования
темнее. Поэтому:
  * нетронутые углы     -> .color = V (сырое из файла), экспорт вернёт ровно V;
  * перекрашенные углы  -> .color_srgb = задуманный sRGB.
Экспорт всегда colors_type='LINEAR' (пишет .color как есть).
"""
import bpy, os
from mathutils import Vector

SRC = "E:/ForGameLead(Materials)/phase3-assets/SM_Tree_01.fbx"
OUT = "E:/game-dev-team/assets/birch/"
WORK = OUT + "_work/"


def hx(h):
    h = h.lstrip('#')
    return (int(h[0:2], 16) / 255.0, int(h[2:4], 16) / 255.0, int(h[4:6], 16) / 255.0)


BARK_TOP = hx('E7E4D8')   # кора берёзы (палитра: ink)
BARK_BOT = hx('6E6A60')   # огрубевший комель (палитра: бетон/камень)
LEAF_UP = hx('5C7A3E')    # чуть подсвеченная листва (палитра: подсвет травы)

TRUNK_ZSPLIT = 0.5        # ниже — комель, выше — подкронная часть ствола


def geom_signature(me):
    """Подпись геометрии: позиции вершин, число треугольников, развёртка."""
    me.calc_loop_triangles()
    verts = sorted(tuple(round(c, 6) for c in v.co) for v in me.vertices)
    uvs = sorted(tuple(round(c, 6) for c in d.uv) for d in me.uv_layers[0].data)
    return (len(me.loop_triangles), len(me.vertices), len(me.polygons), tuple(verts), tuple(uvs))


def load():
    before = set(bpy.data.objects.keys())
    bpy.ops.import_scene.fbx(filepath=SRC)
    new = [o for o in bpy.data.objects if o.name not in before and o.type == 'MESH']
    return new[0]


def classify(ob):
    """Грани ствола/кроны по цвету, что лежит в файле."""
    me = ob.data
    ca = me.color_attributes[0]
    cols = {}
    for p in me.polygons:
        c = tuple(round(x, 4) for x in ca.data[p.loop_indices[0]].color_srgb[:3])
        cols.setdefault(c, []).append(p.index)
    # ствол = группа, у которой вершины лежат ниже
    def zmax(faces):
        return max(me.vertices[v].co.z for fi in faces for v in me.polygons[fi].vertices)
    groups = sorted(cols.items(), key=lambda kv: zmax(kv[1]))
    return set(groups[0][1]), set(groups[1][1])   # trunk_faces, crown_faces


def recolor(ob, name, lighten_crown, uniform_white_trunk=False):
    me = ob.data
    ca = me.color_attributes[0]
    trunk_faces, crown_faces = classify(ob)

    # 1) сохраняем ВСЁ как есть: сырое число из файла обратно в .color
    raw = [tuple(d.color_srgb) for d in ca.data]
    for d, v in zip(ca.data, raw):
        d.color = (v[0], v[1], v[2], 1.0)

    n_trunk = n_crown = 0
    # 2) ствол: градиент снизу вверх (вершин между кольцами нет — см. 20_inspect.log)
    for fi in trunk_faces:
        p = me.polygons[fi]
        for li, vi in zip(p.loop_indices, p.vertices):
            low = me.vertices[vi].co.z < TRUNK_ZSPLIT
            c = BARK_TOP if (uniform_white_trunk or not low) else BARK_BOT
            ca.data[li].color_srgb = (c[0], c[1], c[2], 1.0)
            n_trunk += 1
    # 3) крона: по желанию чуть светлее
    if lighten_crown:
        for fi in crown_faces:
            for li in me.polygons[fi].loop_indices:
                ca.data[li].color_srgb = (LEAF_UP[0], LEAF_UP[1], LEAF_UP[2], 1.0)
                n_crown += 1

    ob.name = 'SM_Tree_01'
    me.name = 'SM_Tree_01'
    print('  %-34s перекрашено углов: ствол=%d крона=%d (граней ствола=%d кроны=%d)'
          % (name, n_trunk, n_crown, len(trunk_faces), len(crown_faces)))
    return ob


def export(ob, path):
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.export_scene.fbx(
        filepath=path, use_selection=True, object_types={'MESH'},
        mesh_smooth_type='FACE', use_mesh_modifiers=True, add_leaf_bones=False,
        bake_anim=False, colors_type='LINEAR',
        apply_scale_options='FBX_SCALE_NONE', global_scale=1.0,
        axis_forward='-Z', axis_up='Y', path_mode='COPY', embed_textures=False)
    print('     EXPORT %s exists=%s size=%d' % (os.path.basename(path), os.path.exists(path),
                                                os.path.getsize(path) if os.path.exists(path) else 0))


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    print('=== ЭТАЛОН (исходный SM_Tree_01) ===')
    ref = load()
    SIG = geom_signature(ref.data)
    print('  tris=%d verts=%d polys=%d' % (SIG[0], SIG[1], SIG[2]))
    ref.name = 'REF_ORIGINAL'
    ref.data.name = 'REF_ORIGINAL'

    print('=== ПЕРЕКРАСКА ===')
    variants = [
        ('SM_Tree_01_birch',           dict(lighten_crown=True)),
        ('SM_Tree_01_birch_origcrown', dict(lighten_crown=False)),
        ('SM_Tree_01_birch_whitetrunk', dict(lighten_crown=True, uniform_white_trunk=True)),
    ]
    made = []
    for fname, kw in variants:
        ob = recolor(load(), fname, **kw)
        sig = geom_signature(ob.data)
        same = (sig == SIG)
        print('     ГЕОМЕТРИЯ ИДЕНТИЧНА ЭТАЛОНУ: %s  (tris %d -> %d)' % (same, SIG[0], sig[0]))
        if not same:
            raise SystemExit('ОСТАНОВ: геометрия изменилась, так нельзя')
        export(ob, OUT + fname + '.fbx')
        ob.name = fname
        ob.data.name = fname
        made.append(ob.name)

    bpy.ops.wm.save_as_mainfile(filepath=WORK + '_qc_recolor.blend')
    print('  BLEND', os.path.exists(WORK + '_qc_recolor.blend'))
    print('DONE')


main()
