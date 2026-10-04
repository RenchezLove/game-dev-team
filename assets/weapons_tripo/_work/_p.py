p = 'E:/game-dev-team/assets/weapons_tripo/_work/10_build.py'
s = open(p, encoding='utf-8').read()
a = "    co[:, 0] *= C['mx'][0] / np.abs(co[:, 0]).max()\n"
b = ("    # width: the whole outline fills the old +-2.4 cm (the handle axis ends up ~0.4 cm off centre,\n"
     "    # which keeps the blade wide instead of squashing it)\n"
     "    co[:, 0] = (co[:, 0] - co[:, 0].min()) / np.ptp(co[:, 0]) * (C['mx'][0] - C['mn'][0]) + C['mn'][0]\n")
assert a in s
s = s.replace(a, b)
a2 = "    co[:, 2] *= C['mx'][2] / np.abs(co[:, 2]).max()\n"
b2 = "    co[:, 2] = (co[:, 2] - co[:, 2].min()) / np.ptp(co[:, 2]) * (C['mx'][2] - C['mn'][2]) + C['mn'][2]\n    hs = co[co[:, 1] < 0.10]\n    print('KNIFE handle centre x %.2f cm, handle width %.2f cm, thickness %.2f cm' % (100 * (hs[:, 0].min() + hs[:, 0].max()) / 2, 100 * np.ptp(hs[:, 0]), 100 * np.ptp(hs[:, 2])))\n"
assert a2 in s
s = s.replace(a2, b2)
open(p, 'w', encoding='utf-8').write(s)
