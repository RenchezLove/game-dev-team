# 2026-07-17 unreal-operator: import NPC Trader (3 modular skeletal meshes) into /Game/Characters/Trader/
# Headless second process (editor is open in parallel). NO map open/save. Only new assets are written.
# Pattern: proven import_armor.py (legacy FbxImportUI) + asset-contract §2.1 (Interchange CVar off).
import unreal
import os

P = "TRIMP|"

SRC = "E:/game-dev-team/assets/npc_trader/"
TRADER_DIR = "/Game/Characters/Trader"
MAT_PATH = "/Game/Materials/M_VColor"
ELDER_HEAD = "/Game/Characters/Elder/SK_Elder_Head"
EXPECTED_SKEL = "/Game/Characters/Shared/Humanoid/HeadAndSkeletonfbx_Head_Skeleton"
SHOT = "E:/ContrarySurvior/ContrarySurvivor/Saved/Screenshots/WindowsEditor/Trader_import_preview.png"

# sidecar npc_trader.asset.md (round-trip numbers, not from memory)
EXPECTED_TRIS = {"SK_Trader_Head": 210, "SK_Trader_Torso": 414, "SK_Trader_Legs": 272}
EXPECTED_VERTS = {"SK_Trader_Head": 131, "SK_Trader_Torso": 238, "SK_Trader_Legs": 167}
ASSETS = ["SK_Trader_Head", "SK_Trader_Torso", "SK_Trader_Legs"]

eal = unreal.EditorAssetLibrary
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()


def log(msg):
    unreal.log(P + " " + str(msg))


log("=== PRE-STATE ===")
for name in ASSETS:
    log("pre-exists " + name + " = " + str(eal.does_asset_exist(TRADER_DIR + "/" + name)))
log("pre-exists BP_Trader = " + str(eal.does_asset_exist(TRADER_DIR + "/BP_Trader")))
for name in ASSETS:
    fbx = SRC + name + ".fbx"
    log("fbx " + fbx + " exists=" + str(os.path.exists(fbx)) + " size=" + str(os.path.getsize(fbx) if os.path.exists(fbx) else -1))

log("=== STEP 0: legacy FBX pipeline (asset-contract 2.1) ===")
before = unreal.SystemLibrary.get_console_variable_int_value("Interchange.FeatureFlags.Import.FBX")
unreal.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")
after = unreal.SystemLibrary.get_console_variable_int_value("Interchange.FeatureFlags.Import.FBX")
log("CVar Interchange.FeatureFlags.Import.FBX before=" + str(before) + " after=" + str(after))

log("=== STEP 1: discover shared skeleton from SK_Elder_Head (not from memory) ===")
elder = unreal.load_asset(ELDER_HEAD)
if elder is None:
    log("FATAL: cannot load SK_Elder_Head")
    raise SystemExit
shared_skel = elder.get_editor_property('skeleton')
SHARED_SKEL_PATH = shared_skel.get_path_name() if shared_skel else "NONE"
log("SHARED SKELETON = " + SHARED_SKEL_PATH)
if EXPECTED_SKEL not in SHARED_SKEL_PATH:
    log("FATAL: elder skeleton != expected " + EXPECTED_SKEL)
    raise SystemExit
elder_mats = elder.get_editor_property('materials')
if len(elder_mats) > 0:
    emi = elder_mats[0].get_editor_property('material_interface')
    log("ELDER slot0 material = " + (emi.get_path_name() if emi else "NONE"))

mat = unreal.load_asset(MAT_PATH)
log("M_VColor loaded = " + (mat.get_path_name() if mat else "NONE"))
if mat is None:
    log("FATAL: no M_VColor")
    raise SystemExit
try:
    log("M_VColor two_sided = " + str(mat.get_editor_property('two_sided')))
except Exception as e:
    log("M_VColor two_sided read note: " + str(e))


def make_skeletal_options(skeleton):
    opt = unreal.FbxImportUI()
    opt.set_editor_property('import_mesh', True)
    opt.set_editor_property('import_as_skeletal', True)
    opt.set_editor_property('import_materials', False)
    opt.set_editor_property('import_textures', False)
    opt.set_editor_property('import_animations', False)
    # elder on disk has PhysicsAssets for Torso/Legs -> mirror elder state
    opt.set_editor_property('create_physics_asset', True)
    opt.set_editor_property('mesh_type_to_import', unreal.FBXImportType.FBXIT_SKELETAL_MESH)
    opt.set_editor_property('original_import_type', unreal.FBXImportType.FBXIT_SKELETAL_MESH)
    opt.set_editor_property('skeleton', skeleton)
    skd = opt.skeletal_mesh_import_data
    skd.set_editor_property('vertex_color_import_option', unreal.VertexColorImportOption.REPLACE)
    # body meshes must NOT touch shared skeleton ref pose (armor precedent)
    skd.set_editor_property('update_skeleton_reference_pose', False)
    return opt


log("=== STEP 2: IMPORT 3 TRADER MESHES vs SHARED SKELETON ===")
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

log("=== STEP 3: assign M_VColor slot0 (rebuild SkeletalMaterial, keep slot name) ===")
for name in ASSETS:
    apath = TRADER_DIR + "/" + name
    mesh = unreal.load_asset(apath)
    if mesh is None:
        log("MATFIX " + name + " = NOT LOADED")
        continue
    mats = mesh.get_editor_property('materials')
    if len(mats) == 0:
        log("MATFIX " + name + " WARN no material slots")
        continue
    old_slot_name = mats[0].get_editor_property('material_slot_name')
    new_slot = unreal.SkeletalMaterial()
    new_slot.set_editor_property('material_interface', mat)
    new_slot.set_editor_property('material_slot_name', old_slot_name)
    new_array = [new_slot] + [mats[i] for i in range(1, len(mats))]
    mesh.set_editor_property('materials', new_array)
    eal.save_asset(apath, only_if_is_dirty=False)  # point-save, NOT save_directory (BP_Trader must stay untouched)
    log("MATFIX " + name + " slot0 name=" + str(old_slot_name) + " -> M_VColor, saved")

