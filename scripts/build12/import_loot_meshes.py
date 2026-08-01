# -*- coding: utf-8 -*-
"""
Импорт мешей лута (Build 1.2): SM_LootSack, SM_LootBackpack, SM_HidePickup
в /Game/Environment/Props/ + назначение материала M_VColor + самопроверка.
Запуск headless (редактор ЗАКРЫТ), вывод с меткой LOOTIMP| (латиницей: лог UE в ASCII).
"""
import os
import unreal

PREFIX = 'LOOTIMP|'
MATERIAL_PATH = '/Game/Materials/M_VColor'
DEST_DIR = '/Game/Environment/Props'
MESHES = [
    ('E:/game-dev-team/assets/loot_bag/SM_LootSack.fbx', 'SM_LootSack'),
    ('E:/game-dev-team/assets/loot_bag/SM_LootBackpack.fbx', 'SM_LootBackpack'),
    ('E:/game-dev-team/assets/hide_pickup/SM_HidePickup.fbx', 'SM_HidePickup'),
]


def say(*parts):
    print(PREFIX + ' '.join(str(p) for p in parts))


def import_one(fbx_path, asset_name, material):
    if not os.path.isfile(fbx_path):
        say('ERROR fbx not found:', fbx_path)
        return False
    say('FBX=', fbx_path, 'size=', os.path.getsize(fbx_path))

    task = unreal.AssetImportTask()
    task.set_editor_property('filename', fbx_path)
    task.set_editor_property('destination_path', DEST_DIR)
    task.set_editor_property('destination_name', asset_name)
    task.set_editor_property('automated', True)
    task.set_editor_property('replace_existing', True)
    task.set_editor_property('save', True)

    options = unreal.FbxImportUI()
    options.set_editor_property('import_mesh', True)
    options.set_editor_property('import_as_skeletal', False)
    options.set_editor_property('import_animations', False)
    options.set_editor_property('import_materials', False)
    options.set_editor_property('import_textures', False)
    options.set_editor_property('mesh_type_to_import', unreal.FBXImportType.FBXIT_STATIC_MESH)
    sm_data = options.get_editor_property('static_mesh_import_data')
    sm_data.set_editor_property('vertex_color_import_option',
                                unreal.VertexColorImportOption.REPLACE)
    sm_data.set_editor_property('combine_meshes', True)
    task.set_editor_property('options', options)

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    imported = [str(p) for p in task.get_editor_property('imported_object_paths')]
    say('IMPORTED_PATHS=', imported)
    if not imported:
        say('ERROR import produced nothing (see LogFbx above)')
        return False

    asset_path = DEST_DIR + '/' + asset_name
    mesh = unreal.load_asset(asset_path)
    if not mesh or not isinstance(mesh, unreal.StaticMesh):
        say('ERROR not loadable as StaticMesh:', asset_path)
        return False

    # Материал: struct-массив отдаёт КОПИЮ — обязателен assign-back (ADR-021).
    mats = mesh.get_editor_property('static_materials')
    for i in range(len(mats)):
        elem = mats[i]
        elem.set_editor_property('material_interface', material)
        mats[i] = elem
    mesh.set_editor_property('static_materials', mats)
    unreal.EditorAssetLibrary.save_asset(asset_path)

    # Самопроверка ПОСЛЕ сохранения: перезагрузка, вершинные цвета, треугольники, материал.
    mesh2 = unreal.load_asset(asset_path)
    has_vc = unreal.EditorStaticMeshLibrary.has_vertex_colors(mesh2)
    tris = unreal.EditorStaticMeshLibrary.get_number_verts(mesh2, 0)
    mats2 = mesh2.get_editor_property('static_materials')
    mat_names = [str(m.get_editor_property('material_interface').get_path_name())
                 if m.get_editor_property('material_interface') else 'NONE' for m in mats2]
    say('CHECK', asset_name, 'has_vertex_colors=', has_vc, 'verts_lod0=', tris,
        'materials=', mat_names)
    if not has_vc:
        say('PROBLEM', asset_name, 'no vertex colors after import')
        return False
    if not mat_names or any(MATERIAL_PATH not in m for m in mat_names):
        say('PROBLEM', asset_name, 'material not assigned')
        return False
    return True


def main():
    material = unreal.load_asset(MATERIAL_PATH)
    if not material:
        say('ERROR material not found:', MATERIAL_PATH)
        say('RESULT= FAIL')
        return
    ok = True
    for fbx, name in MESHES:
        if not import_one(fbx, name, material):
            ok = False
    say('RESULT=', 'OK' if ok else 'FAIL')


main()
