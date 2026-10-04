"""Tripo pistol PM / knife (glb) -> low-poly static weapons that sit exactly where the current in-game
meshes sit (same origin, axes and bounds).  References (the files UE was imported from, matched to the
UE bounds given in the task):
  E:/ForGameLead(Materials)/demo-assets/SM_Pistol.fbx   208 tris
  E:/ForGameLead(Materials)/phase3-assets/SM_Knife.fbx  154 tris
Steps: import -> orient -> fit to reference bounds -> decimate -> smart UV -> bake colour 512 -> export.
Usage: blender -b --factory-startup --python 10_build.py -- pistol|knife
"""
import bpy, bmesh, sys, math
import numpy as np
from mathutils import Matrix, Vector
sys.path.insert(0, 'E:/game-dev-team/assets')
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import propcommon as P
import wcommon as W

OUT = 'E:/game-dev-team/assets/weapons_tripo/'
SRC = 'E:/ContrarySurvior/ContrarySurvivor/Saved/Tripo/'
CFG = {
    'pistol': dict(glb='pistol_pm/pistol_pm.glb', fbx='SM_Pistol', tex='T_PistolPM_D', mat='M_PistolPM',
                   limit=228, mn=(-0.017, -0.158, -0.082), mx=(0.017, 0.039, 0.088)),
    'knife': dict(glb='knife/knife.glb', fbx='SM_Knife', tex='T_KnifeTripo_D', mat='M_KnifeTripo',
                  limit=169, mn=(-0.024, 0.0, -0.010), mx=(0.024, 0.355, 0.010)),
}
which = sys.argv[sys.argv.index('--') + 1]
C = CFG[which]
TEX = 512


def coords(ob):
    a = np.zeros(len(ob.data.vertices) * 3)
    ob.data.vertices.foreach_get('co', a)
    return a.reshape(-1, 3)


def set_coords(ob, a):
    ob.data.vertices.foreach_set('co', a.ravel())
    ob.data.update()


bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC + C['glb'])
src = [o for o in bpy.data.objects if o.type == 'MESH'][0]
for o in list(bpy.data.objects):
    if o is not src:
        bpy.data.objects.remove(o, do_unlink=True)
bpy.context.view_layer.objects.active = src
src.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
src.name = 'src'
co = coords(src)

if which == 'knife':
    # the Tripo knife lies diagonally: principal axes -> Y length, X blade width, Z thickness
    me = src.data
    cen = np.array([p.center[:] for p in me.polygons]); ar = np.array([p.area for p in me.polygons])
    mu = (cen * ar[:, None]).sum(0) / ar.sum()
    d = cen - mu
    w, v = np.linalg.eigh((d * ar[:, None]).T @ d)
    ax_len, ax_wid, ax_thk = v[:, 2], v[:, 1], v[:, 0]
    q = co - mu
    co = np.stack([q @ ax_wid, q @ ax_len, q @ ax_thk], 1)
    # handle = the thicker end -> low Y
    y0, y1 = co[:, 1].min(), co[:, 1].max()
    lo = co[co[:, 1] < y0 + 0.25 * (y1 - y0)]; hi = co[co[:, 1] > y1 - 0.25 * (y1 - y0)]
    if np.ptp(lo[:, 2]) < np.ptp(hi[:, 2]):
        co[:, 1] *= -1; co[:, 0] *= -1
    y0, y1 = co[:, 1].min(), co[:, 1].max()
    # straighten on the handle: its centre line goes onto the Y axis
    L = y1 - y0
    cs = []
    for a, b in ((0.06, 0.16), (0.26, 0.36)):
        s = co[(co[:, 1] > y0 + a * L) & (co[:, 1] < y0 + b * L)]
        cs.append(((s[:, 0].min() + s[:, 0].max()) / 2, s[:, 1].mean(), (s[:, 2].min() + s[:, 2].max()) / 2))
    ang = math.atan2(cs[1][0] - cs[0][0], cs[1][1] - cs[0][1])
    ca, sa = math.cos(ang), math.sin(ang)
    x = co[:, 0] - cs[0][0]; y = co[:, 1] - cs[0][1]
    co[:, 0] = x * ca - y * sa; co[:, 1] = x * sa + y * ca
    co[:, 2] -= (cs[0][2] + cs[1][2]) / 2
    print('KNIFE handle tilt removed deg %.2f' % math.degrees(ang))
    # cutting edge: the side where the blade reaches further from the axis near its middle
    yb = co[:, 1]; Lb = yb.max() - yb.min()
    s = co[(yb > yb.min() + 0.55 * Lb) & (yb < yb.min() + 0.8 * Lb)]
    print('KNIFE blade x range mid-blade %.4f..%.4f (raw units)' % (s[:, 0].min(), s[:, 0].max()))
    EDGE_SIGN = float(sys.argv[sys.argv.index('--') + 2]) if len(sys.argv) > sys.argv.index('--') + 2 else -1.0
    if (abs(s[:, 0].min()) > abs(s[:, 0].max())) != (EDGE_SIGN < 0):
        co[:, 0] *= -1; co[:, 2] *= -1          # 180 deg about Y keeps handedness
    # scale: length exact, width and thickness so the furthest point touches the old bound
    co[:, 1] -= co[:, 1].min()
    co[:, 1] *= C['mx'][1] / co[:, 1].max()
    # width: the whole outline fills the old +-2.4 cm (the handle axis ends up ~0.4 cm off centre,
    # which keeps the blade wide instead of squashing it)
    co[:, 0] = (co[:, 0] - co[:, 0].min()) / np.ptp(co[:, 0]) * (C['mx'][0] - C['mn'][0]) + C['mn'][0]
    co[:, 2] = (co[:, 2] - co[:, 2].min()) / np.ptp(co[:, 2]) * (C['mx'][2] - C['mn'][2]) + C['mn'][2]
    hs = co[co[:, 1] < 0.10]
    print('KNIFE handle centre x %.2f cm, handle width %.2f cm, thickness %.2f cm' % (100 * (hs[:, 0].min() + hs[:, 0].max()) / 2, 100 * np.ptp(hs[:, 0]), 100 * np.ptp(hs[:, 2])))
