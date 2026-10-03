import unreal
eal=unreal.EditorAssetLibrary
ar=unreal.AssetRegistryHelpers.get_asset_registry()
H='/Game/Characters/Shared/Humanoid'
opt=unreal.AssetRegistryDependencyOptions()
def refs(p): return [str(r) for r in (ar.get_referencers(p,opt) or [])]
def deps(p): return [str(r) for r in (ar.get_dependencies(p,opt) or [])]
print('NEW ANIM REFS',refs(H+'/Anim_PistolIdle_Humanoid'))
print('OLD EXISTS',eal.does_asset_exist(H+'/Anim_AimPistol_Humanoid'),'BAK',eal.does_asset_exist(H+'/Anim_AimPistol_Humanoid_Old'))
print('ABP DEPS',[d for d in deps(H+'/ABP_HumanoidCharacter') if 'Anim_' in d or 'Ainm' in d])
for p in ['/Game/Idle_Pistol_IK',H+'/Retarget/RTG_AnimStarterPack_To_Humanoid',H+'/Retarget/IK_AnimStarterPack']:
    if eal.does_asset_exist(p): print('DEL',p,eal.delete_asset(p))
for a in ar.get_assets_by_path('/Game/Environment/Props/LowPolyMarket',recursive=True):
    pk=str(a.package_name); unreal.load_asset(pk); print('RESAVE',pk,eal.save_asset(pk,only_if_is_dirty=False))
f=unreal.ARFilter(class_paths=[unreal.TopLevelAssetPath('/Script/CoreUObject','ObjectRedirector')],package_paths=['/Game/LowPolyMarket','/Game/AnimStarterPack','/Game'],recursive_paths=True)
red=[unreal.load_object(None,str(a.package_name)+'.'+str(a.asset_name)) for a in ar.get_assets(f) if not str(a.package_name).startswith('/Game/Characters/Shared/Humanoid/Anim_AimPistol')]
red=[r for r in red if r]
print('REDIRECTORS',len(red),[r.get_path_name() for r in red][:20])
try: unreal.AssetToolsHelpers.get_asset_tools().fixup_referencers(red,False,unreal.RedirectFixupMode.DELETE_FIXED_UP_REDIRECTORS)
except Exception as e: print('FIXERR',e)
bad=[]
for a in ar.get_assets_by_path('/Game',recursive=True):
    pk=str(a.package_name)
    if pk.startswith('/Game/LowPolyMarket') or pk.startswith('/Game/AnimStarterPack'): continue
    for d in deps(pk):
        if d.startswith('/Game/LowPolyMarket') or d.startswith('/Game/AnimStarterPack'): bad.append((pk,d))
print('OUTSIDE REFS TO PACKS',bad)
if not bad:
    for d in ['/Game/LowPolyMarket','/Game/AnimStarterPack']:
        print('DELDIR',d,eal.delete_directory(d))
print('ALL',unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True))
print('LEFT',[str(a.package_name) for a in ar.get_assets_by_path('/Game/LowPolyMarket',recursive=True)][:10],[str(a.package_name) for a in ar.get_assets_by_path('/Game/AnimStarterPack',recursive=True)][:10])
