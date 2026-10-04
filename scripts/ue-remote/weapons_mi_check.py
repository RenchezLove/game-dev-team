import unreal
mel=unreal.MaterialEditingLibrary; eal=unreal.EditorAssetLibrary
print(mel.get_texture_parameter_names(unreal.load_asset('/Game/Weapons/M_WeaponTripo')))
for mi_,tx in [('MI_PistolPM','T_PistolPM_D'),('MI_KnifeTripo','T_KnifeTripo_D')]:
    mi=unreal.load_asset('/Game/Weapons/'+mi_); tex=unreal.load_asset('/Game/Weapons/'+tx)
    cur=mel.get_material_instance_texture_parameter_value(mi,'Diffuse')
    print(mi_,'before',cur.get_name() if cur else None,'parent',mi.get_editor_property('parent').get_name())
    if cur!=tex:
        print('set',mel.set_material_instance_texture_parameter_value(mi,'Diffuse',tex)); mel.update_material_instance(mi)
        cur=mel.get_material_instance_texture_parameter_value(mi,'Diffuse'); print('after',cur.get_name() if cur else None,'save',eal.save_loaded_asset(mi,False))
    print(tx,tex.blueprint_get_size_x(),tex.blueprint_get_size_y())
