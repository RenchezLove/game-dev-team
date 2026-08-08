import unreal
M = {
 'POI1_Car_Body':      ('Машина_Кузов','ТочкиИнтереса/РазбитаяМашина'),
 'POI1_Car_Hood':      ('Машина_Капот','ТочкиИнтереса/РазбитаяМашина'),
 'POI1_Car_Trunk':     ('Машина_Багажник','ТочкиИнтереса/РазбитаяМашина'),
 'POI1_Car_Glass':     ('Машина_Стекло','ТочкиИнтереса/РазбитаяМашина'),
 'POI1_Car_Door_FL':   ('Машина_Дверь_ПередняяЛевая','ТочкиИнтереса/РазбитаяМашина'),
 'POI1_Car_Door_FR':   ('Машина_Дверь_ПередняяПравая','ТочкиИнтереса/РазбитаяМашина'),
 'POI1_Car_Door_RL':   ('Машина_Дверь_ЗадняяЛевая','ТочкиИнтереса/РазбитаяМашина'),
 'POI1_Car_Door_RR':   ('Машина_Дверь_ЗадняяПравая','ТочкиИнтереса/РазбитаяМашина'),
 'POI1_Car_Wheel_RL':  ('Машина_Колесо_ЗаднееЛевое','ТочкиИнтереса/РазбитаяМашина'),
 'POI1_Car_Wheel_RR':  ('Машина_Колесо_ЗаднееПравое','ТочкиИнтереса/РазбитаяМашина'),
 'POI1_Car_Block_L':   ('Машина_Подпорка_Левая','ТочкиИнтереса/РазбитаяМашина'),
 'POI1_Car_Block_R':   ('Машина_Подпорка_Правая','ТочкиИнтереса/РазбитаяМашина'),
 'POI1_Car_Scratches': ('Машина_Царапины','ТочкиИнтереса/РазбитаяМашина'),
 'POI1_BonePile':      ('КучаКостей_УМашины','ТочкиИнтереса/РазбитаяМашина'),
 'POI1_Blood':         ('ПятноКрови_УМашины','ТочкиИнтереса/РазбитаяМашина'),
 'POI2_Tent':          ('Палатка','ТочкиИнтереса/БрошенныйЛагерь'),
 'POI2_Campfire':      ('Кострище','ТочкиИнтереса/БрошенныйЛагерь'),
 'POI2_Smoke1':        ('Дым1','ТочкиИнтереса/БрошенныйЛагерь'),
 'POI2_Smoke2':        ('Дым2','ТочкиИнтереса/БрошенныйЛагерь'),
 'POI2_Smoke3_Top':    ('Дым3_Верхний','ТочкиИнтереса/БрошенныйЛагерь'),
 'POI2_Crate1':        ('Ящик1','ТочкиИнтереса/БрошенныйЛагерь'),
 'POI2_Crate2':        ('Ящик2','ТочкиИнтереса/БрошенныйЛагерь'),
 'POI2_BonePile':      ('КучаКостей1','ТочкиИнтереса/БрошенныйЛагерь'),
 'POI2_BonePile2':     ('КучаКостей2','ТочкиИнтереса/БрошенныйЛагерь'),
 'POI2_Blood':         ('ПятноКрови1','ТочкиИнтереса/БрошенныйЛагерь'),
 'POI2_Blood2':        ('ПятноКрови2','ТочкиИнтереса/БрошенныйЛагерь'),
 'POI2_Loot':          ('ЛутЛагеря','ТочкиИнтереса/БрошенныйЛагерь'),
}
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/L_World_C')
sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
n = 0
for a in sub.get_all_level_actors():
    lbl = a.get_actor_label()
    if lbl in M:
        new_lbl, folder = M[lbl]
        a.set_actor_label(new_lbl)
        a.set_folder_path(folder)
        n += 1
left = [a.get_actor_label() for a in sub.get_all_level_actors() if 'POI' in a.get_actor_label().upper() or 'POI' in str(a.get_folder_path()).upper()]
print('POIREN|renamed=%d|left=%s' % (n, ';'.join(left) if left else 'NONE'))
ok = unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
print('POIREN|SAVE=%s' % ok)
