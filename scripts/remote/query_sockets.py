# -*- coding: utf-8 -*-
import sys, time

PLUGIN = r"E:/UnrealEngine/UE_5.5/Engine/Plugins/Experimental/PythonScriptPlugin/Content/Python"
sys.path.append(PLUGIN)
import remote_execution as re_mod

CMD = (
    "import unreal\n"
    "paths = [\n"
    "    '/Game/Characters/Armor/SK_Armor_Torso_01.SK_Armor_Torso_01',\n"
    "    '/Game/TestContentAndCode/PreProduction/HeadAndSkeletonfbx_Head_Skeleton.HeadAndSkeletonfbx_Head_Skeleton',\n"
    "]\n"
    "comp = unreal.SkeletalMeshComponent()\n"
    "for p in paths:\n"
    "    obj = unreal.load_object(None, p)\n"
    "    if not obj:\n"
    "        print('SOCK|not_found|' + p)\n"
    "        continue\n"
    "    if isinstance(obj, unreal.SkeletalMesh):\n"
    "        comp.set_skeletal_mesh_asset(obj)\n"
    "        bones = set(comp.get_bone_name(i) for i in range(comp.get_num_bones()))\n"
    "        socks = [s for s in comp.get_all_socket_names() if s not in bones]\n"
    "        for s in socks:\n"
    "            t = comp.get_socket_transform(s, unreal.RelativeTransformSpace.RTS_PARENT_BONE_SPACE)\n"
    "            print('SOCK|mesh=%s|socket=%s|loc=%.1f,%.1f,%.1f|scale=%.3f,%.3f,%.3f' % ("
    "obj.get_name(), s, t.translation.x, t.translation.y, t.translation.z, t.scale3d.x, t.scale3d.y, t.scale3d.z))\n"
    "        if not socks:\n"
    "            print('SOCK|mesh=%s|no_sockets' % obj.get_name())\n"
    "    else:\n"
    "        print('SOCK|asset=%s|class=%s' % (obj.get_name(), obj.get_class().get_name()))\n"
    "sk = unreal.load_object(None, '/Game/TestContentAndCode/PreProduction/HeadAndSkeletonfbx_Head_Skeleton.HeadAndSkeletonfbx_Head_Skeleton')\n"
    "print('SKEL|class=' + (sk.get_class().get_name() if sk else 'None'))\n"
)

def main():
    config = re_mod.RemoteExecutionConfig()
    config.multicast_bind_address = '0.0.0.0'
    config.command_endpoint = ('127.0.0.1', 6779)
    r = re_mod.RemoteExecution(config)
    r.start()
    deadline = time.time() + 25
    node = None
    while time.time() < deadline:
        nodes = r.remote_nodes
        if nodes:
            node = nodes[0]
            break
        time.sleep(0.5)
    if node is None:
        print("NO_REMOTE_NODE")
        r.stop()
        sys.exit(2)
    r.open_command_connection(node["node_id"])
    result = r.run_command(CMD, exec_mode=re_mod.MODE_EXEC_FILE)
    for entry in result.get("output", []):
        print(entry.get("type"), ":", entry.get("output"))
    print("COMMAND_SUCCESS=", result.get("success"))
    r.close_command_connection()
    r.stop()

if __name__ == "__main__":
    main()
