"""Рендеры берёзы: ракурсы, вид сверху, игровая камера, сравнение габаритов, LOD, wireframe.

Игровая камера — параметры из Source/ContrarySurvivor/Characters/PlayerCharacter.h:
pitch -60 град, длина штанги 3000 uu = 30 м, FOV 40 град.
"""
import bpy, bmesh, math, os
from mathutils import Vector, Matrix

WORK = "E:/game-dev-team/assets/birch/_work/"
REN = "E:/game-dev-team/assets/birch/renders/"
PHASE3 = "E:/ForGameLead(Materials)/phase3-assets/"

bpy.ops.wm.open_mainfile(filepath=WORK + '_qc_birch.blend')


def hx(h):
    h = h.lstrip('#')
    return (int(h[0:2], 16) / 255.0, int(h[2:4], 16) / 255.0, int(h[4:6], 16) / 255.0, 1.0)


def vcol_mat(name='M_QC', rough=0.8):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Roughness'].default_value = rough
    a = m.node_tree.nodes.new('ShaderNodeVertexColor')
    a.layer_name = 'Col'
    m.node_tree.links.new(a.outputs['Color'], b.inputs['Base Color'])
    return m


MAT = vcol_mat()
for ob in bpy.data.objects:
    if ob.type == 'MESH':
        ob.data.materials.clear()
        ob.data.materials.append(MAT)

BIRCH = bpy.data.objects['SM_Tree_Birch_01']
LOD1 = bpy.data.objects['SM_Tree_Birch_01_LOD1']
LOD2 = bpy.data.objects['SM_Tree_Birch_01_LOD2']
UCX = bpy.data.objects['UCX_SM_Tree_Birch_01_01']


def import_tree(name):
    """Импорт существующего дерева + починка цвета.
    На реимпорте Blender кладёт СЫРОЕ linear-число из FBX в color_srgb —
    возвращаем его в .color, тогда рендер показывает задуманный цвет."""
    before = set(o.name for o in bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=PHASE3 + name + '.fbx')
    new = [o for o in bpy.data.objects if o.name not in before and o.type == 'MESH'][0]
    ca = new.data.color_attributes[0]
    raw = [tuple(d.color_srgb) for d in ca.data]
    for d, v in zip(ca.data, raw):
        d.color = (v[0], v[1], v[2], 1.0)
    new.data.materials.clear()
    new.data.materials.append(MAT)
    return new


REF_TREE = import_tree('SM_Tree_01')
REF_TREE.name = 'REF_SM_Tree_01'


def ground(size=90.0):
    me = bpy.data.meshes.new('Ground')
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=size / 2)
    bm.to_mesh(me)
    bm.free()
    ca = me.color_attributes.new(name='Col', type='BYTE_COLOR', domain='CORNER')
    for d in ca.data:
        d.color_srgb = hx('3F5A31')
    ob = bpy.data.objects.new('Ground', me)
    ob.data.materials.append(MAT)
    bpy.context.collection.objects.link(ob)
    return ob


GROUND = ground()


def human(loc=(0, 0, 0), h=1.8):
    """Эталон роста 1.8 м."""
    me = bpy.data.meshes.new('Human')
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8,
                          radius1=0.19, radius2=0.15, depth=h,
                          matrix=Matrix.Translation((0, 0, h / 2)))
    bm.to_mesh(me)
    bm.free()
    ca = me.color_attributes.new(name='Col', type='BYTE_COLOR', domain='CORNER')
    for d in ca.data:
        d.color_srgb = hx('C64B2C')
    ob = bpy.data.objects.new('HumanRef', me)
    ob.data.materials.append(MAT)
    ob.location = loc
    bpy.context.collection.objects.link(ob)
    return ob


# ---------- сцена: свет и рендер ----------
sc = bpy.context.scene
try:
    sc.render.engine = 'BLENDER_EEVEE_NEXT'
except TypeError:
    sc.render.engine = 'BLENDER_EEVEE'
sc.view_settings.view_transform = 'Standard'
sc.view_settings.look = 'None'
sc.render.film_transparent = False
sc.render.image_settings.file_format = 'PNG'
try:
    sc.eevee.taa_render_samples = 64
    sc.eevee.use_shadows = True
except AttributeError:
    pass

world = bpy.data.worlds.new('W')
sc.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.55, 0.62, 0.72, 1.0)
world.node_tree.nodes['Background'].inputs[1].default_value = 0.65

sun_d = bpy.data.lights.new('Sun', 'SUN')
sun_d.energy = 3.2
sun_d.angle = math.radians(6.0)
sun = bpy.data.objects.new('Sun', sun_d)
sun.rotation_euler = (math.radians(52), 0, math.radians(38))
bpy.context.collection.objects.link(sun)

fill_d = bpy.data.lights.new('Fill', 'SUN')
fill_d.energy = 1.0
fill_d.angle = math.radians(25.0)
fill = bpy.data.objects.new('Fill', fill_d)
fill.rotation_euler = (math.radians(62), 0, math.radians(-135))
bpy.context.collection.objects.link(fill)

cam_d = bpy.data.cameras.new('Cam')
CAM = bpy.data.objects.new('Cam', cam_d)
bpy.context.collection.objects.link(CAM)
sc.camera = CAM


