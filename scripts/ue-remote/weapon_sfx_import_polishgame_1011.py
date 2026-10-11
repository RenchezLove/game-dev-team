import unreal
# Звуки «мало патронов» и «пустой магазин» (11.10.2026): загрузка в /Game/Audio/Weapons и
# проверка, что ссылки из настроек проекта (UContraryWeaponAudioSettings) на них указывают.
SRC = 'E:/game-dev-team/assets/sfx_ammo_1011/'
DEST = '/Game/Audio/Weapons'
for src, name in [('SFX_Weapon_LowAmmo.wav', 'weapon_low_ammo'), ('SFX_Weapon_DryFire.wav', 'weapon_dry_fire')]:
    path = '%s/%s' % (DEST, name)
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        print('WSFX already exists', path); continue
    t = unreal.AssetImportTask()
    t.filename = SRC + src; t.destination_path = DEST; t.destination_name = name
    t.automated = True; t.replace_existing = True; t.save = True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
    print('WSFX imported', src, '->', [str(p) for p in t.imported_object_paths])
settings = unreal.get_default_object(unreal.load_class(None, '/Script/ContrarySurvivor.ContraryWeaponAudioSettings'))
for prop in ['low_ammo_sound', 'dry_fire_sound']:
    ref = settings.get_editor_property(prop)
    asset = unreal.load_asset(str(ref.get_path_name())) if ref else None
    print('WSFX setting %s -> %s | loaded=%s class=%s duration=%s' % (prop, ref.get_path_name() if ref else None,
        asset is not None, asset.get_class().get_name() if asset else None,
        round(asset.get_editor_property('duration'), 3) if asset else None))
for prop in ['low_ammo_clip_fraction', 'low_ammo_volume', 'dry_fire_min_interval', 'dry_fire_volume']:
    print('WSFX setting %s = %s' % (prop, settings.get_editor_property(prop)))
print('WSFX DONE')
