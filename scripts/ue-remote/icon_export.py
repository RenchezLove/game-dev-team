import unreal
for n in ['T_Item_Pistol','T_Item_Knife']:
    t=unreal.load_asset('/Game/UI/Icons/Items/'+n)
    aid=t.get_editor_property('asset_import_data')
    print(n,t.blueprint_get_size_x(),t.blueprint_get_size_y(),'src',aid.get_first_filename() if aid else None)
    e=unreal.AssetExportTask(); e.set_editor_property('object',t); e.set_editor_property('filename','E:/ContrarySurvior/ContrarySurvivor/Saved/Tripo/weapons/'+n+'.png'); e.set_editor_property('automated',True); e.set_editor_property('replace_identical',True); e.set_editor_property('prompt',False); e.set_editor_property('exporter',unreal.TextureExporterPNG())
    print('  export',unreal.Exporter.run_asset_export_task(e))
