"""Car kit texture + split into parts (after 11_build.py).
One UV atlas for all parts (swatch strip on top: dark plug colour + tail lamp),
bake of the Tripo colour (selected-to-active), bakes of per-texel data (paintable flag,
3D position) -> numpy: paint mask in alpha (1 = body paint, 0 = glass, rubber, chrome,
lamps, rust, plugs), paint neutralised to light grey, rust spots on panel edges / sills /
arches (tones sampled from the abandoned-car reference), tail lamps red + orange + white.
Then split Atlas by 'part', pivots on the hinge axes, save _work/car_kit.blend + png.
Run: blender.exe -b --factory-startup --python 12_bake.py
"""
import bpy, bmesh, math, sys, os
import numpy as np
from mathutils import Vector, Matrix
sys.path.insert(0, 'E:/game-dev-team/assets/abandoned_car_tripo/_work')

WORK = 'E:/game-dev-team/assets/abandoned_car_tripo/_work/'
OUT = 'E:/game-dev-team/assets/abandoned_car_tripo/'
TEX = OUT + 'T_AbandonedCarTripo_D.png'
RUST_REF = 'C:/Users/pgr40/Desktop/Референсы лады/Разбитый (брошеный) атомобиль..png'
RES = 1024
V_TOP = 0.93                    # atlas islands live in v 0..V_TOP, swatches above
DARK_UV = (0.05, 0.965)         # plug / cabin swatch centre
LAMP_UV = (0.15, 0.94, 0.55, 0.995)   # u0, v0, u1, v1 of the tail lamp swatch
WHEEL_UV = (0.80, 0.9655, 0.032)  # wheel disc swatch: centre u, v, radius (painted, the Tripo hub baked badly)
TREAD_UV = (0.90, 0.965)         # tyre tread swatch
GREY = 0.80                     # neutral paint (sRGB) = median paint luminance maps here
SMOOTH_DEG = 35                 # edges sharper than this stay hard
PAINT_BR = (0.02, 0.07)         # b-r ramp: grey/chrome -> blue paint

from carconst import *
bpy.ops.wm.open_mainfile(filepath=WORK + 'car_parts.blend')
sc = bpy.context.scene
atlas = bpy.data.objects['Atlas']
me = atlas.data
pa = me.attributes['part'].data
ka = me.attributes['kind'].data

# ---------- UV atlas ----------
while me.uv_layers:
    me.uv_layers.remove(me.uv_layers[0])
me.uv_layers.new(name='UVMap')
bm = bmesh.new(); bm.from_mesh(me)
pl = bm.faces.layers.int['part']; kl = bm.faces.layers.int['kind']
for f in bm.faces:
    f.select = f[kl] == KIND_PAINT and f[pl] != PID['Wheel']
bm.to_mesh(me); bm.free()
bpy.ops.object.select_all(action='DESELECT')
atlas.select_set(True); bpy.context.view_layer.objects.active = atlas
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.004, correct_aspect=True)
bpy.ops.uv.pack_islands(margin=0.004, rotate=True)
bpy.ops.object.mode_set(mode='OBJECT')
bm = bmesh.new(); bm.from_mesh(me)
pl = bm.faces.layers.int['part']; kl = bm.faces.layers.int['kind']
uv = bm.loops.layers.uv['UVMap']
for f in bm.faces:
    for lp in f.loops:
        c = lp.vert.co
        if f[pl] == PID['Wheel']:
            if abs(f.normal.x) > 0.9:   # both caps: the painted wheel disc (same texels on each side)
                lp[uv].uv = (WHEEL_UV[0] + (c.y - WHEEL_SRC.y) / WHEEL_R * WHEEL_UV[2],
                             WHEEL_UV[1] + (c.z - WHEEL_SRC.z) / WHEEL_R * WHEEL_UV[2])
            else:                       # tread
                lp[uv].uv = TREAD_UV
        elif f[kl] == KIND_PAINT:
            lp[uv].uv = (lp[uv].uv.x, lp[uv].uv.y * V_TOP)
        elif f[kl] == KIND_DARK:
            lp[uv].uv = DARK_UV
        else:   # tail lamp: planar by |x| (outer -> u1) and z
            tx = (abs(c.x) - LAMP_X[0]) / (LAMP_X[1] - LAMP_X[0])
            tz = (c.z - LAMP_Z[0]) / (LAMP_Z[1] - LAMP_Z[0])
            lp[uv].uv = (LAMP_UV[0] + max(0, min(1, tx)) * (LAMP_UV[2] - LAMP_UV[0]),
                         LAMP_UV[1] + max(0, min(1, tz)) * (LAMP_UV[3] - LAMP_UV[1]))
