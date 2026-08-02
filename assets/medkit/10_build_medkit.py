"""Build SM_Medkit - compact first-aid box: bottom case + slightly wider lid,
steel latch on the front (+Y), red cross of two raised bars on the lid top.
Spec from game-lead 2026-08-02. GDD palette: box Bone Ink, latch Cold Steel,
cross Rust Alarm. Budget: small pickup, 40-120 tris.

Headless:
  E:/Programs/Blender/blender.exe -b --factory-startup --python 10_build_medkit.py
"""
import bpy, sys
import bmesh

sys.path.append('E:/game-dev-team/assets')
import propcommon as P

OUT = 'E:/game-dev-team/assets/medkit/'

HEX = dict(BoneInk='#E7E4D8', ColdSteel='#5A6470', RustAlarm='#C64B2C')
PT_BODY, PT_LATCH, PT_CROSS = range(3)


def build():
    bm = bmesh.new()
    # bottom case 25 x 18 x 6 cm, lid overhangs 3 mm all around
    P.box(bm, (-0.125, -0.090, 0.000), (0.125, 0.090, 0.060), PT_BODY)
    P.box(bm, (-0.128, -0.093, 0.060), (0.128, 0.093, 0.110), PT_BODY)
    # latch straddles the seam on the front (+Y)
    P.box(bm, (-0.018, 0.093, 0.045), (0.018, 0.105, 0.078), PT_LATCH)
    # cross: two bars on the lid top; different heights so the overlap
    # region has no coplanar fighting faces
    P.box(bm, (-0.048, -0.015, 0.110), (0.048, 0.015, 0.113), PT_CROSS)
    P.box(bm, (-0.015, -0.048, 0.110), (0.015, 0.048, 0.114), PT_CROSS)
    return bm


def paint(me):
    P.paint_parts(me, {PT_BODY: HEX['BoneInk'],
                       PT_LATCH: HEX['ColdSteel'],
                       PT_CROSS: HEX['RustAlarm']})


def main():
    P.fresh()
    ob = P.finalize(build(), 'SM_Medkit', paint, 'M_Medkit')
    bpy.ops.wm.save_as_mainfile(filepath=OUT + 'medkit.blend')
    print('SAVED', OUT + 'medkit.blend')
    P.export_one(ob, OUT + 'SM_Medkit.fbx')
    P.verify(OUT + 'SM_Medkit.fbx', 'SM_Medkit',
             set(HEX.values()), (40, 120))
    print('DONE')


main()
