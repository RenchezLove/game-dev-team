import bpy
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
bpy.ops.import_scene.fbx(filepath=r'E:\game-dev-team\assets/_handoff/humanoid-export/SK_Cloth_L1_Torso.fbx')
for o in bpy.data.objects:
    if o.type == 'MESH':
        me = o.data
        print('VCOLDUMP MESH %s layers=%s' % (o.name, [(ca.name, ca.domain, ca.data_type) for ca in me.color_attributes]))
        for ca in me.color_attributes:
            vals = set()
            for d in ca.data:
                c = d.color
                vals.add((round(c[0], 2), round(c[1], 2), round(c[2], 2)))
                if len(vals) > 15:
                    break
            print('VCOLDUMP layer=%s uniq=%s' % (ca.name, sorted(vals)))
