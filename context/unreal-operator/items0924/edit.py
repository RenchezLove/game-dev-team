import unreal
L = []
def p(s):
    L.append(str(s)); unreal.log("EDIT|" + str(s))
EAL = unreal.EditorAssetLibrary
dt = unreal.load_asset("/Game/Data/DT_Items")
rows = [str(n) for n in unreal.DataTableFunctionLibrary.get_data_table_row_names(dt)]
for r in ["canned_food","water_bottle","bandage","armor_t2_pants","armor_t3_head","ammo_9mm"]:
    assert r in rows, "row missing " + r
for n,k in zip(rows, unreal.DataTableFunctionLibrary.get_data_table_column_as_string(dt, "LegacyKey")):
    p("LEGACYKEY %s = %s" % (n,k))

def entry(row, count):
    e = unreal.PlacedLootEntry()
    e.set_editor_property("ItemRow", row)
    e.set_editor_property("ItemClass", None)
    e.set_editor_property("Count", count)
    return e

# 1. Level
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level("/Game/Maps/L_World_C")
acts = {a.get_name(): a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()}
pickups = {"Pickup_1": "canned_food", "BP_Pickup_C_10": "canned_food", "BP_Pickup_C_14": "canned_food", "BP_Pickup_C_1": "armor_t2_pants"}
for name, row in pickups.items():
    a = acts[name]
    a.modify()
    cnt = a.get_editor_property("PlacedItemCount")
    ammo = a.get_editor_property("PlacedAmmoAmount")
    lst = [entry(row, max(1, cnt))]
    if ammo > 0:
        lst.append(entry("ammo_9mm", ammo))
    a.set_editor_property("PlacedLootList", lst)
    a.set_editor_property("PlacedItemClass", None)
    a.set_editor_property("PlacedItemCount", 1)
    a.set_editor_property("PlacedAmmoAmount", 0)
    a.set_editor_property("PlacedItemDisplayName", "")
    p("PICKUP %s -> %s x%d%s" % (name, row, max(1,cnt), (" + ammo_9mm x%d" % ammo) if ammo > 0 else ""))
cars = {"BP_AbandonedCar_C_3": ("BP_WaterBottle", "water_bottle"), "BP_AbandonedCar_C_5": ("HeadArmorT3", "armor_t3_head")}
for name, (cls_name, row) in cars.items():
    a = acts[name]
    a.modify()
    lst = list(a.get_editor_property("PlacedLootList"))
    hit = 0
    for i, e in enumerate(lst):
        c = e.get_editor_property("ItemClass")
        if c is not None and cls_name in str(c):
            lst[i] = entry(row, e.get_editor_property("Count")); hit += 1
    assert hit == 1, "car %s hits=%d" % (name, hit)
    a.set_editor_property("PlacedLootList", lst)
    p("CAR %s -> %s" % (name, row))
ok = EAL.save_asset("/Game/Maps/L_World_C", only_if_is_dirty=False)
p("SAVE L_World_C=%s" % ok)

# 2. Bandit
bc = unreal.load_object(None, "/Game/Characters/Bandit/BP_EnemyBandit.BP_EnemyBandit_C")
cdo = unreal.get_default_object(bc)
m = {"Консервы": "canned_food", "Вода": "water_bottle", "Аптечка": "bandage"}
lt = list(cdo.get_editor_property("LootTable"))
hits = 0
for i, e in enumerate(lt):
    k = e.get_editor_property("DisplayName")
    if k in m:
        e.set_editor_property("ItemRow", m[k]); lt[i] = e; hits += 1
assert hits == 3, "bandit hits=%d" % hits
cdo.set_editor_property("LootTable", lt)
ok = EAL.save_asset("/Game/Characters/Bandit/BP_EnemyBandit", only_if_is_dirty=False)
p("SAVE BP_EnemyBandit=%s" % ok)

# 3. Icons off item blueprints
for path in ["/Game/Items/BP_Ammo9mm", "/Game/Items/BP_Knife", "/Game/Weapons/Pistol/BP_Pistol"]:
    name = path.split("/")[-1]
    c = unreal.load_object(None, "%s.%s_C" % (path, name))
    d = unreal.get_default_object(c)
    d.set_editor_property("ItemIcon", None)
    ok = EAL.save_asset(path, only_if_is_dirty=False)
    p("ICON CLEARED %s save=%s" % (name, ok))
p("RESULT=OK")
