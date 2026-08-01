# -*- coding: utf-8 -*-
"""
Импорт торговца (Build 1.2 п.4): три модуля SK_Trader_Head/Torso/Legs на Shared-скелет
гуманоида (как староста и бандит — проверено бинарным грепом с контролем), назначение
материалов (Head — M_VColor_TS: хвосты банданы односторонние, нужен Two-Sided;
Torso/Legs — M_VColor) и подключение модулей в CDO BP_Trader.
Вывод с меткой TRDIMP| (латиницей).
"""
import os
import unreal

PREFIX = 'TRDIMP|'
DEST = '/Game/Characters/Trader'
SKELETON = '/Game/Characters/Shared/Humanoid/HeadAndSkeletonfbx_Head_Skeleton'
MAT_TS = '/Game/Materials/M_VColor_TS'
MAT = '/Game/Materials/M_VColor'
BP_TRADER = '/Game/Characters/Trader/BP_Trader'
MODULES = [
    ('E:/game-dev-team/assets/npc_trader/SK_Trader_Head.fbx', 'SK_Trader_Head', MAT_TS),
    ('E:/game-dev-team/assets/npc_trader/SK_Trader_Torso.fbx', 'SK_Trader_Torso', MAT),
    ('E:/game-dev-team/assets/npc_trader/SK_Trader_Legs.fbx', 'SK_Trader_Legs', MAT),
]


def say(*parts):
    print(PREFIX + ' '.join(str(p) for p in parts))


def import_module(fbx, name, mat_path, skeleton):
    if not os.path.isfile(fbx):
        say('ERROR fbx not found:', fbx)
        return None
    task = unreal.AssetImportTask()
    task.set_editor_property('filename', fbx)
    task.set_editor_property('destination_path', DEST)
    task.set_editor_property('destination_name', name)
    task.set_editor_property('automated', True)
    task.set_editor_property('replace_existing', True)
    task.set_editor_property('save', True)
    options = unreal.FbxImportUI()
    options.set_editor_property('import_mesh', True)
    options.set_editor_property('import_as_skeletal', True)
    options.set_editor_property('import_animations', False)
    options.set_editor_property('import_materials', False)
    options.set_editor_property('import_textures', False)
    options.set_editor_property('create_physics_asset', False)
    options.set_editor_property('mesh_type_to_import', unreal.FBXImportType.FBXIT_SKELETAL_MESH)
    options.set_editor_property('skeleton', skeleton)
    sk_data = options.get_editor_property('skeletal_mesh_import_data')
    sk_data.set_editor_property('vertex_color_import_option',
                                unreal.VertexColorImportOption.REPLACE)
    task.set_editor_property('options', options)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    imported = [str(p) for p in task.get_editor_property('imported_object_paths')]
    say(name, 'IMPORTED_PATHS=', imported)
    if not imported:
        return None

    path = DEST + '/' + name
    mesh = unreal.load_asset(path)
    if not mesh:
        say('ERROR not loadable:', path)
        return None
    got_skel = mesh.get_editor_property('skeleton')
    same = bool(got_skel) and SKELETON in got_skel.get_path_name()
    mat = unreal.load_asset(mat_path)
    mats = mesh.get_editor_property('materials')
    for i in range(len(mats)):
        elem = mats[i]
        elem.set_editor_property('material_interface', mat)
        mats[i] = elem
    mesh.set_editor_property('materials', mats)
    unreal.EditorAssetLibrary.save_asset(path)
    mesh2 = unreal.load_asset(path)
    got_mats = [m.get_editor_property('material_interface').get_path_name()
                if m.get_editor_property('material_interface') else 'NONE'
                for m in mesh2.get_editor_property('materials')]
    say('CHECK', name, 'skeleton_ok=', same, 'materials=', got_mats)
    if not same or any(mat_path not in g for g in got_mats):
        return None
    return mesh2


def main():
    skeleton = unreal.load_asset(SKELETON)
    if not skeleton:
        say('ERROR skeleton not found')
        say('RESULT= FAIL')
        return
    # Материал головы обязан быть двусторонним (хвосты банданы — плоскости).
    mat_ts = unreal.load_asset(MAT_TS)
    two_sided = mat_ts.get_editor_property('two_sided') if mat_ts else None
    say('MAT_TS two_sided=', two_sided)
    if not mat_ts or two_sided is not True:
        say('ERROR M_VColor_TS missing or not two-sided')
        say('RESULT= FAIL')
        return

    meshes = {}
    for fbx, name, mat_path in MODULES:
        m = import_module(fbx, name, mat_path, skeleton)
        if not m:
            say('RESULT= FAIL')
            return
        meshes[name] = m

    # Подключение модулей в CDO BP_Trader (AMasterTrader : AMasterHumanoidCharacter):
    # лидер-меш (Mesh, он же Head) + TorsoMesh + LegsMesh.
    bp = unreal.load_asset(BP_TRADER)
    if not bp:
        say('ERROR BP_Trader not found')
        say('RESULT= FAIL')
        return
    cdo = unreal.get_default_object(bp.generated_class())
    pairs = [('mesh', 'SK_Trader_Head'), ('torso_mesh', 'SK_Trader_Torso'),
             ('legs_mesh', 'SK_Trader_Legs')]
    for prop, asset in pairs:
        comp = cdo.get_editor_property(prop)
        if not comp:
            say('ERROR CDO component missing:', prop)
            say('RESULT= FAIL')
            return
        comp.set_editor_property('skeletal_mesh_asset', meshes[asset])
    unreal.EditorAssetLibrary.save_asset(BP_TRADER)
    cdo2 = unreal.get_default_object(unreal.load_asset(BP_TRADER).generated_class())
    ok = True
    for prop, asset in pairs:
        got = cdo2.get_editor_property(prop).get_editor_property('skeletal_mesh_asset')
        got_name = got.get_name() if got else 'NONE'
        say('CHECK BP_Trader', prop, '=', got_name)
        if got_name != asset:
            ok = False
    say('RESULT=', 'OK' if ok else 'FAIL')


main()
