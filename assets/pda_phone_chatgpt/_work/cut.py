import numpy as np
from PIL import Image, ImageFilter, ImageDraw
im = Image.open('phone.png'); print(im.size, im.mode)
a = np.asarray(im.convert('RGBA')).astype(np.float32)
print('alpha min/max', a[..., 3].min(), a[..., 3].max())
rgb = a[..., :3]; H, W = rgb.shape[:2]
# background is smooth and blurred, the phone is textured: local detail separates them
g = Image.fromarray(rgb.mean(-1).astype(np.uint8))
detail = np.abs(np.asarray(g).astype(np.float32) - np.asarray(g.filter(ImageFilter.GaussianBlur(3))).astype(np.float32))
d = Image.fromarray((np.clip(detail * 20, 0, 255)).astype(np.uint8)).filter(ImageFilter.GaussianBlur(4))
solid = (np.asarray(d) > 22)
# flood the background from the picture border through non-textured pixels
m = Image.fromarray(np.where(solid, 255, 0).astype(np.uint8)).filter(ImageFilter.MaxFilter(9))
fl = m.copy()
for p in [(0, 0), (W - 1, 0), (0, H - 1), (W - 1, H - 1), (W // 2, 0), (W // 2, H - 1), (0, H // 2), (W - 1, H // 2)]:
    if fl.getpixel(p) == 0: ImageDraw.floodfill(fl, p, 128)
body = (np.asarray(fl) != 128)
bi = Image.fromarray((body * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(9)).filter(ImageFilter.GaussianBlur(1.2))
ys, xs = np.where(np.asarray(bi) > 127); print('BODY bbox', xs.min(), ys.min(), xs.max(), ys.max())
out = np.dstack([rgb, np.asarray(bi).astype(np.float32)]).astype(np.uint8)
Image.fromarray(out, 'RGBA').save('phone_cut.png')
chk = Image.new('RGB', (W, H), (255, 0, 255)); chk.paste(Image.fromarray(out, 'RGBA'), (0, 0), Image.fromarray(out, 'RGBA')); chk.save('phone_cut_check.png')
# screen: dark, blue-tinted, untextured region around the centre
r, gg, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
scr = (b > r + 4) & (rgb.max(-1) < 70)
si = Image.fromarray((scr * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(7)).filter(ImageFilter.MaxFilter(7))
fs = si.copy(); ImageDraw.floodfill(fs, (W // 2, H // 2), 128) if fs.getpixel((W // 2, H // 2)) == 255 else None
sm = np.asarray(fs) == 128
ys, xs = np.where(sm); print('SCREEN bbox', xs.min(), ys.min(), xs.max(), ys.max())
for frac in (0.5, 0.9, 0.98):
    cols = np.where(sm.mean(0) > frac * sm.mean(0).max())[0]; rows = np.where(sm.mean(1) > frac * sm.mean(1).max())[0]
    print('SCREEN core', frac, cols.min(), rows.min(), cols.max(), rows.max())
