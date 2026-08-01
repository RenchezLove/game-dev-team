# -*- coding: utf-8 -*-
"""
BP-классы пикапов (Build 1.2 п.6, Ринат: «APickup выведи в BP класс (чтоб наследовался
от твоего CPP), я потом его в редакторе донастрою»).

Создаёт: /Game/System/BP_Pickup (меш SM_LootSack — лут людей и точек) и
/Game/System/BP_PickupWolf (меш SM_HidePickup — дроп волков). Подключает:
CDO BP_Wolf.pickup_class -> BP_PickupWolf, CDO BP_Bandit.pickup_class -> BP_Pickup.
Идемпотентен: существующие ассеты не пересоздаёт, значения сверяет обратным чтением.
Вывод с меткой BPPICK| (латиницей).
"""
import unreal

PREFIX = 'BPPICK|'
SYSTEM_DIR = '/Game/System'
SACK = '/Game/Environment/Props/SM_LootSack'
HIDE = '/Game/Environment/Props/SM_HidePickup'
WOLF_BP = '/Game/Characters/Wolf/BP_Wolf'
BANDIT_CANDIDATES = ['/Game/Characters/Bandit/BP_Bandit',
                     '/Game/Characters/Bandit/BP_BanditEnemy',
                     '/Game/Characters/Bandit/BP_EnemyBandit']


def say(*parts):
    print(PREFIX + ' '.join(str(p) for p in parts))


def ensure_pickup_bp(name, mesh_path):
    bp_path = SYSTEM_DIR + '/' + name
    mesh = unreal.load_asset(mesh_path)
    if not mesh:
        say('ERROR mesh not found:', mesh_path)
        return None
    if unreal.EditorAssetLibrary.does_asset_exist(bp_path):
        say(name, 'already exists - not recreating')
        bp = unreal.load_asset(bp_path)
    else:
        factory = unreal.BlueprintFactory()
        factory.set_editor_property('parent_class', unreal.Pickup)
        bp = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            name, SYSTEM_DIR, unreal.Blueprint, factory)
        if not bp:
            say('ERROR create_asset failed for', name)
            return None
        say(name, 'created, parent=Pickup')

    gen = bp.generated_class()
    cdo = unreal.get_default_object(gen)
    comp = cdo.get_editor_property('mesh_component')
    if not comp:
        say('ERROR', name, 'mesh_component is None on CDO')
        return None
    comp.set_editor_property('static_mesh', mesh)
    unreal.EditorAssetLibrary.save_asset(bp_path)

    # Обратное чтение после сохранения.
    bp2 = unreal.load_asset(bp_path)
    cdo2 = unreal.get_default_object(bp2.generated_class())
    got = cdo2.get_editor_property('mesh_component').get_editor_property('static_mesh')
    got_path = got.get_path_name() if got else 'NONE'
    say('CHECK', name, 'mesh=', got_path)
    if mesh_path not in got_path:
        say('PROBLEM', name, 'mesh not persisted')
        return None
    return bp2.generated_class()


def wire_pickup_class(char_bp_path, pickup_class, label):
    if not unreal.EditorAssetLibrary.does_asset_exist(char_bp_path):
        say('SKIP', label, 'no asset', char_bp_path)
        return False
    bp = unreal.load_asset(char_bp_path)
    cdo = unreal.get_default_object(bp.generated_class())
    cdo.set_editor_property('pickup_class', pickup_class)
    unreal.EditorAssetLibrary.save_asset(char_bp_path)
    cdo2 = unreal.get_default_object(unreal.load_asset(char_bp_path).generated_class())
    got = cdo2.get_editor_property('pickup_class')
    got_name = got.get_name() if got else 'NONE'
    say('CHECK', label, 'pickup_class=', got_name)
    return got_name == pickup_class.get_name()


def main():
    ok = True
    sack_cls = ensure_pickup_bp('BP_Pickup', SACK)
    hide_cls = ensure_pickup_bp('BP_PickupWolf', HIDE)
    if not sack_cls or not hide_cls:
        say('RESULT= FAIL')
        return

    if not wire_pickup_class(WOLF_BP, hide_cls, 'WOLF'):
        ok = False
    bandit_done = False
    for cand in BANDIT_CANDIDATES:
        if unreal.EditorAssetLibrary.does_asset_exist(cand):
            if wire_pickup_class(cand, sack_cls, 'BANDIT'):
                bandit_done = True
            break
    if not bandit_done:
        say('PROBLEM bandit BP not wired')
        ok = False
    say('RESULT=', 'OK' if ok else 'FAIL')


main()
