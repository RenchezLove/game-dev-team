import unreal, sys
out_path = sys.argv[-1] if len(sys.argv) > 1 and sys.argv[-1].endswith('.txt') else None
L = []
def p(s): L.append(str(s))
def gp(o, n):
    try: return o.get_editor_property(n)
    except Exception as e: return "<ERR %s>" % e
def entry_str(e):
    try:
        return "ItemRow=%s ItemClass=%s Count=%s" % (gp(e,"ItemRow"), gp(e,"ItemClass"), gp(e,"Count"))
    except Exception as ex: return "<ERR %s>" % ex

dt = unreal.load_asset("/Game/Data/DT_Items")
p("DT_ROWS=" + ",".join(str(n) for n in unreal.DataTableFunctionLibrary.get_data_table_row_names(dt)))
try:
    icons = unreal.DataTableFunctionLibrary.get_data_table_column_as_string(dt, "Icon")
    names = unreal.DataTableFunctionLibrary.get_data_table_row_names(dt)
    for n,i in zip(names, icons): p("DT_ICON %s = %s" % (n,i))
except Exception as e: p("DT_ICON ERR %s" % e)

# Bandit
bc = unreal.load_object(None, "/Game/Characters/Bandit/BP_EnemyBandit.BP_EnemyBandit_C")
p("BANDIT_CLASS=%s" % bc)
if bc:
    cdo = unreal.get_default_object(bc)
    for i,e in enumerate(gp(cdo,"LootTable")):
        p("BANDIT_LOOT[%d] ItemRow=%s DisplayName=%s DisplayText=%s ItemClass=%s Type=%s" % (i, gp(e,"ItemRow"), gp(e,"DisplayName"), gp(e,"DisplayText"), gp(e,"ItemClass"), gp(e,"ConsumableType")))

# Item BPs with icon
ar = unreal.AssetRegistryHelpers.get_asset_registry()
flt = unreal.ARFilter(class_paths=[unreal.TopLevelAssetPath("/Script/Engine","Blueprint")], package_paths=["/Game"], recursive_paths=True)
base = unreal.load_class(None, "/Script/ContrarySurvivor.MasterInventoryItem")
for ad in ar.get_assets(flt):
    bp = ad.get_asset()
    try: gc = bp.generated_class()
    except Exception: gc = None
    if gc is None: continue
    if not unreal.MathLibrary.class_is_child_of(gc, base): continue
    cdo = unreal.get_default_object(gc)
    p("ITEMBP %s parent=%s ItemIcon=%s SourceItemRow=%s ItemName=%s" % (ad.package_name, str(gc), gp(cdo,"ItemIcon"), gp(cdo,"SourceItemRow"), gp(cdo,"ItemName")))

# Level
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level("/Game/Maps/L_World_C")
want = ["Pickup_1","BP_Pickup_C_10","BP_Pickup_C_14","BP_Pickup_C_1","BP_AbandonedCar_C_3","BP_AbandonedCar_C_5"]
acts = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
for a in acts:
    nm = a.get_name(); lb = a.get_actor_label()
    cls = str(a.get_class().get_name())
    if nm in want or lb in want or "Pickup" in cls or "AbandonedCar" in cls or unreal.MathLibrary.class_is_child_of(a.get_class(), base):
        p("ACTOR name=%s label=%s class=%s" % (nm, lb, cls))
        for prop in ["PlacedItemClass","PlacedItemCount","PlacedAmmoAmount","PlacedItemDisplayName","PlacedItemDisplayText","MoneyAmount","SourceItemRow","ItemIcon"]:
            v = gp(a, prop)
            if not str(v).startswith("<ERR"): p("   %s=%s" % (prop, v))
        pl = gp(a, "PlacedLootList")
        if not str(pl).startswith("<ERR"):
            for i,e in enumerate(pl): p("   LIST[%d] %s" % (i, entry_str(e)))
p("DUMP|RESULT=OK")
txt = "\n".join(L)
open(r"C:/Users/pgr40/AppData/Local/Temp/claude/E--game-dev-team/f6822a25-9b93-4897-b1ec-6d47fde11879/scratchpad/items0924/" + (sys.argv[1] if len(sys.argv)>1 else "dump_before.txt"), "w", encoding="utf-8").write(txt)
unreal.log("DUMP|RESULT=OK")
