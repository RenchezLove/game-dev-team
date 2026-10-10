import re
p = 'E:/game-dev-team/assets/scientist_base/_work/uaz_10_build.py'
s = open(p, encoding='utf-8').read()
old = s[s.index("    if kind == 'mirror':"):s.index("bmesh.ops.triangulate(bm, faces=bm.faces)\nbmesh.ops.recalc_face_normals(bm, faces=bm.faces)\nme = bpy.data.meshes.new('rebuilt')")]
new = '''    vs = [bm.verts.new((x, y, z)) for z in (lo[2], hi[2]) for y in (lo[1], hi[1]) for x in (lo[0], hi[0])]
    for q in ((0, 1, 3, 2), (4, 5, 7, 6), (0, 1, 5, 4), (2, 3, 7, 6), (0, 2, 6, 4), (1, 3, 7, 5)):
        f = bm.faces.new([vs[i] for i in q]); f[tagl] = 1 if kind == 'mirror' else 0
    if kind == 'mirror':                                          # a thin arm from the door to the mirror (4 sides, no caps)
        sgn = 1.0 if lo[0] > 0 else -1.0
        xa, xb = sgn * 0.74, (lo[0] if sgn > 0 else hi[0]); ym = (lo[1] + hi[1]) / 2; zm = lo[2] + 0.25 * (hi[2] - lo[2]); h = 0.016
        r = [[bm.verts.new((x, ym + dy, zm + dz)) for dy, dz in ((-h, -h), (h, -h), (h, h), (-h, h))] for x in (xa, xb)]
        for k in range(4):
            f = bm.faces.new((r[0][k], r[0][(k + 1) % 4], r[1][(k + 1) % 4], r[1][k])); f[tagl] = 1
'''
s = s.replace(old, new)
s = s.replace("bm = bmesh.new()\nNS = 10", "bm = bmesh.new(); tagl = bm.faces.layers.int.new('tag')\nNS = 10")
s = s.replace("img.filepath_raw = OUT + 'T_UAZ452_D.png'; img.file_format = 'PNG'; img.save()", '''# mirrors and their arms: plain dark housing, pale glass on the side that looks back (the bake gives them random texels)
tg = np.zeros(len(low.data.polygons), np.int32); low.data.attributes['tag'].data.foreach_get('value', tg)
nr = np.zeros(len(low.data.polygons) * 3); low.data.polygons.foreach_get('normal', nr); nr = nr.reshape(-1, 3)
fid, bw = sb.raster(low.data, 'UVMap', TEX)
col = np.where((nr[:, 1] < -0.9)[:, None], np.array([[0.36, 0.41, 0.45]]), np.array([[0.09, 0.09, 0.09]]))
m = (fid >= 0) & (tg[np.clip(fid, 0, None)] == 1)
px[m, :3] = col[fid[m]]
for _ in range(5):                                               # and the margin around those islands
    for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        sm = np.roll(m, (dy, dx), (0, 1)); new = sm & ~m & (fid < 0)
        px[new] = np.roll(px, (dy, dx), (0, 1))[new]; m = m | new
print('MIRRORS repainted texels %d (faces %d)' % (int(m.sum()), int((tg == 1).sum())))
low.data.attributes.remove(low.data.attributes['tag'])
img.pixels.foreach_set(px.ravel())
img.filepath_raw = OUT + 'T_UAZ452_D.png'; img.file_format = 'PNG'; img.save()''')
open(p, 'w', encoding='utf-8').write(s)
