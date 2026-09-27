"""Before/after sheets of 15_skin_check renders: top row = before, bottom row = after.
Run: blender.exe -b --factory-startup --python 16_skin_sheet.py
"""
import bpy
import numpy as np

D = 'E:/game-dev-team/assets/hero_tripo/renders/skin/'
SHEETS = {
    'sheet_melee.png': ['melee10_backL', 'melee12_backL', 'melee12_backR', 'melee14_backL',
                        'melee14_backR', 'melee12_front'],
    'sheet_other.png': ['rest_backL', 'rest_front', 'run10_backL', 'run10_front', 'aim_backL', 'aim_front'],
}


def load(p):
    im = bpy.data.images.load(p)
    w, h = im.size
    a = np.array(im.pixels[:], dtype=np.float32).reshape(h, w, 4)
    bpy.data.images.remove(im)
    return a


for out, names in SHEETS.items():
    rows = []
    for tag in ('after', 'before'):          # numpy rows go bottom-up in Blender images
        tiles = []
        for n in names:
            t = load(D + '%s_%s.png' % (tag, n))
            t[:, :3, :3] = 1.0                  # thin white separators
            t[:3, :, :3] = 1.0
            tiles.append(t)
        rows.append(np.concatenate(tiles, axis=1))
    sh = np.concatenate(rows, axis=0)
    h, w, _ = sh.shape
    im = bpy.data.images.new('sheet', w, h, alpha=True)
    im.pixels = sh.ravel()
    im.filepath_raw = D + out
    im.file_format = 'PNG'
    im.save()
    print('SHEET', D + out, w, h)
