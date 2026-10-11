import unreal
print('PIE', unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor())
sms = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
R = 30.0
for n in ('SM_Tree_Pine_01', 'SM_Tree_Pine_02'):
    m = unreal.load_asset('/Game/Environment/Nature/' + n)
    b = m.get_bounds(); bs = m.get_editor_property('body_setup'); ag = bs.get_editor_property('agg_geom')
    print(n, 'bounds', round(b.box_extent.x, 1), round(b.box_extent.y, 1), round(b.box_extent.z * 2, 1), 
          'old counts', [len(ag.get_editor_property(k)) for k in ('box_elems', 'sphere_elems', 'sphyl_elems', 'convex_elems')])
    sms.remove_collisions(m)
    bs = m.get_editor_property('body_setup'); ag = bs.get_editor_property('agg_geom')
    c = unreal.KSphylElem(); h = b.box_extent.z * 2.0
    c.set_editor_property('center', unreal.Vector(0, 0, h * 0.5)); c.set_editor_property('radius', R); c.set_editor_property('length', max(1.0, h - 2 * R))
    ag.set_editor_property('sphyl_elems', [c]); bs.set_editor_property('agg_geom', ag)
    m.modify()
    ag2 = m.get_editor_property('body_setup').get_editor_property('agg_geom')
    print('  new', [(e.get_editor_property('radius'), e.get_editor_property('length'), e.get_editor_property('center').z) for e in ag2.get_editor_property('sphyl_elems')],
          'convex left', len(ag2.get_editor_property('convex_elems')), 'saved', unreal.EditorAssetLibrary.save_loaded_asset(m, False))
