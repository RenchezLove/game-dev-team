import unreal
sm = unreal.load_asset('/Game/Environment/Props/ScientistBase/SM_ArmyTent')
verts, tris, normals, uvs, tangents = unreal.ProceduralMeshLibrary.get_section_from_static_mesh(sm, 0, 0)
wall_out = wall_in = roof_up = roof_down = 0; uvroof = []
for i in range(0, len(tris), 3):
    a, b, c = tris[i], tris[i + 1], tris[i + 2]
    ctr = (verts[a] + verts[b] + verts[c]) / 3.0
    n = normals[a] + normals[b] + normals[c]; n = n / max(n.length(), 1e-6)
    inside_body = abs(ctr.x) <= 275 and -402 <= ctr.y <= 402
    if not inside_body: continue
    if ctr.z > 225:
        if n.z > 0.2: roof_up += 1
        elif n.z < -0.2:
            roof_down += 1
            if len(uvroof) < 6: uvroof.append((round(uvs[a].x, 2), round(uvs[a].y, 2), round(ctr.z)))
    elif 30 < ctr.z < 200 and abs(n.z) < 0.4 and (abs(ctr.x) > 265 or ctr.y < -395):
        radial = unreal.Vector(ctr.x, 0, 0) if abs(ctr.x) > 265 else unreal.Vector(0, ctr.y, 0)
        if n.dot(radial) > 0: wall_out += 1
        else: wall_in += 1
print('WALLS normal outward', wall_out, 'inward', wall_in)
print('ROOF normal up', roof_up, 'down', roof_down, 'uv samples of down-facing', uvroof)
