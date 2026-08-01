# -*- coding: utf-8 -*-
"""
Реимпорт SK_Wolf с новой вершинной покраской (Build 1.2, волк серее).
Поверх существующего /Game/Characters/Wolf/SK_Wolf, скелет и материалы сохраняются.
Вывод с меткой WOLFIMP| (латиницей).
"""
import os
import unreal

PREFIX = 'WOLFIMP|'
FBX = 'E:/game-dev-team/assets/wolf_recolor/SK_Wolf.fbx'
DEST_DIR = '/Game/Characters/Wolf'
ASSET = DEST_DIR + '/SK_Wolf'
SKELETON = DEST_DIR + '/SK_Wolf_Skeleton'


def say(*parts):
    print(PREFIX + ' '.join(str(p) for p in parts))


def snapshot_materials(path):
    mesh = unreal.load_asset(path)
    if not mesh:
        return None
    mats = mesh.get_editor_property('materials')
    return [str(m.get_editor_property('material_interface').get_path_name())
            if m.get_editor_property('material_interface') else 'NONE' for m in mats]


def main():
    if not os.path.isfile(FBX):
        say('ERROR fbx not found:', FBX)
        say('RESULT= FAIL')
        return
    before_mats = snapshot_materials(ASSET)
    say('BEFORE materials=', before_mats)

    skeleton = unreal.load_asset(SKELETON)
    if not skeleton:
        say('ERROR skeleton not found')
        say('RESULT= FAIL')
        return

    task = unreal.AssetImportTask()
    task.set_editor_property('filename', FBX)
    task.set_editor_property('destination_path', DEST_DIR)
    task.set_editor_property('destination_name', 'SK_Wolf')
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
    say('IMPORTED_PATHS=', imported)
    if not imported:
        say('ERROR import produced nothing')
        say('RESULT= FAIL')
        return

    mesh = unreal.load_asset(ASSET)
    ok = True
    got_skel = mesh.get_editor_property('skeleton')
    same = bool(got_skel) and got_skel.get_path_name().startswith(SKELETON)
    say('CHECK skeleton_matches=', same)
    if not same:
        ok = False
    after_mats = snapshot_materials(ASSET)
    say('AFTER materials=', after_mats)
    if before_mats and after_mats != before_mats:
        say('PROBLEM materials changed by reimport')
        ok = False
    has_vc = mesh.has_vertex_colors() if hasattr(mesh, 'has_vertex_colors') else 'NO_API'
    say('CHECK has_vertex_colors=', has_vc)
    if has_vc is False:
        ok = False
    say('RESULT=', 'OK' if ok else 'FAIL')


main()
