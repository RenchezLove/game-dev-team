import unreal
bp=unreal.load_asset('/Game/Characters/Bandit/BP_EnemyBandit')
cdo=unreal.get_default_object(bp.generated_class())
for c in cdo.get_components_by_class(unreal.SkeletalMeshComponent):
    c.modify(); c.set_editor_property('override_materials',[])
bp.modify()
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
print('SAVE',unreal.EditorAssetLibrary.save_loaded_asset(bp,False))
cdo=unreal.get_default_object(unreal.load_asset('/Game/Characters/Bandit/BP_EnemyBandit').generated_class())
for c in cdo.get_components_by_class(unreal.SkeletalMeshComponent):
    print('AFTER',c.get_name(),'override',[m.get_name() if m else None for m in c.get_editor_property('override_materials')],'mats',[m.get_name() if m else None for m in c.get_materials()])
