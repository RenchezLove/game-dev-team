"""Рендеры перекраски: линейка вариантов рядом с исходным деревом + вид с игровой камеры.

Игровая камера (Source/ContrarySurvivor/Characters/PlayerCharacter.h):
наклон -60 град, штанга 3000 uu = 30 м, поле зрения 40 град.
"""
import bpy, bmesh, math, os
from mathutils import Vector, Matrix

WORK = "E:/game-dev-team/assets/birch/_work/"
REN = "E:/game-dev-team/assets/birch/renders/recolor/"
OUT = "E:/game-dev-team/assets/birch/"
SRC_ORIG = "E:/ForGameLead(Materials)/phase3-assets/SM_Tree_01.fbx"
os.makedirs(REN, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)


def hx(h):
    h = h.lstrip('#')
    return (int(h[0:2], 16) / 255.0, int(h[2:4], 16) / 255.0, int(h[4:6], 16) / 255.0, 1.0)


def vcol_mat(name='M_QC'):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Roughness'].default_value = 0.8
    a = m.node_tree.nodes.new('ShaderNodeVertexColor')
    a.layer_name = 'Col'
    m.node_tree.links.new(a.outputs['Color'], b.inputs['Base Color'])
    return m


MAT = vcol_mat()


def load(path, name):
    """Импорт + возврат сырого linear-числа из файла в .color (иначе рендер темнит)."""
    before = set(o.name for o in bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path)
    ob = [o for o in bpy.data.objects if o.name not in before and o.type == 'MESH'][0]
    ca = ob.data.color_attributes[0]
    raw = [tuple(d.color_srgb) for d in ca.data]
    for d, v in zip(ca.data, raw):
        d.color = (v[0], v[1], v[2], 1.0)
    ob.data.materials.clear()
    ob.data.materials.append(MAT)
    ob.name = name
    return ob


ORIG = load(SRC_ORIG, 'A_original')
B_ORIG_CROWN = load(OUT + 'SM_Tree_01_birch_origcrown.fbx', 'B_birch_origcrown')
C_LIGHT = load(OUT + 'SM_Tree_01_birch.fbx', 'C_birch')
D_WHITE = load(OUT + 'SM_Tree_01_birch_whitetrunk.fbx', 'D_birch_whitetrunk')
LINEUP = [ORIG, B_ORIG_CROWN, C_LIGHT, D_WHITE]


def ground(size=120.0):
    me = bpy.data.meshes.new('Ground')
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=size / 2)
    bm.to_mesh(me); bm.free()
    ca = me.color_attributes.new(name='Col', type='BYTE_COLOR', domain='CORNER')
    for d in ca.data:
        d.color_srgb = hx('3F5A31')
    ob = bpy.data.objects.new('Ground', me)
    ob.data.materials.append(MAT)
    bpy.context.collection.objects.link(ob)
    return ob


ground()


def human(loc=(0, 0, 0), h=1.8):
    me = bpy.data.meshes.new('Human')
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8,
                          radius1=0.19, radius2=0.15, depth=h,
                          matrix=Matrix.Translation((0, 0, h / 2)))
    bm.to_mesh(me); bm.free()
    ca = me.color_attributes.new(name='Col', type='BYTE_COLOR', domain='CORNER')
    for d in ca.data:
        d.color_srgb = hx('C64B2C')
    ob = bpy.data.objects.new('HumanRef', me)
    ob.data.materials.append(MAT)
    ob.location = loc
    bpy.context.collection.objects.link(ob)
    return ob


HUM = human((0, 0, 0))

sc = bpy.context.scene
try:
    sc.render.engine = 'BLENDER_EEVEE_NEXT'
except TypeError:
    sc.render.engine = 'BLENDER_EEVEE'
sc.view_settings.view_transform = 'Standard'
sc.view_settings.look = 'None'
sc.render.image_settings.file_format = 'PNG'
try:
    sc.eevee.taa_render_samples = 64
except AttributeError:
    pass

world = bpy.data.worlds.new('W'); sc.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.55, 0.62, 0.72, 1.0)
world.node_tree.nodes['Background'].inputs[1].default_value = 0.65

for rot, en, ang in [((52, 0, 38), 3.2, 6.0), ((62, 0, -135), 1.0, 25.0)]:
    ld = bpy.data.lights.new('L', 'SUN'); ld.energy = en; ld.angle = math.radians(ang)
    lo = bpy.data.objects.new('L', ld)
    lo.rotation_euler = tuple(math.radians(a) for a in rot)
    bpy.context.collection.objects.link(lo)