log("=== STEP 4: RE-LOAD VERIFY ===")
for name in ASSETS:
    apath = TRADER_DIR + "/" + name
    if not eal.does_asset_exist(apath):
        log("VERIFY " + name + " = ASSET DOES NOT EXIST")
        continue
    mesh = unreal.load_asset(apath)
    sk = mesh.get_editor_property('skeleton')
    sk_p = sk.get_path_name() if sk else "NONE"
    try:
        hvc = mesh.has_vertex_colors()
    except Exception as e:
        hvc = "ERR:" + str(e)
    rmats = mesh.get_editor_property('materials')
    rmi = rmats[0].get_editor_property('material_interface') if len(rmats) > 0 else None
    rmi_p = rmi.get_path_name() if rmi else "NONE"
    # legacy pipeline proof (asset-contract 2.1)
    try:
        aid = mesh.get_editor_property('asset_import_data')
        aid_cls = aid.get_class().get_name() if aid else "NONE"
    except Exception as e:
        aid_cls = "ERR:" + str(e)
    log("VERIFY " + name + " skeleton=" + sk_p
        + " SAME_AS_SHARED=" + str(sk_p == SHARED_SKEL_PATH)
        + " has_vertex_colors=" + str(hvc)
        + " slot0=" + rmi_p
        + " import_data_class=" + str(aid_cls))
    physp = apath + "_PhysicsAsset"
    log("VERIFY " + name + " physics_asset_exists=" + str(eal.does_asset_exist(physp)))

log("=== STEP 5: tri/vert counts via GeometryScript (compare to sidecar) ===")
for name in ASSETS:
    mesh = unreal.load_asset(TRADER_DIR + "/" + name)
    counted = False
    for lod_type in [unreal.GeometryScriptLODType.SOURCE_MODEL, unreal.GeometryScriptLODType.RENDER_DATA]:
        if counted:
            break
        try:
            dm = unreal.new_object(unreal.DynamicMesh)
            rl = unreal.GeometryScriptMeshReadLOD()
            rl.set_editor_property('lod_type', lod_type)
            rl.set_editor_property('lod_index', 0)
            r = unreal.GeometryScript_AssetUtils.copy_mesh_from_skeletal_mesh(
                mesh, dm, unreal.GeometryScriptCopyMeshFromAssetOptions(), rl)
            dm2, outcome = r[0], r[1]
            if str(outcome).find("SUCCESS") < 0:
                log("COUNT " + name + " lod_type=" + str(lod_type) + " outcome=" + str(outcome))
                continue
            tris = unreal.GeometryScript_MeshQueries.get_num_triangle_i_ds(dm2)
            verts = unreal.GeometryScript_MeshQueries.get_num_vertex_i_ds(dm2)
            log("COUNT " + name + " lod_type=" + str(lod_type)
                + " tris=" + str(tris) + " (sidecar " + str(EXPECTED_TRIS[name]) + ")"
                + " verts=" + str(verts) + " (sidecar blender-verts " + str(EXPECTED_VERTS[name]) + ")"
                + " TRIS_MATCH=" + str(tris == EXPECTED_TRIS[name]))
            counted = True
            # bonus: distinct vertex colors (data proof of palette)
            try:
                cres = unreal.GeometryScript_MeshQueries.get_mesh_per_vertex_colors(
                    dm2, unreal.GeometryScriptColorList(), False)
                clist = None
                for item in (cres if isinstance(cres, tuple) else [cres]):
                    if isinstance(item, unreal.GeometryScriptColorList):
                        clist = item
                if clist is not None:
                    n = clist.get_color_list_length()
                    distinct = set()
                    for i in range(n):
                        it = clist.get_color_list_item(i)
                        c = it[0] if isinstance(it, tuple) else it
                        distinct.add((round(c.r, 3), round(c.g, 3), round(c.b, 3)))
                    log("VCOL " + name + " sampled=" + str(n) + " distinct=" + str(len(distinct))
                        + " first10=" + str(sorted(distinct)[:10]))
            except Exception as e:
                log("VCOL " + name + " census note: " + str(e))
        except Exception as e:
            log("COUNT " + name + " lod_type=" + str(lod_type) + " ERR: " + str(e))

log("=== STEP 6: SCREENSHOT in fresh blank in-memory world (never saved) ===")
try:
    d = os.path.dirname(SHOT)
    os.makedirs(d, exist_ok=True)
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
        a = eas.spawn_actor_from_object(mesh, unreal.Vector(0, 0, 0), zero)      # front set
        b = eas.spawn_actor_from_object(mesh, unreal.Vector(150, 0, 0), back)    # mirrored set (shows other side)
        log("spawned " + name + " -> " + str(a.get_name()) + " / " + str(b.get_name()))
    cam_loc = unreal.Vector(75, -300, 165)
    cam_rot = unreal.Rotator()
    cam_rot.pitch = -14.0
    cam_rot.yaw = 90.0
    try:
        unreal.EditorLevelLibrary.set_level_viewport_camera_info(cam_loc, cam_rot)
    except Exception:
        unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(cam_loc, cam_rot)
    unreal.AutomationLibrary.take_high_res_screenshot(1920, 1080, SHOT)
    log("screenshot requested -> " + SHOT)
except Exception as e:
    log("SCREENSHOT ERR: " + str(e))

log("=== DONE (no map saved; only Trader assets written) ===")
