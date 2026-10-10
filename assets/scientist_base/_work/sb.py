"""Shared helpers of the scientist base set (Blender 5.1, headless).  Metres, flat shade, one material, one colour texture,
UVMap + LightmapUV, FBX 7400 mesh only.  Unreal draws one side of a face, so every build stores where each face has to look
(face attributes wx/wy/wz) and the export check compares the re-imported FBX with it, face by face."""
import bpy, bmesh, math, os, sys
import numpy as np
import addon_utils
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

ROOT = 'E:/game-dev-team/assets/scientist_base/'
SRCD = ROOT + '_src/'
WORK = ROOT + '_work/'


def args():
    return sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []


def empty():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    addon_utils.enable('io_scene_fbx')


def tri_count(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)


def coords(ob):
    a = np.zeros(len(ob.data.vertices) * 3); ob.data.vertices.foreach_get('co', a)
    return a.reshape(-1, 3)


def set_coords(ob, a):
    ob.data.vertices.foreach_set('co', np.asarray(a, dtype=np.float64).ravel()); ob.data.update()


def only(ob):
    desel(); ob.select_set(True); bpy.context.view_layer.objects.active = ob


def join_meshes(obs, name):
    """Apply world transforms and modifiers-free join of mesh objects into one object."""
    desel()
    for o in obs:
        o.hide_set(False); o.select_set(True)
    bpy.context.view_layer.objects.active = obs[0]
    bpy.ops.object.make_single_user(object=True, obdata=True)
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    if len(obs) > 1:
        bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active; ob.name = name; ob.data.name = name
    return ob


def bm_of(ob):
    bm = bmesh.new(); bm.from_mesh(ob.data); bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table(); return bm


def islands(bm):
    """Connected parts of the mesh: list of face lists."""
    seen = set(); out = []
    for f in bm.faces:
        if f.index in seen:
            continue
        stack = [f]; seen.add(f.index); comp = []
        while stack:
            g = stack.pop(); comp.append(g)
            for v in g.verts:
                for h in v.link_faces:
                    if h.index not in seen:
                        seen.add(h.index); stack.append(h)
        out.append(comp)
    return out


def decimate_to(ob, limit, weld=0.0002, planar_first=None):
    """Collapse decimation of a copy until the triangle count is <= limit. Returns the new object (the old one is removed)."""
    bm = bm_of(ob)
    if weld:
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=weld)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.to_mesh(ob.data); bm.free()
    n0 = tri_count(ob)
    if n0 <= limit:
        return ob, n0, n0
    ratio = limit / n0
    for it in range(40):
        t = ob.copy(); t.data = ob.data.copy(); bpy.context.scene.collection.objects.link(t)
        m = t.modifiers.new('d', 'DECIMATE'); m.ratio = ratio; m.use_collapse_triangulate = True
        only(t); bpy.ops.object.modifier_apply(modifier='d')
        n = tri_count(t)
        if n <= limit:
            break
        bpy.data.objects.remove(t, do_unlink=True); ratio *= 0.985
    name = ob.name
    bpy.data.objects.remove(ob, do_unlink=True)
    t.name = name; t.data.name = name
    return t, n0, n


def clear_uv(me):
    while len(me.uv_layers):
        me.uv_layers.remove(me.uv_layers[0])


def smart_uv(ob, layer='UVMap', angle=66, margin=0.02, rotate=True):
    me = ob.data
    if layer not in me.uv_layers:
        me.uv_layers.new(name=layer)
    me.uv_layers.active = me.uv_layers[layer]
    only(ob)
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(angle), island_margin=margin)
    bpy.ops.uv.pack_islands(margin=margin, shape_method='AABB', rotate=rotate)
    bpy.ops.object.mode_set(mode='OBJECT')


def uvtris(me, layer):
    a = np.zeros(len(me.loops) * 2); me.uv_layers[layer].data.foreach_get('uv', a)
    return a.reshape(len(me.polygons), 3, 2)


