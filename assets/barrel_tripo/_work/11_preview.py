"""Paint-variant sheet for SM_TripoBarrel. Material as in UE:
base = lerp(tex.rgb, tex.rgb * Paint, tex.a) (tex sRGB, Paint linear).
Columns: original bake | faded blue | army green | red | yellow | paint mask (white = paint).
Rows: 3/4 from above (game-like) | side.
Run: blender.exe -b _work/barrel_work.blend --factory-startup --python 11_preview.py
"""
import bpy, sys, os
import numpy as np
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W

OUT = 'E:/game-dev-team/assets/barrel_tripo/renders/'
os.makedirs(OUT, exist_ok=True)
RAW = 'E:/game-dev-team/assets/barrel_tripo/_work/_bake_raw.png'
PAINTS = [('blue', '#6F8CA6'), ('green', '#4A5A36'), ('red', '#9E2B22'), ('yellow', '#D9A521')]
VIEWS = [('top34', (0.55, -1.0, 1.35)), ('side', (0.3, -1.0, 0.12))]


def s2l(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lin(hx):
    return tuple(s2l(int(hx[i:i + 2], 16) / 255) for i in (1, 3, 5)) + (1.0,)


ob = bpy.data.objects['SM_TripoBarrel']
mat = ob.data.materials[0]
nt = mat.node_tree
tex = [n for n in nt.nodes if n.type == 'TEX_IMAGE'][0]
bs = nt.nodes['Principled BSDF']
paint = nt.nodes.new('ShaderNodeRGB')
mul = nt.nodes.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'
mul.inputs['Factor'].default_value = 1.0
nt.links.new(tex.outputs['Color'], mul.inputs['A'])
nt.links.new(paint.outputs['Color'], mul.inputs['B'])
lerp = nt.nodes.new('ShaderNodeMix'); lerp.data_type = 'RGBA'
nt.links.new(tex.outputs['Alpha'], lerp.inputs['Factor'])
nt.links.new(tex.outputs['Color'], lerp.inputs['A'])
nt.links.new(mul.outputs['Result'], lerp.inputs['B'])
raw = nt.nodes.new('ShaderNodeTexImage')
raw.image = bpy.data.images.load(RAW)
ob.data.uv_layers.active_index = 0

sc, cam, suns = W.setup_render(res=420)
sc.render.film_transparent = False


def base(src):
    nt.links.new(src, bs.inputs['Base Color'])


tiles = {}
for vn, vd in VIEWS:
    row = []
    base(raw.outputs['Color'])
    W.frame_and_shoot([ob], vd, OUT + '_%s_orig.png' % vn, margin=1.15, suns=suns); row.append('orig')
    base(lerp.outputs['Result'])
    for pn, hx in PAINTS:
        paint.outputs['Color'].default_value = lin(hx)
        W.frame_and_shoot([ob], vd, OUT + '_%s_%s.png' % (vn, pn), margin=1.15, suns=suns); row.append(pn)
    base(tex.outputs['Alpha'])
    W.frame_and_shoot([ob], vd, OUT + '_%s_mask.png' % vn, margin=1.15, suns=suns); row.append('mask')
    tiles[vn] = row


def load(p):
    im = bpy.data.images.load(p)
    w, h = im.size
    a = np.array(im.pixels[:], dtype=np.float32).reshape(h, w, 4)
    bpy.data.images.remove(im)
    a[:, :2, :3] = 1.0; a[:2, :, :3] = 1.0
    return a


rows = [np.concatenate([load(OUT + '_%s_%s.png' % (vn, t)) for t in tiles[vn]], axis=1)
        for vn, _ in reversed(VIEWS)]            # image rows go bottom-up
sh = np.concatenate(rows, axis=0)
h, w, _ = sh.shape
im = bpy.data.images.new('sheet', w, h, alpha=True)
im.pixels = sh.ravel()
im.filepath_raw = OUT + 'barrel_paint_variants.png'
im.file_format = 'PNG'
im.save()
for f in os.listdir(OUT):
    if f.startswith('_'):
        os.remove(OUT + f)
print('SHEET', OUT + 'barrel_paint_variants.png', w, h)
