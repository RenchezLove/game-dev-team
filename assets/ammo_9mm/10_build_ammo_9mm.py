"""Build SM_Ammo9mm - cardboard 50-round 9x19 box with a red side stripe and
three loose cartridges lying in front (+Y). Spec from game-lead 2026-08-02.
GDD palette: cardboard Dry Earth, stripe Rust Alarm, brass casings XP Gold,
bullet tips Timber. Cartridge = true 9x19 size (30 mm), 8-sided.
Budget 100-260 tris.

Headless:
  E:/Programs/Blender/blender.exe -b --factory-startup --python 10_build_ammo_9mm.py
"""
import bpy, math, sys
import bmesh
from mathutils import Matrix, Vector

sys.path.append('E:/game-dev-team/assets')
import propcommon as P

OUT = 'E:/game-dev-team/assets/ammo_9mm/'

HEX = dict(DryEarth='#7D6A4E', RustAlarm='#C64B2C',
           Brass='#CAA54E', Timber='#8A5A32')
PT_BOX, PT_STRIPE, PT_CASE, PT_TIP = range(4)


def cartridge(bm, center, yaw_deg):
    """9x19: casing 19 mm (brass) + ogive tip 11 mm (copper-brown), axis X,
    lying on the ground (z = radius). Built via lathe along Z then laid down
    the same way the hide roll does: (x,y,z) -> (z,y,-x)."""
    r = 0.005
    profile = [(0.0, -0.0148), (r, -0.0148), (r, 0.0042),      # casing
               (0.0042, 0.0075), (0.0016, 0.0148),             # ogive rings
               (0.0, 0.0148)]                                  # tip pole
    spans = (PT_CASE, PT_CASE, PT_TIP, PT_TIP, PT_TIP)
    sub = bmesh.new()
    P.lathe_spans(sub, profile, 8, spans, ang0=math.radians(22.5))
    M = (Matrix.Translation(Vector(center))
         @ Matrix.Rotation(math.radians(yaw_deg), 4, 'Z'))
    for v in sub.verts:
        x, y, z = v.co
        v.co = M @ Vector((z, y, -x + r))   # lay down, rest on z=0
    me = bpy.data.meshes.new('_tmp')
    sub.to_mesh(me)
    sub.free()
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)


def build():
    bm = bmesh.new()
    # cardboard box 5.8 x 4.3 x 3.2 cm, shifted back (-Y)
    P.box(bm, (-0.029, -0.0295, 0.000), (0.029, 0.0135, 0.032), PT_BOX)
    # printed stripe wraps the sides horizontally
    P.box(bm, (-0.0305, -0.031, 0.009), (0.0305, 0.015, 0.023), PT_STRIPE)
    # three cartridges lying in front of the box side by side (axis X,
    # so they spread along Y toward the viewer; 12 mm pitch > 10 mm dia)
    cartridge(bm, (-0.004, 0.026, 0), 5)
    cartridge(bm, (0.003, 0.038, 0), -3)
    cartridge(bm, (-0.002, 0.050, 0), 8)
    return bm


def paint(me):
    P.paint_parts(me, {PT_BOX: HEX['DryEarth'],
                       PT_STRIPE: HEX['RustAlarm'],
                       PT_CASE: HEX['Brass'],
                       PT_TIP: HEX['Timber']})


def main():
    P.fresh()
    ob = P.finalize(build(), 'SM_Ammo9mm', paint, 'M_Ammo9mm')
    bpy.ops.wm.save_as_mainfile(filepath=OUT + 'ammo_9mm.blend')
    print('SAVED', OUT + 'ammo_9mm.blend')
    P.export_one(ob, OUT + 'SM_Ammo9mm.fbx')
    P.verify(OUT + 'SM_Ammo9mm.fbx', 'SM_Ammo9mm',
             set(HEX.values()), (100, 260))
    print('DONE')


main()
