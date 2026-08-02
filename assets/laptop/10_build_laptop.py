"""Build SM_Laptop - half-open laptop: base with keyboard panel + touchpad,
lid with dark screen opened 110 deg (leans back past vertical), hinge at the
back (-Y), front toward +Y per prop convention. Spec game-lead 2026-08-02.
GDD palette: shell Cold Steel, keyboard/screen Panel Dark, touchpad Concrete
Grey. Budget 40-120 tris.

Headless:
  E:/Programs/Blender/blender.exe -b --factory-startup --python 10_build_laptop.py
"""
import bpy, math, sys
import bmesh
from mathutils import Matrix, Vector

sys.path.append('E:/game-dev-team/assets')
import propcommon as P

OUT = 'E:/game-dev-team/assets/laptop/'

HEX = dict(ColdSteel='#5A6470', PanelDark='#1B2018', Concrete='#6E6A60')
PT_SHELL, PT_DARK, PT_PAD = range(3)

OPEN_DEG = 110.0
HINGE_Y, HINGE_Z = -0.120, 0.016


def build():
    bm = bmesh.new()
    # base 34 x 24 x 1.6 cm
    P.box(bm, (-0.170, -0.120, 0.000), (0.170, 0.120, 0.016), PT_SHELL)
    # keyboard panel sunk 0.5 mm into the deck (no coplanar faces)
    P.box(bm, (-0.150, -0.105, 0.0155), (0.150, 0.015, 0.019), PT_DARK)
    # touchpad
    P.box(bm, (-0.045, 0.045, 0.0155), (0.045, 0.100, 0.0185), PT_PAD)
    # lid + screen built CLOSED (lying on the base), then swung open
    # around the hinge line y=-0.120 z=0.016
    lid_vs, _ = P.box(bm, (-0.170, -0.120, 0.016), (0.170, 0.115, 0.028),
                      PT_SHELL)
    # screen sits on the lid face that looks AT the keyboard when closed
    # (that face turns toward the viewer once opened); sunk 0.5 mm in
    scr_vs, _ = P.box(bm, (-0.150, -0.100, 0.0135), (0.150, 0.090, 0.0165),
                      PT_DARK)
    R = (Matrix.Translation((0, HINGE_Y, HINGE_Z))
         @ Matrix.Rotation(math.radians(OPEN_DEG), 4, 'X')
         @ Matrix.Translation((0, -HINGE_Y, -HINGE_Z)))
    for v in lid_vs + scr_vs:
        v.co = R @ v.co
    return bm


def paint(me):
    P.paint_parts(me, {PT_SHELL: HEX['ColdSteel'],
                       PT_DARK: HEX['PanelDark'],
                       PT_PAD: HEX['Concrete']})


def main():
    P.fresh()
    ob = P.finalize(build(), 'SM_Laptop', paint, 'M_Laptop')
    bpy.ops.wm.save_as_mainfile(filepath=OUT + 'laptop.blend')
    print('SAVED', OUT + 'laptop.blend')
    P.export_one(ob, OUT + 'SM_Laptop.fbx')
    P.verify(OUT + 'SM_Laptop.fbx', 'SM_Laptop',
             set(HEX.values()), (40, 120))
    print('DONE')


main()
