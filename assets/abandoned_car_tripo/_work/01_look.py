"""Look at a blend's meshes from 6 directions (own QC only). args: blend-relative out prefix"""
import bpy, sys, os
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W
tag = sys.argv[sys.argv.index('--') + 1]
wire = '--wire' in sys.argv
OUT = 'E:/game-dev-team/assets/abandoned_car_tripo/_work/_look/'
os.makedirs(OUT, exist_ok=True)
obs = [o for o in bpy.data.objects if o.type == 'MESH' and not o.hide_render]
sc, cam, suns = W.setup_render(res=900)
if wire:
    for o in obs:
        m = o.modifiers.new('wf', 'WIREFRAME'); m.thickness = 0.004; m.use_replace = False
        m.material_offset = 1
        mat = bpy.data.materials.new('wire'); mat.diffuse_color = (1, 0.1, 0.6, 1)
        mat.use_nodes = True; mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (1, 0.05, 0.5, 1)
        o.data.materials.append(mat)
for n, d in (('side', (1, 0, 0.02)), ('top', (0.001, 0, 1)), ('front', (0, 1, 0.1)), ('back', (0, -1, 0.1)),
             ('under', (0.001, 0, -1)), ('q34', (1, 1.2, 0.9))):
    W.frame_and_shoot(obs, d, OUT + '%s_%s.png' % (tag, n), margin=1.03, suns=suns)
