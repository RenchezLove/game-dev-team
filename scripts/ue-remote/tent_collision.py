import unreal, re
# Преграда палатки: только шатёр и тамбур, растяжки и колья игрок проходит насквозь (Ринат, 09.10).
sms = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
sm = unreal.load_asset('/Game/Environment/Props/ScientistBase/SM_ArmyTent')
b = sm.get_bounding_box()
print('BOUNDS', [round(v) for v in (b.min.x, b.min.y, b.min.z)], [round(v) for v in (b.max.x, b.max.y, b.max.z)])
# тамбур со стороны, где у полной модели нет выступа растяжек (у шатра край ровно 400)
front = 1.0 if abs(b.max.y - 400.0) < abs(-b.min.y - 400.0) else -1.0
print('FRONT sign Y', front)
BOXES = [((0.0, front * -57.0, 168.0), (544.4, 686.0, 336.0)), ((0.0, front * 343.0, 100.0), (106.0, 114.0, 200.0))]
sms.remove_collisions(sm)
for _ in BOXES:
    sms.add_simple_collisions(sm, unreal.ScriptCollisionShapeType.BOX)
bs = sm.get_editor_property('body_setup')
ag = bs.get_editor_property('agg_geom')
txt = ag.export_text()
parts = re.findall(r'\(Center=\(X=[-0-9.]+,Y=[-0-9.]+,Z=[-0-9.]+\)(?:,Rotation=\([^)]*\))?,X=[-0-9.]+,Y=[-0-9.]+,Z=[-0-9.]+', txt)
print('BOX ELEMS found', len(parts))
new = txt
for old, (c, s) in zip(parts, BOXES):
    rep = re.sub(r'Center=\(X=[-0-9.]+,Y=[-0-9.]+,Z=[-0-9.]+\)', 'Center=(X=%f,Y=%f,Z=%f)' % c, old, count=1)
    head, tail = rep.rsplit(',X=', 1)
    rep = head + ',X=%f,Y=%f,Z=%f' % s
    new = new.replace(old, rep, 1)
ag.import_text(new)
bs.set_editor_property('agg_geom', ag)
sm.modify()
print('AFTER', sm.get_editor_property('body_setup').get_editor_property('agg_geom').export_text()[:420])
print('simple', sms.get_simple_collision_count(sm), 'SAVE', unreal.EditorAssetLibrary.save_loaded_asset(sm, False))
