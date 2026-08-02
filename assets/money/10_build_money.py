"""Build SM_Money - banknote stack with a kraft-paper band, loot/inventory
item. Proposal approved by game-lead 2026-08-02 from the icon render; his one
note applied here: the loose bills on top are pulled in so the stack reads
tidy (offsets/yaws reduced vs the first render).

Colors are custom muted tones in palette style (approved with the render):
paper edges #D6CFBC, worn bill green #7C8A66 (Faded Sage family), kraft band
#C4A05F (XP Gold family). Budget: tiny pickup, 30-100 tris.

Headless:
  E:/Programs/Blender/blender.exe -b --factory-startup --python 10_build_money.py
"""
import bpy, bmesh, math, sys
from mathutils import Vector, Matrix

sys.path.append('E:/game-dev-team/assets')
import propcommon as P

OUT = 'E:/game-dev-team/assets/money/'

HEX = dict(Paper='#D6CFBC', Bill='#7C8A66', Band='#C4A05F')
PT_STACK, PT_BAND, PT_BILL = range(3)


def build():
    bm = bmesh.new()
    boxes = [   # (size xyz, center xyz, yaw_deg, part)
        # 0.5 mm air gaps between the parts: no coplanar faces, no z-fight
        ((0.156, 0.067, 0.040), (0, 0, 0.020), 0, PT_STACK),
        ((0.034, 0.071, 0.044), (0, 0, 0.022), 0, PT_BAND),
        ((0.156, 0.067, 0.004), (0.0015, 0.001, 0.0465), 5, PT_BILL),
        ((0.150, 0.064, 0.004), (-0.002, -0.001, 0.0510), -4, PT_BILL),
    ]
    for size, center, yaw, part in boxes:
        M = (Matrix.Translation(Vector(center))
             @ Matrix.Rotation(math.radians(yaw), 4, 'Z')
             @ Matrix.Diagonal(Vector(size).to_4d()))
        ret = bmesh.ops.create_cube(bm, size=1.0, matrix=M)
        for v in ret['verts']:
            for f in v.link_faces:
                f.material_index = part
    return bm


def paint(me):
    def bill_or_paper(p, me):
        return HEX['Bill'] if p.normal.z > 0.5 else HEX['Paper']
    P.paint_parts(me, {PT_STACK: bill_or_paper,
                       PT_BAND: HEX['Band'],
                       PT_BILL: bill_or_paper})


def main():
    P.fresh()
    ob = P.finalize(build(), 'SM_Money', paint, 'M_Money')
    bpy.ops.wm.save_as_mainfile(filepath=OUT + 'money.blend')
    print('SAVED', OUT + 'money.blend')
    P.export_one(ob, OUT + 'SM_Money.fbx')
    P.verify(OUT + 'SM_Money.fbx', 'SM_Money',
             set(HEX.values()), (30, 100))
    print('DONE')


main()
