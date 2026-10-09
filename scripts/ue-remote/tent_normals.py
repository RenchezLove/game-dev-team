import unreal
sm = unreal.load_asset('/Game/Environment/Props/ScientistBase/SM_ArmyTent')
d = sm.get_static_mesh_description(0)
print([x for x in dir(d) if 'normal' in x.lower() or 'attribute' in x.lower() or 'instance' in x.lower()][:40])
pm = unreal.ProceduralMeshLibrary
try:
    verts, tris, normals, uvs, tangents = pm.get_section_from_static_mesh(sm, 0, 0)
    print('verts', len(verts), 'tris', len(tris) // 3)
    up_ok = up_bad = side = 0; bad_examples = []
    for i in range(0, len(tris), 3):
        a, b, c = tris[i], tris[i + 1], tris[i + 2]
        e1 = verts[b] - verts[a]; e2 = verts[c] - verts[a]
        g = e1.cross(e2); L = g.length()
        if L < 1e-6: continue
        g = g / L
        n = (normals[a] + normals[b] + normals[c]); n = n / max(n.length(), 1e-6)
        dot = g.dot(n)
        zc = (verts[a].z + verts[b].z + verts[c].z) / 3
        if zc > 220:
            if abs(dot) > 0.5:
                if (n.z > 0.2): up_ok += 1
                else:
                    up_bad += 1
                    if len(bad_examples) < 5: bad_examples.append((round(zc), round(n.x, 2), round(n.y, 2), round(n.z, 2), round(g.z, 2), round(dot, 2)))
            else: side += 1
    print('ROOF tris: normal up', up_ok, '| normal not up', up_bad, '| inconsistent', side, bad_examples)
    alln = [ (verts[tris[i]]-verts[tris[i]]) for i in range(0)]
    pos = neg = 0
    for i in range(0, len(tris), 3):
        a, b, c = tris[i], tris[i + 1], tris[i + 2]
        g = (verts[b] - verts[a]).cross(verts[c] - verts[a])
        if g.length() < 1e-6: continue
        n = normals[a] + normals[b] + normals[c]
        if g.dot(n) > 0: pos += 1
        else: neg += 1
    print('ALL tris: winding·normal >0', pos, '<0', neg)
except Exception as e:
    print('ERR', e)
