import unreal, re
dt = unreal.load_asset('/Game/Data/DT_Items'); L = unreal.DataTableFunctionLibrary
csv = L.export_data_table_to_csv_string(dt)
lines = csv.strip().splitlines(); n0 = len(lines)
I = '/Game/UI/Icons/Items/'
def seticon(row, icon):
    for i, l in enumerate(lines):
        if l.startswith(row + ','):
            parts = l.split('","'); parts[2] = I + icon + '.' + icon; lines[i] = '","'.join(parts)
seticon('shotgun_toz34', 'T_Item_Shotgun'); seticon('ammo_12g', 'T_Item_Ammo12g')
if not any(l.startswith('guard_radio,') for l in lines):
    lines.append('guard_radio,"Рация","NSLOCTEXT(""Items"", ""QuestGuardRadio"", ""Рация"")","' + I + 'T_Item_WalkieTalkie.T_Item_WalkieTalkie","/Game/Environment/Props/ScientistBase/SM_WalkieTalkie.SM_WalkieTalkie","None","/Game/Items/BP_GuardRadio.BP_GuardRadio_C","Quest","999","0.000000","Food","Head","0.000000"')
print('FILL', L.fill_data_table_from_csv_string(dt, '\r\n'.join(lines) + '\r\n'))
after = L.export_data_table_to_csv_string(dt).strip().splitlines()
print('first 18 unchanged', after[:18] == csv.strip().splitlines()[:18], len(after))
for l in after[18:]: print(' ', l)
print('SAVE', unreal.EditorAssetLibrary.save_loaded_asset(dt, False))
