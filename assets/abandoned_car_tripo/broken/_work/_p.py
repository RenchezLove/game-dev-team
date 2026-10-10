p = 'E:/game-dev-team/assets/abandoned_car_tripo/broken/_work/21_export_verify.py'
s = open(p, encoding='utf-8').read()
a = s[s.index("x = -4.2\n"):]
b = '''# two rows: left parts and the hood are looked at from the -X side, right doors from the +X side; whole part in front, dented one 1.3 m further along Y
ROW = {'Door_FL': (-3.0, 0), 'Door_RL': (-3.0, 3.0), 'Door_FR': (3.0, 0), 'Door_RR': (3.0, 3.0), 'Hood': (0.0, 1.0)}
for p in PARTS:
    w, b = pairs[p]; x0, y0 = ROW[p]
    for o, dy in ((w, 0.0), (b, -1.35 if p != 'Hood' else -1.5)):
        o.data.materials.clear(); o.data.materials.append(mat)
        o.location = (x0, y0 + dy, 0.0 if p != 'Hood' else 0.9)
sc, cam, cd, sun = sb.preview_scene()
os.makedirs(sb.WORK + '_prev_tmp/', exist_ok=True); P = []
for i, (yaw, pit, tgt, fov, sd) in enumerate(((290, 30, (-3.0, 0.4, 0.5), 11, (0.6, 0.25, -0.5)), (70, 30, (3.0, 0.4, 0.5), 11, (-0.6, 0.25, -0.5)),
                                              (20, 60, (0.0, 0.3, 0.9), 7, (-0.45, 0.6, -0.66)), (200, 25, (0.0, 0.3, 0.9), 7, (0.45, -0.6, -0.5)))):
    p = sb.WORK + '_prev_tmp/broken_%d.png' % i; P.append(p)
    sb.shoot(sc, cam, cd, sun, p, yaw, pit, 30, fov, tgt, res=(1100, 700), sun_dir=sd)
sb.sheet(P, OUT + 'broken_preview.png', 2)
'''
s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s)
