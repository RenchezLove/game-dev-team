# -*- coding: utf-8 -*-
# ADR-048, волна 2 (game-lead, 2026-07-19): назначение сгенерированных панелей в слоты HUD.
# Ринат удалил свои пустые WBP (2754045) -> слоты Shop/Dialog/PlayerStats назначаем нашими
# сгенерированными (d9109c1). Назначаю ТОЛЬКО пустые слоты. VERIFY-режим: аргумент verify.
import sys
import unreal

VERIFY_ONLY = 'verify' in [a.lower() for a in sys.argv[1:]] if len(sys.argv) > 1 else False

def load_class(path):
    c = unreal.load_object(None, path)
    if c is None:
        unreal.log_error('ASSIGN2: класс не найден: %s' % path)
    return c

hud_class = load_class('/Game/UI/BP_ContrarySurvivorHUD.BP_ContrarySurvivorHUD_C')
if hud_class is None:
    unreal.log_error('ASSIGN2: HUD BP не загрузился')
    sys.exit(1)
hud_cdo = unreal.get_default_object(hud_class)

slots = [
    ('shop_widget_class',         '/Game/UI/WBP_Shop.WBP_Shop_C'),
    ('dialog_widget_class',       '/Game/UI/WBP_Dialog.WBP_Dialog_C'),
    ('player_stats_widget_class', '/Game/UI/WBP_PlayerStats.WBP_PlayerStats_C'),
]

changed = False
for prop, wbp in slots:
    try:
        cur = hud_cdo.get_editor_property(prop)
    except Exception as e:
        unreal.log_error('ASSIGN2: свойство не найдено: %s (%s)' % (prop, e))
        continue
    if VERIFY_ONLY:
        unreal.log('VERIFY HUD %s = %s' % (prop, cur))
        continue
    if cur is not None:
        unreal.log('SKIP HUD %s уже назначен: %s' % (prop, cur))
        continue
    target = load_class(wbp)
    if target is None:
        continue
    hud_cdo.set_editor_property(prop, target)
    changed = True
    unreal.log('ASSIGN HUD %s -> %s' % (prop, wbp))

if not VERIFY_ONLY:
    if changed:
        saved = unreal.EditorAssetLibrary.save_asset('/Game/UI/BP_ContrarySurvivorHUD', only_if_is_dirty=False)
        unreal.log('SAVE /Game/UI/BP_ContrarySurvivorHUD = %s' % saved)
    else:
        unreal.log('SAVE SKIP (изменений нет)')
unreal.log('ASSIGN2-СКРИПТ ЗАВЕРШЁН (verify=%s)' % VERIFY_ONLY)
