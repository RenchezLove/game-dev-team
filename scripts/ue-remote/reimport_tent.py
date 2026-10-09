# Палатка: нормали в сданном FBX смотрят внутрь (замер 09.10: 1293 из 1368 граней) — крыша под солнцем тёмная,
# теневые стены светлые. Переимпорт с расчётом нормалей по обходу граней, затем заново преграда по шатру.
REIMPORT = ['SM_ArmyTent']; ONLY = ['SM_ArmyTent']; COMPUTE_NORMALS = ['SM_ArmyTent']
exec(open('E:/game-dev-team/scripts/ue-remote/import_scibase.py', encoding='utf-8').read())
exec(open('E:/game-dev-team/scripts/ue-remote/tent_collision.py', encoding='utf-8').read())
exec(open('E:/game-dev-team/scripts/ue-remote/normals_ref.py', encoding='utf-8').read())
sm = unreal.load_asset('/Game/Environment/Props/ScientistBase/SM_ArmyTent')
verts, tris, normals, uvs, tangents = unreal.ProceduralMeshLibrary.get_section_from_static_mesh(sm, 0, 0)
flat = 0
for i in range(0, len(tris), 3):
    a, b, c = normals[tris[i]], normals[tris[i + 1]], normals[tris[i + 2]]
    if a.dot(b) > 0.999 and a.dot(c) > 0.999: flat += 1
print('FLAT-shaded tris', flat, 'of', len(tris) // 3)
