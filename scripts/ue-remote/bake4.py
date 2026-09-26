import unreal
l=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
print('BUILD',l.build_light_maps(unreal.LightingBuildQuality.QUALITY_PREVIEW,False))