cam_d = bpy.data.cameras.new('Cam')
CAM = bpy.data.objects.new('Cam', cam_d)
bpy.context.collection.objects.link(CAM)
sc.camera = CAM


def shot(name, loc, target, res=(1500, 900), fov=None, ortho=None):
    CAM.location = Vector(loc)
    CAM.rotation_euler = (Vector(target) - CAM.location).to_track_quat('-Z', 'Y').to_euler()
    if ortho:
        cam_d.type = 'ORTHO'; cam_d.ortho_scale = ortho
    else:
        cam_d.type = 'PERSP'; cam_d.sensor_fit = 'HORIZONTAL'
        cam_d.angle_x = math.radians(fov if fov else 39.6)
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = REN + name + '.png'
    bpy.ops.render.render(write_still=True)
    print('  RENDER %-42s exists=%s' % (name + '.png', os.path.exists(sc.render.filepath)))


def vis(names):
    keep = set(names)
    for ob in bpy.data.objects:
        if ob.type == 'MESH':
            ob.hide_render = ob.name not in keep


PITCH = math.radians(60.0)
FWD = Vector((0.0, math.cos(PITCH), -math.sin(PITCH)))

print('=== РЕНДЕРЫ ПЕРЕКРАСКИ ===')

# 1. Линейка четырёх вариантов сбоку
for i, ob in enumerate(LINEUP):
    ob.location = (-2.7 + i * 1.8, 0, 0)
HUM.location = (-4.9, 0, 0)
vis(['Ground', 'HumanRef'] + [o.name for o in LINEUP])
shot('01_lineup_side', (0.0, -13.5, 1.5), (0.0, 0.0, 1.0), res=(1600, 800), fov=30)

# 2. Та же линейка под наклоном игровой камеры (крупно)
tgt = Vector((0.0, 0.0, 1.0))
shot('02_lineup_gamecam_angle', tuple(tgt - FWD * 13.0), tuple(tgt), res=(1600, 800), fov=30)

# 3. Строго сверху
shot('03_lineup_topdown', (0.0, 0.0, 20.0), (0.0, 0.0, 1.0), res=(1600, 700), ortho=9.5)

# 4. Крупный план ствола: исходный vs берёза
vis(['Ground', 'A_original', 'C_birch'])
ORIG.location = (-0.7, 0, 0); C_LIGHT.location = (0.7, 0, 0)
shot('04_trunk_closeup', (0.0, -4.2, 0.75), (0.0, 0.0, 0.62), res=(1200, 900), fov=28)

# 5. РОЩА в реальном игровом масштабе: берёзы вперемешку с исходными деревьями
for ob in LINEUP:
    ob.location = (0, 0, -50)
GROVE = []
plan = [(-3.4, 2.2, 35, 1.00, C_LIGHT), (2.8, 4.4, 150, 0.94, C_LIGHT),
        (5.6, -1.0, 275, 1.06, C_LIGHT), (-6.2, -2.8, 90, 0.97, C_LIGHT),
        (0.6, 8.0, 205, 1.02, C_LIGHT), (-1.8, -4.6, 10, 1.00, ORIG),
        (7.4, 4.8, 125, 1.05, ORIG), (-8.2, 4.0, 245, 0.95, ORIG),
        (3.6, -5.2, 60, 1.01, ORIG), (-4.4, 7.4, 300, 0.98, C_LIGHT)]
for i, (x, y, rz, s, src) in enumerate(plan):
    o = bpy.data.objects.new('G%02d' % i, src.data)
    o.location = (x, y, 0); o.rotation_euler = (0, 0, math.radians(rz))
    o.scale = (s, s, s)
    bpy.context.collection.objects.link(o)
    GROVE.append(o.name)
HUM.location = (0.0, -1.4, 0)
vis(['Ground', 'HumanRef'] + GROVE)
tgt = Vector((0.0, 0.5, 0.0))
shot('05_grove_gameplay_scale', tuple(tgt - FWD * 30.0), tuple(tgt), res=(1280, 720), fov=40.0)

# 6. Та же роща вдвое ближе — видно ли ствол вообще
shot('06_grove_closer', tuple(tgt - FWD * 15.0), tuple(tgt), res=(1280, 720), fov=40.0)

print('DONE')
