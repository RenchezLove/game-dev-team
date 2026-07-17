# 2026-07-17 unreal-operator: import NPC Trader v2 (clean redo).
# Fixes vs v1: (1) physics assets are now SAVED to disk explicitly (v1 left them in-memory only);
# (2) screenshot: viewport invalidate via LevelEditorSubsystem so the frame actually renders.
# NO map open/save. Only new assets under /Game/Characters/Trader/ are written.
import unreal
import os

P = "TRIMP2|"

SRC = "E:/game-dev-team/assets/npc_trader/"
TRADER_DIR = "/Game/Characters/Trader"
CONTENT_DIR = "E:/ContrarySurvior/ContrarySurvivor/Content/Characters/Trader/"
MAT_PATH = "/Game/Materials/M_VColor"
ELDER_HEAD = "/Game/Characters/Elder/SK_Elder_Head"
EXPECTED_SKEL = "/Game/Characters/Shared/Humanoid/HeadAndSkeletonfbx_Head_Skeleton"
SHOT = "E:/ContrarySurvior/ContrarySurvivor/Saved/Screenshots/WindowsEditor/Trader_import_preview.png"

EXPECTED_TRIS = {"SK_Trader_Head": 210, "SK_Trader_Torso": 414, "SK_Trader_Legs": 272}
ASSETS = ["SK_Trader_Head", "SK_Trader_Torso", "SK_Trader_Legs"]

eal = unreal.EditorAssetLibrary
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()


def log(msg):
    unreal.log(P + " " + str(msg))


log("=== PRE-STATE (fresh process; v1 uassets were deleted file-level) ===")
for name in ASSETS:
    log("pre-exists " + name + " = " + str(eal.does_asset_exist(TRADER_DIR + "/" + name))
        + " disk=" + str(os.path.exists(CONTENT_DIR + name + ".uasset")))

log("=== STEP 0: legacy FBX pipeline (asset-contract 2.1) ===")
unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")
log("CVar Interchange.FeatureFlags.Import.FBX now=" + str(
    unreal.SystemLibrary.get_console_variable_int_value("Interchange.FeatureFlags.Import.FBX")))

elder = unreal.load_asset(ELDER_HEAD)
shared_skel = elder.get_editor_property('skeleton')
SHARED_SKEL_PATH = shared_skel.get_path_name()
log("SHARED SKELETON = " + SHARED_SKEL_PATH)
if EXPECTED_SKEL not in SHARED_SKEL_PATH:
    log("FATAL: unexpected skeleton")
    raise SystemExit
mat = unreal.load_asset(MAT_PATH)
if mat is None:
    log("FATAL: no M_VColor")
    raise SystemExit


def make_skeletal_options(skeleton):
    opt = unreal.FbxImportUI()
    opt.set_editor_property('import_mesh', True)
    opt.set_editor_property('import_as_skeletal', True)
    opt.set_editor_property('import_materials', False)
    opt.set_editor_property('import_textures', False)
    opt.set_editor_property('import_animations', False)
    opt.set_editor_property('create_physics_asset', True)  # mirror elder (Torso/Legs have one)
    opt.set_editor_property('mesh_type_to_import', unreal.FBXImportType.FBXIT_SKELETAL_MESH)
    opt.set_editor_property('original_import_type', unreal.FBXImportType.FBXIT_SKELETAL_MESH)
    opt.set_editor_property('skeleton', skeleton)
    skd = opt.skeletal_mesh_import_data
    skd.set_editor_property('vertex_color_import_option', unreal.VertexColorImportOption.REPLACE)
    skd.set_editor_property('update_skeleton_reference_pose', False)
    return opt


log("=== STEP 1: IMPORT ===")
for name in ASSETS:
    t = unreal.AssetImportTask()
    t.set_editor_property('filename', SRC + name + ".fbx")
    t.set_editor_property('destination_path', TRADER_DIR)
    t.set_editor_property('replace_existing', True)
    t.set_editor_property('automated', True)
    t.set_editor_property('save', True)
    t.set_editor_property('options', make_skeletal_options(shared_skel))
    asset_tools.import_asset_tasks([t])
    log("IMPORT " + name + " returned: " + str(list(t.get_editor_property('imported_object_paths'))))

