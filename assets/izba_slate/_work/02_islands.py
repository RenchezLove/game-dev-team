"""Loose-part census of the source izba + straight-on close-ups.
Run: blender.exe -b _src_import.blend --factory-startup --python 02_islands.py
"""
import bpy, bmesh, sys
import numpy as np
from mathutils import Vector
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W
OUT = 'E:/game-dev-team/assets/izba_slate/_work/'

ob = [o for o in bpy.data.objects if o.type == 'MESH'][0]
me = ob.data
mw = ob.matrix_world
print('UV active', me.uv_layers.active.name, 'render', [u.name for u in me.uv_layers if u.active_render])
img = [i for i in bpy.data.images if i.size[0] == 1024][0]
px = np.array(img.pixels[:], dtype=np.float32).reshape(1024, 1024, 4)

bm = bmesh.new(); bm.from_mesh(me)
bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
uvl = {u.name: bm.loops.layers.uv[u.name] for u in me.uv_layers}
for name, l in uvl.items():
    us = np.array([lp[l].uv[:] for f in bm.faces for lp in f.loops])
    print('UV', name, 'min', us.min(0).round(3), 'max', us.max(0).round(3))
seen = set(); isl = []
for v in bm.verts:
    if v.index in seen:
        continue
    st = [v]; seen.add(v.index); vs = []
    while st:
        a = st.pop(); vs.append(a)
        for e in a.link_edges:
            b = e.other_vert(a)
            if b.index not in seen:
                seen.add(b.index); st.append(b)
    fs = set()
    for a in vs:
        for f in a.link_faces:
            fs.add(f)
    isl.append((vs, list(fs)))
print('ISLANDS', len(isl))
act = bm.loops.layers.uv.active
rows = []
for i, (vs, fs) in enumerate(isl):
    cs = np.array([mw @ a.co for a in vs])
    tris = sum(len(f.verts) - 2 for f in fs)
    cols = {}
    for f in fs:
        uv = np.mean([lp[act].uv[:] for lp in f.loops], 0)
        c = px[int(np.clip(uv[1], 0, 0.999) * 1024), int(np.clip(uv[0], 0, 0.999) * 1024)]
        hx = '%02X%02X%02X' % tuple(int(round(float(a) * 255)) for a in c[:3])
        cols[hx] = cols.get(hx, 0) + f.calc_area()
    top = sorted(cols.items(), key=lambda t: -t[1])[:3]
    rows.append((cs.min(0), cs.max(0), tris, top, i))
rows.sort(key=lambda r: (-r[2]))
for mn, mx, tris, top, i in rows:
    print('ISL %3d tris %4d min %s max %s size %s cols %s' % (
        i, tris, mn.round(2), mx.round(2), (mx - mn).round(2), [(h, round(a, 2)) for h, a in top]))
bm.free()

for p in me.polygons:
    p.use_smooth = False
sc, cam, suns = W.setup_render(res=1100)
for vn, vd in (('pY', (0, 1, 0.02)), ('mY', (0, -1, 0.02)), ('pX', (1, 0, 0.02)), ('mX', (-1, 0, 0.02)),
               ('doorq', (-0.5, 1, 0.5))):
    W.frame_and_shoot([ob], vd, OUT + '_srcflat_%s.png' % vn, margin=0.75, suns=suns)
