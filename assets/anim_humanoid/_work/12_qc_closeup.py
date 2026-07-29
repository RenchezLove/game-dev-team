"""High resolution close-ups of the frames where the skinning is under most strain,
so shoulder stretch and mesh clashes can actually be judged before delivery."""
import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       '11_render_previews.py')).read().split('SLASH_FRAMES =')[0])

sc.render.resolution_x = sc.render.resolution_y = 900

CLOSE = [
    ('Anim_MeleeSlash_Humanoid', 7, 'front', 'knife'),
    ('Anim_MeleeSlash_Humanoid', 12, 'front', 'knife'),
    ('Anim_MeleeSlash_Humanoid', 16, 'front', 'knife'),
    ('Anim_MeleeSlash_Humanoid', 16, 'game_front', 'knife'),
    ('Anim_AimPistol_Humanoid', 1, 'front', 'pistol'),
    ('Anim_AimPistol_Humanoid', 1, 'game_front', 'pistol'),
]

WEAP_MAP = {'pistol': pistol, 'knife': knife}
paths = []
for act, fr, view, wname in CLOSE:
    paths.append(shoot(act, fr, view, WEAP_MAP[wname], '%s f%d %s' % (act.split('_')[1], fr, view)))
montage(paths, REND + 'qc_closeups.png', 3)
print('QC_DONE')
