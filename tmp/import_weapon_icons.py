import unreal, os

# Импорт иконок оружия для тач-слоя (запрос Рината 07-19: «какое оружие в руках»).
# Настройки текстуры — как у T_Icon_Armor_* (tmp/import_armor_icons.py, ADR-043).

SRC = "E:/game-dev-team/docs/contrary-survivor/ui/hud-icons"
DEST = "/Game/UI/Icons"

MAPPING = {
    "pistol.png": "T_Icon_Pistol",
    "knife.png":  "T_Icon_Knife",
}

tools = unreal.AssetToolsHelpers.get_asset_tools()
ok, fail = [], []
for fname, aname in MAPPING.items():
    src_file = os.path.join(SRC, fname)
    if not os.path.isfile(src_file):
        fail.append(f"{fname}: source missing")
        continue
    task = unreal.AssetImportTask()
    task.filename = src_file
    task.destination_path = DEST
    task.destination_name = aname
    task.automated = True
    task.replace_existing = True
    task.save = False
    tools.import_asset_tasks([task])
    tex = unreal.EditorAssetLibrary.load_asset(f"{DEST}/{aname}")
    if not tex:
        fail.append(f"{fname}: import failed")
        continue
    tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_EDITOR_ICON)
    tex.set_editor_property("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
    tex.set_editor_property("srgb", True)
    saved = unreal.EditorAssetLibrary.save_asset(f"{DEST}/{aname}")
    ok.append(f"{aname}({'saved' if saved else 'NOT-SAVED'})")

unreal.log(f"ICONIMPORT_OK[{len(ok)}]: " + ", ".join(ok))
unreal.log(f"ICONIMPORT_FAIL[{len(fail)}]: " + ", ".join(fail))
