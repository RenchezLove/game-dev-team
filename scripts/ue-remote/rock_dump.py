import unreal
mel=unreal.MaterialEditingLibrary
D='/Game/Environment/Props/LowPolyMarket'
m=unreal.load_asset(D+'/M_Rock_Master'); mi=unreal.load_asset(D+'/MI_Rock_01')
print('MI parent',mi.get_editor_property('parent').get_path_name())
for n in mel.get_scalar_parameter_names(m): print('S',n,'default',mel.get_material_default_scalar_parameter_value(m,n),'MI',mel.get_material_instance_scalar_parameter_value(mi,n))
for n in mel.get_vector_parameter_names(m): print('V',n,'default',mel.get_material_default_vector_parameter_value(m,n),'MI',mel.get_material_instance_vector_parameter_value(mi,n))
for n in mel.get_texture_parameter_names(m): 
    t=mel.get_material_instance_texture_parameter_value(mi,n); print('T',n,t.get_name() if t else None)
for n in mel.get_static_switch_parameter_names(m): print('SW',n,'default',mel.get_material_default_static_switch_parameter_value(m,n),'MI',mel.get_material_instance_static_switch_parameter_value(mi,n))
print('MI overrides S',[(str(s.parameter_info.name),s.parameter_value) for s in mi.get_editor_property('scalar_parameter_values')])
print('MI overrides V',[(str(s.parameter_info.name),s.parameter_value) for s in mi.get_editor_property('vector_parameter_values')])
mpc=unreal.load_asset(D+'/MPC_GlobalSettings')
if mpc:
    print('MPC S',[(str(p.parameter_name),p.default_value) for p in mpc.get_editor_property('scalar_parameters')])
    print('MPC V',[(str(p.parameter_name),p.default_value) for p in mpc.get_editor_property('vector_parameters')])
for nme in ['SM_Rock_01','SM_Rock_02','SM_Rock_03']:
    sm=unreal.load_asset('/Game/Environment/Nature/'+nme); print(nme,[x.material_interface.get_name() for x in sm.get_editor_property('static_materials')])