def overlaps(uv, res=1024):
    """Texels covered by the inside of more than one UV triangle."""
    inner = np.zeros((res, res), np.int16)
    for t in range(len(uv)):
        p = uv[t] * res
        d = (p[1, 0] - p[0, 0]) * (p[2, 1] - p[0, 1]) - (p[1, 1] - p[0, 1]) * (p[2, 0] - p[0, 0])
        if abs(d) < 1e-9:
            continue
        x0 = max(int(math.floor(p[:, 0].min())), 0); x1 = min(int(math.ceil(p[:, 0].max())) + 1, res)
        y0 = max(int(math.floor(p[:, 1].min())), 0); y1 = min(int(math.ceil(p[:, 1].max())) + 1, res)
        if x1 <= x0 or y1 <= y0:
            continue
        X, Y = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
        w1 = ((X - p[0, 0]) * (p[2, 1] - p[0, 1]) - (Y - p[0, 1]) * (p[2, 0] - p[0, 0])) / d
        w2 = ((p[1, 0] - p[0, 0]) * (Y - p[0, 1]) - (p[1, 1] - p[0, 1]) * (X - p[0, 0])) / d
        w0 = 1 - w1 - w2
        el = [np.linalg.norm(p[2] - p[1]), np.linalg.norm(p[0] - p[2]), np.linalg.norm(p[1] - p[0])]
        dist = np.minimum(np.minimum(w0 * abs(d) / el[0], w1 * abs(d) / el[1]), w2 * abs(d) / el[2])
        inner[y0:y1, x0:x1] += (dist > 0.6)
    return int((inner > 1).sum())


def lightmap_uv(ob, angle=66, margin=0.03):
    """Second UV set without overlaps for the light map (the active render set stays UVMap)."""
    me = ob.data
    for ang in (angle, 55, 45, 35, 25):
        if 'LightmapUV' in me.uv_layers:
            me.uv_layers.remove(me.uv_layers['LightmapUV'])
        me.uv_layers.new(name='LightmapUV')
        smart_uv(ob, 'LightmapUV', ang, margin)
        ov = overlaps(uvtris(me, 'LightmapUV'), 1024)
        if ov == 0:
            break
    me.uv_layers.active = me.uv_layers['UVMap']; me.uv_layers['UVMap'].active_render = True
    return ang, ov


def hemi(n=32, seed=3):
    r = np.random.RandomState(seed); v = r.normal(size=(n * 4, 3)); v /= np.linalg.norm(v, axis=1)[:, None]
    return v


def open_sides(ob, ground=True, rays=48, extra=()):
    """For every face: share of rays that leave freely from its front and from its back (ground and 'extra' objects block)."""
    bm = bm_of(ob); bm.normal_update()
    geo = [bm]
    V = [v.co.copy() for v in bm.verts]; F = [[v.index for v in f.verts] for f in bm.faces]
    for e in extra:
        b2 = bm_of(e); off = len(V)
        V += [e.matrix_world @ v.co for v in b2.verts]; F += [[v.index + off for v in f.verts] for f in b2.faces]; b2.free()
    if ground:
        mn = np.array([v[:] for v in V]).min(0); off = len(V); z = float(mn[2]) - 1e-4
        V += [Vector((-1e3, -1e3, z)), Vector((1e3, -1e3, z)), Vector((1e3, 1e3, z)), Vector((-1e3, 1e3, z))]; F.append([off, off + 1, off + 2, off + 3])
    tree = BVHTree.FromPolygons(V, F)
    dirs = hemi(rays)
    diag = float(np.linalg.norm(np.ptp(np.array([v.co[:] for v in bm.verts]), axis=0)))
    eps = diag * 2e-4
    front = np.zeros(len(bm.faces)); back = np.zeros(len(bm.faces))
    for f in bm.faces:
        n = f.normal; c = f.calc_center_median()
        nn = np.array(n[:])
        dd = dirs @ nn
        for sign, acc in ((1.0, front), (-1.0, back)):
            sel = dirs[(dd * sign) > 0.15][:rays]
            o = c + n * (eps * sign); free = 0
            for d in sel:
                if tree.ray_cast(o, Vector(d), diag * 4)[0] is None:
                    free += 1
            acc[f.index] = free / max(len(sel), 1)
    bm.free()
    return front, back


