import unreal
p='/Game/Environment/Props/AbandonedCar/M_CarTripo'
m=unreal.load_asset(p)
print('BEFORE',m.get_editor_property('two_sided'))
m.set_editor_property('two_sided',True)
unreal.MaterialEditingLibrary.recompile_material(m)
print('SAVED',unreal.EditorAssetLibrary.save_asset(p,only_if_is_dirty=False))
print('AFTER',unreal.load_asset(p).get_editor_property('two_sided'))
