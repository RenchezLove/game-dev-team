import sys, json, numpy as np
from PIL import Image, ImageFilter
N = 2048
pts = json.load(open('points.json'))          # [[gx,gy,SX,SY],...]
P = np.array(pts, float)
src = P[:, :2]; dst = P[:, 2:]
# global affine dst->src (least squares), used to anchor the far frame
A = np.c_[dst, np.ones(len(dst))]
aff, *_ = np.linalg.lstsq(A, src, rcond=None)
frame = np.array([[x, y] for x in (-300, 1024, 2348) for y in (-300, 1024, 2348) if not (x == 1024 and y == 1024)], float)
dst_all = np.vstack([dst, frame]); src_all = np.vstack([src, np.c_[frame, np.ones(len(frame))] @ aff])
lam = float(sys.argv[1]) if len(sys.argv) > 1 else 200.0
def U(r2): return np.where(r2 > 0, r2 * np.log(np.maximum(r2, 1e-12)), 0.0)
n = len(dst_all)
K = U(((dst_all[:, None, :] - dst_all[None, :, :]) ** 2).sum(-1)) + lam * np.eye(n)
Pm = np.c_[np.ones(n), dst_all]
L = np.zeros((n + 3, n + 3)); L[:n, :n] = K; L[:n, n:] = Pm; L[n:, :n] = Pm.T
rhs = np.zeros((n + 3, 2)); rhs[:n] = src_all
W = np.linalg.solve(L, rhs)
def tps(q):
    Kq = U(((q[:, None, :] - dst_all[None, :, :]) ** 2).sum(-1))
    return Kq @ W[:n] + np.c_[np.ones(len(q)), q] @ W[n:]
res = tps(dst) - src
print('control residual px (gpt scale): max %.1f mean %.1f' % (np.abs(res).max(), np.abs(res).mean()))
print('affine-only residual max %.1f' % np.abs(A @ aff - src).max())
G = 129
gx = np.linspace(0, N - 1, G); gy = np.linspace(0, N - 1, G)
qq = np.array([[x, y] for y in gy for x in gx])
m = tps(qq).reshape(G, G, 2)
mx = np.asarray(Image.fromarray(m[:, :, 0].astype(np.float32), 'F').resize((N, N), Image.BILINEAR))
my = np.asarray(Image.fromarray(m[:, :, 1].astype(np.float32), 'F').resize((N, N), Image.BILINEAR))
img = np.asarray(Image.open('gpt.png').convert('RGB')).astype(np.float32)
H, Wd = img.shape[:2]
inside = (mx >= 0) & (mx <= Wd - 1) & (my >= 0) & (my <= H - 1)
cx = np.clip(mx, 0, Wd - 1.001); cy = np.clip(my, 0, H - 1.001)
x0 = cx.astype(int); y0 = cy.astype(int); fx = (cx - x0)[..., None]; fy = (cy - y0)[..., None]
out = (img[y0, x0] * (1 - fx) * (1 - fy) + img[y0, x0 + 1] * fx * (1 - fy) + img[y0 + 1, x0] * (1 - fx) * fy + img[y0 + 1, x0 + 1] * fx * fy)
o = Image.fromarray(out.clip(0, 255).astype(np.uint8))
# margins outside the source picture: smeared edge colours blurred into plain fog
dist = np.maximum.reduce([-mx, mx - (Wd - 1), -my, my - (H - 1), np.zeros_like(mx)])
t = np.clip(dist / 40.0, 0, 1)[..., None]
blur = np.asarray(o.filter(ImageFilter.GaussianBlur(40))).astype(np.float32)
fog = np.array([150, 152, 156], np.float32)
t2 = np.clip(dist / 220.0, 0, 1)[..., None]
marg = blur * (1 - t2) + fog * t2
fin = np.asarray(o).astype(np.float32) * (1 - t) + marg * t
Image.fromarray(fin.clip(0, 255).astype(np.uint8)).save('warped.png')
print('inside fraction %.3f' % inside.mean())
# check overlay: real roads from the level capture in cyan
raw = np.asarray(Image.open('raw.png').convert('RGB')).astype(np.float32)
mask = ((raw[:, :, 0] - raw[:, :, 2]) > 115)
mi = Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(9)).filter(ImageFilter.MaxFilter(5))
mk = (np.asarray(mi) > 127)
edge = np.asarray(mi.filter(ImageFilter.FIND_EDGES)) > 40
ov = fin.copy(); ov[edge] = [0, 255, 255]
mk_pts = json.load(open('marks.json'))
ovi = Image.fromarray(ov.clip(0, 255).astype(np.uint8))
from PIL import ImageDraw
d = ImageDraw.Draw(ovi)
for X, Y in mk_pts: d.ellipse([X - 7, Y - 7, X + 7, Y + 7], outline=(255, 0, 255), width=3)
ovi.save('check_full.png')
ovi.crop((500, 350, 1700, 1150)).save('check_a.png')
ovi.crop((500, 1000, 1700, 1900)).save('check_b.png')
# largest axis-aligned rectangle (found as common full rows/cols) fully covered by the source picture
rows = np.where(inside.mean(1) > 0.5)[0]; cols = np.where(inside.mean(0) > 0.5)[0]
x0c, x1c, y0c, y1c = cols.min(), cols.max(), rows.min(), rows.max()
while not inside[y0c:y1c + 1, x0c:x1c + 1].all():
    x0c += 1; x1c -= 1; y0c += 1; y1c -= 1
k = 46875.0 / 2048.0
print('CROP px', x0c, y0c, x1c, y1c, 'size', x1c - x0c + 1, y1c - y0c + 1)
print('TopLeft world X=%.1f Y=%.1f' % (28937.5 - x0c * k, 19067.5 - y0c * k))
print('BottomRight world X=%.1f Y=%.1f' % (28937.5 - (x1c + 1) * k, 19067.5 - (y1c + 1) * k))
Image.fromarray(np.asarray(o)[y0c:y1c + 1, x0c:x1c + 1]).save('T_PdaMap_fit.png')
Image.fromarray(np.asarray(o)[y0c:y1c + 1, x0c:x1c + 1]).resize((800, int(800 * (y1c - y0c + 1) / (x1c - x0c + 1)))).save('fit_small.png')
