"""Dump real per-module facts from elder_work.blend for the asset passport
(rule C: numbers from the actual file, not memory)."""
import bpy, sys
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W

bpy.ops.wm.open_mainfile(filepath='E:/game-dev-team/assets/npc_elder/_work/elder_work.blend')
for n in ('SK_Elder_Head', 'SK_Elder_Torso', 'SK_Elder_Legs'):
    ob = bpy.data.objects[n]
    me = ob.data
    xs = [v.co.x for v in me.vertices]; ys = [v.co.y for v in me.vertices]; zs = [v.co.z for v in me.vertices]
    mats = [m.name for m in me.materials]
    print('%-18s tris=%d verts=%d faces=%d mats=%s uv=%s x=[%.3f..%.3f] y=[%.3f..%.3f] z=[%.3f..%.3f]' % (
        n, W.tri_count(ob), len(me.vertices), len(me.polygons), mats,
        [u.name for u in me.uv_layers],
        min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)))
