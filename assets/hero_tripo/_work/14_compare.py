"""Before/after sheet: previous pose sheet (top) over the current one (bottom)."""
import bpy
import numpy as np
R = 'E:/game-dev-team/assets/hero_tripo/renders/'
def load(p):
    im = bpy.data.images.load(p); w, h = im.size
    a = np.array(im.pixels[:], dtype=np.float32).reshape(h, w, 4); bpy.data.images.remove(im); return a
new, old = load(R + 'hero_pose_sheet.png'), load(R + 'hero_pose_sheet_prev.png')
gap = np.ones((12, new.shape[1], 4), dtype=np.float32)
a = np.concatenate([new, gap, old], axis=0)       # pixel rows go bottom-up: old ends on top
im = bpy.data.images.new('cmp', a.shape[1], a.shape[0], alpha=True); im.pixels = a.ravel()
im.filepath_raw = R + 'hero_pose_compare.png'; im.file_format = 'PNG'; im.save()
print('COMPARE', im.filepath_raw, a.shape[1], a.shape[0])
