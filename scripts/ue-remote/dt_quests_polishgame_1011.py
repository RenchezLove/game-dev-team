import unreal, json
# Таблица заданий, правки после игры Рината 11.10.2026:
#  1) тексты заданий старосты переписаны простым современным русским;
#  2) у задания на бандитов — подсказка после покупки пистолета и порог здоровья при выходе из деревни;
#  3) в таблицу добавлены задания «Отнести ноутбук учёным» и «Рация охранника» (раньше жили в коде).
# Числа (цели, награды, цены) не меняются. Повторный запуск ничего не меняет.
dt = unreal.load_asset('/Game/Data/DT_Quests'); L = unreal.DataTableFunctionLibrary
before = L.export_data_table_to_json_string(dt)
rows = json.loads(before)
print('QPOLISH before rows', [r['Name'] for r in rows])
def loc(key, text, ns='Quest'): return 'NSLOCTEXT("%s", "%s", "%s")' % (ns, key, text.replace('\n', '\\n'))

GUARD_ASK = ('Слушай, раз уж ты пришёл, помоги мне. За мной гнались волки из южного логова, и я на бегу потерял рацию. '
    'Она лежит где-то у логова, к югу от деревни. Сам я уйти с поста не могу, а за рацию учёных отвечаю я. Принеси её — и я отдам тебе двустволку и патроны к ней.')

by_name = {r['Name']: r for r in rows}
template = dict(by_name['KillWolves'])

q1 = by_name['KillWolves']
q1['Description'] = loc('Q1Description', 'Волки подходят к самой деревне, люди боятся выйти за дровами и за водой. Уничтожь волчье логово на западе и принеси мне три шкуры.')

q2 = by_name['ClearBanditBase']
q2['Description'] = loc('Q2Description', 'К северу от деревни засели бандиты. Они грабят и нас, и торговца. Убей троих бандитов и принеси мне их ноутбук — я хочу узнать, кто их сюда прислал. С одним ножом туда не ходи: я договорился с торговцем, он продаст тебе пистолет со скидкой. Если монет не хватит, он даст пистолет в долг, а я вычту долг из твоей награды.')
q2['PrepEquipObjectiveText'] = loc('Q2PrepEquip', 'Открой сумку и поставь пистолет в слот оружия')
q2['PrepDebtText'] = loc('Q2PrepDebt', 'В долг, остаток вычтут из награды')
q2['PrepBoughtHintText'] = loc('Q2PrepBoughtHint', 'Пистолет куплен. Закрой окно торговли, открой сумку и поставь пистолет в слот оружия.')
q2['LowHealthWarnThreshold'] = 45
q2['LowHealthWarnText'] = loc('Q2LowHealthWarn', 'Здоровье на исходе. Перед походом на бандитов купи у торговца аптечку и подлечись.')

def fresh(name):
    r = by_name.get(name)
    if r is None:
        r = dict(template); r['Name'] = name; rows.append(r); by_name[name] = r
    # Пустая заготовка: всё, что не задано ниже, — как у строки без целей и наград.
    r.update({'Type': 'Deliver', 'KillTargetTag': 'None', 'TargetCount': 0, 'KillObjectiveLabel': '',
        'RequiredItemRow': 'None', 'RequiredItemCount': 0, 'ItemObjectiveLabel': '', 'MapMarkerTag': 'None',
        'RewardMoney': 0, 'NextQuestRow': 'None', 'TurnInNpcTag': 'None', 'TurnInHintText': '',
        'GiveOnAccept': [], 'RewardItems': [], 'Kind': 'Main', 'PrepItemRow': 'None', 'PrepDealPrice': 0,
        'PrepBuyObjectiveText': '', 'PrepEquipObjectiveText': '', 'PrepDealText': '', 'PrepDebtText': '',
        'PrepBoughtHintText': '', 'LowHealthWarnThreshold': 0, 'LowHealthWarnText': '', 'RewardEquipItemRow': 'None'})
    return r

