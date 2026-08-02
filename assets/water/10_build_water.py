"""Build SM_WaterBottle - 0.5 l plastic drinking water bottle with a cap and
a label band. Spec from game-lead 2026-08-02. Palette has no light blue, so
the body is a custom light blue-grey #8FA6B5 (lightened Cold Steel family -
trader precedent for near-palette tones); label Bone Ink, cap Cold Steel.
Budget 100-260 tris (10-sided lathe).

Headless:
  E:/Programs/Blender/blender.exe -b --factory-startup --python 10_build_water.py
"""
import bpy, sys
import bmesh

sys.path.append('E:/game-dev-team/assets')
import propcommon as P

OUT = 'E:/game-dev-team/assets/water/'

HEX = dict(Plastic='#8FA6B5', BoneInk='#E7E4D8', ColdSteel='#5A6470')
PT_BODY, PT_LABEL, PT_CAP = range(3)


def build():
    bm = bmesh.new()
    profile = [(0.0, 0.000), (0.030, 0.000),          # base
               (0.031, 0.012),                         # base bulge
               (0.031, 0.070), (0.031, 0.130),         # label zone
               (0.031, 0.150),                         # upper body
               (0.024, 0.172), (0.013, 0.192),         # shoulder taper
               (0.013, 0.203),                         # neck
               (0.0155, 0.203), (0.0155, 0.222),       # cap (wider than neck)
               (0.0, 0.222)]                           # cap top
    spans = (PT_BODY, PT_BODY, PT_BODY, PT_LABEL, PT_BODY,
             PT_BODY, PT_BODY, PT_BODY, PT_CAP, PT_CAP, PT_CAP)
    P.lathe_spans(bm, profile, 10, spans)
    return bm


def paint(me):
    P.paint_parts(me, {PT_BODY: HEX['Plastic'],
                       PT_LABEL: HEX['BoneInk'],
                       PT_CAP: HEX['ColdSteel']})


def main():
    P.fresh()
    ob = P.finalize(build(), 'SM_WaterBottle', paint, 'M_WaterBottle')
    bpy.ops.wm.save_as_mainfile(filepath=OUT + 'water.blend')
    print('SAVED', OUT + 'water.blend')
    P.export_one(ob, OUT + 'SM_WaterBottle.fbx')
    P.verify(OUT + 'SM_WaterBottle.fbx', 'SM_WaterBottle',
             set(HEX.values()), (100, 260))
    print('DONE')


main()
