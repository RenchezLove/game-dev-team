import bpy, sys, math
sys.path.insert(0, 'E:/game-dev-team/assets/hero_tripo/_work')
import hcommon as H
from mathutils import Matrix
bpy.ops.wm.open_mainfile(filepath=H.WEAR)
T0 = [bpy.data.objects[n] for n in ('SK_Cloth_T0_Head', 'SK_Cloth_T0_Torso', 'SK_Cloth_T0_Legs')]
H.landmarks(T0, 'T0')
bpy.ops.import_scene.gltf(filepath=H.GLB)
tr = [o for o in bpy.context.selected_objects if o.type == 'MESH'][0]
bpy.context.view_layer.update()
tr.data.transform(Matrix.Rotation(math.radians(-90), 4, 'Z') @ tr.matrix_world)
tr.matrix_world = Matrix.Identity(4)
zmin = min(v.co.z for v in tr.data.vertices)
tr.data.transform(Matrix.Translation((0, 0, -zmin)))
for o in T0: o.hide_viewport = True
H.landmarks([tr], 'TRIPO')
