import unreal
# Учёный из Tripo (сдача моделлера 09.10): три части на общем скелете, цвет волос — параметром материала по маске (красный канал).
SRC = 'E:/game-dev-team/assets/scientist_tripo/'; DEST = '/Game/Characters/Scientist'; PREFIX = 'SK_Scientist_'
TEX = 'T_ScientistTripo_D'; MASK = 'T_ScientistTripo_Mask'; MAT = 'M_ScientistTripo'
at = unreal.AssetToolsHelpers.get_asset_tools(); eal = unreal.EditorAssetLibrary; mel = unreal.MaterialEditingLibrary
print('PIE', unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor())
skel = unreal.load_asset('/Game/Characters/Shared/Humanoid/HeadAndSkeletonfbx_Head_Skeleton')
print('SKEL', skel.get_path_name() if skel else None)

def lin(c):  # sRGB -> линейный цвет
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def imp_tex(name, srgb):
    t = unreal.AssetImportTask()
    for k, v in [('filename', SRC + name + '.png'), ('destination_path', DEST), ('destination_name', name), ('replace_existing', True), ('automated', True), ('save', False)]: t.set_editor_property(k, v)
    at.import_asset_tasks([t]); tex = unreal.load_asset(DEST + '/' + name)
    tex.set_editor_property('max_texture_size', 1024)
    if not srgb:
        tex.set_editor_property('srgb', False); tex.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_MASKS)
    return tex

tex = imp_tex(TEX, True); mask = imp_tex(MASK, False)
mp = DEST + '/' + MAT
mat = unreal.load_asset(mp) if eal.does_asset_exist(mp) else at.create_asset(MAT, DEST, unreal.Material, unreal.MaterialFactoryNew())
mel.delete_all_material_expressions(mat)
ts = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -900, 0); ts.set_editor_property('texture', tex)
ms = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -900, 300); ms.set_editor_property('texture', mask)
ms.set_editor_property('sampler_type', unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
hc = mel.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, -900, 600)
hc.set_editor_property('parameter_name', 'HairColor'); hc.set_editor_property('default_value', unreal.LinearColor(lin(0.309), lin(0.221), lin(0.167), 1))
mul = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -600, 200)
lerp = mel.create_material_expression(mat, unreal.MaterialExpressionLinearInterpolate, -350, 0)
r = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -350, 350); r.set_editor_property('r', 0.9)
print('CONN', [mel.connect_material_expressions(ts, 'RGB', mul, 'A'), mel.connect_material_expressions(hc, '', mul, 'B'),
               mel.connect_material_expressions(ts, 'RGB', lerp, 'A'), mel.connect_material_expressions(mul, '', lerp, 'B'),
               mel.connect_material_expressions(ms, 'R', lerp, 'Alpha'),
               mel.connect_material_property(lerp, '', unreal.MaterialProperty.MP_BASE_COLOR), mel.connect_material_property(r, '', unreal.MaterialProperty.MP_ROUGHNESS)])
mat.set_editor_property('used_with_skeletal_mesh', True)
mel.recompile_material(mat)

def inst(name, rgb):
    p = DEST + '/' + name
    mi = unreal.load_asset(p) if eal.does_asset_exist(p) else at.create_asset(name, DEST, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    mel.set_material_instance_parent(mi, mat)
    mel.set_material_instance_vector_parameter_value(mi, 'HairColor', unreal.LinearColor(lin(rgb[0]), lin(rgb[1]), lin(rgb[2]), 1))
    mel.update_material_instance(mi); return mi

mi_brown = inst('MI_Scientist_Brown', (0.309, 0.221, 0.167)); mi_blond = inst('MI_Scientist_Blond', (0.95, 0.80, 0.50))
tasks = []
for s in ['Head', 'Torso', 'Legs']:
    ui = unreal.FbxImportUI()
    for k, v in [('import_mesh', True), ('import_as_skeletal', True), ('mesh_type_to_import', unreal.FBXImportType.FBXIT_SKELETAL_MESH), ('skeleton', skel), ('import_materials', False), ('import_textures', False), ('import_animations', False), ('create_physics_asset', False), ('automated_import_should_detect_type', False)]: ui.set_editor_property(k, v)
    t = unreal.AssetImportTask()
    for k, v in [('filename', SRC + PREFIX + s + '.fbx'), ('destination_path', DEST), ('destination_name', PREFIX + s), ('replace_existing', True), ('automated', True), ('save', False), ('options', ui)]: t.set_editor_property(k, v)
    tasks.append(t)
at.import_asset_tasks(tasks)
for t in tasks: print('IMPORTED', list(t.get_editor_property('imported_object_paths')))
for a in (tex, mask, mat, mi_brown, mi_blond): print('SAVE', a.get_name(), eal.save_loaded_asset(a, False))
ar = unreal.AssetRegistryHelpers.get_asset_registry()
for s in ['Head', 'Torso', 'Legs']:
    sk = unreal.load_asset(DEST + '/' + PREFIX + s)
    new = []
    for x in sk.get_editor_property('materials'):
        y = unreal.SkeletalMaterial(); y.set_editor_property('material_interface', mi_brown); y.set_editor_property('material_slot_name', x.get_editor_property('material_slot_name')); new.append(y)
    sk.set_editor_property('materials', new)
    ok = eal.save_loaded_asset(sk, False); b = sk.get_bounds()
    d = ar.get_asset_by_object_path('%s/%s%s.%s%s' % (DEST, PREFIX, s, PREFIX, s))
    print('NEW', s, 'save', ok, 'skel', sk.get_editor_property('skeleton').get_name(), 'mats', [x.get_editor_property('material_interface').get_name() for x in sk.get_editor_property('materials')],
          'origin', [round(v) for v in (b.origin.x, b.origin.y, b.origin.z)], 'ext', [round(v) for v in (b.box_extent.x, b.box_extent.y, b.box_extent.z)], 'tris', d.get_tag_value('Triangles'))
