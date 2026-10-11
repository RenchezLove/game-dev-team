import unreal, json
# Выгрузка текстов заданий, разговоров и подсказок, как их видит игра (11.10.2026): таблица
# заданий, размещённые на уровне собеседники и значения по умолчанию чертежей. Ничего не меняет.
def one(s): return str(s).replace('\r', '').replace('\n', '\\n')
dt = unreal.load_asset('/Game/Data/DT_Quests'); L = unreal.DataTableFunctionLibrary
for r in json.loads(L.export_data_table_to_json_string(dt)):
    for k in sorted(r):
        v = r[k]
        if isinstance(v, str) and v and any(u'Ѐ' <= c <= u'ӿ' for c in v):
            print('TXT|DT_Quests|%s|%s|%s' % (r['Name'], k, one(v)))
    print('TXTROW|%s|%s' % (r['Name'], one(json.dumps(r, ensure_ascii=False))))

PROPS = ['dialogue_display_name', 'dialogue_active_prefix', 'dialogue_completed_text', 'first_quest_completed_text',
    'dialogue_turned_in_text', 'dialogue_early_hook_text', 'first_gift_hint_format', 'npc_marker_label',
    'third_quest_carry_text', 'third_quest_done_text', 'notebook_hint_repeat_text',
    'idle_text', 'close_reply_text', 'interact_prompt_action', 'quest_active_text', 'quest_completed_text',
    'quest_turned_in_text', 'quest_just_turned_in_text', 'quest_row', 'foreign_turn_in_text', 'foreign_turn_in_reply_text', 'foreign_turn_in_done_text',
    'after_foreign_turn_in_text', 'not_vouched_text', 'laptop_pass_text', 'laptop_pass_offer_text',
    'offer_text', 'accept_reply_text', 'decline_reply_text', 'running_text', 'paid_text', 'again_reply_text',
    'not_finished_text', 'not_ready_text', 'cooling_text', 'sell_locked_reason_text', 'quest_item_text',
    'tier2_suffix', 'tier3_plus_suffix', 'base_display_name',
    'intro_line1', 'intro_line2', 'intro_objective_go_to_village', 'intro_objective_find_elder', 'intro_skip_hint_text',
    'interact_prompt_pickup_action', 'interact_prompt_trader_action', 'interact_prompt_elder_action',
    'interact_prompt_corpse_action', 'interact_prompt_stash_action', 'progress_saved_message',
    'hint_text_movement', 'hint_text_movement_touch', 'hint_text_attack', 'hint_text_weapon_switch',
    'hint_text_weapon_switch_touch', 'hint_text_pickup', 'hint_text_pickup_touch', 'hint_text_elder',
    'hint_text_inventory', 'hint_text_death', 'hint_text_leave_village', 'wounded_text', 'first_hint_text',
    'end_of_story_message_text']
STRUCTS = ['intro_lines', 'notebook_hint_lines', 'offered_quest', 'second_quest', 'third_quest']

def dump(tag, obj):
    for p in PROPS:
        try: v = obj.get_editor_property(p)
        except Exception: continue
        print('TXT|%s|%s|%s' % (tag, p, one(v)))
    for p in STRUCTS:
        try: v = obj.get_editor_property(p)
        except Exception: continue
        items = v if isinstance(v, (list, unreal.Array)) else [v]
        for i, it in enumerate(items):
            print('TXTS|%s|%s[%d]|%s' % (tag, p, i, one(it.export_text())))

unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/L_World_C')
keys = ['Elder', 'Trader', 'Scientist', 'Guard', 'Talker']
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    cls = a.get_class().get_name()
    if any(k in cls for k in keys):
        dump('LEVEL %s (%s)' % (a.get_actor_label(), cls), a)

for path in ['/Game/Characters/Elder/BP_Elder', '/Game/Characters/Trader/BP_Trader',
    '/Game/Characters/Scientist/BP_ScientistHelmet', '/Game/Characters/Scientist/BP_ScientistQuest',
    '/Game/Characters/Scientist/BP_ScientistTrader', '/Game/Characters/ScientistGuard/BP_ScientistGuard',
    '/Game/Characters/Player/BP_PlayerCharacter', '/Game/System/BP_ContrarySurviorPlayerController',
    '/Game/UI/BP_ContrarySurvivorHUD']:
    name = path.split('/')[-1]
    cls = unreal.load_class(None, '%s.%s_C' % (path, name))
    if not cls: print('TXT|ERR|no class', path); continue
    cdo = unreal.get_default_object(cls)
    dump('CDO %s' % name, cdo)
    for comp_name in ['onboarding', 'onboarding_component']:
        try: dump('CDO %s.%s' % (name, comp_name), cdo.get_editor_property(comp_name))
        except Exception: pass
print('TXT|DONE')