# Третье задание старосты: значения те же, что были в коде (AElderNPC), тексты переписаны.
q3 = fresh('DeliverLaptopToScientists')
q3.update({
    'Title': loc('Q3Title', 'Отнести ноутбук учёным'),
    'Description': loc('Q3Description', 'Я не справился с ноутбуком: данные в нём защищены слишком хорошо для меня. Отнеси его учёным. Их база находится на юго-западе: от перекрёстка иди по дороге на юг. Учёные любят такие загадки, а я не могу оставить деревню. Забирай ноутбук и по дороге никому его не показывай.'),
    'Type': 'Deliver', 'RequiredItemRow': 'laptop', 'RequiredItemCount': 1,
    'ItemObjectiveLabel': loc('Q3ItemObjective', 'Отнести ноутбук учёным'),
    'MapMarkerTag': 'ScientistQuest', 'RewardMoney': 150, 'TurnInNpcTag': 'ScientistQuest',
    'TurnInHintText': loc('Q3TurnInHint', 'отнеси ноутбук учёным'),
    'AcceptReplyText': loc('Q3AcceptReply', 'Отнесу. Я и сам хочу это знать.'),
    'TurnInReplyText': loc('Q3TurnInReply', 'Вот ноутбук.'),
    'CloseReplyText': loc('Q3CloseReply', 'Мне пора.'),
    'GiveOnAccept': [{'ItemRow': 'laptop', 'Count': 1}], 'Kind': 'Main'})

# Задание охранника базы учёных: значения те же, что были в коде (AScientistGuardNPC).
qg = fresh('FetchGuardRadio')
qg.update({
    'Title': loc('GuardRadioTitle', 'Рация охранника'),
    'Description': loc('GuardRadioDescription', 'Стой. Дальше находится база учёных, а я стою здесь на посту.\n' + GUARD_ASK),
    'Type': 'Collect', 'RequiredItemRow': 'guard_radio', 'RequiredItemCount': 1,
    'ItemObjectiveLabel': loc('GuardRadioObjective', 'Найти рацию охранника'),
    'MapMarkerTag': 'GuardRadioSpot', 'RewardMoney': 0,
    'TurnInHintText': loc('GuardRadioTurnInHint', 'верни рацию охраннику'),
    'AcceptReplyText': loc('GuardRadioAccept', 'Поищу твою рацию.'),
    'TurnInReplyText': loc('GuardRadioTurnIn', 'Держи свою рацию.'),
    'CloseReplyText': loc('GuardRadioClose', 'Не сейчас.'),
    'RewardItems': [{'ItemRow': 'shotgun_toz34', 'Count': 1}, {'ItemRow': 'ammo_12g', 'Count': 4}],
    'Kind': 'Side', 'RewardEquipItemRow': 'shotgun_toz34'})

print('QPOLISH fill', L.fill_data_table_from_json_string(dt, json.dumps(rows, ensure_ascii=False)))
after = json.loads(L.export_data_table_to_json_string(dt))
old = {r['Name']: r for r in json.loads(before)}
for r in after:
    o = old.get(r['Name'])
    diff = [k for k in r if o is None or o.get(k) != r[k]]
    print('QPOLISH row %s %s changed cells: %s' % (r['Name'], 'NEW' if o is None else 'old', diff))
    for k in ['Kind', 'TargetCount', 'RequiredItemRow', 'RequiredItemCount', 'RewardMoney', 'MapMarkerTag', 'TurnInNpcTag',
              'GiveOnAccept', 'RewardItems', 'PrepItemRow', 'PrepDealPrice', 'LowHealthWarnThreshold', 'RewardEquipItemRow']:
        print('QPOLISH   %s = %s' % (k, r.get(k)))
print('QPOLISH save', unreal.EditorAssetLibrary.save_loaded_asset(dt, False))
