import unreal
P='/Game/Environment/Props/AbandonedCar/BP_AbandonedCar'
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
def cars():
    return [a for a in eas.get_all_level_actors() if a.get_class().get_name()=='BP_AbandonedCar_C']
def body(a):
    return [c for c in a.get_components_by_class(unreal.StaticMeshComponent) if c.get_name()=='Body'][0]
def show(tag):
    bp=unreal.load_asset(P); cdo=unreal.get_default_object(bp.generated_class())
    print(tag,'cdo',cdo.get_editor_property('car_scale'),[(a.get_actor_label(),a.get_editor_property('car_scale'),round(body(a).get_editor_property('relative_scale3d').x,3)) for a in cars()])
for a in cars(): a.set_editor_property('car_scale',1.0)
show('BEFORE')
def setcdo(v):
    bp=unreal.load_asset(P); cdo=unreal.get_default_object(bp.generated_class())
    cdo.set_editor_property('car_scale',v)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
setcdo(1.2); show('CDO1.2')
setcdo(1.0); show('BACK')
print('HERO',[a.get_name() for a in eas.get_all_level_actors() if 'TripoHero_Raw' in a.get_actor_label()])
for a in eas.get_all_level_actors():
    if a.get_class().get_name() in ('BP_Trader_C','BP_Elder_C'):
        print('NPC',a.get_actor_label(),[c.get_editor_property('cast_shadow') for c in a.get_components_by_class(unreal.MeshComponent)])