def fix_facing(ob, ground=True, tag=''):
    """Turn every face to the side that is open to the outside (ray test); returns (flipped, both sides open, both closed)."""
    front, back = open_sides(ob, ground)
    bm = bm_of(ob); bm.normal_update()
    flip = [f for f in bm.faces if back[f.index] > front[f.index] + 0.12]
    if flip:
        bmesh.ops.reverse_faces(bm, faces=flip)
    bm.normal_update(); bm.to_mesh(ob.data); bm.free(); ob.data.update()
    both = int(((front > 0.3) & (back > 0.3)).sum()); none = int(((front < 0.02) & (back < 0.02)).sum())
    print('%s FACING fixed: flipped %d of %d faces; open on both sides %d; closed on both sides %d' % (tag, len(flip), len(front), both, none))
    return len(flip), both, none


def store_facing(ob):
    """Remember where every face looks now (after fix_facing) - the export check compares the FBX with it."""
    me = ob.data
    for a in ('wx', 'wy', 'wz'):
        if a in me.attributes:
            me.attributes.remove(me.attributes[a])
    N = np.zeros(len(me.polygons) * 3); me.polygons.foreach_get('normal', N); N = N.reshape(-1, 3)
    for i, a in enumerate(('wx', 'wy', 'wz')):
        at = me.attributes.new(a, 'FLOAT', 'FACE'); at.data.foreach_set('value', N[:, i].astype(np.float32))


def flat(ob):
    for p in ob.data.polygons:
        p.use_smooth = False


