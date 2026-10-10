"""Stored normals of every delivered FBX against the geometric face normals (the check asked for after the tent): any face whose saved
vertex normal looks against the face = FAIL.  Run: blender -b --factory-startup --python 95_normals_all.py"""
import bpy, sys, glob, os
sys.path.insert(0, 'E:/game-dev-team/assets/scientist_base/_work')
import sb
files = sorted(glob.glob('E:/game-dev-team/assets/scientist_base/SM_*/*.fbx') + glob.glob('E:/game-dev-team/assets/abandoned_car_tripo/broken/*.fbx') + glob.glob('E:/game-dev-team/assets/scientist_tripo/*.fbx'))
allok = True
for f in files:
    sb.empty(); bpy.ops.import_scene.fbx(filepath=f); bpy.context.view_layer.update()
    for o in [o for o in bpy.data.objects if o.type == 'MESH']:
        bad, low = sb.stored_normals(o)
        closed = sum(1 for e in o.data.edges if False)
        bm = sb.bm_of(o); import bmesh; bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6); op = sum(1 for e in bm.edges if len(e.link_faces) != 2); bm.free()
        print('NORMALS %-34s faces %4d, saved normal against the face: %4d (lowest dot %+.3f), edges without exactly two faces %3d -> %s' % (os.path.basename(f), len(o.data.polygons), bad, low, op, 'ok' if bad == 0 else 'FAIL'))
        allok &= bad == 0
print('NORMALS ALL', 'PASS' if allok else 'FAIL')
