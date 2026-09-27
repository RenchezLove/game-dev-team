"""Tripo barrel (barrel.glb, 545 tris) -> low-poly SM_TripoBarrel (76 tris) with a
512 texture: rebaked Tripo colour x baked AO (ribs/rims read by texture), paint mask
in alpha (1 = paint, 0 = rust / bare metal / dirt), paint neutralised to light grey
so the material can multiply it by a paint colour (lead 09-27, like the car).
Steps: import + ground -> AO of the source into vertex colours -> build 10-sided
low mesh (side, rim top, rim inner wall, lid, bottom) with a hand UV layout ->
bake diffuse colour selected-to-active -> mask + neutralise -> save blend + png.
Run: blender.exe -b --factory-startup --python 10_build_barrel.py
"""
import bpy, bmesh, sys, os, math
import numpy as np
from mathutils import Vector, Matrix

GLB = 'E:/ContrarySurvior/ContrarySurvivor/Saved/Tripo/barrel.glb'
OUT = 'E:/game-dev-team/assets/barrel_tripo/'
WORK = OUT + '_work/'
TEX = OUT + 'T_TripoBarrel_D.png'
RAW = WORK + '_bake_raw.png'
NAME = 'SM_TripoBarrel'
MAT = 'M_TripoBarrel'
RES = 512
N = 10                      # sides
ROT0 = math.radians(9)      # half-step turn: bbox x == y (0.656 m)
R_OUT = 0.332               # vertex radius of the shell (face middles at 0.316 = body 0.315)
R_IN = 0.29                 # inner edge of the top rim (source 0.29)
Z_TOP = 0.85                # rim top (source bbox height 0.850)
Z_LID = 0.79                # lid surface (source 0.78..0.79)
AO_DIST = 0.05              # local AO: rib / rim grooves only
AO_MIX = 0.55               # colour *= lerp(1, ao, AO_MIX)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

# ---------- source: import, apply, stand on Z0 ----------
bpy.ops.import_scene.gltf(filepath=GLB)
src = [o for o in bpy.data.objects if o.type == 'MESH'][0]
bpy.context.view_layer.update()
mw = src.matrix_world.copy()
src.parent = None
src.data.transform(mw)
src.matrix_world = Matrix.Identity(4)
for o in [o for o in bpy.data.objects if o is not src]:
    bpy.data.objects.remove(o, do_unlink=True)
cs = [v.co for v in src.data.vertices]
mn = Vector([min(c[i] for c in cs) for i in range(3)])
mx = Vector([max(c[i] for c in cs) for i in range(3)])
src.data.transform(Matrix.Translation((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z)))
src.name = 'TripoBarrelSrc'
src.data.calc_loop_triangles()
print('SOURCE tris=%d size=(%.3f, %.3f, %.3f)' % (len(src.data.loop_triangles), *(mx - mn)))

# ---------- AO of the source into a colour attribute ----------
sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'
sc.cycles.samples = 64
w = bpy.data.worlds.new('W'); sc.world = w
w.light_settings.distance = AO_DIST
ao = src.data.color_attributes.new('AO', 'FLOAT_COLOR', 'POINT')
src.data.color_attributes.active_color = ao
bpy.ops.object.select_all(action='DESELECT')
src.select_set(True); bpy.context.view_layer.objects.active = src
sc.render.bake.target = 'VERTEX_COLORS'
sc.render.bake.use_selected_to_active = False
bpy.ops.object.bake(type='AO')
aov = np.array([d.color[0] for d in ao.data])
print('AO source: min=%.2f mean=%.2f' % (aov.min(), aov.mean()))

