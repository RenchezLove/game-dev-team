"""Shared constants of the car kit builders (11_build.py, 12_bake.py): Blender frame, nose +Y."""
from mathutils import Vector

WORK = 'E:/game-dev-team/assets/abandoned_car_tripo/_work/'
SHELL_TARGET = 405          # shell tris after collapse, before the seam cuts
FLOOR_Z = 0.62              # down-facing faces below this = underbody / wheel wells
DISSOLVE_DEG = 6            # post-cut flat merge
PLUG_IN = 0.06              # dark plugs sit this far inside the removed panel
PLUG_SIMPLE = 20            # deg, plug outline simplification
CABIN_Z = 0.90              # dark cabin floor

# seams, Blender frame (texture scans _seams.py, 09-27)
DOOR_Z = (0.34, 1.335)                  # door bottom seam .. frame top under the roof
DOOR_FY = (-0.01, 0.92)                 # front door, hinge at the front edge (0.92)
DOOR_RY = (-0.88, -0.01)                # rear door, hinge at the front edge (-0.01)
DOOR_X = 0.76                           # side surface at the hinge line
BELT_Z = 0.94                           # window seal
HOOD_Y = (0.975, 1.965); HOOD_HX = 0.70
TRUNK_Y = (-2.025, -1.42); TRUNK_HX = 0.64
WS = dict(z=(0.955, 1.325), x=(0.60, 0.52), y=(0.55, 1.02))      # windshield
RW = dict(z=(1.03, 1.335), x=(0.60, 0.53), y=(-1.45, -1.0))      # rear window
LAMP_X = (0.32, 0.61); LAMP_Z = (0.56, 0.75)                     # tail lamps (rear render)
WHEEL_R, WHEEL_HW, WHEEL_N = 0.285, 0.09, 10
WHEEL_A0 = 0.3141592653589793   # 18 deg: a ring vertex sits at the bottom (tyre touches Z=0)
WHEEL_SRC = Vector((-0.62, 1.45, 0.285))  # Tripo left-front wheel centre (bake position)

PARTS = ['Body', 'Glass', 'Door_FL', 'Door_FR', 'Door_RL', 'Door_RR', 'Hood', 'Trunk', 'Wheel']
PID = {n: i for i, n in enumerate(PARTS)}
KIND_PAINT, KIND_DARK, KIND_LAMP = 0, 1, 2     # face attribute 'kind'