bm.to_mesh(me); bm.free()
print('UV atlas: islands in v 0..%.2f, swatches above (plug, lamp, wheel disc, tread)' % V_TOP)

# ---------- data attribute for the texel bakes ----------
pa = me.attributes['part'].data     # re-fetch: to_mesh above reallocated the arrays
ka = me.attributes['kind'].data
info = me.color_attributes.new('info', 'FLOAT_COLOR', 'CORNER')
for p in me.polygons:
    part = PARTS[pa[p.index].value]
    paintable = 1.0 if (ka[p.index].value == KIND_PAINT and part not in ('Glass', 'Wheel')) else 0.0
    for li in p.loop_indices:
        info.data[li].color = (paintable, 0, 0, 1)


def emit_mat(name, build):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    em = nt.nodes.new('ShaderNodeEmission')
    nt.links.new(build(nt), em.inputs['Color'])
    nt.links.new(em.outputs['Emission'], out.inputs['Surface'])
    tx = nt.nodes.new('ShaderNodeTexImage')
    nt.nodes.active = tx
    return m, tx


def bake_self(name, build):
    img = bpy.data.images.new(name, RES, RES, alpha=False, float_buffer=True)
    m, tx = emit_mat(name, build); tx.image = img
    me.materials.clear(); me.materials.append(m)
    sc.render.bake.use_selected_to_active = False
    sc.render.bake.margin = 4
    bpy.ops.object.select_all(action='DESELECT')
    atlas.select_set(True); bpy.context.view_layer.objects.active = atlas
    bpy.ops.object.bake(type='EMIT')
    return np.array(img.pixels[:], dtype=np.float32).reshape(RES, RES, 4)


sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 1


def b_info(nt):
    a = nt.nodes.new('ShaderNodeVertexColor'); a.layer_name = 'info'
    return a.outputs['Color']


def b_pos(nt):
    g = nt.nodes.new('ShaderNodeNewGeometry')
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Location'].default_value = (0.5, 0.5, 0.0)
    mp.inputs['Scale'].default_value = (0.5, 1 / 4.4, 1 / 1.6)
    nt.links.new(g.outputs['Position'], mp.inputs['Vector'])
    return mp.outputs['Vector']


INFO = bake_self('_info', b_info)
POS = bake_self('_pos', b_pos)
covered = POS[..., 3] > 0  # alpha of float bake = 1 where written
P3 = np.stack([(POS[..., 0] - 0.5) * 2.0, (POS[..., 1] - 0.5) * 4.4, POS[..., 2] * 1.6], -1)
print('DATA bakes: paintable texels %.3f' % (INFO[..., 0] > 0.5).mean())

# ---------- colour bake from the Tripo source ----------
img = bpy.data.images.new('T_AbandonedCarTripo_D', RES, RES, alpha=True)
bmat = bpy.data.materials.new('_bake'); bmat.use_nodes = True
tx = bmat.node_tree.nodes.new('ShaderNodeTexImage'); tx.image = img
bmat.node_tree.nodes.active = tx
me.materials.clear(); me.materials.append(bmat)
srcs = [bpy.data.objects[n] for n in ('Shell', 'Wheel_2')] + \
       [o for o in bpy.data.objects if o.name.startswith(('Misc_', 'Wiper_'))]
bk = sc.render.bake
bk.use_selected_to_active = True
bk.cage_extrusion = 0.04
bk.max_ray_distance = 0.12
bk.margin = 6
bk.use_pass_direct = False; bk.use_pass_indirect = False; bk.use_pass_color = True
sc.cycles.samples = 8
bpy.ops.object.select_all(action='DESELECT')
for o in srcs:
    o.hide_render = False; o.select_set(True)
