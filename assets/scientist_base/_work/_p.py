p = 'E:/game-dev-team/assets/scientist_base/_work/toz_10_build.py'
s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert a in s, a
    s = s.replace(a, b, 1)
rep("        kind, tgt = 'stock', 230\n", "        kind, tgt = 'stock', 218\n")
rep("    PLAN.append((i, kind, tgt, n, op))\n", "    PLAN.append((i, kind, tgt, n, op)); BND[kind] = (cc.min(0), cc.max(0))\n")
rep("PLAN = []; barrel = None; TRIG = []\n", "PLAN = []; barrel = None; TRIG = []; BND = {}\n")
rep("for lo_, hi_ in TRIG:", """# the breech block of the source barrels filled the space between the fore-end and the receiver under the tubes: a closed dark block there
fe, rc = BND['fore-end'], BND['receiver']
TRIG.append((np.array([-(rx - 0.002), fe[1][1] - 0.07, max(fe[0][2], rc[0][2]) + 0.006]), np.array([rx - 0.002, rc[0][1] + 0.05, zlo + rz])))
print('FILLER block between fore-end and receiver: y %.3f..%.3f z %.3f..%.3f' % (TRIG[-1][0][1], TRIG[-1][1][1], TRIG[-1][0][2], TRIG[-1][1][2]))
for lo_, hi_ in TRIG:""")
open(p, 'w', encoding='utf-8').write(s)
