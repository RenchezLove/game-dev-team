import unreal, json
# Задание на бандитов: шаг «купи пистолет у торговца» (11.10.2026). Меняются только ячейки
# строки ClearBanditBase: реплика выдачи и шесть полей подготовительного шага.
dt = unreal.load_asset('/Game/Data/DT_Quests'); L = unreal.DataTableFunctionLibrary
before = L.export_data_table_to_json_string(dt)
rows = json.loads(before)
print('QPREP before rows', [r['Name'] for r in rows])
def loc(key, text): return 'NSLOCTEXT("Quest", "%s", "%s")' % (key, text)
for r in rows:
    if r['Name'] == 'ClearBanditBase':
        print('QPREP old description', r['Description'])
        r['Description'] = loc('Q2Description', 'Бандиты к северу от деревни обирают и нас, и торговца. Перебей троих и принеси их ноутбук — узнаю, кто их сюда навёл. С одним ножом туда не суйся: я договорился с торговцем, пистолет он отдаст тебе со скидкой. Не хватит монет — даст в долг, вычту из награды.')
        r['PrepItemRow'] = 'pistol'
        r['PrepDealPrice'] = 100
        r['PrepBuyObjectiveText'] = loc('Q2PrepBuy', 'Купи пистолет у торговца')
        r['PrepEquipObjectiveText'] = loc('Q2PrepEquip', 'Поставь пистолет в слот')
        r['PrepDealText'] = loc('Q2PrepDeal', 'Скидка от старосты')
        r['PrepDebtText'] = loc('Q2PrepDebt', 'В долг: остаток спишут с награды')
print('QPREP fill', L.fill_data_table_from_json_string(dt, json.dumps(rows, ensure_ascii=False)))
after = json.loads(L.export_data_table_to_json_string(dt))
old = {r['Name']: r for r in json.loads(before)}
for r in after:
    diff = [k for k in r if old.get(r['Name'], {}).get(k) != r[k]]
    print('QPREP row %s changed cells: %s' % (r['Name'], diff))
    if r['Name'] == 'ClearBanditBase':
        for k in ['Description', 'PrepItemRow', 'PrepDealPrice', 'PrepBuyObjectiveText', 'PrepEquipObjectiveText', 'PrepDealText', 'PrepDebtText', 'RewardMoney']:
            print('QPREP   %s = %s' % (k, r[k]))
    if r['Name'] == 'KillWolves': print('QPREP   KillWolves RewardMoney = %s' % r['RewardMoney'])
print('QPREP save', unreal.EditorAssetLibrary.save_loaded_asset(dt, False))
