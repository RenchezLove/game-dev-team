"""Check sheet: the sample icon and the new ones side by side on the dark tile of the bag, three times enlarged, and at the size of a fingernail.
Run: blender.exe -b --factory-startup --python icon_sheet.py -- <out png> <icon png> [...]
"""
import bpy, sys
import numpy as np
a = sys.argv[sys.argv.index('--') + 1:]
out, paths = a[0], a[1:]
TILE = np.array([0.085, 0.09, 0.10]); Z = 3; S = 256; G = 8
def load(p):
    im = bpy.data.images.load(p, check_existing=False); im.alpha_mode = 'CHANNEL_PACKED'
    px = np.array(im.pixels[:], dtype=np.float32).reshape(im.size[1], im.size[0], 4)
    assert px.shape[0] == S and px.shape[1] == S, (p, px.shape)
    return px
n = len(paths); W = n * (S * Z + G) + G; H = S * Z + 64 + 3 * G
sheet = np.zeros((H, W, 3), np.float32) + 0.02
for i, p in enumerate(paths):
    px = load(p); c = px[..., :3] * px[..., 3:] + TILE * (1 - px[..., 3:])
    big = np.repeat(np.repeat(c, Z, 0), Z, 1)
    x0 = G + i * (S * Z + G)
    sheet[64 + 2 * G:64 + 2 * G + S * Z, x0:x0 + S * Z] = big
    sheet[G:G + 64, x0:x0 + 64] = c.reshape(64, 4, 64, 4, 3).mean((1, 3))
res = bpy.data.images.new('sheet', W, H, alpha=False)
res.pixels.foreach_set(np.concatenate([sheet, np.ones((H, W, 1), np.float32)], 2).ravel())
res.filepath_raw = out; res.file_format = 'PNG'; res.save()
print('SHEET', out, W, H)
