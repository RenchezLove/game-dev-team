"""Build SM_CannedFood - tinned meat can: 12-sided cylinder, metal rims and
lids, paper label band with a dark-red front patch (label art hint, faces
toward +Y). Spec from game-lead 2026-08-02. GDD palette: metal Concrete Grey,
label Bone Ink, patch Muted Blood. Budget 60-160 tris.

Headless:
  E:/Programs/Blender/blender.exe -b --factory-startup --python 10_build_canned_food.py
"""
import bpy, sys
import bmesh

sys.path.append('E:/game-dev-team/assets')
import propcommon as P

OUT = 'E:/game-dev-team/assets/canned_food/'

HEX = dict(Concrete='#6E6A60', BoneInk='#E7E4D8', MutedBlood='#8A2F2A')
PT_METAL, PT_LABEL = range(2)

R = 0.0375   # can radius, height 10.8 cm (standard 338 ml tin)


def build():
    bm = bmesh.new()
    profile = [(0.0, 0.000), (R, 0.000), (R, 0.012),
               (R, 0.096), (R, 0.108), (0.0, 0.108)]
    spans = (PT_METAL, PT_METAL, PT_LABEL, PT_METAL, PT_METAL)
    P.lathe_spans(bm, profile, 12, spans)
    return bm


def paint(me):
    def label(p, me):
        c = p.center
        # front patch: only the two label columns facing +Y (narrow art
        # hint, the label stays mostly paper-beige)
        if c.y > R * 0.55 and abs(c.x) < R * 0.5:
            return HEX['MutedBlood']
        return HEX['BoneInk']
    P.paint_parts(me, {PT_METAL: HEX['Concrete'], PT_LABEL: label})


def main():
    P.fresh()
    ob = P.finalize(build(), 'SM_CannedFood', paint, 'M_CannedFood')
    bpy.ops.wm.save_as_mainfile(filepath=OUT + 'canned_food.blend')
    print('SAVED', OUT + 'canned_food.blend')
    P.export_one(ob, OUT + 'SM_CannedFood.fbx')
    P.verify(OUT + 'SM_CannedFood.fbx', 'SM_CannedFood',
             set(HEX.values()), (60, 160))
    print('DONE')


main()
