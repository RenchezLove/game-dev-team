"""Dented variants of the car parts (doors FL/FR/RL/RR and the hood) made from our own delivered parts, so that seat and hinge stay the same:
the same origin, axes, outline size in the plane of the panel, the same UV in the same car texture.  The whole FBX is imported, a few of its
longest edges are split (UV is interpolated), and the points are pushed across the panel: a dent, a bent free corner, a twist of the plane.
Points on the hinge edge do not move.  Not more than 60 triangles per part.
Run: blender.exe -b --factory-startup --python 20_broken.py
"""
import bpy, bmesh, sys, math, os
import numpy as np
from mathutils import Vector
sys.path.insert(0, 'E:/game-dev-team/assets/scientist_base/_work')
import sb
SRC = 'E:/game-dev-team/assets/abandoned_car_tripo/'
OUT = SRC + 'broken/'
LIMIT = 60; TARGET = 56
# per part: (dent centre u,v; depth m; radius), bent corner (u,v; height m; radius), twist m at the free edge, second dent
CFG = {
    'Door_FL': dict(dent=(0.42, 0.30, 0.085, 0.26), corner=(0.0, 0.0, 0.11, 0.38), twist=0.045, dent2=(0.70, 0.52, 0.04, 0.16)),
    'Door_FR': dict(dent=(0.55, 0.38, 0.075, 0.24), corner=(0.0, 1.0, 0.07, 0.30), twist=-0.035, dent2=(0.25, 0.18, 0.05, 0.18)),
    'Door_RL': dict(dent=(0.35, 0.40, 0.080, 0.25), corner=(0.0, 0.0, 0.09, 0.34), twist=-0.040, dent2=(0.72, 0.22, 0.045, 0.17)),
    'Door_RR': dict(dent=(0.50, 0.25, 0.090, 0.27), corner=(0.0, 0.0, 0.10, 0.36), twist=0.050, dent2=(0.30, 0.55, 0.035, 0.15)),
    'Hood':    dict(dent=(0.60, 0.32, 0.070, 0.24), corner=(1.0, 1.0, 0.12, 0.40), twist=0.030, dent2=(0.45, 0.72, 0.05, 0.20), ridge=(0.55, 0.35, 0.065, 0.10)),
}
sb.empty()
RES = {}
for part, C in CFG.items():
    name = 'SM_AbandonedCar_%s' % part
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=SRC + name + '.fbx')
    ob = [o for o in bpy.data.objects if o not in before and o.type == 'MESH'][0]
    bpy.context.view_layer.update()
    me = ob.data
    assert max(abs(a) for a in ob.matrix_world.translation) < 1e-6
    me.transform(ob.matrix_world); ob.matrix_world.identity()
    whole = ob.copy(); whole.data = me.copy(); whole.name = name + '_whole'; bpy.context.scene.collection.objects.link(whole)
    c0 = sb.coords(ob); mn, mx = c0.min(0), c0.max(0)
    nr = np.zeros(len(me.polygons) * 3); me.polygons.foreach_get('normal', nr); nr = nr.reshape(-1, 3)
    ar = np.zeros(len(me.polygons)); me.polygons.foreach_get('area', ar)
    mean_n = (nr * ar[:, None]).sum(0); ax = int(np.abs(mean_n).argmax()); out_sign = float(np.sign(mean_n[ax]))
    hood = part == 'Hood'
    # panel coordinates: u runs from the free edge (0) to the hinge edge (1), v across
    if hood:
        ua, va = 1, 0; hinge_at_min = True          # hinge at the rear edge (y min), the nose edge is free
    else:
        ua, va = 1, 2; hinge_at_min = False         # hinge at the front edge (y max = 0), the rear edge is free
    print('%s source: tris %d min %s max %s; panel looks along %s%s; uv sets %s; material %s' % (name, sb.tri_count(ob), mn.round(3), mx.round(3), '+' if out_sign > 0 else '-', 'XYZ'[ax],
          [u.name for u in me.uv_layers], [m.name for m in me.materials]))
    # ---- more points: split the longest edges
    bm = sb.bm_of(ob); bmesh.ops.triangulate(bm, faces=bm.faces)
    bmesh.ops.delete(bm, geom=[e for e in bm.edges if not e.link_faces], context='EDGES'); bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
    guard = 0
    while len(bm.faces) < TARGET and guard < 200:
        guard += 1
        e = max([e for e in bm.edges if e.link_faces], key=lambda e: e.calc_length())
        v1, v2 = e.verts
        ne, nv = bmesh.utils.edge_split(e, v1, 0.5)                # a point in the middle of the edge (UV is interpolated) ...
        for f in list(nv.link_faces):                             # ... joined to the opposite corner of every triangle on that edge
            if len(f.verts) == 4:
                opp = [l.vert for l in f.loops if l.vert is not nv and nv not in (l.link_loop_next.vert, l.link_loop_prev.vert)][0]
                bmesh.utils.face_split(f, nv, opp)
    # ---- push the points across the panel
    moved = 0; fixed = 0
    dmin = dmax = 0.0
    for v in bm.verts:
        p = np.array(v.co[:])
        u = (p[ua] - mn[ua]) / (mx[ua] - mn[ua]); w = (p[va] - mn[va]) / (mx[va] - mn[va])
        if hinge_at_min:
            u = 1 - u
            pass
        # u: 0 = free edge, 1 = hinge edge  (for doors y max is the hinge, so u already grows to the hinge)
        hold = min(max((0.93 - u) / 0.22, 0.0), 1.0)      # nothing moves on the hinge edge and next to it
        d = 0.0
        du, dv, depth, rad = C['dent']; d -= depth * math.exp(-(((u - du) ** 2 + (w - dv) ** 2) / rad ** 2))
        du, dv, depth, rad = C['dent2']; d -= depth * math.exp(-(((u - du) ** 2 + (w - dv) ** 2) / rad ** 2))
        cu, cv, h, rad = C['corner']; dist = math.hypot(u - cu, w - cv); d += h * max(0.0, 1 - dist / rad) ** 1.5
        d += C['twist'] * (1 - u) * (2 * w - 1)
        if 'ridge' in C:
            ru, rk, h, s = C['ridge']; d += h * math.exp(-(((u - ru) + rk * (w - 0.5)) / s) ** 2)
        d *= hold
        dmin = min(dmin, d); dmax = max(dmax, d)
        if abs(d) > 1e-6:
            v.co[ax] += out_sign * d; moved += 1
        if hold == 0.0:
            fixed += 1
    bm.normal_update()
    # keep every face looking the way the whole panel looks (a fold must not turn a face inside out)
    flipped = [f for f in bm.faces if False]
    bm.to_mesh(me); bm.free(); me.update()
    for p in me.polygons:
        p.use_smooth = False
    ob.name = name + '_Broken'; me.name = ob.name
    MAT = bpy.data.materials.get('M_CarTripo'); me.materials.clear(); me.materials.append(MAT); whole.data.materials.clear(); whole.data.materials.append(MAT)
    me['panel_axis'] = ax; me['out_sign'] = out_sign; me['ua'] = ua; me['va'] = va
    c1 = sb.coords(ob)
    print('%s_Broken: tris %d, points %d (moved %d, still at the hinge %d); pushed inwards up to %.1f cm, outwards up to %.1f cm' % (name, sb.tri_count(ob), len(c1), moved, fixed, -dmin * 100, dmax * 100))
    RES[part] = (ob, whole, ax, out_sign, mn, mx, (ua, va))
bpy.ops.wm.save_as_mainfile(filepath=OUT + '_work/broken_work.blend')
