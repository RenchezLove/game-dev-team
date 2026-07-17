# stage-f: ВЕРИФИКАЦИЯ дефолтов QuestMarkerTag (свежий headless-процесс, читает с диска).
# Маркер лога: UOPVERIFY:
import unreal

M = "UOPVERIFY: "

def log(msg):
    unreal.log(M + msg)

log("START stage_f_verify_marker_defaults")
ok = True

checks = [
    ("/Game/Characters/Wolf/BP_WolfDen", "WolfDen"),
    ("/Game/Characters/Bandit/BP_BanditBase", "BanditBase"),
    ("/Game/Characters/Wolf/BP_WolfDen2", "WolfDen2"),
]
for asset_path, expected in checks:
    name = asset_path.rsplit("/", 1)[1]
    cls = unreal.load_object(None, "{}.{}_C".format(asset_path, name))
    if cls is None:
        log("FAIL {}: class not found".format(name))
        ok = False
        continue
    cdo = unreal.get_default_object(cls)
    tag = str(cdo.get_editor_property("quest_marker_tag"))
    num = cdo.get_editor_property("num_to_spawn")
    status = "OK" if tag == expected else "MISMATCH"
    if tag != expected:
        ok = False
    log("{} {}: quest_marker_tag='{}' expected='{}' num_to_spawn={}".format(
        status, name, tag, expected, num))

child = unreal.load_object(None, "/Game/Characters/Wolf/BP_WolfDen2.BP_WolfDen2_C")
parent = unreal.load_object(None, "/Game/Characters/Wolf/BP_WolfDen.BP_WolfDen_C")
if child and parent:
    is_child = unreal.MathLibrary.class_is_child_of(child, parent)
    log("PARENT CHECK: BP_WolfDen2_C is child of BP_WolfDen_C = {}".format(is_child))
    if not is_child:
        ok = False
    try:
        bp = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Wolf/BP_WolfDen2")
        pc = bp.get_editor_property("parent_class")
        log("PARENT PROPERTY on BP asset: {}".format(pc.get_name() if pc else None))
    except Exception as e:
        log("PARENT PROPERTY read failed: {}".format(e))
else:
    log("FAIL: child or parent class not loaded")
    ok = False

log("RESULT: {}".format("ALL_OK" if ok else "FAILED"))
