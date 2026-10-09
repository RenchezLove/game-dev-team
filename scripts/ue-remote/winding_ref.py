import unreal
def stat(path):
    sm = unreal.load_asset(path)
    verts, tris, normals, uvs, tangents = unreal.ProceduralMeshLibrary.get_section_from_static_mesh(sm, 0, 0)
    b = sm.get_bounding_box(); c0 = (b.min + b.max) / 2.0
    gout = ginn = agree = disagree = 0
    for i in range(0, len(tris), 3):
        a, bb, c = tris[i], tris[i + 1], tris[i + 2]
        ctr = (verts[a] + verts[bb] + verts[c]) / 3.0 - c0
        g = (verts[bb] - verts[a]).cross(verts[c] - verts[a])
        n = normals[a] + normals[bb] + normals[c]
        if g.dot(ctr) > 0: gout += 1
        else: ginn += 1
        if g.dot(n) > 0: agree += 1
        else: disagree += 1
    print(path.rsplit('/', 1)[1], '| cross(e1,e2) outward', gout, 'inward', ginn, '| cross agrees with normal', agree, 'disagrees', disagree)
for p in ('/Engine/BasicShapes/Cube', '/Game/Environment/Props/ScientistBase/SM_PersonalChest', '/Game/Environment/Props/ScientistBase/SM_UAZ452', '/Game/Environment/Props/ScientistBase/SM_StashChest', '/Game/Environment/Props/ScientistBase/SM_Oscilloscope', '/Game/Weapons/Shotgun/SM_Shotgun_TOZ34', '/Game/Environment/Props/ScientistBase/SM_ArmyTent'):
    try: stat(p)
    except Exception as e: print(p, 'ERR', e)