atlas.select_set(True); bpy.context.view_layer.objects.active = atlas
bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'})
COL = np.array(img.pixels[:], dtype=np.float32).reshape(RES, RES, 4)
raw = bpy.data.images.new('_raw', RES, RES, alpha=True); raw.pixels = COL.ravel()
raw.filepath_raw = WORK + '_bake_raw.png'; raw.file_format = 'PNG'; raw.save()
print('BAKED colour from', [o.name for o in srcs])


# ---------- rust ----------
def vnoise(p, scale, seed):
    """3D value noise on points p (N,3)."""
    q = p * scale
    i0 = np.floor(q).astype(np.int64); t = q - i0
    t = t * t * (3 - 2 * t)

    def h(ix, iy, iz):
        n = (ix * 73856093) ^ (iy * 19349663) ^ (iz * 83492791) ^ (seed * 2654435761)
        n = (n ^ (n >> 13)) * 1274126177
        return ((n ^ (n >> 16)) & 0xFFFF) / 65535.0
    r = 0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (t[:, 0] if dx else 1 - t[:, 0]) * (t[:, 1] if dy else 1 - t[:, 1]) * (t[:, 2] if dz else 1 - t[:, 2])
                r = r + w * h(i0[:, 0] + dx, i0[:, 1] + dy, i0[:, 2] + dz)
    return r


flat = P3.reshape(-1, 3)
x, y, z = flat[:, 0], flat[:, 1], flat[:, 2]
ax = np.abs(x)
edge = np.full(len(flat), 9.0)
side = ax > 0.6
for sy in (DOOR_RY[0], DOOR_FY[0], DOOR_FY[1]):
    edge = np.where(side & (z > DOOR_Z[0] - 0.02) & (z < DOOR_Z[1]), np.minimum(edge, np.abs(y - sy)), edge)
edge = np.where(side & (y > DOOR_RY[0]) & (y < DOOR_FY[1]), np.minimum(edge, np.abs(z - DOOR_Z[0])), edge)
topf = z > 0.7
for sy in HOOD_Y + TRUNK_Y:
    edge = np.where(topf & (ax < 0.75), np.minimum(edge, np.abs(y - sy)), edge)
edge = np.where(topf & (y > 0.9), np.minimum(edge, np.abs(ax - HOOD_HX)), edge)
edge = np.where(topf & (y < -1.35), np.minimum(edge, np.abs(ax - TRUNK_HX)), edge)
arch = np.full(len(flat), 9.0)
for wy in (1.44, -0.97):
    arch = np.minimum(arch, np.abs(np.hypot(y - wy, z - 0.285) - 0.37))
arch = np.where(ax > 0.55, arch, 9.0)
score = (0.55 * np.clip(1 - edge / 0.05, 0, 1) + 0.6 * np.clip(1 - arch / 0.07, 0, 1)
         + 0.55 * np.clip((0.44 - z) / 0.12, 0, 1))
nz = 0.65 * vnoise(flat, 9.0, 1) + 0.35 * vnoise(flat, 28.0, 2)
spots = np.clip((vnoise(flat, 6.0, 3) - 0.80) / 0.08, 0, 1)          # rare spots anywhere
rust = np.clip((score * (0.4 + nz) + spots * nz - 0.55) / 0.12, 0, 1).reshape(RES, RES)
rust *= (INFO[..., 0] > 0.5)

ref = bpy.data.images.load(RUST_REF)
R = np.array(ref.pixels[:], dtype=np.float32).reshape(-1, 4)[:, :3]
sel = (R[:, 0] > R[:, 1] * 1.25) & (R[:, 1] > R[:, 2] * 1.1) & (R[:, 0] > 0.25) & (R[:, 0] < 0.8)
tones = R[sel]
rust_dark = np.percentile(tones, 25, axis=0); rust_light = np.percentile(tones, 75, axis=0)
print('RUST ref: %d pixels, tone dark %s light %s' % (sel.sum(), rust_dark.round(3), rust_light.round(3)))
tone = nz.reshape(RES, RES, 1)
rust_rgb = rust_dark * (1 - tone) + rust_light * tone

