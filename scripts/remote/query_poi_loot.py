# -*- coding: utf-8 -*-
# Живой редактор: dirty-пакеты + поиск акторов POI/Loot/Pickup на карте.
import sys, time

PLUGIN = r"E:/UnrealEngine/UE_5.5/Engine/Plugins/Experimental/PythonScriptPlugin/Content/Python"
sys.path.append(PLUGIN)
import remote_execution as re_mod

CMD = (
    "import unreal\n"
    "d1 = unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()\n"
    "d2 = unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()\n"
    "print('DIRTY=' + repr([p.get_name() for p in list(d1) + list(d2)]))\n"
    "actors = unreal.EditorLevelLibrary.get_all_level_actors()\n"
    "for a in actors:\n"
    "    lbl = a.get_actor_label()\n"
    "    if ('POI' in lbl) or ('Loot' in lbl) or ('Pickup' in lbl):\n"
    "        loc = a.get_actor_location()\n"
    "        print('ACTOR|%s|%s|%.0f,%.0f,%.0f' % (lbl, a.get_class().get_name(), loc.x, loc.y, loc.z))\n"
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