def tex_material(ob, name, img):
    mat = bpy.data.materials.new(name); mat.use_nodes = True
    tn = mat.node_tree.nodes.new('ShaderNodeTexImage'); tn.image = img
    b = mat.node_tree.nodes['Principled BSDF']
    mat.node_tree.links.new(tn.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.9
    mat.node_tree.nodes.active = tn
    mat.use_backface_culling = True
    ob.data.materials.clear(); ob.data.materials.append(mat)
    for p in ob.data.polygons:
        p.material_index = 0
    return mat


def bake_colour(src_obs, low, img, cage, maxdist, margin=8, samples=4):
    """Bake the base colour of the source objects onto the low mesh (selected to active)."""
    scn = bpy.context.scene
    scn.render.engine = 'CYCLES'; scn.cycles.samples = samples; scn.cycles.device = 'CPU'
    bk = scn.render.bake
    bk.use_selected_to_active = True; bk.cage_extrusion = cage; bk.max_ray_distance = maxdist; bk.margin = margin
    bk.use_pass_direct = False; bk.use_pass_indirect = False; bk.use_pass_color = True
    desel()
    for s in src_obs:
        s.hide_render = False; s.hide_set(False); s.select_set(True)
    low.select_set(True); bpy.context.view_layer.objects.active = low
    bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'})
    px = np.array(img.pixels[:], dtype=np.float32).reshape(img.size[1], img.size[0], 4)
    return px


def save_png(px, path, name=None):
    """px: H x W x 3|4 float 0..1 in sRGB display values, row 0 = bottom."""
    h, w = px.shape[:2]
    if px.shape[2] == 3:
        px = np.concatenate([px, np.ones((h, w, 1), px.dtype)], 2)
    img = bpy.data.images.new(name or os.path.basename(path)[:-4], w, h, alpha=False)
    img.pixels.foreach_set(px.astype(np.float32).ravel())
    img.filepath_raw = path; img.file_format = 'PNG'
    sc = bpy.context.scene; sc.render.image_settings.color_mode = 'RGB'
    img.save()
    return img


def load_px(path):
    img = bpy.data.images.load(path, check_existing=False)
    px = np.array(img.pixels[:], dtype=np.float32).reshape(img.size[1], img.size[0], img.channels)
    return img, px


def raster(me, layer, res):
    """Rasterise UV triangles: returns (face index per texel or -1, barycentric weights H x W x 3)."""
    uv = uvtris(me, layer)
    fid = -np.ones((res, res), np.int32); bw = np.zeros((res, res, 3), np.float32)
    for t in range(len(uv)):
        p = uv[t] * res
        d = (p[1, 0] - p[0, 0]) * (p[2, 1] - p[0, 1]) - (p[1, 1] - p[0, 1]) * (p[2, 0] - p[0, 0])
        if abs(d) < 1e-12:
            continue
        x0 = max(int(math.floor(p[:, 0].min())) - 1, 0); x1 = min(int(math.ceil(p[:, 0].max())) + 2, res)
        y0 = max(int(math.floor(p[:, 1].min())) - 1, 0); y1 = min(int(math.ceil(p[:, 1].max())) + 2, res)
        if x1 <= x0 or y1 <= y0:
            continue
        X, Y = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
        w1 = ((X - p[0, 0]) * (p[2, 1] - p[0, 1]) - (Y - p[0, 1]) * (p[2, 0] - p[0, 0])) / d
        w2 = ((p[1, 0] - p[0, 0]) * (Y - p[0, 1]) - (p[1, 1] - p[0, 1]) * (X - p[0, 0])) / d
        w0 = 1 - w1 - w2
        inside = (w0 >= -1e-4) & (w1 >= -1e-4) & (w2 >= -1e-4)
        sub = fid[y0:y1, x0:x1]; sb_ = bw[y0:y1, x0:x1]
        sub[inside] = t
        sb_[inside] = np.stack([w0, w1, w2], -1)[inside]
    return fid, bw


def dilate(px, mask, steps=8):
    """Grow painted texels (mask True) into the empty ones around - no dark seams on island borders."""
    px = px.copy(); m = mask.copy()
    for _ in range(steps):
        acc = np.zeros_like(px); cnt = np.zeros(m.shape, np.float32)
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            sm = np.roll(m, (dy, dx), (0, 1)); sp = np.roll(px, (dy, dx), (0, 1))
            acc += sp * sm[..., None]; cnt += sm
        new = (~m) & (cnt > 0)
        px[new] = acc[new] / cnt[new][:, None]; m |= new
    return px


def place(ob, front_axis=None):
    """Origin to the middle of the footprint on the ground (z min = 0)."""
    c = coords(ob); mn = c.min(0); mx = c.max(0)
    c -= np.array([(mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2, mn[2]])
    set_coords(ob, c)


def export_fbx(obs, path):
    desel()
    for o in obs:
        o.hide_set(False); o.hide_render = False; o.select_set(True)
        drop_custom_normals(o.data)
    bpy.context.view_layer.objects.active = obs[0]
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={'MESH'}, mesh_smooth_type='FACE', use_mesh_modifiers=True,
                             add_leaf_bones=False, bake_anim=False, path_mode='AUTO', colors_type='LINEAR')
    print('FILE %s %.1f KB' % (path, os.path.getsize(path) / 1024))


def ref_of(ob):
    me = ob.data; T = len(me.polygons)
    C = np.zeros(T * 3); me.polygons.foreach_get('center', C)
    Wn = np.zeros((T, 3))
    for i, a in enumerate(('wx', 'wy', 'wz')):
        t = np.zeros(T, np.float32); me.attributes[a].data.foreach_get('value', t); Wn[:, i] = t
    return C.reshape(-1, 3), Wn


def roundtrip(path, name, ref, limit, tex_paths, tex_max, uv_expect=('UVMap', 'LightmapUV'), origin_ground=True, centred=True, lo=0, ground_check=True, extra_ok=True):
    """Re-import the written FBX into an empty scene and check it. Returns (ok, dict of measured numbers)."""
    empty()
    bpy.ops.import_scene.fbx(filepath=path)
    bpy.context.view_layer.update()
    meshes = [o for o in bpy.data.objects if o.type == 'MESH']
    print('%s objects in file: %s' % (name, sorted((o.name, o.type) for o in bpy.data.objects)))
    o = [m for m in meshes if m.name == name][0]; me = o.data; mw = o.matrix_world; n3 = mw.to_3x3()
    cs = np.array([mw @ v.co for v in me.vertices])
    loc, rot, scl = mw.decompose()
    tris = sum(len(p.vertices) - 2 for p in me.polygons)
    mn, mx = cs.min(0), cs.max(0)
    print('%s tris=%d verts=%d min=%s max=%s size=%s (m)' % (name, tris, len(me.vertices), mn.round(4), mx.round(4), (mx - mn).round(4)))
    print('%s origin=%s rot=%s scale=%s materials=%s uv=%s smooth_faces=%d' % (name, tuple(round(a, 5) for a in loc), tuple(round(a, 4) for a in rot.to_euler()), tuple(round(a, 4) for a in scl),
          [m.name for m in me.materials if m], [u.name for u in me.uv_layers], sum(1 for p in me.polygons if p.use_smooth)))
    # facing: every face against the direction stored by the builder
    RC, RW = ref
    C = np.array([mw @ p.center for p in me.polygons]); N = np.array([(n3 @ p.normal).normalized() for p in me.polygons])
    wrong = 0; worst = 0.0
    if len(C) == len(RC):
        from mathutils.kdtree import KDTree
        kd = KDTree(len(RC))
        for i, c in enumerate(RC):
            kd.insert(Vector(c), i)
        kd.balance()
        used = np.zeros(len(RC), np.int32)
        for i in range(len(C)):
            # several faces can share a centre (two-sided sheets): take the candidate whose stored direction matches best
            cand = kd.find_range(Vector(C[i]), 1e-4) or [kd.find(Vector(C[i]))]
            best = max(cand, key=lambda r: float(np.dot(N[i], RW[r[1]])))
            worst = max(worst, best[2]); used[best[1]] += 1
            if float(np.dot(N[i], RW[best[1]])) < 0.9:
                wrong += 1
        unmatched = int((used == 0).sum())
    else:
        unmatched = abs(len(C) - len(RC)); wrong = 10 ** 6
    up, dn = int((N[:, 2] > 0.5).sum()), int((N[:, 2] < -0.5).sum())
    print('%s facing: %d faces compared with the builder directions, worst centre distance %.6f m, wrong %d, builder faces without a pair %d (look up %d, down %d, sideways %d)' % (
        name, len(C), worst, wrong, unmatched, up, dn, len(C) - up - dn))
    nbad, nmin = stored_normals(o)
    print('%s stored normals: faces whose saved vertex normal looks against the face %d of %d (lowest dot %.3f)' % (name, nbad, len(me.polygons), nmin))
    ovs = {}
    for layer in [u.name for u in me.uv_layers]:
        uv = uvtris(me, layer); ovs[layer] = overlaps(uv)
        print('%s uv %s range %.4f..%.4f overlapping texels at 1024: %d' % (name, layer, uv.min(), uv.max(), ovs[layer]))
    tex_ok = True
    for tp in tex_paths:
        ti = bpy.data.images.load(tp)
        print('%s texture %s %dx%d %.1f KB' % (name, os.path.basename(tp), ti.size[0], ti.size[1], os.path.getsize(tp) / 1024))
        tex_ok &= max(ti.size) <= tex_max and ti.size[0] > 0
    uvr = np.concatenate([uvtris(me, l).ravel() for l in [u.name for u in me.uv_layers]])
    ok = (len([m for m in meshes if m.name == name]) == 1 and len([m for m in me.materials if m]) == 1 and [u.name for u in me.uv_layers] == list(uv_expect)
          and lo <= tris <= limit and wrong == 0 and nbad == 0 and unmatched == 0 and worst < 1e-3 and max(abs(a) for a in loc) < 1e-5 and all(abs(a - 1) < 1e-4 for a in scl)
          and uvr.min() > -1e-4 and uvr.max() < 1 + 1e-4 and tex_ok and sum(1 for p in me.polygons if p.use_smooth) == 0)
    if 'LightmapUV' in ovs:
        ok &= ovs['LightmapUV'] == 0
    if origin_ground:
        ok &= abs(mn[2]) < 1e-4
    if centred:
        ok &= abs(mn[0] + mx[0]) < 2e-3 and abs(mn[1] + mx[1]) < 2e-3
    print('%s triangles %d (allowed %d..%d)' % (name, tris, lo, limit))
    print('%s ROUNDTRIP %s' % (name, 'PASS' if ok else 'FAIL'))
    return ok, dict(tris=tris, mn=mn, mx=mx, ovs=ovs)


def preview_scene(bg=(0.42, 0.45, 0.48), ground=(0.16, 0.14, 0.09), ground_z=0.0):
    sc = bpy.context.scene
    try:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    except Exception:
        sc.render.engine = 'BLENDER_EEVEE'
    sc.view_settings.view_transform = 'Standard'
    w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs[0].default_value = (*bg, 1); w.node_tree.nodes['Background'].inputs[1].default_value = 0.9
    if ground is not None:
        bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, ground_z))
        gr = bpy.context.active_object
        gm = bpy.data.materials.new('ground'); gm.use_nodes = True
        gm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (*ground, 1)
        gr.data.materials.append(gm)
    sun = bpy.data.objects.new('Sun', bpy.data.lights.new('Sun', 'SUN')); sc.collection.objects.link(sun); sun.data.energy = 3.0
    cd = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', cd); sc.collection.objects.link(cam); sc.camera = cam; cd.clip_end = 300; cd.clip_start = 0.01
    return sc, cam, cd, sun


