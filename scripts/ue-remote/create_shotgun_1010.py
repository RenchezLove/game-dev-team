import unreal
# Чертёж двустволки, пачка патронов 12 калибра и их строки в таблице предметов (значки подставятся позже).
eal = unreal.EditorAssetLibrary; at = unreal.AssetToolsHelpers.get_asset_tools()
print('PIE', unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor())
def make_bp(name, folder, parent):
    p = folder + '/' + name
    if eal.does_asset_exist(p): return unreal.load_asset(p)
    f = unreal.BlueprintFactory(); f.set_editor_property('parent_class', parent)
    return at.create_asset(name, folder, unreal.Blueprint, f)
pm = unreal.load_asset('/Game/Weapons/SM_Pistol'); b = pm.get_bounding_box()
print('PISTOL bounds', [round(v) for v in (b.min.x, b.min.y, b.min.z)], [round(v) for v in (b.max.x, b.max.y, b.max.z)])
pcdo = unreal.get_default_object(unreal.load_asset('/Game/Weapons/Pistol/BP_Pistol').generated_class())
bp = make_bp('BP_Shotgun', '/Game/Weapons/Shotgun', unreal.Shotgun)
cdo = unreal.get_default_object(bp.generated_class())
for c in cdo.get_components_by_class(unreal.StaticMeshComponent):
    if c.get_name() == 'ItemMesh':
        c.set_editor_property('static_mesh', unreal.load_asset('/Game/Weapons/Shotgun/SM_Shotgun_TOZ34'))
snd = pcdo.get_editor_property('fire_sound_variations')
print('pistol sounds', [s.get_name() for s in snd if s])
cdo.set_editor_property('fire_sound_variations', snd)
for k in ['damage', 'pellets_per_shot', 'pellet_spread_angle', 'range', 'ammo_type', 'grip_offset_location', 'grip_offset_rotation', 'fire_sound_volume']:
    try: print('  SHOTGUN', k, cdo.get_editor_property(k), '| PISTOL', pcdo.get_editor_property(k))
    except Exception as e: print('  ', k, 'ERR', str(e)[:80])
unreal.BlueprintEditorLibrary.compile_blueprint(bp); print('SAVE BP_Shotgun', eal.save_loaded_asset(bp, False))
ab = make_bp('BP_Ammo12g', '/Game/Items', unreal.ShotgunAmmoItem)
unreal.BlueprintEditorLibrary.compile_blueprint(ab); print('SAVE BP_Ammo12g', eal.save_loaded_asset(ab, False))
dt = unreal.load_asset('/Game/Data/DT_Items')
csv = dt.export_to_csv_string() if hasattr(dt, 'export_to_csv_string') else unreal.DataTableFunctionLibrary.export_data_table_to_csv_string(dt)
open('E:/game-dev-team/scripts/ue-remote/_dt_items_before_1010.csv', 'w', encoding='utf-8').write(csv)
rows = [str(x) for x in unreal.DataTableFunctionLibrary.get_data_table_row_names(dt)]
add = []
if 'shotgun_toz34' not in rows:
    add.append('shotgun_toz34,"","NSLOCTEXT(""Items"", ""ShotgunTOZ34"", ""Двустволка"")","None","/Game/Weapons/Shotgun/SM_Shotgun_TOZ34.SM_Shotgun_TOZ34","None","/Game/Weapons/Shotgun/BP_Shotgun.BP_Shotgun_C","Weapon","1","300.000000","Food","Head","0.000000"')
if 'ammo_12g' not in rows:
    add.append('ammo_12g,"","NSLOCTEXT(""Items"", ""Ammo12g"", ""Патроны 12 калибра"")","None","None","None","/Game/Items/BP_Ammo12g.BP_Ammo12g_C","Resource","999","4.000000","Food","Head","0.000000"')
if add:
    new = csv.rstrip('\r\n') + '\r\n' + '\r\n'.join(add) + '\r\n'
    print('FILL problems', unreal.DataTableFunctionLibrary.fill_data_table_from_csv_string(dt, new))
    after = unreal.DataTableFunctionLibrary.export_data_table_to_csv_string(dt) if not hasattr(dt, 'export_to_csv_string') else dt.export_to_csv_string()
    old_lines = csv.strip().splitlines(); new_lines = after.strip().splitlines()
    print('OLD ROWS UNCHANGED', old_lines == new_lines[:len(old_lines)], len(old_lines), len(new_lines))
    for l in new_lines[len(old_lines):]: print('  +', l)
    print('SAVE DT', eal.save_loaded_asset(dt, False))
