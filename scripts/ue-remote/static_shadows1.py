import unreal
ST=unreal.ComponentMobility.STATIC
BPS={
 '/Game/Environment/Props/AbandonedCar/BP_AbandonedCar':{'vol':True,'only':None,'noshadow':('Glass','Scratches')},
 '/Game/Characters/Bandit/BP_BanditBase':{'vol':False,'only':None,'noshadow':()},
 '/Game/Characters/Wolf/BP_WolfDen':{'vol':False,'only':None,'noshadow':()},
 '/Game/Environment/Props/Campfire/BP_Campfire':{'vol':False,'only':('Mesh',),'noshadow':()},
}
def base(n):
    return n.replace('_GEN_VARIABLE','')
def fix(c,cfg,inst):
    n=base(c.get_name())
    isroot=c.get_class().get_name()=='SceneComponent'
    ismesh=c.get_class().get_name()=='StaticMeshComponent'
    if not (isroot or ismesh): return None
    if ismesh and cfg['only'] is not None and n not in cfg['only']: return None
    if inst: c.set_mobility(ST)
    else: c.set_editor_property('mobility',ST)
    if ismesh:
        if cfg['vol']: c.set_editor_property('lightmap_type',unreal.LightmapType.FORCE_VOLUMETRIC)
        if n in cfg['noshadow']: c.set_editor_property('cast_shadow',False)
    return n
sds=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem); lib=unreal.SubobjectDataBlueprintFunctionLibrary
for p,cfg in BPS.items():
    bp=unreal.load_asset(p)
    objs=[]
    for h in sds.k2_gather_subobject_data_for_blueprint(bp):
        o=lib.get_object(lib.get_data(h))
        if o and isinstance(o,unreal.SceneComponent) and o not in objs: objs.append(o)
    objs.sort(key=lambda o:0 if o.get_class().get_name()=='SceneComponent' else 1)
    done=[fix(o,cfg,False) for o in objs]
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    print('BP',p,[d for d in done if d],'saved',unreal.EditorAssetLibrary.save_asset(p,only_if_is_dirty=False))
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
cls={unreal.load_asset(p).generated_class().get_name():cfg for p,cfg in BPS.items()}
for a in eas.get_all_level_actors():
    cfg=cls.get(a.get_class().get_name())
    if not cfg: continue
    a.modify()
    fix(a.root_component,cfg,True)
    for c in a.get_components_by_class(unreal.StaticMeshComponent): fix(c,cfg,True)
    print('INST',a.get_actor_label(),[(c.get_name(),str(c.get_editor_property('mobility')).split('.')[-1].split(':')[0]) for c in a.get_components_by_class(unreal.StaticMeshComponent)][:3],'root',str(a.root_component.get_editor_property('mobility')))
    if a.get_class().get_name()=='BP_WorldLook_C': pass
for a in eas.get_all_level_actors():
    if a.get_class().get_name()!='BP_WorldLook_C': continue
    a.modify()
    d=a.get_components_by_class(unreal.DirectionalLightComponent)[0]
    ls=d.get_editor_property('lightmass_settings'); ls.set_editor_property('light_source_angle',3.0); d.set_editor_property('lightmass_settings',ls)
    s=a.get_components_by_class(unreal.SkyLightComponent)[0]
    s.set_editor_property('intensity',4.5)
    print('LOOK angle',d.get_editor_property('lightmass_settings').get_editor_property('light_source_angle'),'sky',s.get_editor_property('intensity'))
bp=unreal.load_asset('/Game/Environment/Lighting/BP_WorldLook')
for h in sds.k2_gather_subobject_data_for_blueprint(bp):
    o=lib.get_object(lib.get_data(h))
    if isinstance(o,unreal.DirectionalLightComponent):
        ls=o.get_editor_property('lightmass_settings'); ls.set_editor_property('light_source_angle',3.0); o.set_editor_property('lightmass_settings',ls)
    if isinstance(o,unreal.SkyLightComponent): o.set_editor_property('intensity',4.5)
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
print('LOOKBP',unreal.EditorAssetLibrary.save_asset('/Game/Environment/Lighting/BP_WorldLook',only_if_is_dirty=False))
print('LVL',unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level())
