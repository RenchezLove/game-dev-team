import unreal
# Проба в СВОЕЙ рабочей копии (ws-pda), ничего не сохраняет: ставит машине облезлость PROBE,
# запускает игру в редакторе и читает параметр материала у машины в игровом мире.
OUT = r"E:/game-dev-team/logs/pie_probe2_uazpaint_1010.txt"
PROBE = 0.25
lines = []
state = {"ticks": 0, "pie_ticks": 0, "done": False, "handle": None, "started": False, "travel_tick": 0, "first_world": None}
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
cls = unreal.load_class(None, '/Script/ContrarySurvivor.AbandonedCar')


def say(s):
    lines.append(s)
    unreal.log("PROBE|" + s)


def mat_info(m):
    if not m:
        return 'None'
    out = '%s[%s]' % (m.get_name(), type(m).__name__)
    if isinstance(m, unreal.MaterialInstance):
        p = m.get_editor_property('parent')
        out += ' parent=%s S=%s' % (p.get_name() if p else None,
            [(str(x.parameter_info.name), round(x.parameter_value, 3)) for x in m.get_editor_property('scalar_parameter_values')])
    if isinstance(m, unreal.MaterialInstanceDynamic):
        out += ' outer=%s peel_now=%s' % (m.get_outer().get_name(), round(m.get_scalar_parameter_value('PaintPeel'), 3))
    return out


def find_uaz(world):
    for a in unreal.GameplayStatics.get_all_actors_of_class(world, cls):
        if 'UAZ' in a.get_class().get_name():
            return a
    return None


def dump(world, tag):
    a = find_uaz(world) if world else None
    if not a:
        say('%s: УАЗ не найден' % tag)
        return
    say('%s ACTOR %s peel_field=%s' % (tag, a.get_name(), round(a.get_editor_property('paint_peel'), 4)))
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        if c.get_name() in ('Body', 'DoorFL', 'Trunk', 'WheelFL'):
            say('  %s %s override=%s slot0: %s' % (tag, c.get_name(),
                [m.get_name() if m else None for m in c.get_editor_property('override_materials')], mat_info(c.get_material(0))))


def finish():
    state["done"] = True
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    if state["handle"]:
        unreal.unregister_slate_post_tick_callback(state["handle"])
    unreal.SystemLibrary.quit_editor()


def tick(dt):
    if state["done"]:
        return
    state["ticks"] += 1
    try:
        if not state["started"]:
            if state["ticks"] < 30:
                return
            w = ues.get_editor_world()
            say('editor world = %s' % (w.get_path_name() if w else None))
            dump(w, 'EDITOR-как-сохранено')
            a = find_uaz(w)
            if a:
                a.set_editor_property('paint_peel', PROBE)
                dump(w, 'EDITOR-после-правки-поля')
            say("save level = %s" % les.save_current_level())
            les.editor_request_begin_play()
            state["started"] = True
            return
        if les.is_in_play_in_editor() and ues.get_game_world():
            state["pie_ticks"] += 1
            gw = ues.get_game_world()
            if state["pie_ticks"] == 60:
                dump(gw, "GAME-копия-мира-редактора")
                state["first_world"] = gw.get_path_name()
                say("world before travel = %s" % state["first_world"])
                unreal.GameplayStatics.open_level(gw, "L_World_C")
                state["travel_tick"] = state["pie_ticks"]
            elif state["travel_tick"] and state["pie_ticks"] > state["travel_tick"] + 200 and find_uaz(gw):
                say("world after travel = %s" % gw.get_path_name())
                dump(gw, "GAME-уровень-загружен-с-диска")
                les.editor_request_end_play()
                finish()
            elif state["pie_ticks"] > 5000:
                say("после переезда УАЗ не найден")
                finish()
        elif state["ticks"] > 6000:
            say('игра в редакторе не запустилась')
            finish()
    except Exception as e:
        say('ОШИБКА %s' % e)
        finish()


unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/L_World_C')
state["handle"] = unreal.register_slate_post_tick_callback(tick)
