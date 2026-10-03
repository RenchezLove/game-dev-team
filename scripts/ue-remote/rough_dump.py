import unreal
mel=unreal.MaterialEditingLibrary
ar=unreal.AssetRegistryHelpers.get_asset_registry()
for a in ar.get_assets_by_path('/Game',recursive=True):
    n=str(a.asset_name)
    if ('Ground' in n or 'Grass' in n) and str(a.asset_class_path.asset_name) in ('Material','MaterialInstanceConstant'):
        o=a.get_asset(); p=o.get_path_name()
        if isinstance(o,unreal.Material):
            print('MAT',p,'scalars',[str(x) for x in mel.get_scalar_parameter_names(o)],'vectors',[str(x) for x in mel.get_vector_parameter_names(o)])
            for s in mel.get_scalar_parameter_names(o): print('    ',s,'=',mel.get_material_default_scalar_parameter_value(o,s))
        else:
            print('MI',p,'parent',o.get_editor_property('parent').get_path_name() if o.get_editor_property('parent') else None,'scalars',[(str(s.parameter_info.name),s.parameter_value) for s in o.get_editor_property('scalar_parameter_values')])
used={}
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        for m in c.get_materials():
            if m and ('Ground' in m.get_name() or 'Grass' in m.get_name()):
                k=m.get_path_name(); used.setdefault(k,set()).add(a.get_actor_label()+'/'+(c.static_mesh.get_name() if c.static_mesh else '-'))
for k,v in used.items(): print('USED',k,len(v),sorted(v)[:4])