def look_at(cam, target):
    d = Vector(target) - cam.location
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def shot(name, loc, target, res=(1100, 1100), fov=None, ortho=None, wire=False):
    CAM.location = Vector(loc)
    look_at(CAM, target)
    if ortho:
        cam_d.type = 'ORTHO'
        cam_d.ortho_scale = ortho
    else:
        cam_d.type = 'PERSP'
        cam_d.sensor_fit = 'HORIZONTAL'
        cam_d.angle_x = math.radians(fov if fov else 39.6)
    sc.render.resolution_x, sc.render.resolution_y = res
    for ob in bpy.data.objects:
        if ob.type == 'MESH':
            ob.show_wire = wire
            ob.show_all_edges = wire
    sc.render.filepath = REN + name + '.png'
    bpy.ops.render.render(write_still=True)
    p = sc.render.filepath
    print('  RENDER %-40s exists=%s size=%d' % (name + '.png', os.path.exists(p),
                                                os.path.getsize(p) if os.path.exists(p) else 0))


def vis(objs_visible):
    names = set(objs_visible)
    for ob in bpy.data.objects:
        if ob.type == 'MESH':
            ob.hide_render = ob.name not in names


ALL = ['Ground']
print('=== РЕНДЕРЫ ===')

# 1-3. Кругом: три ракурса берёзы в рост
vis(ALL + ['SM_Tree_Birch_01'])
BIRCH.location = (0, 0, 0)
for i, (ang, nm) in enumerate([(0, '01_birch_front'), (120, '02_birch_side'), (235, '03_birch_back')]):
    a = math.radians(ang)
    r = 5.6
    shot(nm, (r * math.sin(a), -r * math.cos(a), 1.9), (0, 0, 1.15), fov=32)

# 4. Крупный план ствола — чёрточки на коре
shot('04_birch_bark_closeup', (1.5, -1.5, 1.1), (0.0, 0.05, 0.85), fov=30)

# 5. Строгий вид сверху (птичий)
shot('05_birch_topdown_strict', (0.05, 0.1, 14.0), (0.05, 0.1, 1.2), ortho=2.6)

# 6. Wireframe
shot('06_birch_wireframe', (4.4, -4.4, 2.6), (0, 0, 1.15), fov=34, wire=True)

# 7. Сравнение габаритов с SM_Tree_01 + эталон роста 1.8 м
HUM = human((-1.9, 0, 0))
REF_TREE.location = (1.9, 0, 0)
vis(ALL + ['SM_Tree_Birch_01', 'REF_SM_Tree_01', 'HumanRef'])
shot('07_size_vs_SM_Tree_01', (0.0, -11.5, 2.6), (0.0, 0.0, 1.15), res=(1400, 900), fov=26)

# 8. То же сверху
shot('08_size_vs_SM_Tree_01_top', (0.0, 0.0, 15.0), (0.0, 0.0, 1.1), res=(1400, 900), ortho=6.4)

# 9. Линейка LOD
vis(ALL + ['SM_Tree_Birch_01', 'SM_Tree_Birch_01_LOD1', 'SM_Tree_Birch_01_LOD2'])
BIRCH.location = (-2.2, 0, 0)
LOD1.location = (0.0, 0, 0)
LOD2.location = (2.2, 0, 0)
shot('09_lods_0_1_2', (0.0, -12.0, 2.6), (0.0, 0.0, 1.15), res=(1500, 900), fov=26)
shot('10_lods_0_1_2_wire', (0.0, -12.0, 2.6), (0.0, 0.0, 1.15), res=(1500, 900), fov=26, wire=True)

# 11. Коллизия UCX поверх меша
vis(ALL + ['SM_Tree_Birch_01', 'UCX_SM_Tree_Birch_01_01'])
BIRCH.location = (0, 0, 0)
shot('11_collision_UCX', (4.4, -4.4, 2.4), (0, 0, 1.1), fov=34, wire=True)

# 12-13. ИГРОВАЯ КАМЕРА: pitch -60, FOV 40, дистанция 30 м. Рощица.
GROVE = []
for i, (x, y, rz, s, src) in enumerate([
        (-3.2, 2.4, 40, 1.00, BIRCH), (2.6, 4.6, 155, 0.92, BIRCH),
        (5.4, -1.2, 280, 1.06, BIRCH), (-6.0, -2.6, 95, 0.96, BIRCH),
        (0.4, 8.2, 210, 1.02, BIRCH), (-1.6, -4.4, 15, 1.00, REF_TREE),
        (7.2, 5.0, 130, 1.05, REF_TREE), (-8.0, 4.2, 250, 0.95, REF_TREE)]):
    o = bpy.data.objects.new('Grove_%02d' % i, src.data)
    o.location = (x, y, 0)
    o.rotation_euler = (0, 0, math.radians(rz))
    o.scale = (s, s, s)
    bpy.context.collection.objects.link(o)
    GROVE.append(o.name)

BIRCH.location = (0, 0, 0)
REF_TREE.location = (2.8, -6.5, 0)
HUM.location = (0.0, -1.6, 0)
vis(ALL + GROVE + ['SM_Tree_Birch_01', 'REF_SM_Tree_01', 'HumanRef'])

pitch = math.radians(60.0)
dist = 30.0
tgt = Vector((0.0, 0.5, 0.0))
fwd = Vector((0.0, math.cos(pitch), -math.sin(pitch)))
shot('12_gameplay_camera_grove', tuple(tgt - fwd * dist), tuple(tgt),
     res=(1280, 720), fov=40.0)

# 13. Тот же кадр, только берёзы (проверка читаемости сверху)
vis(ALL + [n for n, o in zip(GROVE, GROVE) if True] + ['SM_Tree_Birch_01', 'HumanRef'])
for n in GROVE:
    if bpy.data.objects[n].data == REF_TREE.data:
        bpy.data.objects[n].hide_render = True
shot('13_gameplay_camera_birch_only', tuple(tgt - fwd * dist), tuple(tgt),
     res=(1280, 720), fov=40.0)

print('DONE')
