import bpy, sys, math
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
from mathutils import Vector, Matrix
def dump(tag):
    for o in bpy.data.objects:
        print(tag, 'OBJ', o.name, o.type, 'parent', o.parent.name if o.parent else None, 'loc', tuple(round(a, 3) for a in o.matrix_world.to_translation()),
              'rot', tuple(round(a, 3) for a in o.matrix_world.to_euler()), 'scl', tuple(round(a, 3) for a in o.matrix_world.to_scale()))
        if o.type == 'MESH':
            me = o.data
            cs = [o.matrix_world @ v.co for v in me.vertices]
            print(tag, '  tris', sum(len(p.vertices) - 2 for p in me.polygons), 'verts', len(me.vertices), 'x %.3f..%.3f y %.3f..%.3f z %.3f..%.3f' % (
                min(c.x for c in cs), max(c.x for c in cs), min(c.y for c in cs), max(c.y for c in cs), min(c.z for c in cs), max(c.z for c in cs)),
                'uv', [u.name for u in me.uv_layers], 'cols', [c.name for c in me.color_attributes], 'mats', [m.name for m in me.materials if m],
                'groups', len(o.vertex_groups), 'mods', [(m.type, getattr(m, 'object', None) and m.object.name) for m in o.modifiers])
        if o.type == 'ARMATURE':
            for b in o.data.bones:
                print(tag, '  BONE %-13s parent=%-13s head=(%.3f,%.3f,%.3f) tail=(%.3f,%.3f,%.3f) connect=%s' % (b.name, b.parent.name if b.parent else '-', *b.head_local, *b.tail_local, b.use_connect))
            print(tag, '  action', o.animation_data.action.name if o.animation_data and o.animation_data.action else None)
    print(tag, 'ACTIONS', [(a.name, tuple(a.frame_range)) for a in bpy.data.actions], 'fps', bpy.context.scene.render.fps)
bpy.ops.wm.open_mainfile(filepath='E:/ForGameLead(Materials)/phase3-assets/_build/wolf.blend'); dump('SRC')
bpy.ops.wm.open_mainfile(filepath='E:/game-dev-team/assets/anim_wolf/_work/_qc_wolf_death.blend'); dump('DEATH')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath='E:/ContrarySurvior/ContrarySurvivor/Saved/Tripo/wolf/wolf.glb')
bpy.context.view_layer.update(); dump('GLB')
for im in bpy.data.images: print('IMG', im.name, tuple(im.size))
import wcommon as W
tr = [o for o in bpy.data.objects if o.type == 'MESH'][0]
sc, cam, suns = W.setup_render(res=800); sc.render.film_transparent = False
for vn, vd in (('px', (1, 0, 0.1)), ('mx', (-1, 0, 0.1)), ('py', (0, 1, 0.1)), ('my', (0, -1, 0.1)), ('top', (0.001, -0.02, 1)), ('q', (1, -1, 0.6))):
    W.frame_and_shoot([tr], vd, 'E:/game-dev-team/assets/wolf_tripo/_work/_look/raw_%s.png' % vn, suns=suns)
