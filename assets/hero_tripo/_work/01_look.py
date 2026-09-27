import bpy, sys, math
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W
from mathutils import Vector
OUT='E:/game-dev-team/assets/hero_tripo/_work/_look/'
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath='E:/ContrarySurvior/ContrarySurvivor/Saved/Tripo/hero.glb')
ob=[o for o in bpy.data.objects if o.type=='MESH'][0]
sc,cam,suns=W.setup_render(700)
for nm,d in (('px',(1,0,0)),('nx',(-1,0,0)),('py',(0,1,0)),('ny',(0,-1,0))):
    W.frame_and_shoot([ob], d, OUT+'tripo_%s.png'%nm, suns=suns)
