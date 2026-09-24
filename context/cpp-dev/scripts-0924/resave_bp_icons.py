# ADR-088 п.2: пересохранить три чертежа предметов с пустой картинкой (ItemIcon).
import unreal
OUT = r"C:/Users/pgr40/AppData/Local/Temp/claude/E--game-dev-team/f6822a25-9b93-4897-b1ec-6d47fde11879/scratchpad/resave_bp_icons.txt"
L = []
for p in ["/Game/Items/BP_Ammo9mm", "/Game/Items/BP_Knife", "/Game/Weapons/Pistol/BP_Pistol"]:
    bp = unreal.load_asset(p)
    cdo = unreal.get_default_object(bp.generated_class())
    before = cdo.get_editor_property("item_icon")
    cdo.set_editor_property("item_icon", None)
    after = cdo.get_editor_property("item_icon")
    ok = unreal.EditorAssetLibrary.save_asset(p, only_if_is_dirty=False)
    L.append("%s | before=%s | after=%s | saved=%s" % (p, before, after, ok))
with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(L))
unreal.log("RESAVEICONS|RESULT=OK n=%d" % len(L))
