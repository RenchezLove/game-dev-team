"""Recolor the wolf from warm brown ("dog-like", Rinat) to steel grey, keeping
the dark-back / light-belly split and the near-black nose.

Where the colour lives (verified in build_wolf.py, not memory): vertex paint
'Col' (CORNER/BYTE_COLOR) on SK_Wolf inside wolf.blend. The old batch stored
LINEAR floats as raw bytes (bmesh lp[cl] = lin(sRGB)) and exported with FBX
defaults - this script writes the new colours in the SAME encoding and exports
with the SAME settings, so nothing changes downstream except the hue.

Old sRGB intents (build_wolf.py): back (0.33,0.29,0.25), belly (0.50,0.46,0.40),
nose (0.10,0.09,0.09). New: back (0.31,0.33,0.36), belly (0.46,0.48,0.50).

Run:  blender.exe -b "E:/ForGameLead(Materials)/phase3-assets/_build/wolf.blend"
          --factory-startup --python 10_recolor_wolf.py
Saves wolf.blend (backup: assets/wolf_recolor/_work/wolf_brown_backup.blend)
and exports assets/wolf_recolor/SK_Wolf.fbx (the phase3-assets original FBX is
left untouched as the "before" reference).
"""
import bpy, os, addon_utils

OUT = 'E:/game-dev-team/assets/wolf_recolor/'
SRC_BLEND = 'E:/ForGameLead(Materials)/phase3-assets/_build/wolf.blend'
OLD_FBX = 'E:/ForGameLead(Materials)/phase3-assets/SK_Wolf.fbx'


def s2l(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lin(rgb):
    return tuple(s2l(c) for c in rgb) + (1.0,)


OLD_BACK = lin((0.33, 0.29, 0.25))
OLD_BELLY = lin((0.50, 0.46, 0.40))
OLD_NOSE = lin((0.10, 0.09, 0.09))
NEW_BACK = lin((0.31, 0.33, 0.36))
NEW_BELLY = lin((0.46, 0.48, 0.50))

me = bpy.data.objects['SK_Wolf'].data
ca = me.color_attributes['Col']
assert ca.domain == 'CORNER' and ca.data_type == 'BYTE_COLOR'

TOL = 2.5 / 255.0


def close(a, b):
    return all(abs(x - y) <= TOL for x, y in zip(a[:3], b[:3]))


counts = {'back': 0, 'belly': 0, 'nose': 0, 'unknown': 0}
unknown_vals = set()
for d in ca.data:
    raw = tuple(d.color_srgb)          # raw stored bytes = the linear numbers
    if close(raw, OLD_BACK):
        d.color_srgb = NEW_BACK
        counts['back'] += 1
    elif close(raw, OLD_BELLY):
        d.color_srgb = NEW_BELLY
        counts['belly'] += 1
    elif close(raw, OLD_NOSE):
        counts['nose'] += 1            # nose stays
    else:
        counts['unknown'] += 1
        unknown_vals.add(tuple(round(v, 3) for v in raw[:3]))
me.update()
print('RECOLOR loops: back=%(back)d belly=%(belly)d nose=%(nose)d unknown=%(unknown)d' % counts)
if counts['unknown']:
    print('RECOLOR FAIL unknown colours present:', sorted(unknown_vals))
    raise SystemExit(1)

bpy.ops.wm.save_mainfile(filepath=SRC_BLEND)
print('SAVED', SRC_BLEND)

# rest-pose export, settings identical to build_wolf.py (defaults, no colors_type)
arm = bpy.data.objects['WolfRig']
mesh_obj = bpy.data.objects['SK_Wolf']
if arm.animation_data:
    arm.animation_data.action = None
bpy.ops.object.select_all(action='DESELECT')
mesh_obj.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
path = OUT + 'SK_Wolf.fbx'
bpy.ops.export_scene.fbx(filepath=path, use_selection=True,
                         object_types={'MESH', 'ARMATURE'}, mesh_smooth_type='FACE',
                         add_leaf_bones=False, bake_anim=False,
                         use_mesh_modifiers=True, path_mode='AUTO')
print('EXPORTED %s exists=%s bytes=%s' % (path, os.path.exists(path), os.path.getsize(path)))

# ---- round trip: new file vs old file, only the hue may differ ----


def census(fbx):
    bpy.ops.wm.read_homefile(use_factory_startup=True)
    addon_utils.enable('io_scene_fbx')
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.ops.import_scene.fbx(filepath=fbx)
    mo = [o for o in bpy.data.objects if o.type == 'MESH'][0]
    m = mo.data
    tris = sum(len(p.vertices) - 2 for p in m.polygons)
    bones = len([o for o in bpy.data.objects if o.type == 'ARMATURE'][0].data.bones)
    cc = {}
    at = m.color_attributes[0]
    for d in at.data:
        k = tuple(round(v * 255) for v in d.color_srgb[:3])
        cc[k] = cc.get(k, 0) + 1
    return tris, len(m.vertices), bones, sorted(cc.items(), key=lambda kv: -kv[1])


for tag, f in (('OLD', OLD_FBX), ('NEW', path)):
    tris, verts, bones, cc = census(f)
    print('VERIFY %s tris=%d verts=%d bones=%d colors=%s' % (tag, tris, verts, bones, cc[:6]))
print('RECOLOR_DONE')
