import unreal
mel = unreal.MaterialEditingLibrary
m = unreal.load_asset('/Game/Environment/Props/AbandonedCar/M_CarTripo')
print('scalars', mel.get_scalar_parameter_names(m), 'vectors', mel.get_vector_parameter_names(m), 'tex', mel.get_texture_parameter_names(m))
t = unreal.T3DExporter if hasattr(unreal, 'T3DExporter') else None
import re
e = unreal.AssetExportTask(); e.set_editor_property('object', m); e.set_editor_property('filename', 'E:/game-dev-team/scripts/ue-remote/_m_cartripo.t3d'); e.set_editor_property('automated', True); e.set_editor_property('prompt', False); e.set_editor_property('replace_identical', True)
print('export', unreal.Exporter.run_asset_export_task(e))
for p in ['/Game/Environment/Props/UAZ452/MI_UAZ452Kit']:
    mi = unreal.load_asset(p)
    print(p, 'parent', mi.get_editor_property('parent').get_path_name(), 'S', [(str(x.parameter_info.name), x.parameter_value) for x in mi.get_editor_property('scalar_parameter_values')], 'V', [(str(x.parameter_info.name), x.parameter_value) for x in mi.get_editor_property('vector_parameter_values')])
print(unreal.EditorAssetLibrary.find_package_referencers_for_asset('/Game/Environment/Props/AbandonedCar/M_CarTripo', False))
