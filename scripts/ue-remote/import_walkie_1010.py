ONLY = ['SM_WalkieTalkie']
src = open('E:/game-dev-team/scripts/ue-remote/import_scibase.py', encoding='utf-8').read()
src = src.replace("    ('SM_StashChest',", "    ('SM_WalkieTalkie', 'SM_WalkieTalkie', 'T_WalkieTalkie_D', 0, None),\n    ('SM_StashChest',")
exec(src)
