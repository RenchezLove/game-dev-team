"""Export the five dented parts and check each written FBX against the whole part it replaces: triangles (<= 60), origin, the same outline size
in the plane of the panel, the hinge edge point for point, UV inside the UV of the whole part (the same car texture), no face turned inside out.
Then one preview sheet: whole and dented side by side from the game camera.
Run: blender.exe -b broken_work.blend --factory-startup --python 21_export_verify.py"""
import bpy, sys, math, os
import numpy as np
from mathutils import Vector
sys.path.insert(0, 'E:/game-dev-team/assets/scientist_base/_work')
import sb
SRC = 'E:/game-dev-team/assets/abandoned_car_tripo/'; OUT = SRC + 'broken/'
PARTS = ['Door_FL', 'Door_FR', 'Door_RL', 'Door_RR', 'Hood']
INFO = {}
for p in PARTS:
    o = bpy.data.objects['SM_AbandonedCar_%s_Broken' % p]
    INFO[p] = (int(o.data['panel_axis']), float(o.data['out_sign']), int(o.data['ua']), int(o.data['va']))
    for k in ('panel_axis', 'out_sign', 'ua', 'va'):
        del o.data[k]
    sb.export_fbx([o], OUT + o.name + '.fbx')
def load(path):
    before = set(bpy.data.objects); bpy.ops.import_scene.fbx(filepath=path)
    o = [o for o in bpy.data.objects if o not in before and o.type == 'MESH'][0]; bpy.context.view_layer.update(); return o
ok_all = True
sb.empty()
pairs = {}
for p in PARTS:
    ax, sgn, ua, va = INFO[p]
    w = load(SRC + 'SM_AbandonedCar_%s.fbx' % p); b = load(OUT + 'SM_AbandonedCar_%s_Broken.fbx' % p); pairs[p] = (w, b)
    cw = np.array([w.matrix_world @ v.co for v in w.data.vertices]); cb = np.array([b.matrix_world @ v.co for v in b.data.vertices])
    lw, lb = w.matrix_world.translation, b.matrix_world.translation
    tris = sum(len(q.vertices) - 2 for q in b.data.polygons)
    same_plane = max(abs(cw[:, a].min() - cb[:, a].min()) + abs(cw[:, a].max() - cb[:, a].max()) for a in (ua, va))
    span = np.ptp(cw[:, ua]); hinge_w = cw[np.abs(cw[:, ua] - (cw[:, ua].min() if p == 'Hood' else cw[:, ua].max())) < 0.06 * span]
    hd = max(np.linalg.norm(cb - h, axis=1).min() for h in hinge_w)
    uw = sb.uvtris(w.data, w.data.uv_layers[0].name).reshape(-1, 2); ub = sb.uvtris(b.data, b.data.uv_layers[0].name).reshape(-1, 2)
    uv_in = (ub.min(0) >= uw.min(0) - 1e-4).all() and (ub.max(0) <= uw.max(0) + 1e-4).all()
    n3 = b.matrix_world.to_3x3(); nd = np.array([(n3 @ q.normal).normalized()[ax] * sgn for q in b.data.polygons])
    nw = np.array([(w.matrix_world.to_3x3() @ q.normal).normalized()[ax] * sgn for q in w.data.polygons])
    push = (cb[:, ax] * sgn).min() - (cw[:, ax] * sgn).min(), (cb[:, ax] * sgn).max() - (cw[:, ax] * sgn).max()
    ok = (tris <= 60 and lb.length < 1e-6 and (lw - lb).length < 1e-6 and same_plane < 1e-4 and hd < 1e-4 and uv_in and len(b.data.uv_layers) == 1 and len(b.data.materials) == 1
          and (nd > 0).sum() >= (nw > 0).sum() * len(nd) / max(len(nw), 1) - 1e-9 and all(abs(a - 1) < 1e-4 for a in b.matrix_world.to_scale()))
    print('%-8s tris %d (whole %d) | origin broken %s whole %s | outline in the panel plane differs by %.6f m | hinge edge points (%d) found in the broken part within %.6f m | '
          'UV inside the UV of the whole part: %s (uv set %s, material %s) | faces looking outwards %d of %d (whole: %d of %d) -> %s' % (
          p, tris, sum(len(q.vertices) - 2 for q in w.data.polygons), tuple(round(a, 5) for a in lb), tuple(round(a, 5) for a in lw), same_plane, len(hinge_w), hd,
          uv_in, [u.name for u in b.data.uv_layers], [m.name for m in b.data.materials], int((nd > 0).sum()), len(nd), int((nw > 0).sum()), len(nw), 'ok' if ok else 'FAILED'))
    ok_all &= ok
print('BROKEN PARTS ROUNDTRIP', 'PASS' if ok_all else 'FAIL')
# ---- preview: the parts stand as on the car (doors upright, hood flat), whole on the left, dented on the right
tex = bpy.data.images.load(SRC + 'T_AbandonedCarTripo_D.png')
mat = bpy.data.materials.new('prev'); mat.use_nodes = True; nt = mat.node_tree
tn = nt.nodes.new('ShaderNodeTexImage'); tn.image = tex
mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'; mix.inputs[0].default_value = 1.0
mix.inputs['B'].default_value = (0.25, 0.42, 0.55, 1)
nt.links.new(tn.outputs['Color'], mix.inputs['A'])
m2 = nt.nodes.new('ShaderNodeMix'); m2.data_type = 'RGBA'
nt.links.new(tn.outputs['Alpha'], m2.inputs[0]); nt.links.new(tn.outputs['Color'], m2.inputs['A']); nt.links.new(mix.outputs['Result'], m2.inputs['B'])
nt.links.new(m2.outputs['Result'], nt.nodes['Principled BSDF'].inputs['Base Color']); nt.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.8
mat.use_backface_culling = False
# two rows: left parts and the hood are looked at from the -X side, right doors from the +X side; whole part in front, dented one 1.3 m further along Y
ROW = {'Door_FL': (-3.0, 0), 'Door_RL': (-3.0, 3.0), 'Door_FR': (3.0, 0), 'Door_RR': (3.0, 3.0), 'Hood': (0.0, 1.0)}
for p in PARTS:
    w, b = pairs[p]; x0, y0 = ROW[p]
    for o, dy in ((w, 0.0), (b, -1.35 if p != 'Hood' else -1.5)):
        o.data.materials.clear(); o.data.materials.append(mat)
        o.location = (x0, y0 + dy, 0.0 if p != 'Hood' else 0.9)
sc, cam, cd, sun = sb.preview_scene()
os.makedirs(sb.WORK + '_prev_tmp/', exist_ok=True); P = []
for i, (yaw, pit, tgt, fov, sd) in enumerate(((290, 30, (-3.0, 0.4, 0.5), 11, (0.6, 0.25, -0.5)), (70, 30, (3.0, 0.4, 0.5), 11, (-0.6, 0.25, -0.5)),
                                              (20, 60, (0.0, 0.3, 0.9), 7, (-0.45, 0.6, -0.66)), (200, 25, (0.0, 0.3, 0.9), 7, (0.45, -0.6, -0.5)))):
    p = sb.WORK + '_prev_tmp/broken_%d.png' % i; P.append(p)
    sb.shoot(sc, cam, cd, sun, p, yaw, pit, 30, fov, tgt, res=(1100, 700), sun_dir=sd)
sb.sheet(P, OUT + 'broken_preview.png', 2)
