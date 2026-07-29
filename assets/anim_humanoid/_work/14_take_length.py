"""Read the take length straight out of the FBX container.

Needed because a re-import shows the scene range, which can simply be Blender's
factory 1..250 default rather than anything the file says. Unreal takes the length
from the AnimationStack, so that is what has to be checked.
"""
import bpy, sys, os, addon_utils
addon_utils.enable('io_scene_fbx')
from io_scene_fbx import parse_fbx

OUT = 'E:/game-dev-team/assets/anim_humanoid/'
FILES = ['Anim_AimPistol_Humanoid', 'Anim_FirePistol_Humanoid', 'Anim_MeleeSlash_Humanoid']
KTIME = 46186158000        # FBX time unit: ticks per second

for name in FILES:
    path = OUT + name + '.fbx'
    root, version = parse_fbx.parse(path)
    print('==== %s  fbx_version=%d' % (os.path.basename(path), version))
    stacks, layers, curvenodes = 0, 0, 0
    for child in root.elems:
        if child.id == b'Objects':
            for e in child.elems:
                if e.id == b'AnimationStack':
                    stacks += 1
                    label = e.props[1].decode('utf-8', 'replace') if len(e.props) > 1 else '?'
                    start = stop = None
                    for sub in e.elems:
                        if sub.id == b'Properties70':
                            for p in sub.elems:
                                pname = p.props[0]
                                if pname == b'LocalStart':
                                    start = p.props[-1]
                                elif pname == b'LocalStop':
                                    stop = p.props[-1]
                    if start is not None and stop is not None:
                        secs = (stop - start) / float(KTIME)
                        print('  AnimationStack "%s": %.4f s  -> %.1f frames at 30 fps'
                              % (label, secs, secs * 30.0))
                    else:
                        print('  AnimationStack "%s": no LocalStart/LocalStop' % label)
                elif e.id == b'AnimationLayer':
                    layers += 1
                elif e.id == b'AnimationCurveNode':
                    curvenodes += 1
        elif child.id == b'Takes':
            for e in child.elems:
                if e.id == b'Take':
                    label = e.props[0].decode('utf-8', 'replace')
                    for sub in e.elems:
                        if sub.id in (b'LocalTime', b'ReferenceTime'):
                            a, b = sub.props[0], sub.props[1]
                            print('  Take "%s" %s: %.4f s' % (
                                label, sub.id.decode(), (b - a) / float(KTIME)))
        elif child.id == b'GlobalSettings':
            for sub in child.elems:
                if sub.id == b'Properties70':
                    for p in sub.elems:
                        if p.props[0] in (b'UpAxis', b'FrontAxis', b'CoordAxis',
                                          b'UpAxisSign', b'FrontAxisSign', b'CoordAxisSign',
                                          b'UnitScaleFactor', b'TimeMode'):
                            print('  global %-16s = %s' % (p.props[0].decode(), p.props[-1]))
    print('  counts: stacks=%d layers=%d curve_nodes=%d' % (stacks, layers, curvenodes))
print('TAKE_DONE')
