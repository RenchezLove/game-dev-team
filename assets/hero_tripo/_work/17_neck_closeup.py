import bpy, sys
sys.path.insert(0, 'E:/game-dev-team/assets/hero_tripo/_work')
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W, hpose as P
OUT = 'E:/game-dev-team/assets/hero_tripo/renders/skin/'
sc, cam, suns = W.setup_render(res=560)
P.shoot((0.3, 1, 0.5), (0, 0, 1.52), 0.40, OUT + 'after_neck_back_closeup.png', suns)
grey = bpy.data.materials.new('grey')
for n in ('SK_Cloth_T0_Head', 'SK_Cloth_T0_Torso'):
    me = bpy.data.objects[n].data; me.materials[0] = grey
P.shoot((0.3, 1, 0.5), (0, 0, 1.52), 0.40, OUT + '_neck_grey.png', suns)
