import unreal
def stat(path):
    sm = unreal.load_asset(path)
    verts, tris, normals, uvs, tangents = unreal.ProceduralMeshLibrary.get_section_from_static_mesh(sm, 0, 0)
    b = sm.get_bounding_box(); c0 = (b.min + b.max) / 2.0
    out = inn = 0
    for i in range(0, len(tris), 3):
        a, bb, c = tris[i], tris[i + 1], tris[i + 2]
        ctr = (verts[a] + verts[bb] + verts[c]) / 3.0 - c0
        n = normals[a] + normals[bb] + normals[c]
        if n.dot(ctr) > 0: out += 1
        else: inn += 1
    print(path.rsplit('/', 1)[1], 'normals outward', out, 'inward', inn, 'allow_cpu', sm.get_editor_property('allow_cpu_access'))
for p in ('/Engine/BasicShapes/Cube', '/Game/Environment/Props/SM_BanditBarrel', '/Game/Environment/Props/ScientistBase/SM_PersonalChest', '/Game/Environment/Props/ScientistBase/SM_UAZ452', '/Game/Environment/Props/ScientistBase/SM_ArmyTent'):
    try: stat(p)
    except Exception as e: print(p, 'ERR', e)
