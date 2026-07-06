"""Colorspace discriminator test (team-lead request 07-06, UE double-encode bug).
Batch-1/2 FBX were exported with the exporter DEFAULT colors_type='SRGB'
(export_fbx_bin.py reads BYTE_COLOR via `color_srgb` -> stored hex bytes go
into the FBX as-is; UE then encodes once more on import = double encode).
This exports SK_Armor_T1_Torso with the OPPOSITE colors_type='LINEAR' into
SK_Armor_T1_Torso_cstest.fbx (original untouched) and dumps the dominant
color values found in both files after a fresh re-import.
Run: blender.exe -b --factory-startup --python 07_cstest_colorspace.py
"""
import bpy, sys, os
sys.path.insert(0, 'E:/game-dev-team/assets/armor_wearables')
import wcommon as W

OUT = W.WORKDIR + 'SK_Armor_T1_Torso_cstest.fbx'
bpy.ops.wm.open_mainfile(filepath=W.WORKDIR + '_work/wearables_work.blend')
rig = bpy.data.objects['RootAnim']
for pb in rig.pose.bones:                      # rest pose before export
    pb.rotation_mode = 'XYZ'
    pb.rotation_euler = (0, 0, 0)
    pb.location = (0, 0, 0)
    pb.scale = (1, 1, 1)
ob = bpy.data.objects['SK_Armor_T1_Torso']
bpy.ops.object.select_all(action='DESELECT')
ob.select_set(True)
rig.select_set(True)
bpy.context.view_layer.objects.active = ob
bpy.ops.export_scene.fbx(
    filepath=OUT, use_selection=True,
    object_types={'MESH', 'ARMATURE'}, mesh_smooth_type='FACE',
    use_mesh_modifiers=False, add_leaf_bones=False, bake_anim=False,
    path_mode='AUTO', colors_type='LINEAR')   # <-- only change vs batch exports
print('EXPORTED %s (%.1f KB)' % (OUT, os.path.getsize(OUT) / 1024))


def dump(path, label):
    """Re-import and show dominant per-loop color values as hex bytes.
    Import colors_type default 'SRGB' stores file floats verbatim as bytes,
    so this prints exactly what sits in the FBX."""
    W.fresh()
    meshes, arms, rest = W.import_fbx(path)
    me = meshes[0].data
    ca = me.color_attributes[0]
    cnt = {}
    for i in range(len(ca.data)):
        c = ca.data[i].color_srgb
        hx = '#%02X%02X%02X' % (round(c[0] * 255), round(c[1] * 255), round(c[2] * 255))
        cnt[hx] = cnt.get(hx, 0) + 1
    top = sorted(cnt.items(), key=lambda kv: -kv[1])[:6]
    print('DUMP %-24s attr=%s(%s/%s) loops=%d top hex: %s' % (
        label, ca.name, ca.domain, ca.data_type, len(ca.data), top))


dump(W.WORKDIR + 'SK_Armor_T1_Torso.fbx', 'ORIGINAL(default=SRGB)')
dump(OUT, 'CSTEST(LINEAR)')
