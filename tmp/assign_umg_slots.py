# -*- coding: utf-8 -*-
# ADR-048: назначение сгенерированных WBP в слоты BP (game-lead, 2026-07-18).
# Правила: назначаю ТОЛЬКО пустые слоты из моего списка; слоты Рината (Shop/Dialog/PlayerStats)
# не трогаю — только печатаю их состояние. VERIFY-режим: запуск с аргументом verify.
import sys
import unreal

VERIFY_ONLY = 'verify' in [a.lower() for a in sys.argv[1:]] if len(sys.argv) > 1 else False

def load_class(path):
    c = unreal.load_object(None, path)
    if c is None:
        unreal.log_error('ASSIGN: класс не найден: %s' % path)
    return c

def cdo_of(bp_class_path):
    c = load_class(bp_class_path)
    if c is None:
        return None
    return unreal.get_default_object(c)

def get_prop(obj, names):
    for n in names:
        try:
            return n, obj.get_editor_property(n)
        except Exception:
            continue
    return None, None

def set_prop(obj, names, value):
    for n in names:
        try:
            obj.set_editor_property(n, value)
            return n
        except Exception:
            continue
    return None

# --- HUD ---
hud_cdo = cdo_of('/Game/UI/BP_ContrarySurvivorHUD.BP_ContrarySurvivorHUD_C')
if hud_cdo is None:
    unreal.log_error('ASSIGN: HUD BP не загрузился')
    sys.exit(1)

my_hud_slots = [
    (['inventory_widget_class'],       '/Game/UI/WBP_Inventory.WBP_Inventory_C'),
    (['death_widget_class'],           '/Game/UI/WBP_Death.WBP_Death_C'),
    (['quest_tracker_widget_class'],   '/Game/UI/WBP_QuestTracker.WBP_QuestTracker_C'),
    (['interact_prompt_widget_class'], '/Game/UI/WBP_InteractPrompt.WBP_InteractPrompt_C'),
]
rinat_hud_slots = [['shop_widget_class'], ['dialog_widget_class'], ['player_stats_widget_class']]

changed_hud = False
for names, wbp in my_hud_slots:
    n, cur = get_prop(hud_cdo, names)
    if n is None:
        unreal.log_error('ASSIGN: свойство не найдено: %s' % names)
        continue
    if VERIFY_ONLY:
        unreal.log('VERIFY HUD %s = %s' % (n, cur))
        continue
    if cur is not None:
        unreal.log('SKIP HUD %s уже назначен: %s' % (n, cur))
        continue
    target = load_class(wbp)
    if target is None:
        continue
    ok = set_prop(hud_cdo, names, target)
    if ok:
        changed_hud = True
        unreal.log('ASSIGN HUD %s -> %s' % (ok, wbp))

for names in rinat_hud_slots:
    n, cur = get_prop(hud_cdo, names)
    unreal.log('INFO HUD слот Рината %s = %s' % (n if n else names, cur))

# --- Контроллер ---
pc_cdo = cdo_of('/Game/System/BP_ContrarySurviorPlayerController.BP_ContrarySurviorPlayerController_C')
if pc_cdo is None:
    unreal.log_error('ASSIGN: контроллер BP не загрузился')
    sys.exit(1)

changed_pc = False
n, cur = get_prop(pc_cdo, ['touch_controls_widget_class'])
if VERIFY_ONLY:
    unreal.log('VERIFY PC touch_controls_widget_class = %s' % cur)
else:
    if cur is not None:
        unreal.log('SKIP PC touch_controls_widget_class уже назначен: %s' % cur)
    else:
        target = load_class('/Game/UI/WBP_TouchControls.WBP_TouchControls_C')
        if target is not None:
            ok = set_prop(pc_cdo, ['touch_controls_widget_class'], target)
            if ok:
                changed_pc = True
                unreal.log('ASSIGN PC touch_controls_widget_class -> WBP_TouchControls_C')

n, cur = get_prop(pc_cdo, ['enable_touch_controls', 'bEnableTouchControls'])
if VERIFY_ONLY:
    unreal.log('VERIFY PC enable_touch_controls = %s' % cur)
else:
    unreal.log('INFO PC enable_touch_controls (до) = %s' % cur)
    if cur is False:
        ok = set_prop(pc_cdo, ['enable_touch_controls', 'bEnableTouchControls'], True)
        if ok:
            changed_pc = True
            unreal.log('ASSIGN PC enable_touch_controls -> True (для ПК-смоука и стилизации Рината)')

# --- Сохранение ---
if not VERIFY_ONLY:
    eal = unreal.EditorAssetLibrary
    for path, ch in [('/Game/UI/BP_ContrarySurvivorHUD', changed_hud),
                     ('/Game/System/BP_ContrarySurviorPlayerController', changed_pc)]:
        if ch:
            saved = eal.save_asset(path, only_if_is_dirty=False)
            unreal.log('SAVE %s = %s' % (path, saved))
        else:
            unreal.log('SAVE SKIP %s (изменений нет)' % path)
unreal.log('ASSIGN-СКРИПТ ЗАВЕРШЁН (verify=%s)' % VERIFY_ONLY)
