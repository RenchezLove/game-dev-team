p = 'E:/game-dev-team/assets/scientist_base/_work/osc_10_build.py'
s = open(p, encoding='utf-8').read()
a = s[s.index("bpy.ops.wm.open_mainfile("):s.index("for md in list(src.modifiers):")]
b = '''sb.empty()                                                       # the source object is appended into a clean scene (its own file has an odd saved context)
with bpy.data.libraries.load(sb.SRCD + 'oscillograph/source/oscilloscope.blend', link=False) as (df, dt):
    dt.objects = ['oscilloscope']
src = dt.objects[0]; bpy.context.scene.collection.objects.link(src)
bpy.context.view_layer.update()
'''
s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s)
