import unreal

P = "GLSOCKET|"
def log(m):
    unreal.log(P + m)

def inspect_char(bp_path, label):
    if not unreal.EditorAssetLibrary.does_asset_exist(bp_path):
        log("%s: NO ASSET %s" % (label, bp_path))
        return None
    bp = unreal.EditorAssetLibrary.load_asset(bp_path)
    gen_class = bp.generated_class() if isinstance(bp, unreal.Blueprint) else None
    if gen_class is None:
        log("%s: generated_class FAIL" % label)
        return None
    cdo = unreal.get_default_object(gen_class)
    loc = cdo.get_editor_property("weapon_grip_location")
    rot = cdo.get_editor_property("weapon_grip_rotation")
    log("%s: grip_loc=%s grip_rot=%s" % (label, loc, rot))
    mesh_comp = cdo.get_editor_property("mesh")
    mesh_asset = mesh_comp.get_editor_property("skeletal_mesh_asset") if mesh_comp else None
    if mesh_asset is None:
        log("%s: leader mesh asset NONE" % label)
        return None
    skel = mesh_asset.get_editor_property("skeleton")
    log("%s: leader_mesh=%s skeleton=%s" % (label, mesh_asset.get_path_name(), skel.get_path_name() if skel else "NONE"))
    return mesh_asset

player_mesh = inspect_char("/Game/Characters/Player/BP_PlayerCharacter", "PLAYER")
for cand in ["/Game/Characters/Bandit/BP_Bandit", "/Game/Characters/Bandit/BP_BanditEnemy", "/Game/Characters/Bandit/BP_EnemyBandit"]:
    if unreal.EditorAssetLibrary.does_asset_exist(cand):
        inspect_char(cand, "BANDIT")
        break
else:
    found = unreal.EditorAssetLibrary.list_assets("/Game/Characters/Bandit", recursive=True)
    log("BANDIT dir list: %s" % ", ".join([str(a) for a in found]))

if player_mesh:
    try:
        sock = unreal.new_object(unreal.SkeletalMeshSocket, outer=player_mesh)
        log("new_object OK")
        try:
            sock.set_editor_property("socket_name", "WeaponGripSocketProbe")
            sock.set_editor_property("bone_name", "R_Hand")
            log("SET_NAME_OK name=%s bone=%s" % (sock.get_editor_property("socket_name"), sock.get_editor_property("bone_name")))
        except Exception as e:
            log("SET_NAME_FAIL: %s" % e)
    except Exception as e:
        log("NEW_OBJECT_FAIL: %s" % e)
log("PROBE DONE (nothing saved)")
