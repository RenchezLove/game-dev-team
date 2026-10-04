import bpy, sys
import numpy as np
import addon_utils
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W
OUT = 'E:/game-dev-team/assets/weapons_tripo/_work/_look/'
for tag, f in (('pistol', 'E:/ForGameLead(Materials)/demo-assets/SM_Pistol.fbx'), ('knife', 'E:/ForGameLead(Materials)/phase3-assets/SM_Knife.fbx')):
    bpy.ops.wm.read_factory_settings(use_empty=True); addon_utils.enable('io_scene_fbx')
    bpy.ops.import_scene.fbx(filepath=f); bpy.context.view_layer.update()
    o = [o for o in bpy.data.objects if o.type == 'MESH'][0]; me = o.data
    cs = np.array([o.matrix_world @ v.co for v in me.vertices])
    print('OLD', tag, 'slices along Y (cm): y | x range | z range | n')
    for y0 in np.arange(np.floor(cs[:, 1].min() * 50) / 50, cs[:, 1].max() + 1e-6, 0.02):
        q = (cs[:, 1] >= y0 - 1e-6) & (cs[:, 1] < y0 + 0.02 - 1e-6)
        if q.any():
            print('OLD %s y %+5.1f..%+5.1f x %+5.1f..%+5.1f z %+5.1f..%+5.1f n=%d' % (tag, y0 * 100, y0 * 100 + 2, cs[q, 0].min() * 100, cs[q, 0].max() * 100, cs[q, 2].min() * 100, cs[q, 2].max() * 100, q.sum()))
    ca = me.color_attributes[0] if me.color_attributes else None
    if ca:
        mat = bpy.data.materials.new('v'); mat.use_nodes = True
        vc = mat.node_tree.nodes.new('ShaderNodeVertexColor'); vc.layer_name = ca.name
        mat.node_tree.links.new(vc.outputs['Color'], mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
        me.materials.clear(); me.materials.append(mat)
    sc, cam, suns = W.setup_render(res=700); sc.render.film_transparent = False
    for vn, vd in (('px', (1, 0, 0.05)), ('top', (0.001, -0.02, 1)), ('q', (1, -1, 0.6))):
        W.frame_and_shoot([o], vd, OUT + 'old_%s_%s.png' % (tag, vn), suns=suns)