def shoot(sc, cam, cd, sun, path, yaw_deg, pitch_deg, dist, fov_deg, target, res=(1280, 960), sun_dir=(-0.45, 0.6, -0.66)):
    """yaw 0 = camera stands on -Y of the target and looks to +Y."""
    yaw, pit = math.radians(yaw_deg), math.radians(pitch_deg)
    d = Vector((math.sin(yaw) * math.cos(pit), -math.cos(yaw) * math.cos(pit), math.sin(pit)))
    cam.location = Vector(target) + d * dist
    cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()
    cd.sensor_fit = 'HORIZONTAL'; cd.angle_x = math.radians(fov_deg)
    sun.rotation_euler = Vector(sun_dir).normalized().to_track_quat('-Z', 'Y').to_euler()
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print('RENDER', path)


def sheet(paths, out, cols=2):
    """Glue renders of the same size into one sheet."""
    ims = [load_px(p)[1] for p in paths]
    h, w = ims[0].shape[:2]; rows = (len(ims) + cols - 1) // cols
    S = np.ones((rows * h, cols * w, 4), np.float32)
    for i, im in enumerate(ims):
        r, c = divmod(i, cols)
        if im.shape[2] == 3:
            im = np.concatenate([im, np.ones((h, w, 1), np.float32)], 2)
        S[(rows - 1 - r) * h:(rows - r) * h, c * w:(c + 1) * w] = im
    save_png(S, out)
    print('SHEET', out)


