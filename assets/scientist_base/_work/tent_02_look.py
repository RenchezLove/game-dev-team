"""Tent source after welding: boundary loops, wall planes, entrance close-ups with back faces culled.
Run: blender.exe -b --factory-startup --python tent_02_look.py"""
import bpy, sys, bmesh, math
import numpy as np
sys.path.insert(0, 'E:/game-dev-team/assets/scientist_base/_work')
import sb
sb.empty()
bpy.ops.wm.obj_import(filepath=sb.SRCD + 'tent-model-free/source/unrar/Tent/Tent.obj')
ob = sb.join_meshes([o for o in bpy.data.objects if o.type == 'MESH'], 'src')
print('IMPORT tris', sb.tri_count(ob))
bm = sb.bm_of(ob)
# are the doubled faces exact copies or flipped copies?
key = {}
same = flip = 0
for f in bm.faces:
    k = tuple(sorted(tuple(round(c, 2) for c in v.co) for v in f.verts))
    if k in key:
        if f.normal.dot(key[k]) > 0: same += 1
        else: flip += 1
    key[k] = f.normal.copy()
print('DOUBLES same direction %d, flipped %d of %d faces' % (same, flip, len(bm.faces)))
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.01)
print('AFTER WELD faces %d' % len(bm.faces))
bm.faces.ensure_lookup_table(); bm.normal_update()
comps = sorted(sb.islands(bm), key=lambda c: -len(c)); canvas = comps[0]
be = [e for e in {e for f in canvas for e in f.edges} if len(e.link_faces) == 1]
# boundary loops
adj = {}
for e in be:
    for v in e.verts:
        adj.setdefault(v, []).append(e)
seen = set(); loops = []
for e in be:
    if e in seen: continue
    st = [e]; seen.add(e); grp = []
    while st:
        g = st.pop(); grp.append(g)
        for v in g.verts:
            for h in adj[v]:
                if h not in seen: seen.add(h); st.append(h)
    loops.append(grp)
for g in loops:
    c = np.array([v.co[:] for e in g for v in e.verts])
    print('LOOP edges %3d min %s max %s' % (len(g), c.min(0).round(1), c.max(0).round(1)))
C = np.array([v.co[:] for v in {v for f in canvas for v in f.verts}])
for z in (20, 60, 100, 115, 130, 150, 170):
    s = C[abs(C[:, 2] - z) < 8]
    if len(s): print('SLICE z~%3d: x %.0f..%.0f y %.0f..%.0f n %d' % (z, s[:, 0].min(), s[:, 0].max(), s[:, 1].min(), s[:, 1].max(), len(s)))
low = C[C[:, 2] < 15]
print('LOW canvas verts: z %.1f..%.1f' % (low[:, 2].min(), low[:, 2].max()))
for name, m in (('x<-200', low[:, 0] < -200), ('x>140', low[:, 0] > 140), ('y<-190', low[:, 1] < -190), ('y>70', low[:, 1] > 70)):
    if m.any(): print('  bottom %s: z mean %.1f (n %d) x %.0f..%.0f y %.0f..%.0f' % (name, low[m][:, 2].mean(), m.sum(), low[m][:, 0].min(), low[m][:, 0].max(), low[m][:, 1].min(), low[m][:, 1].max()))
ar = np.array([f.calc_area() for f in canvas]); N = np.array([f.normal[:] for f in canvas]); Cc = np.array([f.calc_center_median()[:] for f in canvas])
print('CANVAS area by direction: +x %.0f -x %.0f +y %.0f -y %.0f up %.0f down %.0f' % tuple(ar[m].sum() for m in (N[:, 0] > 0.7, N[:, 0] < -0.7, N[:, 1] > 0.7, N[:, 1] < -0.7, N[:, 2] > 0.5, N[:, 2] < -0.5)))
dn = N[:, 2] < -0.5
print('DOWN faces: n %d, centres min %s max %s' % (dn.sum(), Cc[dn].min(0).round(0), Cc[dn].max(0).round(0)))
vx = Cc[:, 0] > 150
print('VESTIBULE faces (x>150): n %d min %s max %s; by direction +x %d -x %d +y %d -y %d up %d down %d' % (vx.sum(), Cc[vx].min(0).round(0), Cc[vx].max(0).round(0), *[(m & vx).sum() for m in (N[:, 0] > 0.7, N[:, 0] < -0.7, N[:, 1] > 0.7, N[:, 1] < -0.7, N[:, 2] > 0.5, N[:, 2] < -0.5)]))
bm.to_mesh(ob.data); bm.free()
img = bpy.data.images.load(sb.SRCD + 'tent-model-free/textures/Tex_0129_0.png')
sb.tex_material(ob, 'm', img)
sc, cam, cd, sun = sb.preview_scene(ground=None)
P = []
for i, (yaw, pit, tgt, dist) in enumerate(((90, 15, (150, -70, 80), 500), (60, 35, (150, -70, 80), 500), (120, 50, (100, -70, 80), 600), (90, 5, (0, -70, 60), 180), (0, 60, (0, -60, 80), 900), (270, 20, (0, -60, 80), 800))):
    cd.clip_end = 5000; cd.clip_start = 1
    p = sb.WORK + '_look/tent_cull_%d.png' % i; P.append(p)
    sb.shoot(sc, cam, cd, sun, p, yaw, pit, dist, 45, tgt, res=(800, 600))
sb.sheet(P, sb.WORK + '_look/tent_cull_sheet.png', 3)