else:
    # the Tripo pistol already points its muzzle to -Y with the grip down, like the current one
    mn = co.min(0); mx = co.max(0)
    tmn = np.array(C['mn']); tmx = np.array(C['mx'])
    co = (co - mn) / (mx - mn) * (tmx - tmn) + tmn
    print('PISTOL scale per axis', ((tmx - tmn) / (mx - mn)).round(3))
set_coords(src, co)
# mirrored coordinates flip the winding -> recalc
bm = bmesh.new(); bm.from_mesh(src.data)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(src.data); bm.free()

# ---- low-poly copy
low = src.copy(); low.data = src.data.copy(); low.name = C['fbx']
bpy.context.scene.collection.objects.link(low)
bm = bmesh.new(); bm.from_mesh(low.data)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0002)
bmesh.ops.triangulate(bm, faces=bm.faces)
bm.to_mesh(low.data); bm.free()
n0 = W.tri_count(low)
bound = [e for e in low.data.edges] and None
ratio = C['limit'] / n0
for it in range(12):
    t = low.copy(); t.data = low.data.copy(); bpy.context.scene.collection.objects.link(t)
    m = t.modifiers.new('d', 'DECIMATE'); m.ratio = ratio; m.use_collapse_triangulate = True
    bpy.context.view_layer.objects.active = t
    bpy.ops.object.select_all(action='DESELECT'); t.select_set(True)
    bpy.ops.object.modifier_apply(modifier='d')
    n = W.tri_count(t)
    if n <= C['limit']:
        break
    bpy.data.objects.remove(t, do_unlink=True)
    ratio *= 0.985
bpy.data.objects.remove(low, do_unlink=True)
low = t; low.name = C['fbx']; low.data.name = C['fbx']
print('DECIMATE welded %d -> %d tris (limit %d)' % (n0, n, C['limit']))
# decimation pulls the extremes in a little -> put the bounds back exactly
lc = coords(low); sc_ = coords(src)
for a in range(3):
    l0, l1 = lc[:, a].min(), lc[:, a].max(); s0, s1 = sc_[:, a].min(), sc_[:, a].max()
    lc[:, a] = (lc[:, a] - l0) / (l1 - l0) * (s1 - s0) + s0
set_coords(low, lc)

# ---- UV + bake
me = low.data
while len(me.uv_layers):
    me.uv_layers.remove(me.uv_layers[0])
me.uv_layers.new(name='UVMap')
bpy.ops.object.select_all(action='DESELECT'); low.select_set(True)
bpy.context.view_layer.objects.active = low
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.02)
bpy.ops.uv.pack_islands(margin=0.02, shape_method='AABB')
bpy.ops.object.mode_set(mode='OBJECT')
img = bpy.data.images.new(C['tex'], TEX, TEX, alpha=False)
mat = bpy.data.materials.new(C['mat']); mat.use_nodes = True
tn = mat.node_tree.nodes.new('ShaderNodeTexImage'); tn.image = img
mat.node_tree.links.new(tn.outputs['Color'], mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.8
mat.node_tree.nodes.active = tn
me.materials.clear(); me.materials.append(mat)
for p in me.polygons:
    p.use_smooth = False
scn = bpy.context.scene
scn.render.engine = 'CYCLES'; scn.cycles.samples = 8; scn.cycles.device = 'CPU'
bk = scn.render.bake
bk.use_selected_to_active = True
bk.cage_extrusion = 0.004; bk.max_ray_distance = 0.012; bk.margin = 8
bk.use_pass_direct = False; bk.use_pass_indirect = False; bk.use_pass_color = True
bpy.ops.object.select_all(action='DESELECT'); src.select_set(True); low.select_set(True)
bpy.context.view_layer.objects.active = low
bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'})
img.filepath_raw = OUT + C['tex'] + '.png'; img.file_format = 'PNG'; img.save()
px = np.array(img.pixels[:]).reshape(TEX, TEX, 4)
print('BAKE saved %s  black texels (rgb<0.02) %.1f%%' % (C['tex'], 100 * (px[:, :, :3].max(2) < 0.02).mean()))
src.hide_render = True
bpy.ops.wm.save_as_mainfile(filepath=OUT + '_work/%s_work.blend' % which)
P.export_one(low, OUT + C['fbx'] + '.fbx')
lc = coords(low)
print('RESULT %s tris %d min %s max %s (cm)' % (which, W.tri_count(low), (lc.min(0) * 100).round(2), (lc.max(0) * 100).round(2)))
