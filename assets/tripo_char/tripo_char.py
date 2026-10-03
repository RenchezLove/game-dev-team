"""Tripo character (glb) -> 3 skinned slot meshes on our 21-bone RootAnim, fitted to the T0 Tripo hero
(ADR-095). Generalised from hero_tripo/_work/10_build.py and armor_t1_tripo/_work/10_build.py:
import+orient -> weld -> centre on the torso -> head alignment -> decimate -> rebake -> Tripo-proportioned
rig -> heat-skin -> pose onto OUR rest -> bake -> thicken -> fit to T0 at the slot cuts -> heat-skin to
RootAnim -> clavicle weight fix -> (coat skirts to the thigh bones) -> split slots -> save blend.
Per-character numbers live in configs.py; build(cfg) is called by <char>_tripo/_work/10_build.py.
"""
import bpy, bmesh, sys, os, math
sys.path.insert(0, 'E:/game-dev-team/assets/hero_tripo/_work')
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import hcommon as H
import wcommon as W
from mathutils import Vector, Matrix, kdtree
from mathutils.bvhtree import BVHTree

HERO = 'E:/game-dev-team/assets/hero_tripo/_work/hero_work.blend'
TEXRES = 1024
HAND_L, HAND_W = 0.5, 0.7           # Tripo hand 0.20 m -> T0 size, as on the hero
THICK_LIMB = 1.18                   # limbs as on the T0 hero
WAIST_AX, NECK_AX = -0.001, -0.03   # y of the vertical axes the T0 rings are measured from
HEM_Z = 0.914                       # top garment hem lands just above the waist overlap 0.900..0.910
COLLAR_TOP = 1.528                  # collar stays under the head slot (cut at 1.532)
T0_HEAD_CY = -0.013                 # depth centre of the T0 head