log("=== STEP 2: matfix slot0 -> M_VColor + SAVE meshes AND physics assets ===")
for name in ASSETS:
    apath = TRADER_DIR + "/" + name
    mesh = unreal.load_asset(apath)
    mats = mesh.get_editor_property('materials')
    old_slot_name = mats[0].get_editor_property('material_slot_name')
    new_slot = unreal.SkeletalMaterial()
    new_slot.set_editor_property('material_interface', mat)
    new_slot.set_editor_property('material_slot_name', old_slot_name)
    mesh.set_editor_property('materials', [new_slot] + [mats[i] for i in range(1, len(mats))])
    eal.save_asset(apath, only_if_is_dirty=False)
    log("MATFIX " + name + " slot0 name=" + str(old_slot_name) + " -> M_VColor, saved")
    pa = mesh.get_editor_property('physics_asset')
    if pa is not None:
        pa_path = pa.get_path_name().split('.')[0]
        ok = eal.save_asset(pa_path, only_if_is_dirty=False)
        log("PHYSSAVE " + name + " -> " + pa_path + " save_asset=" + str(ok)
            + " disk=" + str(os.path.exists(CONTENT_DIR + pa_path.split('/')[-1] + ".uasset")))
    else:
        log("PHYSSAVE " + name + " physics_asset=None (elder head precedent)")

log("=== STEP 3: RE-LOAD VERIFY ===")
for name in ASSETS:
    apath = TRADER_DIR + "/" + name
    mesh = unreal.load_asset(apath)
    sk_p = mesh.get_editor_property('skeleton').get_path_name()
    hvc = mesh.has_vertex_colors()
    rmi = mesh.get_editor_property('materials')[0].get_editor_property('material_interface')
    aid = mesh.get_editor_property('asset_import_data')
    log("VERIFY " + name
        + " SAME_AS_SHARED=" + str(sk_p == SHARED_SKEL_PATH)
        + " has_vertex_colors=" + str(hvc)
        + " slot0=" + (rmi.get_path_name() if rmi else "NONE")
        + " import_data_class=" + (aid.get_class().get_name() if aid else "NONE")
        + " mesh_on_disk=" + str(os.path.exists(CONTENT_DIR + name + ".uasset")))
    try:
        dm = unreal.new_object(unreal.DynamicMesh)
        rl = unreal.GeometryScriptMeshReadLOD()
        rl.set_editor_property('lod_type', unreal.GeometryScriptLODType.SOURCE_MODEL)
        rl.set_editor_property('lod_index', 0)
        r = unreal.GeometryScript_AssetUtils.copy_mesh_from_skeletal_mesh(
            mesh, dm, unreal.GeometryScriptCopyMeshFromAssetOptions(), rl)
        dm2, outcome = r[0], r[1]
        tris = unreal.GeometryScript_MeshQueries.get_num_triangle_i_ds(dm2)
        log("COUNT " + name + " tris=" + str(tris) + " (sidecar " + str(EXPECTED_TRIS[name])
            + ") TRIS_MATCH=" + str(tris == EXPECTED_TRIS[name]) + " outcome=" + str(outcome))
    except Exception as e:
        log("COUNT " + name + " ERR: " + str(e))

log("=== STEP 4: SCREENSHOT (blank in-memory world, never saved; invalidate viewports) ===")
try:
    os.makedirs(os.path.dirname(SHOT), exist_ok=True)
    if os.path.exists(SHOT):
        os.remove(SHOT)
    world = unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
    log("blank world = " + str(world.get_name() if world else "NONE"))
    unreal.SystemLibrary.execute_console_command(None, "r.EyeAdaptationQuality 0")
    unreal.SystemLibrary.execute_console_command(None, "r.DefaultFeature.AutoExposure 0")
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    lrot = unreal.Rotator()
    lrot.pitch = -40.0
    lrot.yaw = 70.0
    eas.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 400), lrot)
    zero = unreal.Rotator()
    back = unreal.Rotator()
    back.yaw = 180.0
    for name in ASSETS:
        mesh = unreal.load_asset(TRADER_DIR + "/" + name)
        eas.spawn_actor_from_object(mesh, unreal.Vector(0, 0, 0), zero)
        eas.spawn_actor_from_object(mesh, unreal.Vector(150, 0, 0), back)
    log("spawned 2x3 skeletal mesh actors (front set at X=0, back set at X=150 yaw=180)")
    cam_loc = unreal.Vector(75, -300, 165)
    cam_rot = unreal.Rotator()
    cam_rot.pitch = -14.0
    cam_rot.yaw = 90.0
    try:
        unreal.EditorLevelLibrary.set_level_viewport_camera_info(cam_loc, cam_rot)
    except Exception:
        unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(cam_loc, cam_rot)
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    les.editor_invalidate_viewports()
    res = unreal.AutomationLibrary.take_high_res_screenshot(1920, 1080, SHOT)
    les.editor_invalidate_viewports()
    log("screenshot requested (res=" + str(res) + ") -> " + SHOT)
except Exception as e:
    log("SCREENSHOT ERR: " + str(e))

log("=== DONE v2 (no map saved) ===")
