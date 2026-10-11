import unreal
# Проба в СВОЕЙ рабочей копии, ничего не сохраняет: запускает игру в редакторе, создаёт окно
# смартфона из настоящего WBP_Pda и кнопку смартфона, даёт им прожить несколько кадров.
# Числа печатает сам код окна строкой «QA: pda phone layout» и проба строками PROBE|.
state = {"ticks": 0, "pie_ticks": 0, "done": False, "handle": None, "started": False, "w": None, "b": None}
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)


def say(s):
    unreal.log("PROBE|" + s)


def finish():
    state["done"] = True
    if state["handle"]:
        unreal.unregister_slate_post_tick_callback(state["handle"])
    unreal.SystemLibrary.quit_editor()


def report(tag):
    w = state["w"]
    plate = w.get_widget_from_name('PanelPlate') if w else None
    if plate:
        slot = unreal.WidgetLayoutLibrary.slot_as_canvas_slot(plate)
        g = plate.get_cached_geometry()
        ls = unreal.SlateLibrary.get_local_size(g)
        sz = slot.get_size() if slot else None
        say('%s plate slot=%s drawn=%.1fx%.1f ratio=%.3f viewport=%s scale=%.3f' % (tag, sz, ls.x, ls.y, (ls.x / ls.y) if ls.y else 0,
            unreal.WidgetLayoutLibrary.get_viewport_size(ues.get_game_world()), unreal.WidgetLayoutLibrary.get_viewport_scale(ues.get_game_world())))
    else:
        say('%s подложка не найдена' % tag)
    b = state["b"]
    if b:
        tree_icon = None
        for wd in unreal.WidgetLibrary.get_all_widgets_of_class(ues.get_game_world(), unreal.Image, False) if hasattr(unreal, 'WidgetLibrary') else []:
            if wd.get_name() == 'PdaIcon':
                tree_icon = wd
        if tree_icon:
            ls = unreal.SlateLibrary.get_local_size(tree_icon.get_cached_geometry())
            say('%s icon drawn=%.1fx%.1f' % (tag, ls.x, ls.y))


def tick(dt):
    if state["done"]:
        return
    state["ticks"] += 1
    try:
        if not state["started"]:
            if state["ticks"] < 30:
                return
            les.editor_request_begin_play()
            state["started"] = True
            return
        if les.is_in_play_in_editor() and ues.get_game_world():
            state["pie_ticks"] += 1
            world = ues.get_game_world()
            if state["pie_ticks"] == 40:
                pc = unreal.GameplayStatics.get_player_controller(world, 0); unreal.SystemLibrary.execute_console_command(world, "QaShowPda", pc); say("команда открытия окна подана")
            if False:
                t = state["t"]; imp = t.get_editor_property("imported_size"); say("кадр %d: картинка смартфона сейчас %dx%d (пропорции %.3f), исходный размер %dx%d (пропорции %.3f)" % (state["pie_ticks"], t.blueprint_get_size_x(), t.blueprint_get_size_y(), t.blueprint_get_size_x() / max(1, t.blueprint_get_size_y()), imp.x, imp.y, imp.x / max(1, imp.y)))
            if state["pie_ticks"] == 121:
                les.editor_request_end_play()
                finish()
        elif state["ticks"] > 9000:
            say('игра в редакторе не запустилась')
            finish()
    except Exception as e:
        say('ОШИБКА %s' % e)
        finish()


unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/L_World_C')
state["handle"] = unreal.register_slate_post_tick_callback(tick)