# ---------- mask + neutral paint ----------
rgb = COL[..., :3]
br = rgb[..., 2] - rgb[..., 0]
t = np.clip((br - PAINT_BR[0]) / (PAINT_BR[1] - PAINT_BR[0]), 0, 1)
paint = t * t * (3 - 2 * t) * (INFO[..., 0] > 0.5)
rust = rust * np.clip(paint * 2 - 0.5, 0, 1)     # rust only on painted metal (not on door glass, chrome)
lum = rgb @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
k = GREY / float(np.median(lum[paint > 0.99]))
grey = np.clip(lum * k, 0, 1)[..., None].repeat(3, 2)
mask = paint * (1 - rust)
out = np.where(mask[..., None] >= 0.98, grey, rgb)
out = out * (1 - rust[..., None]) + rust_rgb * rust[..., None]

# swatches (v rows from the bottom)
def box(u0, v0, u1, v1):
    return slice(int(v0 * RES), int(v1 * RES)), slice(int(u0 * RES), int(u1 * RES))


out[box(DARK_UV[0] - 0.04, DARK_UV[1] - 0.02, DARK_UV[0] + 0.04, DARK_UV[1] + 0.02)] = (0.05, 0.05, 0.055)
mask[box(DARK_UV[0] - 0.04, DARK_UV[1] - 0.02, DARK_UV[0] + 0.04, DARK_UV[1] + 0.02)] = 0
u0, v0, u1, v1 = LAMP_UV
RED, ORANGE, WHITE, SEP = (0.62, 0.05, 0.04), (0.93, 0.45, 0.06), (0.90, 0.90, 0.86), (0.12, 0.11, 0.11)
vm = (v0 + v1) / 2
out[box(u0, vm, u1, v1)] = RED                                  # upper half red
out[box(u0, v0, u0 + 0.25 * (u1 - u0), vm)] = ORANGE           # lower row: inner orange
out[box(u0 + 0.25 * (u1 - u0), v0, u0 + 0.55 * (u1 - u0), vm)] = WHITE   # reverse light
out[box(u0 + 0.55 * (u1 - u0), v0, u1, vm)] = ORANGE            # outer orange (as on the ref)
out[box(u0, vm - 0.002, u1, vm + 0.002)] = SEP
for uu in (0.25, 0.55):
    out[box(u0 + uu * (u1 - u0) - 0.002, v0, u0 + uu * (u1 - u0) + 0.002, v1)] = SEP
mask[box(u0, v0, u1, v1)] = 0
# wheel disc (steel wheel like the Tripo one) + tread
TYRE = (0.07, 0.07, 0.075)
cu, cv, cr = WHEEL_UV
sl = box(cu - cr * 1.05, cv - cr * 1.05, cu + cr * 1.05, cv + cr * 1.05)
vv, uu = np.mgrid[sl[0], sl[1]]
rr = np.hypot((uu + 0.5) / RES - cu, (vv + 0.5) / RES - cv) / cr
ang = np.arctan2((vv + 0.5) / RES - cv, (uu + 0.5) / RES - cu)
disc = np.empty(rr.shape + (3,), np.float32); disc[:] = TYRE
disc[rr < 0.72] = (0.70, 0.71, 0.72)                                  # steel rim
disc[(rr > 0.60) & (rr < 0.66)] = (0.42, 0.43, 0.44)                  # rim step
disc[rr < 0.26] = (0.84, 0.85, 0.86)                                  # hub cap
holes = (np.abs(rr - 0.44) < 0.07) & (np.cos(4 * ang) > 0.8)
disc[holes] = (0.16, 0.16, 0.17)                                      # 4 holes
disc[rr < 0.06] = (0.5, 0.5, 0.5)
out[sl] = disc; mask[sl] = 0
out[box(TREAD_UV[0] - 0.02, TREAD_UV[1] - 0.02, TREAD_UV[0] + 0.02, TREAD_UV[1] + 0.02)] = TYRE
mask[box(TREAD_UV[0] - 0.02, TREAD_UV[1] - 0.02, TREAD_UV[0] + 0.02, TREAD_UV[1] + 0.02)] = 0
fin_px = np.concatenate([np.clip(out, 0, 1), mask[..., None]], 2).astype(np.float32)
fin = bpy.data.images.new('T_AbandonedCarTripo_D_final', RES, RES, alpha=True)
fin.pixels = fin_px.ravel()
fin.filepath_raw = TEX; fin.file_format = 'PNG'; fin.save(); fin.filepath = TEX
bpy.data.images.remove(img); fin.name = 'T_AbandonedCarTripo_D'
print('TEXTURE %s: paint(a>0.99) %.3f of texels, rust texels %.3f of paintable, grey k=%.2f' % (
    TEX, (mask > 0.99).mean(), (rust > 0.5).sum() / max(1, (INFO[..., 0] > 0.5).sum()), k))

