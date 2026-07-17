# stage-f: дефолты QuestMarkerTag в BP-классах логова/базы + наследник BP_WolfDen2
# Запуск: headless UnrealEditor-Cmd -ExecutePythonScript (ADR-021). Маркер лога: UOPTAG:
import unreal

M = "UOPTAG: "

def log(msg):
    unreal.log(M + msg)

log("START stage_f_set_marker_defaults")

# --- 1+2: дефолт QuestMarkerTag на CDO существующих BP ---
targets = [
    ("/Game/Characters/Wolf/BP_WolfDen", "WolfDen"),
    ("/Game/Characters/Bandit/BP_BanditBase", "BanditBase"),
]
for asset_path, tag in targets:
    name = asset_path.rsplit("/", 1)[1]
    cls = unreal.load_object(None, "{}.{}_C".format(asset_path, name))
    if cls is None:
        log("FAIL load class {}".format(asset_path))
        continue
    cdo = unreal.get_default_object(cls)
    before = str(cdo.get_editor_property("quest_marker_tag"))
    cdo.set_editor_property("quest_marker_tag", unreal.Name(tag))
    after = str(cdo.get_editor_property("quest_marker_tag"))
    saved = unreal.EditorAssetLibrary.save_asset(asset_path, only_if_is_dirty=False)
    log("SET {}: before='{}' after='{}' saved={}".format(name, before, after, saved))

# --- 3: наследник BP_WolfDen2 (parent = BP_WolfDen_C), тег WolfDen2 ---
child_path = "/Game/Characters/Wolf/BP_WolfDen2"
if unreal.EditorAssetLibrary.does_asset_exist(child_path):
    log("BP_WolfDen2 ALREADY EXISTS at {} - создание пропущено".format(child_path))
else:
    parent_cls = unreal.load_object(None, "/Game/Characters/Wolf/BP_WolfDen.BP_WolfDen_C")
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", parent_cls)
    at = unreal.AssetToolsHelpers.get_asset_tools()
    new_bp = at.create_asset("BP_WolfDen2", "/Game/Characters/Wolf", None, factory)
    if new_bp is None:
        log("FAIL create_asset BP_WolfDen2 returned None")
    else:
        unreal.BlueprintEditorLibrary.compile_blueprint(new_bp)
        log("CREATED {}".format(new_bp.get_path_name()))

child_cls = unreal.load_object(None, child_path + ".BP_WolfDen2_C")
if child_cls is None:
    log("FAIL load class BP_WolfDen2_C")
else:
    child_cdo = unreal.get_default_object(child_cls)
    child_cdo.set_editor_property("quest_marker_tag", unreal.Name("WolfDen2"))
    after = str(child_cdo.get_editor_property("quest_marker_tag"))
    num = child_cdo.get_editor_property("num_to_spawn")
    saved = unreal.EditorAssetLibrary.save_asset(child_path, only_if_is_dirty=False)
    log("SET BP_WolfDen2: tag='{}' num_to_spawn={} saved={}".format(after, num, saved))

log("DONE stage_f_set_marker_defaults")