# source material: tripo colour x lerp(1, AO, AO_MIX)
smat = src.data.materials[0]
nt = smat.node_tree
tex = [n for n in nt.nodes if n.type == 'TEX_IMAGE'][0]
bsdf = [n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'][0]
attr = nt.nodes.new('ShaderNodeAttribute'); attr.attribute_name = 'AO'
mixf = nt.nodes.new('ShaderNodeMix'); mixf.data_type = 'FLOAT'
mixf.inputs['Factor'].default_value = AO_MIX
mixf.inputs['A'].default_value = 1.0
nt.links.new(attr.outputs['Fac'], mixf.inputs['B'])
mul = nt.nodes.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'
mul.inputs['Factor'].default_value = 1.0
nt.links.new(tex.outputs['Color'], mul.inputs['A'])
nt.links.new(mixf.outputs['Result'], mul.inputs['B'])
nt.links.new(mul.outputs['Result'], bsdf.inputs['Base Color'])

# ---------- low mesh ----------
me = bpy.data.meshes.new(NAME)
low = bpy.data.objects.new(NAME, me)
sc.collection.objects.link(low)
bm = bmesh.new()
uvl = bm.loops.layers.uv.new('UVMap')


def ring(r, z):
    return [bm.verts.new((r * math.cos(ROT0 + 2 * math.pi * i / N), r * math.sin(ROT0 + 2 * math.pi * i / N), z))
            for i in range(N)]


def band(lo, hi, v0, v1):
    """Quads between two rings, UV strip u 0..1, v v0 (lo) .. v1 (hi)."""
    for i in range(N):
        j = (i + 1) % N
        f = bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
        for lp, (u, v) in zip(f.loops, ((i / N, v0), ((i + 1) / N, v0), ((i + 1) / N, v1), (i / N, v1))):
            lp[uvl].uv = (u, v)


def disc(rg, cu, cv, rad, flip):
    f = bm.faces.new(list(reversed(rg)) if flip else rg)
    for lp in f.loops:
        p = lp.vert.co
        r = math.hypot(p.x, p.y)
        lp[uvl].uv = (cu + p.x / r * rad, cv + p.y / r * rad * (-1 if flip else 1))


b0 = ring(R_OUT, 0.0)
t0 = ring(R_OUT, Z_TOP)
t1 = ring(R_IN, Z_TOP)
l0 = ring(R_IN, Z_LID)
# UV layout (0..1): side v 0.40..1.00 | rim top 0.335..0.385 | rim wall 0.285..0.335 | lid + bottom discs
band(b0, t0, 0.40, 1.00)
band(t0, t1, 0.385, 0.335)
band(t1, l0, 0.335, 0.285)
disc(l0, 0.25, 0.135, 0.125, False)
disc(b0, 0.75, 0.135, 0.125, True)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
bmesh.ops.triangulate(bm, faces=bm.faces[:])
bm.to_mesh(me); bm.free()
for p in me.polygons:
    p.use_smooth = False
me.update()
me.calc_loop_triangles()
bmv = bmesh.new(); bmv.from_mesh(me)
vol = bmv.calc_volume(signed=True); bmv.free()
cs = [v.co for v in me.vertices]
print('LOW tris=%d verts=%d signed_volume=%.4f size=(%.3f, %.3f, %.3f) zmin=%.3f' % (
    len(me.loop_triangles), len(me.vertices), vol,
    max(c.x for c in cs) - min(c.x for c in cs), max(c.y for c in cs) - min(c.y for c in cs),
    max(c.z for c in cs) - min(c.z for c in cs), min(c.z for c in cs)))

# ---------- bake colour (x AO) onto the low mesh ----------
img = bpy.data.images.new('T_TripoBarrel_D', RES, RES, alpha=True)
bmat = bpy.data.materials.new(MAT)
bmat.use_nodes = True
bn = bmat.node_tree.nodes.new('ShaderNodeTexImage')
bn.image = img
bmat.node_tree.nodes.active = bn
me.materials.append(bmat)
bk = sc.render.bake
bk.target = 'IMAGE_TEXTURES'
bk.use_selected_to_active = True
bk.cage_extrusion = 0.03
bk.max_ray_distance = 0.08
bk.margin = 8
bk.use_pass_direct = False
bk.use_pass_indirect = False
bk.use_pass_color = True
sc.cycles.samples = 16
bpy.ops.object.select_all(action='DESELECT')
src.select_set(True); low.select_set(True)
bpy.context.view_layer.objects.active = low
bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'})
img.filepath_raw = RAW; img.file_format = 'PNG'; img.save()
print('BAKED', RAW)

# ---------- paint mask + neutral grey paint ----------
# Measured on the side strip of the raw bake (stored sRGB values): paint r-b ~ -0.04
# (median rgb .35/.37/.39), rust r-b > 0.15 (median .37/.22/.11). Dark lines are the
# baked AO of ribs/rims = shaded paint, they stay paintable. No separate dirt/bare metal
# colour exists in the Tripo texture.
RUST_A, RUST_B = -0.01, 0.12    # r-b ramp paint -> rust
GREY = 0.82                     # median paint luminance -> this light grey (sRGB)
px = np.array(img.pixels[:], dtype=np.float32).reshape(RES, RES, 4)
rgb = px[..., :3]
t = np.clip((rgb[..., 0] - rgb[..., 2] - RUST_A) / (RUST_B - RUST_A), 0, 1)
mask = 1.0 - t * t * (3 - 2 * t)
lum = rgb @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
k = GREY / float(np.median(lum[mask > 0.99]))
grey = np.clip(lum * k, 0, 1)[..., None].repeat(3, axis=2)
# grey only on fully painted texels: on a partial texel UE shows lerp(rgb, rgb*Paint, a),
# so a grey rgb there reads as a pale halo round every rust spot; the original
# rust/edge colour gives a dark rusty rim instead.
out = np.concatenate([np.where(mask[..., None] >= 0.98, grey, rgb), mask[..., None]], axis=2)
fin = bpy.data.images.new('T_TripoBarrel_D_final', RES, RES, alpha=True)
fin.pixels = out.ravel()
fin.filepath_raw = TEX; fin.file_format = 'PNG'
fin.save()
fin.filepath = TEX
bn.image = fin
bpy.data.images.remove(img)
fin.name = 'T_TripoBarrel_D'
print('MASK paint share=%.3f (texels a>0.5), rust share=%.3f (a<0.5), grey k=%.2f -> %s' % (
    (mask > 0.5).mean(), (mask < 0.5).mean(), k, TEX))
# final material: texture straight into base colour (UE gets its own paint material)
nt = bmat.node_tree
bs = nt.nodes.get('Principled BSDF')
nt.links.new(bn.outputs['Color'], bs.inputs['Base Color'])
bs.inputs['Roughness'].default_value = 0.8
bpy.data.objects.remove(src, do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=WORK + 'barrel_work.blend')
print('SAVED', WORK + 'barrel_work.blend')
