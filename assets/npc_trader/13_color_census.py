"""Color census of the exported trader FBX: re-import each file and count faces
per stored vcol byte-hex (bytes == palette sRGB hexes by convention). Proof that
the palette actually landed in the files (lesson: judge colors by DATA, not by
render previews). NB: Blender re-import is NOT a UE truth source for on-screen
color (07-09 lesson) — this only checks the stored bytes.
Run: blender.exe -b --factory-startup --python 13_color_census.py
"""
import bpy, sys
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W

HERE = 'E:/game-dev-team/assets/npc_trader/'
PALETTE = {
    '#C89A7A': 'SKIN', '#4A3826': 'STUBBLE/HAIR', '#2B2823': 'EYES|BOOTS',
    '#494C52': 'BANDANA', '#33302B': 'SWEATER', '#5A6470': 'VEST(ColdSteel)',
    '#4D5661': 'POCKET', '#E0A32E': 'AMBER(AmberLoot)', '#6E6A60': 'PANTS(Concrete)',
    '#605C52': 'PANTS_PKT', '#1D1A17': 'SOLE',
}


def s2l(u):
    u /= 255.0
    return (u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4) * 255.0


# The FBX stores LINEAR floats (colors_type='LINEAR', asset-contract §2.1), so a
# Blender re-import shows the palette converted sRGB->linear. Match against that.
LINEAR = {}
for hx, name in PALETTE.items():
    lin = '#%02X%02X%02X' % tuple(round(s2l(int(hx[i:i + 2], 16))) for i in (1, 3, 5))
    LINEAR[lin] = '%s (srgb %s)' % (name, hx)
for n in ('SK_Trader_Head', 'SK_Trader_Torso', 'SK_Trader_Legs'):
    W.fresh()
    meshes, arms, _ = W.import_fbx(HERE + n + '.fbx')
    me = meshes[0].data
    ca = me.color_attributes[0]
    cnt = {}
    for p in me.polygons:
        c = ca.data[p.loop_indices[0]].color_srgb
        hx = '#%02X%02X%02X' % (round(c[0] * 255), round(c[1] * 255), round(c[2] * 255))
        cnt[hx] = cnt.get(hx, 0) + 1
    print('\n%s vcol=%s/%s/%s faces_by_hex:' % (n, ca.name, ca.domain, ca.data_type))
    for hx, k in sorted(cnt.items(), key=lambda kv: -kv[1]):
        near = LINEAR.get(hx)
        if near is None:      # byte rounding: try +-1 per channel
            for lh, nm in LINEAR.items():
                if all(abs(int(hx[i:i + 2], 16) - int(lh[i:i + 2], 16)) <= 1 for i in (1, 3, 5)):
                    near = nm + ' [±1 byte]'
                    break
        print('  %s n=%4d %s' % (hx, k, near or '?? NOT IN PALETTE'))
print('\nCENSUS DONE')
