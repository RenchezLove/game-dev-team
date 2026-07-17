import unreal, os

SRC = "E:/game-dev-team/docs/contrary-survivor/ui/hud-icons"
DEST = "/Game/UI/Icons"

MAPPING = {
    "armor-t1-head.png":  "T_Icon_Armor_T1_Head",
    "armor-t1-torso.png": "T_Icon_Armor_T1_Torso",
    "armor-t1-legs.png":  "T_Icon_Armor_T1_Legs",
    "armor-t2-head.png":  "T_Icon_Armor_T2_Head",
    "armor-t2-torso.png": "T_Icon_Armor_T2_Torso",
    "armor-t2-legs.png":  "T_Icon_Armor_T2_Legs",
    "armor-t3-head.png":  "T_Icon_Armor_T3_Head",
    "armor-t3-torso.png": "T_Icon_Armor_T3_Torso",
    "armor-t3-legs.png":  "T_Icon_Armor_T3_Legs",
    "slot-head.png":      "T_Icon_Slot_Head",
    "slot-torso.png":     "T_Icon_Slot_Torso",
    "slot-legs.png":      "T_Icon_Slot_Legs",
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
    path = f"{DEST}/{aname}.{aname}"
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

if unreal.EditorAssetLibrary.does_directory_exist("/Game/_DIAG_ElderLegs"):
    deleted = unreal.EditorAssetLibrary.delete_directory("/Game/_DIAG_ElderLegs")
    unreal.log(f"DIAG_CLEANUP: delete_directory=/Game/_DIAG_ElderLegs result={deleted}")
else:
    unreal.log("DIAG_CLEANUP: /Game/_DIAG_ElderLegs not in registry")
