"""Close-ups of slot seams (neck, waist) and face, rest pose vs Tripo source."""
import bpy, sys, math
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W
from mathutils import Vector
OUT = 'E:/game-dev-team/assets/hero_tripo/renders/'
bpy.ops.wm.open_mainfile(filepath='E:/game-dev-team/assets/hero_tripo/_work/hero_work.blend')
parts = [bpy.data.objects[n] for n in ('SK_Cloth_T0_Head', 'SK_Cloth_T0_Torso', 'SK_Cloth_T0_Legs')]
sc, cam, suns = W.setup_render(res=700)
cam.data.type = 'ORTHO'
def shot(center, size, d, name):
    c = Vector(center); vd = Vector(d).normalized()
    cam.location = c + vd * 3
    fwd = -vd
    cam.rotation_euler = fwd.to_track_quat('-Z', 'Y').to_euler()
    cam.data.ortho_scale = size
    for s in suns: s.rotation_euler = (fwd + Vector((0.3, 0, -0.4))).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = OUT + name
    bpy.ops.render.render(write_still=True)
    print('RENDER', name)
shot((0, 0, 1.62), 0.45, (0, -1, 0.1), 'close_head_front.png')
shot((0, 0, 1.55), 0.5, (0.7, -0.7, 0.2), 'close_neck_tq.png')
shot((0, 0, 0.92), 0.6, (0.7, -0.7, 0.2), 'close_waist_tq.png')
shot((0.55, 0, 1.34), 0.8, (0, -1, 0.1), 'close_arm_front.png')
