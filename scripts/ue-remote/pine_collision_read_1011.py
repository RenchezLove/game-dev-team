import unreal
print('PIE', unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor())
for n in ('SM_Tree_Pine_01', 'SM_Tree_Pine_02'):
    m = unreal.load_asset('/Game/Environment/Nature/' + n)
    b = m.get_bounds(); bs = m.get_editor_property('body_setup'); ag = bs.get_editor_property('agg_geom')
    print(n, 'bounds ext', b.box_extent, 'origin', b.origin, 'flag', bs.get_editor_property('collision_trace_flag'))
    for k in ('box_elems', 'sphere_elems', 'sphyl_elems', 'convex_elems'):
        for e in ag.get_editor_property(k):
            d = {}
            for p in ('center', 'radius', 'length', 'x', 'y', 'z', 'rotation'):
                try: d[p] = e.get_editor_property(p)
                except Exception: pass
            if k == 'convex_elems':
                eb = e.get_editor_property('elem_box'); d['box'] = (eb.min, eb.max)
            print('  ', k, d)
