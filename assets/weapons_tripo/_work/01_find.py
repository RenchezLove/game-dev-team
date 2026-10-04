import bpy, glob, os
import numpy as np
import addon_utils
c = chr(92)
files = []
for root in ('E:/game-dev-team', 'E:/ForGameLead(Materials)', 'E:/ContrarySurvior/ContrarySurvivor'):
    for dp, dn, fn in os.walk(root):
        if any(s in dp for s in ('Intermediate', 'DerivedDataCache', '.git', 'Binaries', 'node_modules')):
            continue
        for f in fn:
            if f.lower().endswith('.fbx') and ('knife' in f.lower() or 'pistol' in f.lower()):
                files.append(os.path.join(dp, f).replace(c, '/'))
for f in sorted(files):
    bpy.ops.wm.read_factory_settings(use_empty=True); addon_utils.enable('io_scene_fbx')
    try:
        bpy.ops.import_scene.fbx(filepath=f)
    except Exception as e:
        print('FOUND', f, 'import failed', e); continue
    bpy.context.view_layer.update()
    for o in [o for o in bpy.data.objects if o.type == 'MESH']:
        cs = np.array([o.matrix_world @ v.co for v in o.data.vertices])
        print('FOUND %s | %s tris %d min %s max %s | %s' % (f, o.name, sum(len(p.vertices) - 2 for p in o.data.polygons), (cs.min(0) * 100).round(1), (cs.max(0) * 100).round(1), __import__('time').strftime('%Y-%m-%d', __import__('time').localtime(os.path.getmtime(f)))))
