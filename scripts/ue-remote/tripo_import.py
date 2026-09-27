import unreal
src='E:/ContrarySurvior/ContrarySurvivor/Saved/Tripo/barrel.glb'
dst='/Game/Environment/Props/Tripo'
t=unreal.AssetImportTask()
t.set_editor_property('filename',src)
t.set_editor_property('destination_path',dst)
t.set_editor_property('destination_name','SM_TripoBarrel')
t.set_editor_property('automated',True)
t.set_editor_property('replace_existing',True)
t.set_editor_property('save',True)
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
print('IMPORTED',list(t.get_editor_property('imported_object_paths')))
for p in unreal.EditorAssetLibrary.list_assets(dst,recursive=True):
    a=unreal.load_asset(p)
    print('ASSET',p,type(a).__name__)
    if isinstance(a,unreal.StaticMesh):
        b=a.get_bounding_box()
        print('  size',b.max-b.min,'min',b.min,'tris',a.get_num_triangles(0))
old=unreal.load_asset('/Game/Environment/Props/SM_BanditBarrel')
b=old.get_bounding_box(); print('OLD size',b.max-b.min,'min',b.min,'tris',old.get_num_triangles(0))
