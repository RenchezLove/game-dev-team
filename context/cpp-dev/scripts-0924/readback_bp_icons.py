# Обратное чтение в НОВОМ запуске: ItemIcon и ключ трёх чертежей после пересохранения.
import unreal
OUT = r"C:/Users/pgr40/AppData/Local/Temp/claude/E--game-dev-team/f6822a25-9b93-4897-b1ec-6d47fde11879/scratchpad/readback_bp_icons.txt"
L = []
for p in ["/Game/Items/BP_Ammo9mm", "/Game/Items/BP_Knife", "/Game/Weapons/Pistol/BP_Pistol"]:
    bp = unreal.load_asset(p)
    cdo = unreal.get_default_object(bp.generated_class())
    icon = cdo.get_editor_property("item_icon")
    L.append("%s | item_icon=%s | is_null=%s | item_name=%s" % (p, icon, str(icon) in ("None", "") or icon is None, cdo.get_editor_property("item_name")))
with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(L))
unreal.log("READBACKICONS|RESULT=OK n=%d" % len(L))
