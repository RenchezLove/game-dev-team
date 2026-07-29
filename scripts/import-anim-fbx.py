# -*- coding: utf-8 -*-
"""
Импорт анимационного FBX в проект ContrarySurvivor одной командой.

ЗАЧЕМ. Когда моделлер сдаёт FBX с анимацией, её нужно втянуть в проект на ПРАВИЛЬНЫЙ
скелет и убедиться, что она реально приехала. Скрипт делает это без единого клика
и сам себя проверяет: сверяет скелет, длину, число кадров и имена костных дорожек.

КАК ЗАПУСКАТЬ (редактор должен быть ЗАКРЫТ):
  "E:/UnrealEngine/UE_5.5/Engine/Binaries/Win64/UnrealEditor-Cmd.exe" ^
      "E:/ContrarySurvior/ContrarySurvivor/ContrarySurvivor.uproject" ^
      -ExecutePythonScript="E:/game-dev-team/scripts/import-anim-fbx.py <путь_к_fbx> <папка> <имя> [скелет]" ^
      -unattended -nopause -nosplash -abslog="E:/game-dev-team/logs/anim-import.log"

  Пример:
      ... -ExecutePythonScript="E:/game-dev-team/scripts/import-anim-fbx.py
          E:/art/anim/Knife_Slash.fbx /Game/Characters/Shared/Humanoid Anim_Knife_Slash"

  Аргументы:
    1) путь к FBX-файлу (абсолютный);
    2) папка назначения в проекте (начинается с /Game/);
    3) имя будущего ассета анимации;
    4) необязательно — путь к скелету. Если не указан, берётся скелет,
       на котором работает ABP_HumanoidCharacter (см. DEFAULT_SKELETON).

  Редактор ОТКРЫТ? Тогда запускать коммандлет нельзя (драка за файлы) — выполнить
  этот же файл через живой Python-канал редактора (см. context/unreal-operator).

ВЫВОД. Каждая строка начинается с метки ANIMIMP| — её удобно выдёргивать из лога
командой grep -a "ANIMIMP|". Итог печатается строкой ANIMIMP|RESULT= OK или FAIL.
Печать латиницей намеренно: лог UE в ASCII, кириллица в нём превращается в кашу.
"""

import sys
import os
import unreal

PREFIX = 'ANIMIMP|'

# Скелет, на котором работает ABP_HumanoidCharacter (решение лида от 2026-07-28:
# новые анимации импортируем именно на него, два скелета-дубля не сводим).
DEFAULT_SKELETON = '/Game/TestContentAndCode/PreProduction/HeadAndSkeletonfbx_Head_Skeleton'


def say(*parts):
    print(PREFIX + ' '.join(str(p) for p in parts))


def fail(message):
    say('ERROR', message)
    say('RESULT= FAIL')
    return False


def import_anim(fbx_path, dest_dir, asset_name, skeleton_path):
    # --- проверки до действия: без них импорт молча создаёт мусор ---
    if not os.path.isfile(fbx_path):
        return fail('fbx not found: %s' % fbx_path)
    if not dest_dir.startswith('/Game/'):
        return fail('destination must start with /Game/ : %s' % dest_dir)

    skeleton = unreal.load_asset(skeleton_path)
    if not skeleton:
        return fail('skeleton not found: %s' % skeleton_path)
    if not isinstance(skeleton, unreal.Skeleton):
        return fail('not a Skeleton asset: %s' % skeleton_path)

    say('FBX=', fbx_path, 'size=', os.path.getsize(fbx_path))
    say('DEST=', dest_dir + '/' + asset_name)
    say('SKELETON=', skeleton.get_path_name())

    task = unreal.AssetImportTask()
    task.set_editor_property('filename', fbx_path)
    task.set_editor_property('destination_path', dest_dir)
    task.set_editor_property('destination_name', asset_name)
    task.set_editor_property('automated', True)
    task.set_editor_property('replace_existing', True)
    task.set_editor_property('save', True)

    options = unreal.FbxImportUI()
    options.set_editor_property('import_animations', True)
    options.set_editor_property('import_mesh', False)
    options.set_editor_property('import_as_skeletal', True)
    options.set_editor_property('import_materials', False)
    options.set_editor_property('import_textures', False)
    options.set_editor_property('create_physics_asset', False)
    options.set_editor_property('mesh_type_to_import', unreal.FBXImportType.FBXIT_ANIMATION)
    options.set_editor_property('original_import_type', unreal.FBXImportType.FBXIT_SKELETAL_MESH)
    options.set_editor_property('skeleton', skeleton)
    task.set_editor_property('options', options)

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

    # МИНА (поймана 2026-07-28): поле result у задачи импорта в UE 5.5 объявлено
    # устаревшим и защищённым — чтение роняет скрипт УЖЕ ПОСЛЕ успешного импорта.
    # Итог берём из списка путей, а не из result.
    imported = [str(p) for p in task.get_editor_property('imported_object_paths')]
    say('IMPORTED_PATHS=', imported)
    if not imported:
        return fail('import produced nothing (see LogFbx above for the reason)')

    # --- проверка результата: ассет есть, скелет тот, данные не пустые ---
    ok = True
    for path in imported:
        asset = unreal.load_asset(path.split('.')[0])
        if not asset:
            say('CHECK', path, 'NOT_LOADABLE')
            ok = False
            continue
        say('CHECK', asset.get_name(), 'class=', asset.get_class().get_name())
        if not isinstance(asset, unreal.AnimSequence):
            say('CHECK', asset.get_name(), 'is not AnimSequence -- skipped')
            continue

        got_skeleton = asset.get_editor_property('skeleton')
        same_skeleton = bool(got_skeleton) and got_skeleton.get_path_name() == skeleton.get_path_name()
        frames = asset.get_editor_property('number_of_sampled_frames')
        length = asset.get_play_length()
        tracks = [str(n) for n in unreal.AnimationLibrary.get_animation_track_names(asset)]
        say('   skeleton_matches=', same_skeleton, 'frames=', frames,
            'length=', round(length, 4), 'bone_tracks=', len(tracks))
        if not same_skeleton:
            say('   PROBLEM: skeleton differs:', got_skeleton.get_path_name() if got_skeleton else None)
            ok = False
        if frames <= 0 or length <= 0.0:
            say('   PROBLEM: animation is empty')
            ok = False
        if not tracks:
            say('   PROBLEM: no bone tracks')
            ok = False

    say('RESULT=', 'OK' if ok else 'FAIL')
    return ok


def main():
    args = sys.argv[1:]
    if len(args) < 3:
        say('USAGE: import-anim-fbx.py <abs_fbx_path> </Game/dest/folder> <AssetName> [skeleton_path]')
        say('RESULT= FAIL')
        return False
    fbx_path = args[0].replace('\\', '/')
    dest_dir = args[1].rstrip('/')
    asset_name = args[2]
    skeleton_path = args[3] if len(args) > 3 else DEFAULT_SKELETON
    return import_anim(fbx_path, dest_dir, asset_name, skeleton_path)


main()
