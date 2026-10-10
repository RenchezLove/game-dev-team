"""Shotgun with back faces culled (as Unreal draws it): six sides of the whole gun and six close looks at the receiver, guard and fore-end.
Run: blender -b toz_work.blend --factory-startup --python toz_12_cullcheck.py"""
import bpy, sys, os
sys.path.insert(0, 'E:/game-dev-team/assets/scientist_base/_work')
import sb
T = sb.ROOT + 'SM_Shotgun_TOZ34/'
ob = bpy.data.objects['SM_Shotgun_TOZ34']
for o in bpy.data.objects:
    o.hide_render = o is not ob
img = bpy.data.images.load(T + 'T_Shotgun_TOZ34_D.png', check_existing=False); m = sb.tex_material(ob, 'prev', img)
assert m.use_backface_culling
sc, cam, cd, sun = sb.preview_scene(ground=None, bg=(0.75, 0.2, 0.75))          # magenta behind: any hole shows at once
P = []
def sh(tag, yaw, pit, tgt, dist, fov):
    p = sb.WORK + '_prev_tmp/toz_cull_%s.png' % tag; P.append(p)
    import math
    sb.shoot(sc, cam, cd, sun, p, yaw, pit, dist, fov, tgt, res=(1100, 500), sun_dir=(-math.sin(math.radians(yaw)) * 0.5 + 0.2, math.cos(math.radians(yaw)) * 0.5, -0.5 if pit > -30 else 0.6))
C = (0, -0.30, 0.0)
for tag, yaw, pit in (('right', 90, 0), ('left', 270, 0), ('top', 90, 89), ('bottom', 90, -89), ('muzzle', 0, 5), ('butt', 180, 5)):
    sh('whole_' + tag, yaw, pit, C, 2.6, 26 if tag in ('right', 'left', 'top', 'bottom') else 6)
R = (0, -0.14, 0.02)
for tag, yaw, pit in (('right', 90, 5), ('left', 270, 5), ('front_right_low', 50, -20), ('front_left_high', 310, 35), ('below', 90, -70), ('above', 270, 70)):
    sh('close_' + tag, yaw, pit, R, 1.2, 20)
sb.sheet(P, T + 'SM_Shotgun_TOZ34_cullcheck.png', 2)
