"""Is the re-exported tent FBX the same mesh and UV as the delivered one? Run: blender -b --factory-startup --python tent_cmp.py"""
import bpy, sys
import numpy as np
sys.path.insert(0, 'E:/game-dev-team/assets/scientist_base/_work')
import sb
def load(p):
    sb.empty(); bpy.ops.import_scene.fbx(filepath=p)
    o = [o for o in bpy.data.objects if o.type == 'MESH'][0]; me = o.data
    co = np.array([o.matrix_world @ v.co for v in me.vertices]); pv = np.zeros(len(me.loops), np.int32); me.loops.foreach_get('vertex_index', pv)
    return co[pv], {u.name: sb.uvtris(me, u.name).reshape(-1, 2) for u in me.uv_layers}
a, ua = load(sb.WORK + '_tent_old.fbx'); b, ub = load(sb.ROOT + 'SM_ArmyTent/SM_ArmyTent.fbx')
same = a.shape == b.shape
print('COMPARE corners %d vs %d; max position difference %.7f m; UV difference: %s' % (len(a), len(b), np.abs(a - b).max() if same else -1, {k: float(np.abs(ua[k] - ub[k]).max()) for k in ua} if same else 'n/a'))
