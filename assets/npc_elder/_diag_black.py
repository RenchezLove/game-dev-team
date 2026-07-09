"""Diagnostic (rule C: measure, don't guess): re-import the exported FBX and
count how many vertex colors are BLACK (0,0,0). Answers game-lead's question —
are the 76% black verts on the armor a paint bug, or normal hidden geometry?
Reports per FBX: black corners %, black verts % (a vert = black if EVERY loop
touching it is black), and whether black verts sit on interior (base body) or
surface. Run: blender.exe -b --factory-startup --python _diag_black.py
"""
import bpy, addon_utils, os

FILES = [
    'E:/game-dev-team/assets/armor_wearables/SK_Armor_T2_Torso.fbx',
    'E:/game-dev-team/assets/armor_wearables/SK_Cloth_T0_Torso.fbx',
    'E:/game-dev-team/assets/npc_elder/SK_Elder_Torso.fbx',
    'E:/game-dev-team/assets/npc_elder/SK_Elder_Head.fbx',
    'E:/game-dev-team/assets/npc_elder/SK_Elder_Legs.fbx',
]


def is_black(c, eps=0.02):
    return c[0] < eps and c[1] < eps and c[2] < eps


for path in FILES:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    addon_utils.enable('io_scene_fbx')
    bpy.ops.import_scene.fbx(filepath=path)
    meshes = [o for o in bpy.data.objects if o.type == 'MESH']
    for ob in meshes:
        me = ob.data
        ca = me.color_attributes.get('Col') or (me.color_attributes[0] if me.color_attributes else None)
        if ca is None:
            print('%-26s NO COLOR ATTR' % os.path.basename(path))
            continue
        dom = ca.domain
        n = len(ca.data)
        # corner or point domain
        black = sum(1 for d in ca.data if is_black(d.color))
        # per-vertex: black if all loops on the vert are black
        vblack = 0
        vcount = len(me.vertices)
        if dom == 'CORNER':
            per_v_allblack = [True] * vcount
            per_v_seen = [False] * vcount
            for poly in me.polygons:
                for li in poly.loop_indices:
                    vi = me.loops[li].vertex_index
                    per_v_seen[vi] = True
                    if not is_black(ca.data[li].color):
                        per_v_allblack[vi] = False
            vblack = sum(1 for i in range(vcount) if per_v_seen[i] and per_v_allblack[i])
        else:  # POINT
            vblack = black
        print('%-26s dom=%s attr_n=%d black_attr=%d(%.0f%%) verts=%d vblack=%d(%.0f%%)' % (
            os.path.basename(path), dom, n, black, 100.0 * black / max(1, n),
            vcount, vblack, 100.0 * vblack / max(1, vcount)))
print('DIAG DONE')
