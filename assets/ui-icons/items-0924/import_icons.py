import unreal, os
SRC = r"C:/Users/pgr40/AppData/Local/Temp/claude/E--game-dev-team/f6822a25-9b93-4897-b1ec-6d47fde11879/scratchpad/icons_out"
DST = "/Game/UI/Icons/Items"
OLD = ["/Game/UI/Icons/T_Icon_Armor_%s_%s" % (t, s) for t in ("T1","T2","T3") for s in ("Head","Torso","Legs")] + ["/Game/UI/Icons/T_Icon_Knife", "/Game/UI/Icons/T_Icon_Pistol", "/Game/UI/Icons/Items/Icon_Knife2"]
log = []
reg = unreal.AssetRegistryHelpers.get_asset_registry()
opts = unreal.AssetRegistryDependencyOptions(include_soft_package_references=True, include_hard_package_references=True, include_searchable_names=True, include_soft_management_references=False, include_hard_management_references=False)
ref = unreal.load_asset(DST + "/T_Item_Pistol")
props = ["compression_settings", "lod_group", "srgb", "mip_gen_settings", "never_stream", "max_texture_size"]
old_vals = {p: ref.get_editor_property(p) for p in props}
log.append("OLD pistol settings: %s size %dx%d" % (old_vals, ref.blueprint_get_size_x(), ref.blueprint_get_size_y()))
tasks = []
for f in sorted(os.listdir(SRC)):
    t = unreal.AssetImportTask()
    t.filename = SRC + "/" + f; t.destination_path = DST; t.destination_name = f[:-4]
    t.replace_existing = True; t.replace_existing_settings = False; t.automated = True; t.save = False
    tasks.append(t)
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
for t in tasks:
    p = DST + "/" + t.destination_name
    a = unreal.load_asset(p)
    for k, v in old_vals.items(): a.set_editor_property(k, v)
    unreal.EditorAssetLibrary.save_asset(p, only_if_is_dirty=False)
    a = unreal.load_asset(p)
    log.append("IMPORTED %s %dx%d comp=%s lod=%s" % (p, a.blueprint_get_size_x(), a.blueprint_get_size_y(), a.get_editor_property("compression_settings"), a.get_editor_property("lod_group")))
for p in OLD:
    if not unreal.EditorAssetLibrary.does_asset_exist(p):
        log.append("MISSING " + p); continue
    refs = reg.get_referencers(p.rsplit(".",1)[0], opts) or []
    refs = [str(r) for r in refs if str(r) != p]
    if refs:
        log.append("KEEP (referenced by %s) %s" % (refs, p))
    else:
        ok = unreal.EditorAssetLibrary.delete_asset(p)
        log.append("DELETED %s -> %s" % (p, ok))
open(SRC + "/../import_log.txt", "w", encoding="utf-8").write("\n".join(log))
