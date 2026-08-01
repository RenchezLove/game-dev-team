import bpy, addon_utils
addon_utils.enable('io_scene_fbx')
bpy.ops.wm.read_factory_settings(use_empty=True)
addon_utils.enable('io_scene_fbx')
for f, tag in (('SK_Trader_Legs.fbx', 'LEGS'), ('SK_Trader_Torso.fbx', 'TORSO')):
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.ops.import_scene.fbx(filepath='E:/game-dev-team/assets/npc_trader/' + f)
    me = [o for o in bpy.data.objects if o.type == 'MESH'][0].data
    cc = {}
    for d in me.color_attributes[0].data:
        k = tuple(round(v * 255) for v in d.color_srgb[:3])
        cc[k] = cc.get(k, 0) + 1
    print(tag, sorted(cc.items(), key=lambda kv: -kv[1])[:6])
