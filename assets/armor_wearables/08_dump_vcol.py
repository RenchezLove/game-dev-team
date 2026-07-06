"""Proof-dump: dominant vertex-color values inside exported FBX files.
Import stores file floats verbatim as bytes, so the hexes below are exactly
what sits in each FBX. After the colors_type='LINEAR' fix these must be the
LINEAR (dark) values, not the palette hexes.
Run: blender.exe -b --factory-startup --python 08_dump_vcol.py
"""
import bpy, sys
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W


def dump(path, label):
    W.fresh()
    meshes, arms, rest = W.import_fbx(path)
    me = meshes[0].data
    ca = me.color_attributes[0]
    cnt = {}
    for i in range(len(ca.data)):
        c = ca.data[i].color_srgb
        hx = '#%02X%02X%02X' % (round(c[0] * 255), round(c[1] * 255), round(c[2] * 255))
        cnt[hx] = cnt.get(hx, 0) + 1
    top = sorted(cnt.items(), key=lambda kv: -kv[1])[:5]
    print('DUMP %-22s top hex in file: %s' % (label, top))


dump(W.WORKDIR + 'SK_Armor_T1_Torso.fbx', 'SK_Armor_T1_Torso')
dump(W.WORKDIR + 'SK_Armor_T2_Torso.fbx', 'SK_Armor_T2_Torso')
