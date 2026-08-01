# -*- coding: utf-8 -*-
# Подключается к живому редактору UE по remote_execution, печатает список
# несохранённых (dirty) пакетов и сохраняет их. Запуск движковым python.
import sys, time

PLUGIN = r"E:/UnrealEngine/UE_5.5/Engine/Plugins/Experimental/PythonScriptPlugin/Content/Python"
sys.path.append(PLUGIN)
import remote_execution as re_mod

CMD = (
    "import unreal\n"
    "d1 = unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()\n"
    "d2 = unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()\n"
    "names = [p.get_name() for p in list(d1) + list(d2)]\n"
    "print('DIRTY_LIST=' + repr(names))\n"
    "if names:\n"
    "    ok = unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)\n"
    "    print('SAVE_RESULT=' + repr(ok))\n"
    "else:\n"
    "    print('SAVE_RESULT=nothing_to_save')\n"
)

def main():
    r = re_mod.RemoteExecution()
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
