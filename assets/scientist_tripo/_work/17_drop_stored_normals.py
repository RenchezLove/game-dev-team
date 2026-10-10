"""The three slots carried the stored normals of the Tripo glb through the decimation: on 36 faces they looked against the face.
Drop them in the work file (flat shading from the faces), then export_verify.py writes clean FBX.
Run: blender -b scientist_work.blend --factory-startup --python 17_drop_stored_normals.py"""
import bpy
for s in ('Head', 'Torso', 'Legs'):
    me = bpy.data.objects['SK_Scientist_' + s].data
    had = 'custom_normal' in me.attributes
    if had:
        me.attributes.remove(me.attributes['custom_normal'])
    for p in me.polygons:
        p.use_smooth = False
    me.update(); print('SLOT %s: stored normals %s' % (s, 'removed' if had else 'were not there'))
bpy.ops.wm.save_mainfile()
