"""Do both heads sit on the scientist torso without a gap: his own head and the hero head in the cap (SK_Armor_T1_Head)?
The lowest ring of each head (z 1.532) against the surface of the scientist torso, and the torso top ring (1.549) against each head.
Run: blender.exe -b --factory-startup --python 16_heads_fit.py"""
import bpy, sys
import numpy as np
sys.path.insert(0, 'E:/game-dev-team/assets/scientist_base/_work')
import sb
from mathutils.bvhtree import BVHTree
def load(p):
    before = set(bpy.data.objects); bpy.ops.import_scene.fbx(filepath=p); bpy.context.view_layer.update()
    o = [o for o in bpy.data.objects if o not in before and o.type == 'MESH'][0]
    V = [o.matrix_world @ v.co for v in o.data.vertices]; F = [list(p.vertices) for p in o.data.polygons]
    return V, F
sb.empty()
A = 'E:/game-dev-team/assets/'
TV, TF = load(A + 'scientist_tripo/SK_Scientist_Torso.fbx'); tt = BVHTree.FromPolygons(TV, TF)
top = [v for v in TV if abs(v.z - 1.549) < 1e-3]
for nm, p in (('own head SK_Scientist_Head', A + 'scientist_tripo/SK_Scientist_Head.fbx'), ('hero head in the cap SK_Armor_T1_Head', A + 'armor_t1_tripo/SK_Armor_T1_Head.fbx'), ('hero head T0', A + 'hero_tripo/SK_Cloth_T0_Head.fbx')):
    try:
        HV, HF = load(p)
    except Exception as e:
        print('HEAD %s: file not loaded (%s)' % (nm, e)); continue
    ht = BVHTree.FromPolygons(HV, HF)
    zmin = min(v.z for v in HV); ring = [v for v in HV if v.z < zmin + 1e-3]
    d1 = np.array([tt.find_nearest(v)[3] for v in ring]); d2 = np.array([ht.find_nearest(v)[3] for v in top])
    print('HEAD %s: lowest z %.3f, ring of %d points lies on the scientist torso within max %.4f m (mean %.4f); torso top ring (%d points at z 1.549) lies on this head within max %.4f m (mean %.4f)' % (
        nm, zmin, len(ring), d1.max(), d1.mean(), len(top), d2.max(), d2.mean()))
