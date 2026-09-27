import unreal
bp=unreal.load_object(None,'/Game/Characters/Player/BP_PlayerCharacter.BP_PlayerCharacter_C')
cdo=unreal.get_default_object(bp)
print('PARENT',bp.get_super_class().get_name() if hasattr(bp,'get_super_class') else '?')
for c in cdo.get_components_by_class(unreal.SkeletalMeshComponent):
    m=c.get_editor_property('skeletal_mesh_asset') if hasattr(c,'skeletal_mesh_asset') else c.get_skeletal_mesh_asset()
    ab=c.get_editor_property('anim_class')
    print('COMP',c.get_name(),'mesh',m.get_path_name() if m else None,'anim',ab.get_name() if ab else None)
done=set()
paths=['/Game/Characters/Shared/Humanoid/HeadAndSkeletonfbx_Head','/Game/Characters/Shared/Humanoid/TorsoAndSkeleton_Torso','/Game/Characters/Shared/Humanoid/LegsAndSkeleton_Legs','/Game/Characters/Bandit/SK_Bandit_Torso','/Game/Characters/Shared/Clothing/SK_Cloth_T0_Torso','/Game/Characters/Shared/Armor/SK_Armor_T1_Torso']
for c in cdo.get_components_by_class(unreal.SkeletalMeshComponent):
    m=c.get_skeletal_mesh_asset()
    if m: paths.append(m.get_path_name().split('.')[0])
for p in paths:
    if p in done: continue
    done.add(p)
    m=unreal.load_asset(p)
    if not m: print('MISSING',p); continue
    sk=m.get_editor_property('skeleton')
    b=m.get_bounds()
    mats=[x.get_editor_property('material_interface') for x in m.get_editor_property('materials')]
    lod=unreal.SkeletalMeshEditorSubsystem if False else None
    print('MESH',p,'skel',sk.get_path_name() if sk else None,'box',b.box_extent,'mats',[x.get_name() if x else None for x in mats])
    try:
        print('  verts',unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem).get_num_verts(m,0))
    except Exception as e: print('  verts?',e)
sk=unreal.load_asset('/Game/Characters/Shared/Humanoid/HeadAndSkeletonfbx_Head_Skeleton')
print('SKEL0',sk.get_path_name())
m=unreal.load_asset('/Game/Characters/Shared/Humanoid/TorsoAndSkeleton_Torso')
names=[]
i=0
while True:
    n=m.get_bone_name(i) if hasattr(m,'get_bone_name') else None
    if not n or str(n)=='None': break
    names.append(str(n)); i+=1
    if i>200: break
print('BONES',len(names),names)
