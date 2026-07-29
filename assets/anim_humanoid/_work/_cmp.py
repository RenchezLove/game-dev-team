import bpy, os, sys, addon_utils
addon_utils.enable('io_scene_fbx')
from io_scene_fbx import parse_fbx
KTIME = 46186158000
for path in [
  "E:/ForGameLead(Materials)/Порядок (PipeLine) создания мешей,анимаций AMasterHumanoidCharacter импорт и экспорт/Anim_Run_Humanoid .fbx",
  "E:/game-dev-team/assets/armor_wearables/SK_Armor_T1_Torso.fbx"]:
    root, ver = parse_fbx.parse(path)
    print('====', os.path.basename(path), 'ver', ver)
    for child in root.elems:
        if child.id == b'GlobalSettings':
            for sub in child.elems:
                if sub.id == b'Properties70':
                    for p in sub.elems:
                        if p.props[0] in (b'UpAxis', b'FrontAxis', b'CoordAxis', b'UpAxisSign',
                                          b'FrontAxisSign', b'CoordAxisSign', b'UnitScaleFactor', b'TimeMode'):
                            print('  %-16s = %s' % (p.props[0].decode(), p.props[-1]))
        if child.id == b'Takes':
            for e in child.elems:
                if e.id == b'Take':
                    for sub in e.elems:
                        if sub.id == b'LocalTime':
                            print('  Take "%s" %.4f s' % (e.props[0].decode('utf-8','replace'),
                                                          (sub.props[1]-sub.props[0])/float(KTIME)))
