import unreal
# Палатка: нормали сданного файла вывернуты относительно обхода граней на 1227 из 1368 треугольников
# (замер winding_ref.py). Пересчитываем нормали в самой сетке Unreal по геометрии.
sms = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
P = '/Game/Environment/Props/ScientistBase/SM_ArmyTent'
sm = unreal.load_asset(P)
bs = sms.get_lod_build_settings(sm, 0)
print('before recompute_normals', bs.recompute_normals, 'recompute_tangents', bs.recompute_tangents)
bs.recompute_normals = True; bs.recompute_tangents = True
sms.set_lod_build_settings(sm, 0, bs)
print('after', sms.get_lod_build_settings(sm, 0).recompute_normals, 'simple collisions kept', sms.get_simple_collision_count(sm), 'SAVE', unreal.EditorAssetLibrary.save_loaded_asset(sm, False))
exec(open('E:/game-dev-team/scripts/ue-remote/winding_ref.py', encoding='utf-8').read())
sm = unreal.load_asset(P)
verts, tris, normals, uvs, tangents = unreal.ProceduralMeshLibrary.get_section_from_static_mesh(sm, 0, 0)
flat = 0
for i in range(0, len(tris), 3):
    a, b, c = normals[tris[i]], normals[tris[i + 1]], normals[tris[i + 2]]
    if a.dot(b) > 0.999 and a.dot(c) > 0.999: flat += 1
print('FLAT-shaded tris', flat, 'of', len(tris) // 3)
