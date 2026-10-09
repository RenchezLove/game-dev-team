import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in eas.get_all_level_actors():
    for c in a.get_components_by_class(unreal.LightComponentBase):
        col = c.get_editor_property('light_color')
        extra = ''
        if isinstance(c, unreal.DirectionalLightComponent):
            r = c.get_world_rotation() if hasattr(c, 'get_world_rotation') else a.get_actor_rotation()
            extra = 'pitch %.1f yaw %.1f use_temp %s temp %s' % (r.pitch, r.yaw, c.get_editor_property('use_temperature'), c.get_editor_property('temperature'))
        if isinstance(c, (unreal.DirectionalLightComponent, unreal.SkyLightComponent)):
            print(a.get_actor_label(), '|', c.get_class().get_name(), c.get_name(), '| intensity', c.get_editor_property('intensity'), '| color', (col.r, col.g, col.b), '|', c.get_editor_property('mobility'), extra)
