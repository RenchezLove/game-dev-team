"""Build SM_GroundPlane for ContrarySurvivor level.

Spec (from game-lead):
  - Flat plane in XY (horizontal), normals strictly +Z (up).
  - Size 360 x 360 Blender meters  => UE imports x100 => 36000 x 36000 UE units
    (project convention: build in METERS, FBX import uniform_scale=1, UE Convert Unit x100;
     matches existing props e.g. pistol 0.2m Blender -> 20 UE cm).
  - Pivot (origin) at CENTER of plane, Z=0.
  - Grid density ~2 m per cell => 180 x 180 segments => 181 x 181 = 32761 verts.
  - UV: planar 0..1 across whole plane.
  - Vertex colors: ALL black (0,0,0) in 'Col' attribute (CORNER/BYTE). Material reads
    vcol as road mask (black = grass default, white = dirt/road painted later).
  - One material slot (vcol material; UE will assign its own material).

Headless: E:/Programs/Blender/blender.exe -b --factory-startup --python build_ground_plane.py
Self-verifies via FBX round-trip into a factory scene.
"""
import bpy, bmesh, addon_utils
from mathutils import Vector

addon_utils.enable('io_scene_fbx')

OUT_FBX = 'E:/game-dev-team/assets/ground_plane/SM_GroundPlane.fbx'
NAME = 'SM_GroundPlane'
MAT_NAME = 'M_GroundPlane'
SIZE = 360.0          # meters in Blender (-> 36000 UE units)
SEG = 180             # segments per side -> 181x181 verts, 2.0 m per cell
HALF = SIZE / 2.0     # 180.0
STEP = SIZE / SEG     # 2.0


def make_vcol_material(name):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    vc = nt.nodes.new('ShaderNodeVertexColor')
    vc.layer_name = 'Col'
    bsdf.inputs['Metallic'].default_value = 0.0
    bsdf.inputs['Roughness'].default_value = 0.9
    nt.links.new(vc.outputs['Color'], bsdf.inputs['Base Color'])
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat


def build():
    # clean factory scene already (-b --factory-startup); remove default objects
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)

    bm = bmesh.new()
    # vertex grid, centered on origin, Z=0
    verts = {}
    for j in range(SEG + 1):
        for i in range(SEG + 1):
            x = -HALF + i * STEP
            y = -HALF + j * STEP
            verts[(i, j)] = bm.verts.new((x, y, 0.0))
    bm.verts.ensure_lookup_table()

    # faces: CCW viewed from +Z so face normal points +Z
    for j in range(SEG):
        for i in range(SEG):
            v00 = verts[(i, j)]
            v10 = verts[(i + 1, j)]
            v11 = verts[(i + 1, j + 1)]
            v01 = verts[(i, j + 1)]
            bm.faces.new((v00, v10, v11, v01))
    bm.faces.ensure_lookup_table()

    # layers: UV 0..1 planar, vcol 'Col' black
    uv_layer = bm.loops.layers.uv.new('UVMap')
    col_layer = bm.loops.layers.color.new('Col')  # CORNER / byte color (MLoopCol)
    for f in bm.faces:
        for lp in f.loops:
            co = lp.vert.co
            u = (co.x + HALF) / SIZE
            v = (co.y + HALF) / SIZE
            lp[uv_layer].uv = (u, v)
            lp[col_layer] = (0.0, 0.0, 0.0, 1.0)  # black

    # ensure normals up (+Z)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    # recalc may pick either side for a flat sheet; force +Z explicitly
    flipped = 0
    for f in bm.faces:
        if f.normal.z < 0.0:
            f.normal_flip()
            flipped += 1
    bm.normal_update()

    me = bpy.data.meshes.new(NAME)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = False
    me.update()

    ob = bpy.data.objects.new(NAME, me)
    bpy.context.collection.objects.link(ob)
    me.materials.append(make_vcol_material(MAT_NAME))

    # report pre-export
    nz_bad = sum(1 for p in me.polygons if p.normal.z < 0.99)
    print('BUILD verts=%d faces=%d flipped_to_up=%d faces_not_up=%d'
          % (len(me.vertices), len(me.polygons), flipped, nz_bad))
    d = ob.dimensions
    print('BUILD dims_m=(%.3f, %.3f, %.3f)' % (d.x, d.y, d.z))

    # export FBX (same settings as project props: MESH only, FACE smooth, no axis override)
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.export_scene.fbx(
        filepath=OUT_FBX,
        use_selection=True,
        object_types={'MESH'},
        mesh_smooth_type='FACE',
        use_mesh_modifiers=True,
        add_leaf_bones=False,
        bake_anim=False,
        path_mode='AUTO',
    )
    print('EXPORTED', OUT_FBX)


def verify():
    """Round-trip: reimport the FBX into a fresh factory scene and check."""
    bpy.ops.wm.read_homefile(use_factory_startup=True)
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    addon_utils.enable('io_scene_fbx')
    bpy.ops.import_scene.fbx(filepath=OUT_FBX)
    meshes = [o for o in bpy.data.objects if o.type == 'MESH']
    print('VERIFY imported_meshes=%d' % len(meshes))
    ob = meshes[0]
    me = ob.data
    # apply object transform to read true world dims
    bbmin = Vector((1e9, 1e9, 1e9))
    bbmax = Vector((-1e9, -1e9, -1e9))
    mw = ob.matrix_world
    for v in me.vertices:
        w = mw @ v.co
        for k in range(3):
            bbmin[k] = min(bbmin[k], w[k])
            bbmax[k] = max(bbmax[k], w[k])
    dim = bbmax - bbmin
    print('VERIFY name=%s verts=%d polys=%d' % (ob.name, len(me.vertices), len(me.polygons)))
    print('VERIFY bbox_min=(%.3f,%.3f,%.3f) bbox_max=(%.3f,%.3f,%.3f)'
          % (bbmin.x, bbmin.y, bbmin.z, bbmax.x, bbmax.y, bbmax.z))
    print('VERIFY dims=(%.3f,%.3f,%.3f)' % (dim.x, dim.y, dim.z))
    # pivot/origin location in world
    org = mw.to_translation()
    print('VERIFY object_origin_world=(%.4f,%.4f,%.4f)' % (org.x, org.y, org.z))
    # normals up
    me.calc_normals_split() if hasattr(me, 'calc_normals_split') else None
    not_up = sum(1 for p in me.polygons if (mw.to_3x3() @ p.normal).z < 0.99)
    print('VERIFY polys_not_up=%d (of %d)' % (not_up, len(me.polygons)))
    # vertex colors
    ca = me.color_attributes
    print('VERIFY color_attrs=%s' % ([(c.name, c.domain, c.data_type) for c in ca]))
    if ca:
        layer = ca[0]
        mx = 0.0
        n = len(layer.data)
        for d in layer.data:
            col = d.color
            mx = max(mx, col[0], col[1], col[2])
        print('VERIFY vcol attr=%s entries=%d max_rgb=%.5f (0 => all black)'
              % (layer.name, n, mx))
    # uv range
    uvl = me.uv_layers.active
    if uvl:
        us = [d.uv[0] for d in uvl.data]
        vs = [d.uv[1] for d in uvl.data]
        print('VERIFY uv u=[%.3f..%.3f] v=[%.3f..%.3f]'
              % (min(us), max(us), min(vs), max(vs)))
    print('VERIFY materials=%s' % [m.name for m in me.materials])


build()
verify()
print('DONE')