def smooth(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def build(C):
    OUTDIR = C['outdir']; WORK = OUTDIR + '_work/'
    TEX = OUTDIR + C['tex']
    NECK_Z, HEAD_Z, SH_X = C['neck_z'], C['head_z'], C['sh_x']
    coat = C.get('coat')

    # ---------- T0 hero surface (the body standard) + its legs for the pelvis graft ----------
    bpy.ops.wm.open_mainfile(filepath=HERO)
    bm0 = bmesh.new()
    for n in ('SK_Cloth_T0_Head', 'SK_Cloth_T0_Torso', 'SK_Cloth_T0_Legs'):
        bm0.from_mesh(bpy.data.objects[n].data)
    T0 = BVHTree.FromBMesh(bm0)
    bm0.free()
    lo = bpy.data.objects['SK_Cloth_T0_Legs']
    gn0 = {g.index: g.name for g in lo.vertex_groups}
    G_CO = [v.co.copy() for v in lo.data.vertices]
    G_W = [{g.group: g.weight for g in v.groups if g.weight > 1e-4} for v in lo.data.vertices]
    G_F = [tuple(p.vertices) for p in lo.data.polygons]

    def t0_r(axy, co, z):
        d = Vector((co.x, co.y - axy, 0.0))
        if d.length < 1e-6:
            return None
        hit = T0.ray_cast(Vector((0.0, axy, z)), d.normalized(), 0.6)[0]
        return math.hypot(hit.x, hit.y - axy) if hit else None

    bpy.ops.wm.open_mainfile(filepath=H.WEAR)
    import addon_utils; addon_utils.enable('io_scene_fbx')
    rig = bpy.data.objects['RootAnim']
    for o in [o for o in bpy.data.objects if o.type == 'MESH']:
        bpy.data.objects.remove(o, do_unlink=True)
    if rig.animation_data:
        rig.animation_data.action = None
    for pb in rig.pose.bones:
        pb.matrix_basis = Matrix.Identity(4)

    # ---------- import + orient (face -Y, left +X, feet on Z0) ----------
    bpy.ops.import_scene.gltf(filepath=C['glb'])
    hero = [o for o in bpy.context.selected_objects if o.type == 'MESH'][0]
    for o in list(bpy.context.selected_objects):
        if o is not hero:
            bpy.data.objects.remove(o, do_unlink=True)
    bpy.context.view_layer.update()
    hero.data.transform(Matrix.Rotation(math.radians(C['yaw']), 4, 'Z') @ hero.matrix_world)
    hero.parent = None
    hero.matrix_world = Matrix.Identity(4)
    me = hero.data
    vs = me.vertices
    zmin = min(v.co.z for v in vs)
    chest = [v.co for v in vs if 1.0 < v.co.z - zmin < 1.3]
    xc = (min(c.x for c in chest) + max(c.x for c in chest)) / 2
    yc = (min(c.y for c in chest) + max(c.y for c in chest)) / 2
    me.transform(Matrix.Translation((-xc, -0.001 - yc, -zmin)))
    hero.name = me.name = 'TripoChar'
    me.calc_loop_triangles()
    print('TRIPO raw tris=%d verts=%d height=%.3f' % (len(me.loop_triangles), len(me.vertices), max(v.co.z for v in vs)))
    bm = bmesh.new(); bm.from_mesh(me)
    n0 = len(bm.verts)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
    bm.to_mesh(me); bm.free(); me.update()
    print('WELD %d -> %d verts' % (n0, len(me.vertices)))

    # centre on the torso depth (pockets / a beard skew the bounding box), then put the head over the spine
    tree, _ = H.bvh_of([hero])
    crotch = H.ray(tree, (0, -0.001, 0.3), (0, 0, 1)).z
    zm = (crotch + 0.03 + 1.38) / 2
    f = H.ray(tree, (0, -2, zm), (0, 1, 0)); k = H.ray(tree, (0, 2, zm), (0, -1, 0))
    dy = -0.001 - (f.y + k.y) / 2
    me.transform(Matrix.Translation((0, dy, 0)))
    hb = [v.co for v in me.vertices if HEAD_Z + 0.10 < v.co.z < HEAD_Z + 0.20 and abs(v.co.x) < 0.15]
    hcy = (min(c.y for c in hb) + max(c.y for c in hb)) / 2
    dh = max(-0.03, min(0.03, T0_HEAD_CY - hcy))
    for v in me.vertices:
        if abs(v.co.x) < 0.25:
            v.co.y += dh * smooth(NECK_Z - 0.08, HEAD_Z + 0.02, v.co.z)
    me.update()
    print('CENTRE torso depth at z=%.2f: y shift %.3f; head depth centre %.3f -> shift %.3f (T0 %.3f)' % (zm, dy, hcy, dh, T0_HEAD_CY))

    # ---------- measure Tripo joints ----------
    cos = [v.co.copy() for v in me.vertices]
    tree, _ = H.bvh_of([hero])
    HIP_Z = crotch + 0.03
    arm = {}
    for i in range(15, 90):
        x = i * 0.01
        best = None
        for j in range(-12, 21):
            y = j * 0.01
            up = H.ray(tree, (x, y, 1.1), (0, 0, 1)); dn = H.ray(tree, (x, y, 2.2), (0, 0, -1))
            if up and dn and 0 < dn.z - up.z < 0.4:
                if best is None or dn.z - up.z > best[0]:
                    best = (dn.z - up.z, (up.z + dn.z) / 2)
        if best:
            f = H.ray(tree, (x, -2, best[1]), (0, 1, 0)); k = H.ray(tree, (x, 2, best[1]), (0, -1, 0))
            if f and k:
                arm[i] = (best[0], best[1], (f.y + k.y) / 2)
    tip = max(c.x for c in cos)
    xs = sorted(arm)
    drops = [(arm[a][0] - arm[b][0], b) for a, b in zip(xs, xs[1:]) if 0.55 < b * 0.01 < 0.8]
    WR_X = max(drops)[1] * 0.01 - 0.005
    EL_X = SH_X + 0.5637 * (WR_X - SH_X)

    def arm_at(x):
        i = min(arm, key=lambda q: abs(q * 0.01 - x))
        return Vector((x, arm[i][2], arm[i][1]))

    SH = arm_at(SH_X); EL = arm_at(EL_X); WR = arm_at(WR_X); TIPP = arm_at(tip - 0.02)
    SP2_Z = SH.z

    def leg_centre(z):
        a = H.ray(tree, (2, -0.001, z), (-1, 0, 0)); b = H.ray(tree, (0.0005, -0.001, z), (1, 0, 0))
        if coat and z > coat['hem_raw'] - 0.01:          # under the coat there is no leg: take the T0 thigh line
            return None
        cx = (a.x + b.x) / 2
        f = H.ray(tree, (cx, -2, z), (0, 1, 0)); k = H.ray(tree, (cx, 2, z), (0, -1, 0))
        return Vector((cx, (f.y + k.y) / 2, z))

    KN_Z = HIP_Z * (0.458 / 0.837)
    kn = leg_centre(KN_Z)
    th = leg_centre(HIP_Z - 0.08)
    if th is None:
        th = Vector((0.105 + (kn.x - 0.126) * 0.5, kn.y, HIP_Z - 0.08))
    feet = [c for c in cos if c.x > 0.02 and c.z < 0.10]
    fmn_y, fmx_y = min(c.y for c in feet), max(c.y for c in feet)
    fcx = (min(c.x for c in feet) + max(c.x for c in feet)) / 2
    AN_Z = HIP_Z * (0.037 / 0.837)
    AN = Vector((fcx, fmx_y - (0.112 - (-0.001)) / (0.112 - (-0.243)) * (fmx_y - fmn_y), AN_Z))
    print('TRIPO joints: crotch=%.3f hip=%.3f thigh=%s knee=%s ankle=%s foot_y=[%.3f..%.3f]' % (
        crotch, HIP_Z, tuple(round(a, 3) for a in th), tuple(round(a, 3) for a in kn), tuple(round(a, 3) for a in AN), fmn_y, fmx_y))
    print('TRIPO arm: shoulder=%s elbow=%s wrist=%s tip=%.3f' % (
        tuple(round(a, 3) for a in SH), tuple(round(a, 3) for a in EL), tuple(round(a, 3) for a in WR), tip))

    src = hero.copy(); src.data = me.copy(); src.name = 'TripoSrc'
    bpy.context.collection.objects.link(src)

    me.calc_loop_triangles()
    t0n = len(me.loop_triangles)
    if t0n > C['target_tris']:
        md = hero.modifiers.new('Dec', 'DECIMATE')
        md.ratio = C['target_tris'] / t0n
        md.use_collapse_triangulate = True
        bpy.context.view_layer.objects.active = hero
        bpy.ops.object.modifier_apply(modifier=md.name)
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bm.to_mesh(me); bm.free(); me.update()
    print('DECIMATE %d -> %d tris' % (t0n, W.tri_count(hero)))
    if C.get('ears'):                                    # a decimated ear collapses into a spike: pull it to the head
        E = C['ears']; ne = 0
        for v in me.vertices:
            c = v.co
            if E['z'][0] < c.z < E['z'][1] and E['y'][0] < c.y < E['y'][1] and abs(c.x) > E['x']:
                c.x = math.copysign(E['x'] + (abs(c.x) - E['x']) * E['keep'], c.x); ne += 1
        me.update()
        print('EARS %d verts beyond |x| %.3f pulled in (%.0f%% of the protrusion kept)' % (ne, E['x'], E['keep'] * 100))
    if coat:                                             # clean ring just under the coat hem: trousers below it go to the legs slot
        CUT_RAW = coat['hem_raw'] - 0.012
        bm = bmesh.new(); bm.from_mesh(me)
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=(0, 0, CUT_RAW), plane_no=(0, 0, 1))
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])
        bm.to_mesh(me); bm.free(); me.update()
    RAWZ = [v.co.z for v in me.vertices]                 # heights in the raw model, for hem / coat rules
    if coat:
        la = me.attributes.new('isleg', 'INT', 'FACE')
        for p in me.polygons:
            la.data[p.index].value = int(sum(RAWZ[i] for i in p.vertices) / len(p.vertices) < CUT_RAW)
        print('COAT cut under the hem at raw z %.3f: %d trouser tris, mesh %d tris' % (CUT_RAW, sum(d.value for d in la.data), W.tri_count(hero)))

    while me.uv_layers:
        me.uv_layers.remove(me.uv_layers[0])
    me.uv_layers.new(name='UVMap')
    W.smart_uv(hero)
    bimg = bpy.data.images.new(C['tex'][:-4], TEXRES, TEXRES, alpha=False)
    bmat = bpy.data.materials.new('_bake')
    bmat.use_nodes = True
    bn_ = bmat.node_tree.nodes.new('ShaderNodeTexImage')
    bn_.image = bimg
    bmat.node_tree.nodes.active = bn_
    me.materials.clear()
    me.materials.append(bmat)
    scn = bpy.context.scene
    scn.render.engine = 'CYCLES'
    scn.cycles.samples = 4
    scn.cycles.device = 'CPU'
    bk = scn.render.bake
    bk.use_selected_to_active = True
    bk.cage_extrusion = 0.012
    bk.max_ray_distance = 0.04
    bk.margin = 8
    bk.use_pass_direct = False
    bk.use_pass_indirect = False
    bk.use_pass_color = True
    bpy.ops.object.select_all(action='DESELECT')
    src.select_set(True); hero.select_set(True)
    bpy.context.view_layer.objects.active = hero
    bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'})
    bpy.data.objects.remove(src, do_unlink=True)
    print('REBAKE diffuse colour %d onto %d tris' % (TEXRES, W.tri_count(hero)))
    px = bimg.pixels[:]

    def texel(uv):
        x = min(TEXRES - 1, max(0, int(uv.x * TEXRES))); y = min(TEXRES - 1, max(0, int(uv.y * TEXRES)))
        i = (y * TEXRES + x) * 4
        return Vector((px[i], px[i + 1], px[i + 2]))

    def face_colours():
        uvl = me.uv_layers['UVMap'].data
        out = []
        for p in me.polygons:
            c = sum((uvl[li].uv for li in p.loop_indices), Vector((0, 0))) / len(p.loop_indices)
            pts = [c] + [c.lerp(uvl[li].uv, 0.5) for li in p.loop_indices]
            out.append(sum((texel(q) for q in pts), Vector((0, 0, 0))) / len(pts))
        return out

    def is_skin(c):
        return c[0] > 0.5 and c[0] > c[2] * 1.25

    # ---------- Tripo-proportioned copy of RootAnim ----------
    O = {b.name: (b.head_local.copy(), b.tail_local.copy()) for b in rig.data.bones}
    T = {}
    y0 = -0.001
    root = Vector((0, y0, HIP_Z))
    sp2 = Vector((0, y0, SP2_Z))
    T['C_Root'] = (root, root.lerp(sp2, 0.509))
    T['C_Spine01'] = (T['C_Root'][1], sp2)
    T['C_Spine02'] = (sp2, Vector((0, y0, NECK_Z)))
    T['C_Neck'] = (Vector((0, y0, NECK_Z)), Vector((0, y0, HEAD_Z)))
    T['C_Head'] = (Vector((0, y0, HEAD_Z)), Vector((0, y0, HEAD_Z)) + (O['C_Head'][1] - O['C_Head'][0]))
    for s, sx in (('L', 1), ('R', -1)):
        m = lambda v: Vector((v.x * sx, v.y, v.z))
        names = (('L_UpperArm', 'L_Shoulder', 'L_Arm', 'L_Hand') if s == 'L' else
                 ('R_UpperArm', 'R_Arm', 'Pelvis_009_R_002', 'R_Hand'))
        hand_len = (O[names[3]][1] - O[names[3]][0]).length
        hdir = (m(TIPP) - m(WR)).normalized()
        T[names[0]] = (sp2, m(SH))
        T[names[1]] = (m(SH), m(EL))
        T[names[2]] = (m(EL), m(WR))
        T[names[3]] = (m(WR), m(WR) + hdir * hand_len)
        thigh = Vector((th.x * sx, th.y, HIP_Z))
        knee = Vector((kn.x * sx, kn.y, KN_Z))
        ank = m(AN)
        T[s + '_Pelvis'] = (root, thigh)
        T[s + '_Thigh'] = (thigh, knee)
        T[s + '_Claf'] = (knee, ank)
        T[s + '_Foot'] = (ank, ank + (O[s + '_Foot'][1] - O[s + '_Foot'][0]))
    assert sorted(T) == sorted(O), set(O) ^ set(T)

    trig = rig.copy(); trig.data = rig.data.copy()
    trig.name = trig.data.name = 'TripoRig'
    bpy.context.collection.objects.link(trig)
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = trig
    trig.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    for eb in trig.data.edit_bones:
        eb.use_connect = False
    for eb in trig.data.edit_bones:
        eb.head, eb.tail = T[eb.name]
        eb.inherit_scale = 'NONE'
    bpy.ops.object.mode_set(mode='OBJECT')

    def heat_skin(mesh, arm_ob):
        for vg in list(mesh.vertex_groups):
            mesh.vertex_groups.remove(vg)
        for md in [m for m in mesh.modifiers if m.type == 'ARMATURE']:
            mesh.modifiers.remove(md)
        mesh.parent = None
        bpy.ops.object.select_all(action='DESELECT')
        mesh.select_set(True); arm_ob.select_set(True)
        bpy.context.view_layer.objects.active = arm_ob
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
        un = [v for v in mesh.data.vertices if not any(g.weight > 1e-4 for g in v.groups)]
        print('HEAT %s -> %s groups=%d unweighted=%d' % (mesh.name, arm_ob.name, len(mesh.vertex_groups), len(un)))
        assert len(mesh.vertex_groups) == 21, 'heat skin failed'
        if un:                                  # loose shells the heat solver skipped
            kd_src = [v for v in mesh.data.vertices if any(g.weight > 1e-4 for g in v.groups)]
            kd = kdtree.KDTree(len(kd_src))
            for i, v in enumerate(kd_src):
                kd.insert(v.co, i)
            kd.balance()
            gn = [g.name for g in mesh.vertex_groups]
            zs_ = [v.co.z for v in un]
            for v in un:
                _, i, _ = kd.find(v.co)
                for g in kd_src[i].groups:
                    mesh.vertex_groups[gn[g.group]].add([v.index], g.weight, 'REPLACE')
            print('  filled %d unweighted verts from the nearest skinned vertex (z %.3f..%.3f)' % (len(un), min(zs_), max(zs_)))

    heat_skin(hero, trig)
    # neck and head follow only the neck / head / upper spine bones: a stray clavicle weight on an ear is
    # stretched sideways by the arm-length fit and becomes a spike
    keepb = {'C_Spine02', 'C_Neck', 'C_Head'}
    gnm = {g.index: g.name for g in hero.vertex_groups}
    nfix = 0
    for v in me.vertices:
        if v.co.z < NECK_Z + 0.02 or abs(v.co.x) > 0.2:
            continue
        w = {gnm[g.group]: g.weight for g in v.groups if g.weight > 0}
        if all(k in keepb for k in w):
            continue
        good = {k: a for k, a in w.items() if k in keepb} or {'C_Head': 1.0}
        tot = sum(good.values())
        for g in list(v.groups):
            hero.vertex_groups[g.group].remove([v.index])
        for k, a in good.items():
            hero.vertex_groups[k].add([v.index], a / tot, 'REPLACE')
        nfix += 1
    print('HEAD weights for the fit: arm/clavicle weights removed on %d verts above z %.3f' % (nfix, NECK_Z + 0.02))
    order = []
    def walk(b):
        order.append(b.name)
        for c in b.children:
            walk(c)
    for b in trig.data.bones:
        if b.parent is None:
            walk(b)
    for bn in order:
        ob_b = rig.data.bones[bn]
        lt = (T[bn][1] - T[bn][0]).length
        if bn in ("L_Hand", "R_Hand"):
            S = Matrix.Diagonal((HAND_W, HAND_L, HAND_W, 1.0))
        else:
            S = Matrix.Diagonal((1.0, ob_b.length / lt, 1.0, 1.0))
        trig.pose.bones[bn].matrix = ob_b.matrix_local @ S
        bpy.context.view_layer.update()
    err = 0.0
    for bn in order:
        pb = trig.pose.bones[bn]
        err = max(err, (pb.head - O[bn][0]).length, 0 if bn in ("L_Hand", "R_Hand") else (pb.tail - O[bn][1]).length)
        print('  conform %-18s len T=%.3f O=%.3f scale=%.2f' % (bn, (T[bn][1] - T[bn][0]).length, rig.data.bones[bn].length,
                                                             rig.data.bones[bn].length / (T[bn][1] - T[bn][0]).length))
    print('CONFORM max joint error = %.5f m' % err)
    bpy.ops.object.select_all(action='DESELECT')
    hero.select_set(True)
    bpy.context.view_layer.objects.active = hero
    md = [m for m in hero.modifiers if m.type == 'ARMATURE'][0]
    bpy.ops.object.modifier_apply(modifier=md.name)
    hero.parent = None
    hero.matrix_world = Matrix.Identity(4)

    # ---------- thicken body ----------
    AXIAL = {'C_Root', 'C_Spine01', 'C_Spine02', 'L_Pelvis', 'R_Pelvis'}
    RADIAL = {'L_UpperArm', 'R_UpperArm', 'L_Shoulder', 'L_Arm', 'R_Arm', 'Pelvis_009_R_002',
              'L_Thigh', 'R_Thigh', 'L_Claf', 'R_Claf'}
    TA = C['thick_torso']

    def thick_at(bn, co):
        if bn in AXIAL:
            return Vector((co.x * TA, -0.001 + (co.y + 0.001) * TA, co.z))
        if bn in RADIAL:
            a, b = O[bn]
            ab = b - a
            t = max(0.0, min(1.0, (co - a).dot(ab) / ab.length_squared))
            p = a + ab * t
            return p + (co - p) * THICK_LIMB
        return co.copy()

    gname = {g.index: g.name for g in hero.vertex_groups}
    for v in me.vertices:
        if v.co.z > 1.50:                 # neck and head are never thickened (a stray clavicle weight turned an ear into a spike)
            continue
        ws = [(gname[g.group], g.weight) for g in v.groups if g.weight > 1e-4]
        tot = sum(w for _, w in ws)
        if tot <= 0:
            continue
        new = Vector((0, 0, 0))
        for bn, w in ws:
            new += thick_at(bn, v.co) * (w / tot)
        v.co = new
    me.update()
    zs = [v.co.z for v in me.vertices]
    print('THICKEN torso x%.2f limbs x%.2f: z=[%.3f..%.3f]' % (TA, THICK_LIMB, min(zs), max(zs)))
    bpy.data.objects.remove(trig, do_unlink=True)

    # ---------- FIT TO T0 at the slot cuts ----------
    if coat:
        # top of the trousers takes the T0 thigh shape, so the T0 pelvis grafted above it continues the leg
        ring = sorted(v.co.z for v in me.vertices if abs(RAWZ[v.index] - CUT_RAW) < 1e-4)
        cut_conf = ring[len(ring) // 2]
        legv = set()
        for p in me.polygons:
            if me.attributes['isleg'].data[p.index].value:
                legv.update(p.vertices)
        nth = 0
        for i in legv:
            c = me.vertices[i].co
            if abs(RAWZ[i] - CUT_RAW) < 1e-4:
                c.z = cut_conf
            if c.z < cut_conf - 0.08:
                continue
            sd = 1.0 if c.x > 0 else -1.0
            ax = sd * (0.105 + (0.837 - c.z) / (0.837 - 0.458) * 0.021)
            d = Vector((c.x - ax, c.y + 0.001, 0.0))
            hit = T0.ray_cast(Vector((ax, -0.001, min(c.z, cut_conf - 0.001))), d.normalized(), 0.4)[0] if d.length > 1e-5 else None
            if hit:
                w = smooth(cut_conf - 0.08, cut_conf - 0.015, c.z)
                q = 1 + w * (math.hypot(hit.x - ax, hit.y + 0.001) / d.length - 1)
                c.x = ax + d.x * q; c.y = -0.001 + d.y * q; nth += 1
        me.update()
        print('COAT trouser ring under the hem is at z=%.3f on our skeleton; %d trouser verts fitted to the T0 thighs' % (cut_conf, nth))
    jset, cset = set(), set()
    nclamp = 0
    if C.get('hem_raw'):
        # waist: everything from the hem of the top garment upwards is "garment" (raw heights)
        jset = {v.index for v in me.vertices if RAWZ[v.index] >= C['hem_raw'] - 0.004 and v.co.z < 1.05 and abs(v.co.x) < 0.33}
        edge = sorted(me.vertices[i].co.z for i in jset if RAWZ[i] < C['hem_raw'] + 0.03)
        hem = edge[len(edge) // 2]
        print('WAIST top-garment hem (raw z %.3f) is at z=%.3f after the fit to the skeleton -> %.3f (%d garment verts in the band)' % (
            C['hem_raw'], hem, HEM_Z, len(jset)))
        PW = [(0.84, 0.84), (hem, HEM_Z), (hem + 0.16, hem + 0.16)]
        for v in me.vertices:
            if 0.84 < v.co.z < hem + 0.16 and abs(v.co.x) < 0.33:
                v.co.z = H.pwl(v.co.z, PW)
        for v in me.vertices:
            if v.index in jset and v.co.z < HEM_Z:
                v.co.z = HEM_Z; nclamp += 1
            elif v.index not in jset and v.co.z > HEM_Z - 0.001 and 0.84 < v.co.z < 1.0 and abs(v.co.x) < 0.33 and RAWZ[v.index] < C['hem_raw'] - 0.004:
                v.co.z = HEM_Z - 0.001                  # trouser verts stay below the hem
    col = C.get('collar')
    if col:
        FC = face_colours()
        bm = bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
        def garment(f):
            return (not is_skin(FC[f.index])) and col['pred'](FC[f.index])
        def collar_ok(f):
            c = f.calc_center_median()
            if not garment(f) or abs(c.x) > 0.25 or max(RAWZ[v.index] for v in f.verts) > col['raw_cap']:
                return False
            if c.z > 1.50:
                r0 = t0_r(NECK_AX, c, min(c.z, 1.531))
                return r0 is None or math.hypot(c.x, c.y - NECK_AX) > r0 + 0.006
            return True
        seeds = [f for f in bm.faces if garment(f) and 1.30 < f.calc_center_median().z < 1.44 and abs(f.calc_center_median().x) < 0.2]
        got = set(f.index for f in seeds); st = list(seeds)
        while st:
            f = st.pop()
            for e in f.edges:
                for g in e.link_faces:
                    if g.index not in got and collar_ok(g):
                        got.add(g.index); st.append(g)
        cset = {v.index for fi in got for v in bm.faces[fi].verts if v.co.z > 1.44}
        bm.free()
        ctop = max([me.vertices[i].co.z for i in cset] or [0])
        nsq = 0
        if ctop > COLLAR_TOP:
            for i in cset:
                c = me.vertices[i].co
                if c.z > 1.47:
                    c.z = 1.47 + (c.z - 1.47) * (COLLAR_TOP - 1.47) / (ctop - 1.47); nsq += 1
        print('NECK collar: %d verts, top %.3f -> %.3f (%d squeezed)' % (len(cset), ctop, min(ctop, COLLAR_TOP), nsq))

    nold = len(me.vertices)
    old = [v.co.copy() for v in me.vertices]
    bm = bmesh.new(); bm.from_mesh(me)
    for z in C['planes']:
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=(0, 0, z), plane_no=(0, 0, 1))
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])
    bm.to_mesh(me); bm.free(); me.update()
    assert max((me.vertices[i].co - old[i]).length for i in range(nold)) < 1e-6
    print("CUT planes %s: tris = %d (+%d verts on the planes)" % (C['planes'], W.tri_count(hero), len(me.vertices) - nold))

    nw = nn = npw = npn = 0
    if coat:
        # the coat stays outside the T0 trouser ring it covers (the pelvis graft carries that ring)
        cv = set()
        for p in me.polygons:
            if not me.attributes['isleg'].data[p.index].value:
                cv.update(p.vertices)
        for i in cv:
            c = me.vertices[i].co
            if 0.83 < c.z < 0.96 and abs(c.x) < 0.33:
                r0 = t0_r(WAIST_AX, c, min(max(c.z, 0.86), 0.908)); r = math.hypot(c.x, c.y - WAIST_AX)
                if r0 and r < r0 + 0.02:
                    q = (r0 + 0.02) / r
                    c.x *= q; c.y = WAIST_AX + (c.y - WAIST_AX) * q; npw += 1
    for v in me.vertices:
        c = v.co
        if v.index in jset:
            if c.z < 1.0:
                r0 = t0_r(WAIST_AX, c, 0.905); r = math.hypot(c.x, c.y - WAIST_AX)
                if r0 and r < r0 + 0.014:
                    q = (r0 + 0.014) / r
                    c.x *= q; c.y = WAIST_AX + (c.y - WAIST_AX) * q; npw += 1
        elif C.get('hem_raw') and 0.84 < c.z < HEM_Z - 0.0005 and abs(c.x) < 0.33:
            w = smooth(0.84, 0.885, c.z)
            r0 = t0_r(WAIST_AX, c, min(max(c.z, 0.89), 0.911)); r = math.hypot(c.x, c.y - WAIST_AX)
            if r0 and r > 1e-4:
                q = 1 + w * (r0 / r - 1)
                c.x *= q; c.y = WAIST_AX + (c.y - WAIST_AX) * q; nw += 1
        elif v.index in cset:
            r0 = t0_r(NECK_AX, c, min(max(c.z, 1.50), 1.531)); r = math.hypot(c.x, c.y - NECK_AX)
            if r0 and c.z > 1.49 and r < r0 + 0.012:
                q = (r0 + 0.012) / r
                c.x *= q; c.y = NECK_AX + (c.y - NECK_AX) * q; npn += 1
        elif C.get('neck_fit') and 1.49 < c.z < 1.60 and abs(c.x) < 0.2:
            w = smooth(1.49, 1.525, c.z) * (1 - smooth(1.556, 1.60, c.z))
            r0 = t0_r(NECK_AX, c, c.z); r = math.hypot(c.x, c.y - NECK_AX)
            if r0 and r > 1e-4 and w > 0 and (c.z <= 1.556 or abs(r0 - r) < 0.015):   # above the cut band do not drag ears to the T0 ears
                q = 1 + w * (r0 / r - 1)
                c.x *= q; c.y = NECK_AX + (c.y - NECK_AX) * q; nn += 1
    me.update()
    print('FIT waist: %d verts to the T0 trouser ring, %d hem verts clamped to z %.3f, %d pushed outside' % (nw, nclamp, HEM_Z, npw))
    print('FIT neck: %d verts to the T0 neck/chin surface, %d collar verts pushed outside' % (nn, npn))

    if C.get('nape_fill'):
        FC = face_colours()
        uvl = me.uv_layers['UVMap'].data
        skinf = [p for p, c in zip(me.polygons, FC) if is_skin(c)]
        chin = min(skinf, key=lambda p: (Vector(p.center) - Vector(C['skin_at'])).length)
        cuv = sum((uvl[li].uv for li in chin.loop_indices), Vector((0, 0))) / len(chin.loop_indices)
        nnape = 0
        for p in me.polygons:
            vv = [me.vertices[vi] for vi in p.vertices]
            c = Vector(p.center)
            if c.y <= -0.04 or any(v.index in cset for v in vv) or is_skin(FC[p.index]):
                continue
            if min(v.co.z for v in vv) < 1.499 or max(v.co.z for v in vv) > 1.61 or c.z > 1.565:
                continue
            ok = True
            for v in vv:
                r0 = t0_r(NECK_AX, v.co, min(v.co.z, 1.556))
                if r0 is None or math.hypot(v.co.x, v.co.y - NECK_AX) > r0 + (0.008 if v.co.z < 1.556 else 0.03):
                    ok = False
            if ok:
                for li in p.loop_indices:
                    uvl[li].uv = cuv
                nnape += 1
        print('NAPE skin fill: %d faces -> texel %s' % (nnape, tuple(round(a, 2) for a in texel(cuv))))

    # ---------- final skin on RootAnim ----------
    heat_skin(hero, rig)
    bpy.ops.object.select_all(action='DESELECT')
    hero.select_set(True)
    bpy.context.view_layer.objects.active = hero
    bpy.ops.object.vertex_group_clean(group_select_mode='ALL', limit=0.05)
    bpy.ops.object.vertex_group_limit_total(group_select_mode='ALL', limit=4)
    bpy.ops.object.vertex_group_normalize_all(group_select_mode='ALL', lock_active=False)

    # upper-body weight fix (same as the hero, 09-27: clavicles roll ~90 deg in melee/aim)
    CLAV = {'L_UpperArm': 'L_Shoulder', 'R_UpperArm': 'R_Arm'}
    for bn in ('C_Root', 'C_Spine01', 'C_Spine02', 'C_Neck', 'L_Shoulder', 'R_Arm', 'L_Thigh', 'R_Thigh'):
        if bn not in hero.vertex_groups:
            hero.vertex_groups.new(name=bn)
    VG = {g.name: g for g in hero.vertex_groups}
    gname = {g.index: g.name for g in hero.vertex_groups}
    nclav = nhead = 0
    for v in me.vertices:
        w = {gname[g.group]: g.weight for g in v.groups if g.weight > 0}
        add = {}
        for cl, armb in CLAV.items():
            wc = w.pop(cl, 0.0)
            if wc <= 0:
                continue
            nclav += 1
            s = smooth(0.20, 0.32, abs(v.co.x))
            t = smooth(1.22, 1.34, v.co.z)
            add[armb] = add.get(armb, 0.0) + wc * s
            add['C_Spine02'] = add.get('C_Spine02', 0.0) + wc * (1 - s) * t
            add['C_Spine01'] = add.get('C_Spine01', 0.0) + wc * (1 - s) * (1 - t)
        if v.co.z < 1.50 and w.get('C_Head', 0) > 0:
            nhead += 1
            add['C_Neck'] = add.get('C_Neck', 0.0) + w.pop('C_Head')
        if not add:
            continue
        for q, a in add.items():
            w[q] = w.get(q, 0.0) + a
        for cl in CLAV:
            VG[cl].remove([v.index])
        if 'C_Head' not in w:
            VG['C_Head'].remove([v.index])
        for q, a in w.items():
            VG[q].add([v.index], a, 'REPLACE')
    print('WEIGHT FIX: clavicle weights moved on %d verts, head->neck below chin on %d verts' % (nclav, nhead))

    if coat:
        # coat skirts: below the waist the coat follows the thigh of its side, so a stepping leg carries
        # its half of the skirt instead of poking through it; blended across the middle and up to the waist
        isleg = [d.value for d in me.attributes['isleg'].data]
        coatv = set()
        for p in me.polygons:
            if not isleg[p.index]:
                coatv.update(p.vertices)
        nsk = 0
        for v in me.vertices:
            if v.index not in coatv or v.co.z > coat['heat_full'] or abs(v.co.x) > 0.45:
                continue
            h = smooth(coat['heat_from'], coat['heat_full'], v.co.z)            # share of the automatic weights
            t = 1 - smooth(coat['skirt_full'], coat['skirt_top'], v.co.z)       # share of the thighs in the rest
            wl = smooth(-0.05, 0.05, v.co.x)
            w = {gname[g.group]: g.weight * h for g in v.groups if g.weight > 0}
            for bn, a in (('C_Root', (1 - h) * (1 - t)), ('L_Thigh', (1 - h) * t * wl), ('R_Thigh', (1 - h) * t * (1 - wl))):
                w[bn] = w.get(bn, 0.0) + a
            for g in list(v.groups):
                hero.vertex_groups[g.group].remove([v.index])
            for q, a in w.items():
                if a > 1e-4:
                    VG[q].add([v.index], a, 'REPLACE')
            nsk += 1
        print('COAT skirts: %d verts: pelvis bone between z %.2f and %.2f, thigh bones below (full below %.2f)' % (nsk, coat['skirt_top'], coat['heat_from'], coat['skirt_full']))
    bpy.ops.object.vertex_group_clean(group_select_mode='ALL', limit=0.02)
    bpy.ops.object.vertex_group_limit_total(group_select_mode='ALL', limit=4)
    bpy.ops.object.vertex_group_normalize_all(group_select_mode='ALL', lock_active=False)
    left = sum(1 for v in me.vertices for g in v.groups if gname[g.group] in CLAV and g.weight > 0)
    print('WEIGHTS clavicle weights left: %d' % left)
    W.rebind(hero, rig)

    # ---------- material (one texture) ----------
    bimg.filepath_raw = TEX
    bimg.file_format = 'PNG'
    bimg.save()
    bimg.filepath = TEX
    mat = bpy.data.materials.new(C['mat'])
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Metallic'].default_value = 0.0
    bsdf.inputs['Roughness'].default_value = 0.8
    tx = nt.nodes.new('ShaderNodeTexImage')
    tx.image = bimg
    nt.links.new(tx.outputs['Color'], bsdf.inputs['Base Color'])
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    me.materials.clear()
    me.materials.append(mat)
    for p in me.polygons:
        p.material_index = 0
        p.use_smooth = False

    # ---------- split into slots ----------
    isleg = [d.value for d in me.attributes['isleg'].data] if coat else None
    if coat:
        keep = {'Head': lambda p: p.center.z > 1.532,
                'Torso': lambda p: p.center.z < 1.549 and not isleg[p.index],
                'Legs': lambda p: bool(isleg[p.index])}
        hem_conf = cut_conf
    else:
        keep = {'Head': lambda p: p.center.z > 1.532,
                'Torso': lambda p: 0.900 < p.center.z < 1.549,
                'Legs': lambda p: p.center.z < 0.910}
    parts = []
    for sname in ('Head', 'Torso', 'Legs'):
        name = C['prefix'] + sname
        ob = hero.copy(); ob.data = me.copy()
        ob.name = ob.data.name = name
        bpy.context.collection.objects.link(ob)
        flags = [keep[sname](p) for p in me.polygons]
        bm = bmesh.new(); bm.from_mesh(ob.data); bm.faces.ensure_lookup_table()
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if not flags[f.index]], context='FACES')
        if coat and sname == 'Legs':
            # pelvis graft: the T0 trousers from the coat hem up to the waist cut, flat trouser colour;
            # the T0 legs also carry a strip of the sweater hem (wide ring above 0.865) - left out
            uvl = bm.loops.layers.uv.active
            dl = bm.verts.layers.deform.verify()
            tf = min(bm.faces, key=lambda f: (f.calc_center_median() - Vector(coat['trouser_at'])).length)
            tuv = sum((l[uvl].uv for l in tf.loops), Vector((0, 0))) / 3
            def on_strip(c):            # not on the innermost T0 surface seen from the axis = the sweater strip lying over the trousers
                if c.z < 0.80:
                    return False
                r0 = t0_r(WAIST_AX, c, min(c.z, 0.9095))
                return r0 is not None and math.hypot(c.x, c.y - WAIST_AX) > r0 + 0.004
            gb = bmesh.new()
            dl0 = gb.verts.layers.deform.verify()
            gv = []
            for i, c in enumerate(G_CO):
                nv = gb.verts.new(c)
                for k, w in G_W[i].items():
                    nv[dl0][k] = w
                gv.append(nv)
            for fv in G_F:
                gb.faces.new([gv[i] for i in fv])
            bmesh.ops.bisect_plane(gb, geom=gb.verts[:] + gb.edges[:] + gb.faces[:], dist=1e-5, plane_co=(0, 0, hem_conf),
                                   plane_no=(0, 0, 1), clear_inner=True)
            bmesh.ops.triangulate(gb, faces=[f for f in gb.faces if len(f.verts) > 3])
            gi = {g.name: g.index for g in ob.vertex_groups}
            for bn in ('L_Thigh', 'R_Thigh', 'C_Root'):
                if bn not in gi:
                    gi[bn] = ob.vertex_groups.new(name=bn).index
            for k in {k for w in G_W for k in w}:
                if gn0[k] not in gi:
                    gi[gn0[k]] = ob.vertex_groups.new(name=gn0[k]).index
            new = {}
            ng = 0
            for f0 in gb.faces:
                if any(on_strip(v.co) for v in f0.verts):
                    continue
                for v in f0.verts:
                    if v not in new:
                        sq = 1 - 0.18 * smooth(hem_conf, hem_conf + 0.05, v.co.z) * (1 - smooth(0.875, 0.905, v.co.z))   # keep clear of the coat between the two rings
                        nv = bm.verts.new(Vector((v.co.x * sq, -0.001 + (v.co.y + 0.001) * sq, v.co.z)))
                        # same thigh rule as the coat skirts, so the pelvis moves with the coat and stays inside it
                        t = 1 - smooth(coat['skirt_full'], coat['skirt_top'], v.co.z)
                        wl = smooth(-0.05, 0.05, v.co.x)
                        # (the T0 weights put the buttocks on the thighs: they came out through the back of the coat)
                        for bn, w in (('C_Root', 1 - t), ('L_Thigh', t * wl), ('R_Thigh', t * (1 - wl))):
                            if w > 1e-4:
                                nv[dl][gi[bn]] = nv[dl].get(gi[bn], 0.0) + w
                        new[v] = nv
                f = bm.faces.new([new[v] for v in f0.verts])
                for l in f.loops:
                    l[uvl].uv = tuv
                ng += 1
            gb.free()
            print('GRAFT T0 pelvis: %d tris from z %.3f to 0.910, trouser texel %s' % (ng, hem_conf, tuple(round(a, 2) for a in texel(tuv))))
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])
        bm.to_mesh(ob.data); bm.free(); ob.data.update()
        for p in ob.data.polygons:
            p.use_smooth = False
        for a in [a for a in ob.data.attributes if a.name == 'isleg']:
            ob.data.attributes.remove(a)
        used = {ob.vertex_groups[g.group].name for v in ob.data.vertices for g in v.groups if g.weight > 1e-4}
        for vg in list(ob.vertex_groups):
            if vg.name not in used:
                ob.vertex_groups.remove(vg)
        W.rebind(ob, rig)
        zs = [v.co.z for v in ob.data.vertices]
        print('SLOT %-18s tris=%d verts=%d z=[%.3f..%.3f] groups=%s' % (
            name, W.tri_count(ob), len(ob.data.vertices), min(zs), max(zs), sorted(g.name for g in ob.vertex_groups)))
        parts.append(ob)
    print('TOTAL tris = %d' % sum(W.tri_count(o) for o in parts))
    bpy.data.objects.remove(hero, do_unlink=True)
    bpy.ops.wm.save_as_mainfile(filepath=WORK + C['id'] + '_work.blend')
    print('SAVED', WORK + C['id'] + '_work.blend')