def uv_clean(ob, layer='UVMap', margin=0.012, angles=(66, 55, 45, 35, 25), res=1024):
    """Smart UV with the widest angle that leaves no overlapping texels."""
    for ang in angles:
        smart_uv(ob, layer, ang, margin)
        ov = overlaps(uvtris(ob.data, layer), res)
        if ov == 0:
            break
    print('UV %s angle %d overlapping texels at %d: %d' % (layer, ang, res, ov))
    return ang, ov


def desel():
    """Deselect everything without an operator (the operator refuses to run in files saved with an odd context)."""
    bpy.context.view_layer.update()
    for o in list(bpy.context.scene.objects):
        if o is not None and o.name in bpy.context.view_layer.objects:
            o.select_set(False)


def load_dae_simple(path, name='src'):
    """Minimal Collada reader (Blender 5 has no Collada import): one mesh, a polylist indexed by VERTEX only, Y up -> Z up."""
    import xml.etree.ElementTree as ET
    ns = {'c': 'http://www.collada.org/2005/11/COLLADASchema'}
    root = ET.parse(path).getroot()
    obs = []
    for g in root.findall('.//c:geometry', ns):
        mesh = g.find('c:mesh', ns)
        srcs = {}
        for s in mesh.findall('c:source', ns):
            fa = s.find('c:float_array', ns); acc = s.find('.//c:accessor', ns)
            srcs['#' + s.get('id')] = np.array(fa.text.split(), float).reshape(-1, int(acc.get('stride')))
        vin = {i.get('semantic'): i.get('source') for i in mesh.find('c:vertices', ns).findall('c:input', ns)}
        pos = srcs[vin['POSITION']]; uv = srcs[vin['TEXCOORD']][:, :2] if 'TEXCOORD' in vin else None
        pl = mesh.find('c:polylist', ns)
        if pl is None:
            pl = mesh.find('c:triangles', ns)
        nin = len(pl.findall('c:input', ns))
        idx = np.array(pl.find('c:p', ns).text.split(), int).reshape(-1, nin)[:, 0]
        vc = pl.find('c:vcount', ns)
        vcount = np.array(vc.text.split(), int) if vc is not None else np.full(len(idx) // 3, 3)
        faces = []; o = 0
        for n in vcount:
            faces.append(idx[o:o + n].tolist()); o += n
        me = bpy.data.meshes.new(name)
        me.from_pydata([(p[0], -p[2], p[1]) for p in pos], [], faces); me.update()
        if uv is not None:
            l = me.uv_layers.new(name='UVMap')
            lv = np.zeros(len(me.loops), np.int32); me.loops.foreach_get('vertex_index', lv)
            l.data.foreach_set('uv', uv[lv].ravel())
        ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob); obs.append(ob)
    bpy.context.view_layer.update()
    return obs


