"""Build the trader from Tripo on our skeleton (see assets/tripo_char/tripo_char.py, numbers in configs.py).
Run: blender.exe -b --factory-startup --python 10_build.py
"""
import sys
sys.path.insert(0, 'E:/game-dev-team/assets/tripo_char')
import tripo_char, configs
tripo_char.build(configs.CFG['trader'])
