import sys, time
sys.path.append(r"E:/UnrealEngine/UE_5.5/Engine/Plugins/Experimental/PythonScriptPlugin/Content/Python")
import remote_execution as re_mod
code=open(sys.argv[1],encoding='utf-8').read()
c=re_mod.RemoteExecutionConfig(); c.multicast_bind_address='0.0.0.0'; c.command_endpoint=('127.0.0.1',6779)
r=re_mod.RemoteExecution(c); r.start()
node=None; t=time.time()+25
while time.time()<t:
    if r.remote_nodes: node=r.remote_nodes[0]; break
    time.sleep(0.5)
if not node: print("NO_REMOTE_NODE"); r.stop(); sys.exit(2)
r.open_command_connection(node["node_id"])
res=r.run_command(code, exec_mode=re_mod.MODE_EXEC_FILE)
for e in res.get("output",[]): print(e.get("output"),end='' if str(e.get("output")).endswith('\n') else '\n')
print("RESULT_OK" if res.get("success") else "RESULT_FAIL "+str(res.get("result")))
r.close_command_connection(); r.stop()