def drop_custom_normals(me):
    """Stored (custom) normals of an imported source survive welding and decimation and may look against the face
    (the tent, 2026-10-09: dark roof in Unreal).  Flat-shaded models are exported with normals computed from the faces."""
    for n in ('custom_normal',):
        if n in me.attributes:
            me.attributes.remove(me.attributes[n])
    me.update()


def stored_normals(o):
    """Normals as they are stored in the imported file against the geometric normal of every face: (faces with a bad one, lowest dot)."""
    me = o.data
    cn = np.zeros(len(me.loops) * 3, np.float32); me.corner_normals.foreach_get('vector', cn); cn = cn.reshape(-1, 3)
    fn = np.zeros(len(me.polygons) * 3, np.float32); me.polygons.foreach_get('normal', fn); fn = fn.reshape(-1, 3)
    ls = np.zeros(len(me.polygons), np.int32); me.polygons.foreach_get('loop_start', ls); lt = np.zeros(len(me.polygons), np.int32); me.polygons.foreach_get('loop_total', lt)
    bad = 0; lowest = 1.0
    for i in range(len(me.polygons)):
        d = float((cn[ls[i]:ls[i] + lt[i]] @ fn[i]).min())
        lowest = min(lowest, d); bad += d <= 0.0
    return int(bad), lowest
