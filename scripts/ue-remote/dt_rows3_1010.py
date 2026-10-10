import unreal
dt = unreal.load_asset('/Game/Data/DT_Items'); L = unreal.DataTableFunctionLibrary
csv = L.export_data_table_to_csv_string(dt); lines = csv.strip().splitlines()
for i, l in enumerate(lines):
    if l.startswith('guard_radio,'): lines[i] = l.replace('guard_radio,"Рация",', 'guard_radio,"",', 1)
    if l.startswith('ammo_12g,'): lines[i] = l.replace('"4.000000"', '"5.000000"')
print('FILL', L.fill_data_table_from_csv_string(dt, '\r\n'.join(lines) + '\r\n'))
after = L.export_data_table_to_csv_string(dt).strip().splitlines()
print('first 18 unchanged', after[:18] == csv.strip().splitlines()[:18]); [print(' ', l[:120]) for l in after[18:]]
print('SAVE', unreal.EditorAssetLibrary.save_loaded_asset(dt, False))
