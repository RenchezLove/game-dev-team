import unreal, json
# Выгрузка таблицы предметов (11.10.2026): класс, служебный ключ и предел стопки каждой строки.
dt = unreal.load_asset('/Game/Data/DT_Items'); L = unreal.DataTableFunctionLibrary
for r in json.loads(L.export_data_table_to_json_string(dt)):
    print('ITEMROW|%s|%s' % (r['Name'], json.dumps(r, ensure_ascii=False).replace('\n', ' ')))
print('ITEMROW|DONE')
