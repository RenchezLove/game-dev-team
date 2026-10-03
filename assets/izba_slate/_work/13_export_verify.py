"""Export SM_IzbaSlate.fbx and verify by re-importing it next to the old SM_VillageHouse.fbx.
Run: blender.exe -b izba_work.blend --factory-startup --python 13_export_verify.py
"""
import bpy, bmesh, os, sys, math
import numpy as np
import addon_utils
sys.path.insert(0, 'E:/game-dev-team/assets')
import propcommon as PC

OUT = 'E:/game-dev-team/assets/izba_slate/'
FBX = OUT + 'SM_IzbaSlate.fbx'
TEX = OUT + 'T_IzbaSlate_D.png'
OLD = 'E:/ForGameLead(Materials)/demo-assets/SM_VillageHouse.fbx'

addon_utils.enable('io_scene_fbx')
PC.export_one(bpy.data.objects['SM_IzbaSlate'], FBX)
print('FILE %s %.1f KB' % (FBX, os.path.getsize(FBX) / 1024))


def load(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    addon_utils.enable('io_scene_fbx')
    bpy.ops.import_scene.fbx(filepath=path)
    bpy.context.view_layer.update()
    ms = [o for o in bpy.data.objects if o.type == 'MESH']
    return ms, [o.type for o in bpy.data.objects]


def stats(tag, ob):
    me = ob.data; mw = ob.matrix_world
    cs = np.array([mw @ v.co for v in me.vertices])
    tris = sum(len(p.vertices) - 2 for p in me.polygons)
    loc, rot, scl = mw.decompose()
    print('%s tris=%d verts=%d min=%s max=%s size=%s' % (tag, tris, len(me.vertices), cs.min(0).round(3), cs.max(0).round(3), (cs.max(0) - cs.min(0)).round(3)))
    print('%s origin=%s rot=%s scale=%s' % (tag, tuple(round(a, 4) for a in loc), tuple(round(a, 4) for a in rot.to_euler()), tuple(round(a, 4) for a in scl)))
    low = cs[cs[:, 2] < 0.4]; walls = cs[(cs[:, 2] > 0.6) & (cs[:, 2] < 2.2)]
    print('%s ground part (z<0.4): x %.3f..%.3f y %.3f..%.3f | walls (z 0.6..2.2): x %.3f..%.3f y %.3f..%.3f' % (
        tag, low[:, 0].min(), low[:, 0].max(), low[:, 1].min(), low[:, 1].max(),
        walls[:, 0].min(), walls[:, 0].max(), walls[:, 1].min(), walls[:, 1].max()))
    step = low[low[:, 1] < walls[:, 1].min() - 0.05]
    if len(step):
        print('%s porch/step in front of the -Y wall: x %.3f..%.3f (centre %.3f) y down to %.3f' % (tag, step[:, 0].min(), step[:, 0].max(), (step[:, 0].min() + step[:, 0].max()) / 2, step[:, 1].min()))
    back = low[low[:, 1] > walls[:, 1].max() + 0.05]
    print('%s anything on the ground behind the +Y wall: %d verts' % (tag, len(back)))
    bm = bmesh.new(); bm.from_mesh(me)
    print('%s open_edges=%d smooth_faces=%d signed_volume=%.2f' % (tag, sum(1 for e in bm.edges if len(e.link_faces) != 2), sum(1 for f in bm.faces if f.smooth), bm.calc_volume(signed=True)))
    bm.free()
    return cs


ms, types = load(OLD)
old = stats('OLD', ms[0])
# old ridge direction: the highest roof verts (below the chimney) form the ridge line
me = ms[0].data
print('OLD materials=%s uv=%s' % ([m.name for m in me.materials], [u.name for u in me.uv_layers]))

ms, types = load(FBX)
print('NEW objects in file: %s' % types)
ob = ms[0]; me = ob.data
new = stats('NEW', ob)
imgs = [bpy.path.abspath(n.image.filepath) for m in me.materials if m and m.node_tree for n in m.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image]
print('NEW materials=%s uv=%s colour_attrs=%s textures=%s' % ([m.name for m in me.materials], [u.name for u in me.uv_layers], [c.name for c in me.color_attributes], imgs))
# door: the deep recess back face on the -Y side (normal -Y, well behind the wall plane)
mw = ob.matrix_world
best = {}
for p in me.polygons:
    n = (mw.to_3x3() @ p.normal).normalized(); c = mw @ p.center
    if n.y < -0.95 and -1.6 < c.y < -1.0 and c.z < 2.3 and abs(c.x) < 2.3:
        best.setdefault(round(c.y, 2), []).append((c.x, c.z, p.area))
for y, l in best.items():
    print('NEW door leaf (faces looking -Y at y=%.2f, wall plane y=-1.85): x centre %.2f, z centre %.2f, area %.2f m2' % (
        y, np.mean([a[0] for a in l]), np.mean([a[1] for a in l]), sum(a[2] for a in l)))
# ridge direction: top slate verts
top = new[new[:, 2] > 3.95]; top = top[top[:, 2] < 4.2]
print('NEW ridge cap verts span x %.3f..%.3f y %.3f..%.3f -> ridge runs along %s' % (top[:, 0].min(), top[:, 0].max(), top[:, 1].min(), top[:, 1].max(), 'X' if np.ptp(top[:, 0]) > np.ptp(top[:, 1]) else 'Y'))
ot = old[(old[:, 2] > 3.2) & (old[:, 2] < 3.75)]
print('OLD upper roof verts (z 3.2..3.75) span x %.3f..%.3f y %.3f..%.3f' % (ot[:, 0].min(), ot[:, 0].max(), ot[:, 1].min(), ot[:, 1].max()))

# UV checks on the re-imported mesh
T = len(me.polygons)
def uvs(layer):
    a = np.zeros(len(me.loops) * 2, np.float32); me.uv_layers[layer].data.foreach_get('uv', a); return a.reshape(T, 3, 2).astype(np.float64)
def overlap(uv, res):
    inner = np.zeros((res, res), np.int16)
    for t in range(len(uv)):
        p = uv[t] * res
        d = (p[1, 0] - p[0, 0]) * (p[2, 1] - p[0, 1]) - (p[1, 1] - p[0, 1]) * (p[2, 0] - p[0, 0])
        if abs(d) < 1e-9:
            continue
        x0 = max(int(math.floor(p[:, 0].min())), 0); x1 = min(int(math.ceil(p[:, 0].max())) + 1, res)
        y0 = max(int(math.floor(p[:, 1].min())), 0); y1 = min(int(math.ceil(p[:, 1].max())) + 1, res)
        X, Y = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
        w1 = ((X - p[0, 0]) * (p[2, 1] - p[0, 1]) - (Y - p[0, 1]) * (p[2, 0] - p[0, 0])) / d
        w2 = ((p[1, 0] - p[0, 0]) * (Y - p[0, 1]) - (p[1, 1] - p[0, 1]) * (X - p[0, 0])) / d
        w0 = 1 - w1 - w2
        el = [np.linalg.norm(p[2] - p[1]), np.linalg.norm(p[0] - p[2]), np.linalg.norm(p[1] - p[0])]
        dist = np.minimum(np.minimum(w0 * abs(d) / el[0], w1 * abs(d) / el[1]), w2 * abs(d) / el[2])
        inner[y0:y1, x0:x1] += (dist > 0.6)
    return int((inner > 1).sum()), float((inner > 0).mean())
for layer in [u.name for u in me.uv_layers]:
    u = uvs(layer)
    ov, cov = overlap(u, 2048)
    print('NEW uv %s range %.4f..%.4f overlapping texels at 2048: %d, covered %.3f' % (layer, u.min(), u.max(), ov, cov))

im = bpy.data.images.load(TEX)
px = np.array(im.pixels[:], dtype=np.float32).reshape(im.size[1], im.size[0], im.channels)
rgb = px[..., :3]
sat = (rgb.max(-1) - rgb.min(-1)).mean()
print('TEXTURE %s %dx%d channels=%d depth=%d %.1f KB mean_rgb=%s mean_saturation=%.3f' % (
    TEX, im.size[0], im.size[1], im.channels, im.depth, os.path.getsize(TEX) / 1024, rgb.reshape(-1, 3).mean(0).round(3), sat))

tris = sum(len(p.vertices) - 2 for p in me.polygons)
sz = new.max(0) - new.min(0); osz = old.max(0) - old.min(0)
ok = (len(ms) == 1 and tris <= 4000 and len(me.materials) == 1 and len(me.uv_layers) == 2
      and abs(sz[0] - osz[0]) < 2e-3 and abs(sz[1] - osz[1]) < 2e-3
      and np.abs(new.min(0)[:2] - old.min(0)[:2]).max() < 2e-3 and np.abs(new.max(0)[:2] - old.max(0)[:2]).max() < 2e-3
      and abs(new.min(0)[2]) < 1e-4 and im.size[0] == 1024)
print('FOOTPRINT new %s vs old %s' % (sz.round(3), osz.round(3)))
print('ROUNDTRIP', 'PASS' if ok else 'FAIL')
