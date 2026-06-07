# Архитектурные решения (ADR)

> Каждое решение по инструментам и архитектуре фиксируется здесь. «Нативное проверено» означает живую проверку реестра коннекторов, а не память.

## ADR-001 — Движок системы: субагенты Claude Code, standalone, game-lead = корень
Система game-dev — самостоятельная (не вложена в другие системы агентов). Движок — субагенты Claude Code (`.claude/agents/*.md`). `game-lead` запускается как главная сессия (`claude --agent game-lead`) и порождает специалистов.
**Причина:** субагент Claude Code не может порождать субагентов (подтверждено по code.claude.com/docs). Делая `game-lead` корнем-главной-сессией, получаем рабочее дерево «лид → специалисты». Будь game-lead вложенным субагентом, он не смог бы звать специалистов. Запас на многоуровневость в будущем — через agent teams (отдельный механизм), не через субагенты.

## ADR-002 — modeler-3d: Blender через официальный сервер blender-mcp (CLI-уровень)
Инструмент 3D — официальный сервер **blender-mcp v1.0.0** (Blender Lab), заведённый в Claude Code **CLI**, НЕ через бандл Claude Desktop.
- Установка: `uv tool install` из `git+https://projects.blender.org/lab/blender_mcp.git#subdirectory=mcp`. Бинарь: `C:\Users\pgr40\.local\bin\blender-mcp.exe`.
- Регистрация: проектно в `.mcp.json` (сервер `blender`).
- Привязка к агенту `modeler-3d` через `mcpServers: [blender]` (только этот агент видит инструменты Blender).
- Сторона Blender: аддон **Blender Lab v1.0.0**, слушает `localhost:9876`, auto-start.
Самодельный MCP на `bpy` не используем — есть официальный сервер.
**Статус:** заведено и проверено живыми вызовами (get_objects_summary, get_object_detail_summary, render_viewport_to_path). Рабочие нюансы — см. [ADR-011](#adr-011--blender-рабочие-нюансы-один-клиент-на-сокет-output_path-у-render_viewport).

## ADR-003 — unreal-operator: MCP-сервер @runreal/unreal-mcp (UE Python/Remote Execution под капотом)
Нативного коннектора Unreal в реестре Claude нет (проверено несколькими запросами — граница проверки), встроенного навыка тоже нет → по правилу «нативное первым» спускаемся на уровень MCP. Выбран сервер **`@runreal/unreal-mcp`**, который ходит в редактор по UE Python / Remote Execution. Computer Use остаётся крайним случаем, если программного пути не хватит.
- Регистрация: проектно в `.mcp.json`, сервер `unreal`. **Запуск через абсолютный путь к `node.exe` + абсолютный путь к `dist/bin.js` пакета** (`command: "C:\\Program Files\\nodejs\\node.exe"`, `args: ["…\\@runreal\\unreal-mcp\\dist\\bin.js"]`) — надёжная форма, по аналогии с blender (полный путь к бинарю).
  - **Почему не голый `npx`:** 2026-06-06 первая попытка упала на старте — `claude mcp list` показал `unreal … ✗ Failed to connect`, тулы `mcp__unreal__*` в сессию не загрузились. Причина: неинтерактивная оболочка, через которую харнесс стартует MCP-серверы, **не видит `C:\Program Files\nodejs` в PATH** (`npx`/`node` NOT FOUND), хотя Node реально установлен (node v24.16.0). blender-сервер цепляется, т.к. задан полным путём к `.exe`. Фикс — указать **абсолютный путь к `node.exe`** и прямо к `dist/bin.js` пакета, минуя резолв `npx`.
- **Multicast Bind Address = `0.0.0.0` обязателен** (UE → Project Settings → Plugins → Python Remote Execution). С дефолтным loopback-адресом multicast от node-клиента **не сходится** с редактором, тулы не отвечают. На Windows ставить именно `0.0.0.0`.
- **Редактор UE должен быть открыт и ПОЛНОСТЬЮ загружен ДО старта `claude`.** Если проект ещё грузится / редактор не поднят — MCP-сервер `unreal` стартует и сразу падает (`exit → ✗ Failed to connect`), тулы в сессию не попадают. Порядок: сначала открыть проект в UE и дождаться полной загрузки, затем запускать `claude`.
- Привязка к агенту: `unreal-operator` через `mcpServers: [unreal]` (только он видит `mcp__unreal__*`, по правилу из CLAUDE.md).
- Сторона UE: проект открыт в редакторе, **Python Editor Script Plugin** + **Enable Remote Execution** включены; к редактору подключается один клиент.
- **Предусловие рантайма:** серверу нужен **Node.js**. 2026-06-06 установлен `winget install OpenJS.NodeJS.LTS` → **node v24.16.0**, npm 11.13.0 (`C:\Program Files\nodejs`). Пакет `@runreal/unreal-mcp` существует (`npm view` → version 0.1.4).
**Статус: ПРОВАЛИДИРОВАН живыми вызовами** (2026-06-06, смоук-тест в сессии). Поднялось **20 тулзов `mcp__unreal__*`**. `editor_project_info` → проект **ContrarySurvivor**, движок **UE 5.5.4** (`5.5.4-40574608+++UE5+Release-5.5`), **GAS + Enhanced Input** включены, 7233 ассета. Запись/чтение/удаление проверены: create+delete `SmokeTestCube` (outliner 5→6→5), `HighResShot` дал реальный PNG (визуально подтверждён Ринатом).
- **Рабочие квирки (проверено живыми вызовами):**
  - **Скриншоты:** рабочий рецепт постоянного снимка — **окно UE в фокусе** → `editor_console_command HighResShot <WxH>` → файл в `<ProjectDir>/Saved/Screenshots/WindowsEditor/`. Без фокуса high-res пайплайн **не тикает** и не завершается (`is_task_done()` висит). `editor_take_screenshot` рендерит корректно, но пишет в **эфемерный tmp** (harness удаляет до след. вызова) — для отдаваемых артефактов непригоден. SceneCapture2D из Python даёт **неосвещённый/чёрный** кадр — не использовать для скринов сцены.
  - **`get_unreal_project_path()` в обёртке возвращает «not set»** → путь брать из `editor_project_info` / `unreal.Paths` (либо разово выставить `set_unreal_project_path`). Реальный путь проекта: `E:/ContrarySurvior/ContrarySurvivor/`.
  - **`editor_get_world_outliner` отдаёт внутренние имена актёров, не labels** → для точечных операций резолвить label через Python либо удалять/искать по label (`editor_delete_object` по label работает).

## ADR-004 — concept-artist: навык canvas-design
Нативного коннектора-генератора изображений в реестре нет. Используем нативный навык canvas-design (png/pdf). Внешний генератор не вводим.
**Статус:** проводка навыка в Claude Code — на Фазе инструментов.

## ADR-005 — sound: коннектор Splice (Фаза расширения)
AI-генератора музыки нативного нет. Нативный коннектор Splice (prompt_to_stack, describe_a_sound, download_asset) — для SFX/сэмплов. Платный (подписка Splice). Оригинальная музыка — отдельный вопрос при необходимости.

## ADR-006 — Бэкап ассетов: нативный коннектор Google Drive
Нативный коннектор Google Drive подключён. Крупные ассеты бэкапятся через него.

## ADR-007 — cpp-dev / qa: Claude Code нативно
Код, git, сборка, тесты — через Claude Code (полный доступ к диску/bash). MCP не нужен.

## ADR-008 — Состав команды: расширение
База: game-lead + cpp-dev, unreal-operator, modeler-3d, concept-artist, qa. На Фазе расширения добавляются: game-designer, tech-artist, sound, плюс level-designer и ui-ux-designer (жанру top-down survival + RPG критичны зоны/лут и тяжёлый UI). narrative пока вложен в game-designer; аналитик отложен (нет прод-игры).

## ADR-009 — Платформы: Android (слабые устройства), iOS отложен
Цель — ПК + Android с прицелом на слабые устройства. iOS отложен. Точные min-spec — `game-lead` берёт из диздока на Фазе подключения проекта.

## ADR-010 — Делегирование: game-lead без ограничений
`game-lead` имеет `tools: Agent` без аллоулиста — может звать любого специалиста. Эффективная глубина делегирования = 1 уровень (ограничение субагентов). Параллелизм ≤3 — процессное правило.

## ADR-011 — Blender: рабочие нюансы (один клиент на сокет, output_path у render_viewport)
Эксплуатационные правила для сервера blender-mcp из [ADR-002](#adr-002--modeler-3d-blender-через-официальный-сервер-blender-mcp-cli-уровень):
- **Один клиент на сокет 9876.** Desktop-коннектор Blender держать **выключенным**: к аддону Blender Lab подключается один клиент. CLI-сервер `blender` и Desktop-коннектор одновременно на `localhost:9876` конфликтуют — оставляем только CLI-проводку.
- **`render_viewport_to_path` игнорирует `output_path`.** Инструмент пишет PNG в свой серверный temp (вида `…\AppData\Local\Temp\blender_*\blender_mcp\…`) и возвращает фактический путь в `filepath`; переданный `output_path` на место записи не влияет. **После рендера копировать из возвращённого `filepath` в целевую папку проекта** и подтверждать наличие файла там (протокол B). Проверено: рендер сцены `Scene` 1920×1080 → temp, скопирован в `E:\game-dev-team\logs\blender_viewport.png` (1 151 657 байт).

## ADR-012 — unreal-operator: автономный скриншот без фокуса окна (take_high_res_screenshot)
Рабочий рецепт **автономного** снимка редактора UE 5.5 **без вывода окна в фокус и без кликов** — для отдаваемых артефактов. Уточняет/дополняет квирк «Скриншоты» из [ADR-003](#adr-003--unreal-operator-mcp-сервер-runrealunreal-mcp-ue-pythonremote-execution-под-капотом): рецепт с `HighResShot`+фокус остаётся валидным для ручного снимка, ниже — автономная альтернатива.

**Рецепт (проверен живыми вызовами 2026-06-07):**
1. Через `editor_run_python` вызвать `unreal.AutomationLibrary.take_high_res_screenshot(W, H, out)`, где `out` — **постоянный** путь (напр. `<ProjectSavedDir>/Screenshots/WindowsEditor/auto_shot.png`, папку создать `os.makedirs(..., exist_ok=True)`).
2. Готовность проверять **по факту записи файла**: `os.path.exists(p)` + `os.path.getsize(p)` через `editor_run_python`. Файл пишется отложенно (по завершении кадра), обычно ~3–5 с; при NOT_YET — подождать и перепроверить.
3. **НЕ использовать `editor_take_screenshot`** — рендерит в эфемерный tmp, который harness удаляет до следующего вызова (для отдаваемого артефакта непригоден).
4. **НЕ использовать `HighResShot`** для автономного режима — high-res пайплайн требует фокуса окна, без фокуса не тикает и `is_task_done()` висит.

**Обязательное предусловие (иначе файл не запишется):**
- Настройка редактора **"Use Less CPU when in Background" = OFF** (троттлинг CPU в фоне выключен).
- Окно редактора **открыто и НЕ свёрнуто** (свёрнутое/троттлящее окно не тикает кадры → `take_high_res_screenshot` ставит запрос в очередь, но PNG не пишется).

**Доказательство (протокол B):** 1-й прогон 2026-06-07 при включённом троттлинге → `NOT_YET` (файл не появился за ~6 с). После OFF + развёрнутого окна — повтор тех же шагов → `OK`, `E:/ContrarySurvior/ContrarySurvivor/Saved/Screenshots/WindowsEditor/auto_shot.png`, **1 594 187 байт** (подтверждён `os.path.getsize`).

**Ограничение: предусловие машинное, не проектное — в репо не попадает.**
- "Use Less CPU when in Background" — это ключ `bThrottleCPUWhenNotForeground` в секции `[/Script/UnrealEd.EditorPerformanceSettings]` (класс `UEditorPerformanceSettings`, модуль `UnrealEd`).
- Хранится в **per-user/машинном** файле `%LOCALAPPDATA%\UnrealEngine\5.5\Saved\Config\WindowsEditor\EditorSettings.ini` (фактически найдено: `C:\Users\pgr40\AppData\Local\UnrealEngine\5.5\Saved\Config\WindowsEditor\EditorSettings.ini`, строка `bThrottleCPUWhenNotForeground=False`).
- В конфигах **проекта** (`E:/ContrarySurvior/ContrarySurvivor/Saved/Config/**`, `.../Config/**`) ключа **нет** (рекурсивный поиск — пусто). Значит **в систему контроля версий не попадает** и на другой машине/у другого пользователя его нужно **выставлять заново вручную** (Editor Preferences → General → Performance → снять «Use Less CPU when in Background»).
- Гипотеза для переноса в репо (НЕ проверено, требует дизайн-решения): значение потенциально можно зафиксировать на уровне проекта через `Config/DefaultEditorPerProjectUserSettings.ini` с той же секцией/ключом — такого файла в репо сейчас нет. Применять только после живой проверки, что project-default перебивает per-user значение.

## ADR-013 — ContrarySurvivor: риск дрейфа AFS SecurityToken в публичном репо (follow-up отложен)
Контекст: проектные `Config/*.ini` репозитория **ContrarySurvivor** (`github.com/RenchezLove/ContrarySurvivor`, **публичный**) заведены под VCS, чтобы зафиксировать настройки runreal MCP (`bRemoteExecution=True`, `RemoteExecutionMulticastBindAddress=0.0.0.0`). При этом в `Config/DefaultEngine.ini`, секция `[/Script/AndroidFileServerEditor.AndroidFileServerRuntimeSettings]`, лежал dev-токен `SecurityToken` (плагин **Android File Server**, AFS). Перед первым трекингом значение обнулено (`SecurityToken=`) — в git-историю реальный токен **не попадал** (коммит `f7542ad`); сквозной скан остальных `Config/*.ini` секретов не нашёл.

**Решение (правило):** секрет в репозиторий не кладём — независимо от публичности репо. Это не разовая мера, а постоянное правило для проектных конфигов под VCS.

**Остаточный риск (контингентный):** файл `Config/DefaultEngine.ini` теперь трекается. Если AFS-плагин активно используется, UE может **локально перегенерировать** `SecurityToken` → появится непустое значение, которое легко случайно закоммитить и запушить в публичный репо.

**Рассмотренные варианты защиты:**
- **(a) `git update-index --skip-worktree Config/DefaultEngine.ini` — ОТКЛОНЁН.** Обоснование: флаг локальный, **не переезжает на другую машину** (на ноуте защиты не будет), и **прячет легитимные правки** настроек этого файла (риск незаметно потерять/проглядеть нужное изменение конфигурации).
- **(b) Вынести AFS-секцию/токен в per-user конфиг вне VCS**, в проектном `DefaultEngine.ini` оставить только Python Remote Execution + multicast. Структурно чисто, но требует правки и живой проверки, что AFS подхватывает per-user.
- **(c) Отключить плагин AFS**, если Android File Server в разработке не используется — тогда токен не генерируется и проблема снимается в корне.

**Статус: follow-up отложен.** Внедрять защиту сейчас НЕ требуется — на момент решения `Config/*.ini` чисты (скан 2026-06-07: реальных секретов нет, AFS-токен в HEAD пуст), риск лишь контингентный. Выбор между **(b)** и **(c)** зависит от факта: **использует ли Ринат Android File Server** в рабочем процессе. Решение по этому факту — за Ринатом; до него фикс не внедряем. Если AFS не нужен — приоритет (c); если нужен — (b).