# ---------- split into parts, pivots ----------
PIVOT = {
    'Body': Vector((0, 0, 0)), 'Glass': Vector((0, 0, 0)),
    'Door_FL': Vector((-DOOR_X, DOOR_FY[1], DOOR_Z[0])), 'Door_FR': Vector((DOOR_X, DOOR_FY[1], DOOR_Z[0])),
    'Door_RL': Vector((-DOOR_X, DOOR_RY[1], DOOR_Z[0])), 'Door_RR': Vector((DOOR_X, DOOR_RY[1], DOOR_Z[0])),
    'Wheel': WHEEL_SRC.copy(),
}
hz = {}
for p in me.polygons:
    n = PARTS[pa[p.index].value]
    if n in ('Hood', 'Trunk'):
        for vi in p.vertices:
            co = me.vertices[vi].co
            edge_y = HOOD_Y[0] if n == 'Hood' else TRUNK_Y[1]
            if abs(co.y - edge_y) < 0.02:
                hz.setdefault(n, []).append(co.z)
PIVOT['Hood'] = Vector((0, HOOD_Y[0], max(hz['Hood'])))
PIVOT['Trunk'] = Vector((0, TRUNK_Y[1], max(hz['Trunk'])))
mat = bpy.data.materials.new('M_CarTripo'); mat.use_nodes = True
gmat = bpy.data.materials.new('M_CarTripoGlass'); gmat.use_nodes = True
for m in (mat, gmat):
    nt = m.node_tree; bs = nt.nodes['Principled BSDF']
    t2 = nt.nodes.new('ShaderNodeTexImage'); t2.image = fin
    nt.links.new(t2.outputs['Color'], bs.inputs['Base Color'])
    bs.inputs['Roughness'].default_value = 0.6
me.color_attributes.remove(me.color_attributes['info'])
for name in PARTS:
    ob = atlas.copy(); ob.data = me.copy(); ob.name = ob.data.name = 'SM_AbandonedCar_' + name
    sc.collection.objects.link(ob)
    bm = bmesh.new(); bm.from_mesh(ob.data)
    pl = bm.faces.layers.int['part']
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f[pl] != PID[name]], context='FACES')
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
    bm.transform(Matrix.Translation(-PIVOT[name]))
    bm.to_mesh(ob.data); bm.free()
    for a in ('part', 'kind'):
        ob.data.attributes.remove(ob.data.attributes[a])
    ob.data.materials.clear(); ob.data.materials.append(gmat if name == 'Glass' else mat)
    for p in ob.data.polygons:
        p.material_index = 0
    ob.data.shade_smooth()                       # smooth by angle: hides the decimation facets
    ob.data.set_sharp_from_angle(angle=math.radians(SMOOTH_DEG))
    ob.location = (0, 0, 0)
    cs = [v.co for v in ob.data.vertices]
    print('PART %-24s tris=%3d pivot(blender)=(%.3f, %.3f, %.3f) local min=(%.3f %.3f %.3f) max=(%.3f %.3f %.3f)' % (
        ob.name, len(ob.data.polygons), *PIVOT[name], *[min(c[i] for c in cs) for i in range(3)],
        *[max(c[i] for c in cs) for i in range(3)]))
bpy.data.objects.remove(atlas, do_unlink=True)
for o in list(bpy.data.objects):
    if not o.name.startswith('SM_AbandonedCar_'):
        bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=WORK + 'car_kit.blend')
print('SAVED', WORK + 'car_kit.blend')
