import bpy, bmesh, sys, glob
import numpy as np
import addon_utils
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W
OUT = 'E:/game-dev-team/assets/weapons_tripo/_work/_look/'
def dump(tag, obs):
    for o in obs:
        me = o.data; mw = o.matrix_world
        cs = np.array([mw @ v.co for v in me.vertices])
        print(tag, o.name, 'tris', sum(len(p.vertices) - 2 for p in me.polygons), 'verts', len(me.vertices), 'min', cs.min(0).round(4), 'max', cs.max(0).round(4), 'size', (cs.max(0) - cs.min(0)).round(4),
              'loc', tuple(round(a, 4) for a in mw.to_translation()), 'rot', tuple(round(a, 3) for a in mw.to_euler()), 'scale', tuple(round(a, 3) for a in mw.to_scale()),
              'uv', [u.name for u in me.uv_layers], 'cols', [c.name for c in me.color_attributes], 'mats', [m.name for m in me.materials if m])
for f in sorted(glob.glob('E:/game-dev-team/assets/pistol/*.fbx') + glob.glob('E:/game-dev-team/assets/knife/*.fbx') + ['E:/ForGameLead(Materials)/demo-assets/SM_Pistol.fbx']):
    bpy.ops.wm.read_factory_settings(use_empty=True); addon_utils.enable('io_scene_fbx')
    bpy.ops.import_scene.fbx(filepath=f); bpy.context.view_layer.update()
    dump('OLD ' + f.replace(chr(92), '/').split('assets/')[-1], [o for o in bpy.data.objects if o.type == 'MESH'])
for n in ('pistol_pm', 'knife'):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath='E:/ContrarySurvior/ContrarySurvivor/Saved/Tripo/%s/%s.glb' % (n, n)); bpy.context.view_layer.update()
    obs = [o for o in bpy.data.objects if o.type == 'MESH']
    dump('GLB ' + n, obs)
    for im in bpy.data.images: print('IMG', n, im.name, tuple(im.size))
    for p in obs[0].data.polygons: p.use_smooth = False
    sc, cam, suns = W.setup_render(res=700); sc.render.film_transparent = False
    for vn, vd in (('px', (1, 0, 0.05)), ('my', (0, -1, 0.05)), ('top', (0.001, -0.02, 1)), ('q', (1, -1, 0.6))):
        W.frame_and_shoot(obs, vd, OUT + '%s_%s.png' % (n, vn), suns=suns)
