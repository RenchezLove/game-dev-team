import bpy
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
bpy.ops.import_scene.fbx(filepath=r'E:\game-dev-team\assets\armor_wearables\SK_Armor_T1_Torso.fbx')
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.fbx(filepath=r'E:\game-dev-team\assets\armor_wearables\SK_Armor_T1_Torso_cstest.fbx', use_selection=True, add_leaf_bones=False, colors_type='LINEAR')
print('CSTEST EXPORT DONE')
