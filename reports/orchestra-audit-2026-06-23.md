# Технический аудит оркестра game-dev-team

> **Дата:** 2026-06-23 · **Аудитор:** game-lead · **Цель:** оценка возможности переноса оркестра с Claude Code на OpenAI Agents SDK.
> **Метод:** прочитаны реальные файлы конфигурации, определения агентов, хуки, MCP-пакеты на диске (анти-галл. протокол: каждый факт — из артефакта; оценки помечены явно).
> **Калибровка:** разделы 1–9 — ПРОВЕРЕНО по файлам репозитория `E:/game-dev-team`. Раздел 10 — ОЦЕНКА (миграция); конкретный API OpenAI Agents SDK перед реализацией обязательно сверить с актуальной докой OpenAI — в этой сессии доку SDK я не открывал.

---

## 1. Архитектура

### Список агентов (6 активных; определения — `.claude/agents/*.md`)

| Агент | Файл | Роль |
| --- | --- | --- |
| `game-lead` | `.claude/agents/game-lead.md` | Руководитель. Главная сессия (`claude --agent game-lead`). Принимает задачу от Рината, декомпозирует, делегирует, синтезирует, держит интеграцию/мерж, эскалирует. |
| `cpp-dev` | `.claude/agents/cpp-dev.md` | C++ программист UE 5.5. Игровой код, движковый код, интеграция C++↔Blueprints, доказательство компиляции. |
| `unreal-operator` | `.claude/agents/unreal-operator.md` | Оператор UE 5.5. Сцены, ассеты, Blueprints, настройки проекта, сборка/упаковка (ПК/Android). |
| `modeler-3d` | `.claude/agents/modeler-3d.md` | 3D-моделлер. Blender: моделирование, ретопология, UV, материалы, анимации, экспорт в UE. |
| `concept-artist` | `.claude/agents/concept-artist.md` | Концепт-художник. Палитры/типосистемы, UI-макеты (HUD/меню), арт-дирекшн, текстовые спек-листы на ассеты. Визуал — code-render (HTML/CSS+SVG→PNG/PDF). |
| `qa` | `.claude/agents/qa.md` | Тестирование, прогон сборки/тестов UE, мерж-гейт. Подтверждает фичу только реальным артефактом. |

Запланированы (ADR-008, ещё не созданы): `game-designer`, `tech-artist`, `sound`, `level-designer`, `ui-ux-designer`.

### Подчинение и делегирование

- **Дерево плоское, глубина делегирования = 1** (ADR-001, ADR-010). `game-lead` — корень-главная-сессия. Все 5 специалистов — терминальные листья.
- **Субагент НЕ может порождать субагента** (ограничение Claude Code, подтверждено по code.claude.com/docs). Если подзадача требует другого специалиста — специалист возвращает результат `game-lead`, тот делегирует дальше.
- **Параллелизм ≤3** одновременно (процессное правило, чтобы не раздувать контекст).
- Делегирование делает только `game-lead` инструментом `Agent`; межагентная коммуникация — `SendMessage` (имена напарников по роли: `cpp`, `unreal`, `modeler`, `concept`, `qa`).

### Схема делегирования

```
                 Ринат (пользователь)
                        │  задача / приёмка / эскалация
                        ▼
   ┌─────────────────────────────────────────────┐
   │  game-lead  (главная сессия, claude --agent) │
   │  декомпозиция · делегирование · синтез · мерж│
   └─────────────────────────────────────────────┘
        │ Agent (spawn ≤3 || )      ▲ SendMessage (результат + пруф)
        ▼                           │
   ┌──────────┬───────────────┬──────────────┬────────────────┬──────────┐
   │ cpp-dev  │ unreal-operator│ modeler-3d   │ concept-artist │   qa     │
   │ C++/build│ UE editor/MCP  │ Blender/MCP  │ code-render    │ build/   │
   │          │                │              │                │ merge-gate│
   └──────────┴───────────────┴──────────────┴────────────────┴──────────┘
                        │ qa-гейт (PASS+артефакт) → game-lead создаёт .claude/QA_OK → merge в master
```

---

## 2. Промпты

Системный промпт каждого агента = тело его `.md`-файла после YAML-frontmatter. Дополнительно в контекст КАЖДОГО агента грузится `CLAUDE.md` (корневой, project-instructions). Файлы контекста агенты подгружают по правилу bootstrap (только нужный срез), не постоянно.

Общие подключаемые файлы контекста (для всех):
- `CLAUDE.md` — грузится автоматически (правила, GATE, анти-галл. протокол, bootstrap).
- `context/_shared.md` — стек, конвенции, зоны ответственности.
- `context/<agent>/context.md` — личная живая память (блок «🧭 СЕЙЧАС»).
- `context/<agent>/archive.md` — прошлое (read-on-demand).
- `docs/decisions.md` — ADR (по запросу).
- `docs/contrary-survivor/*` — дизайн-правда (по запросу, по активной фазе).

### 2.1 game-lead
- **Путь:** `.claude/agents/game-lead.md`
- **Frontmatter:** `tools: Agent, SendMessage, Read, Write, Edit, Glob, Grep, Bash, mcp__unreal__*` · `mcpServers: [unreal]` · `model: inherit`
- **Контекст:** `CLAUDE.md`, `context/_shared.md`, `context/game-lead/context.md`, `context/game-lead/archive.md`, `docs/decisions.md`, `docs/contrary-survivor/*` (по запросу).
- **Полный текст промпта:**

> Ты — `game-lead`, руководитель команды ИИ-разработчиков игр. Работаешь как главная сессия и можешь вызывать любого специалиста через инструмент Agent.
> Команда: `cpp-dev`, `unreal-operator`, `modeler-3d`, `concept-artist`, `qa` (позже добавятся game-designer, tech-artist, sound, level-designer, ui-ux-designer).
> **Цикл работы:** 1) Прими задачу от Рината; если неоднозначна/затрагивает дизайн, которого нет в источнике истины — задай вопрос ДО делегирования. 2) Декомпозируй по зонам ответственности (`context/_shared.md`). 3) Делегируй ≤3 специалистам параллельно, цитируя формулировку из источника истины. 4) Получив результаты, проверь доказательство (лог сборки/теста, путь, git); без доказательства — возвращай. 5) Синтезируй; перед интеграцией прогони через `qa`. 6) Отчитайся Ринату; нерешённые/дизайнерские вопросы — эскалируй.
> **Правила:** субагенты не зовут субагентов (дерево плоское); диздок — единственный источник истины, грузишь по запросу; соблюдай анти-галл. протокол из `CLAUDE.md`; нативное первым; ADR в `docs/decisions.md`, дистилляция в `context/game-lead/context.md`.

### 2.2 cpp-dev
- **Путь:** `.claude/agents/cpp-dev.md`
- **Frontmatter:** `tools: SendMessage, Read, Write, Edit, Glob, Grep, Bash` · `model: inherit`
- **Контекст:** `CLAUDE.md`, `context/_shared.md`, `context/cpp-dev/context.md`, `context/cpp-dev/archive.md`, исходники UE-проекта (по запросу).
- **Полный текст промпта:**

> Ты — `cpp-dev`, C++ программист команды. Стек: UE 5.5, C++ через Visual Studio 2022 (Game Dev C++), интеграция с Blueprints. Подробности — `context/_shared.md`.
> **Как работаешь:** 1) Перед правкой прочитай реальные файлы. 2) API/классы/макросы/узлы используй, только подтвердив, что они есть **именно в UE 5.5**. 3) Чистый код по конвенциям UE (UPROPERTY/UFUNCTION, naming, модульность). 4) **Доказательство компиляции обязательно** — «собирается» только после реальной сборки с логом. 5) Не выдумывай пути/классы/плагины. 6) Дизайнерские вопросы эскалируй `game-lead`.
> Возвращай `game-lead`: что изменено (пути), лог сборки, что проверено, допущения. Дистилляция — `context/cpp-dev/context.md`.

### 2.3 unreal-operator
- **Путь:** `.claude/agents/unreal-operator.md`
- **Frontmatter:** `tools: SendMessage, Read, Write, Edit, Glob, Grep, Bash, mcp__unreal__*` · `mcpServers: [unreal]` · `model: inherit`
- **Контекст:** `CLAUDE.md`, `context/_shared.md`, `context/unreal-operator/context.md`, ADR-003/011/012/021 (`docs/decisions.md`), реальное состояние UE-проекта (по запросу).
- **Полный текст промпта:**

> Ты — `unreal-operator`, оператор Unreal Engine 5.5. Зона: сцены, ассеты, Blueprints, настройки проекта, сборка/упаковка под ПК и Android.
> **Механизм:** приоритет — программный путь UE Python API / Remote Control (надёжнее GUI на Windows); Computer Use — крайний случай. До проводки инструмента формируешь точные исполнимые артефакты (UE Python-скрипты, пошаговые инструкции) и отдаёшь `game-lead`.
> **Правила:** 1) Узлы/классы/ассеты/плагины — только подтвердив, что есть в UE 5.5 и в реальном проекте. 2) Перед изменением — прочитай реальное состояние. 3) «Собралось/упаковалось» — только с логом. 4) Дизайнерские вопросы эскалируй.
> **Скриншоты — автономный режим (ADR-012):** `editor_run_python` → `unreal.AutomationLibrary.take_high_res_screenshot(W,H,out)` в постоянный путь; готовность по `os.path.exists`+`getsize`; НЕ `editor_take_screenshot` (эфемерный tmp), НЕ `HighResShot` для автономного; предусловие «Use Less CPU when in Background = OFF» и окно не свёрнуто.
> Возвращай `game-lead`: что сделано, скрипт/шаги, лог, доказательства, допущения. Дистилляция — `context/unreal-operator/context.md`.

### 2.4 modeler-3d
- **Путь:** `.claude/agents/modeler-3d.md`
- **Frontmatter:** `tools: SendMessage, Read, Write, Edit, Glob, Grep, Bash, mcp__blender__*` · `mcpServers: [blender]` · `model: inherit`
- **Контекст:** `CLAUDE.md`, `context/_shared.md`, `context/modeler-3d/context.md`, ADR-002/011/022 (`docs/decisions.md`), спек-листы от concept-artist (по запросу).
- **Полный текст промпта:**

> Ты — `modeler-3d`, 3D-моделлер команды. Инструмент — нативный коннектор Blender. Зона: моделирование, ретопология, UV, материалы, анимации, экспорт в UE (FBX/glTF).
> **Правила:** 1) Работай от ТЗ на ассет (от `concept-artist`/`game-lead`); визуальный стиль — из источника истины, не изобретай. 2) Перед правкой проверь реальное состояние файла/сцены. 3) Бюджет под платформу (слабый Android): полигонаж, текстуры, материалы; лимиты из постановки, нет — спроси. 4) «Экспортировано/готово» — только после реального экспорта с проверкой файла на диске. 5) Крупные ассеты — бэкап на Google Drive.
> Возвращай `game-lead`: что смоделировано, пути, параметры (поликаунт/текстуры), доказательства экспорта, допущения. Дистилляция — `context/modeler-3d/context.md`.

### 2.5 concept-artist
- **Путь:** `.claude/agents/concept-artist.md`
- **Frontmatter:** `tools: SendMessage, Read, Write, Edit, Glob, Grep, Bash, Skill` · `model: inherit` *(MCP не подключён)*
- **Контекст:** `CLAUDE.md`, `context/_shared.md`, `context/concept-artist/context.md`, ADR-004, диздок (по запросу).
- **Полный текст промпта (сжато — самый длинный файл):**

> Ты — `concept-artist`. **Скоуп (ADR-004):** (1) палитры/цвето- и типосистемы (HTML/CSS+SVG→PNG/PDF); (2) UI-макеты HUD/меню на HTML/CSS; (3) письменная арт-дирекшн (.md); (4) текстовые спек-листы на ассет для modeler-3d.
> **Граница инструмента:** фигуративный/живописный концепт-арт нативным тулсетом НЕ закрывается (нет генератора изображений) — не имитировать code-render'ом, эскалировать `game-lead`. Силуэты/блокауты/градиент-мудборды — вне скоупа.
> **Инструмент визуала — нативный code-render:** HTML/CSS+инлайн SVG → PNG через headless Edge: `msedge.exe --headless=new --disable-gpu --hide-scrollbars --no-sandbox --window-size=W,H --screenshot="ABS\OUT.png" "file:///ABS/PATH.html"`; PDF — `--print-to-pdf`. Python/Pillow на машине НЕТ; Node v24 есть (puppeteer/sharp — запас). **Протокол B:** после рендера подтверждай файл `ls -l` (путь+размер).
> **Правила:** стиль/лор — из источника истины; варианты на отбор `game-lead`, финал у Рината через `game-lead`; статусы черновик/на отбор/утверждено; только фича-ветка. Дистилляция — `context/concept-artist/context.md`.

### 2.6 qa
- **Путь:** `.claude/agents/qa.md`
- **Frontmatter:** `tools: SendMessage, Read, Glob, Grep, Bash` · `model: inherit` *(нет Write/Edit — только чтение+запуск)*
- **Контекст:** `CLAUDE.md`, `context/_shared.md`, `context/qa/context.md`.
- **Полный текст промпта:**

> Ты — `qa`, тестировщик и мерж-гейт команды. Только чтение кода + запуск сборки/тестов через bash; код не правишь.
> **Что делаешь:** 1) Прогон сборки и тестов по постановке. 2) Проверка фичи против критериев. 3) Мерж-гейт: «зелёный» только если сборка и тесты реально прошли.
> **Правила (жёстко):** никогда не подтверждай фичу без фактического артефакта (лог/результат теста); «тесты прошли» — только после реального прогона с выводом; отрицательный результат — граница проверки; нашёл проблему — опиши (что/где/стектрейс/repro), возвращай `game-lead`, не чини сам.
> Вердикт: PASS/FAIL + доказательства. Дистилляция — `context/qa/context.md`.

---

## 3. Инструменты по агентам

Типы: **built-in** (встроенные инструменты Claude Code), **MCP** (через MCP-сервер), **delegation/coordination** (управление командой). Кастомных собственных инструментов-плагинов в репо НЕТ — «кастомные» возможности реализованы через `Bash` + внешние CLI (Edge headless, UnrealEditor-Cmd, blender.exe).

| Инструмент | Тип | Класс | Назначение | У кого |
| --- | --- | --- | --- | --- |
| `Agent` | built-in | coordination | Спавн специалистов (делегирование) | game-lead |
| `SendMessage` | built-in | coordination | Сообщения между агентами | все |
| `Read` | built-in | файлы | Чтение файлов/изображений/PDF | все |
| `Write` | built-in | файлы | Запись файла | все, кроме qa |
| `Edit` | built-in | файлы | Точечная правка файла | все, кроме qa |
| `Glob` | built-in | поиск | Поиск файлов по маске | все |
| `Grep` | built-in | поиск | Поиск по содержимому (ripgrep) | все |
| `Bash` | built-in | оболочка | Запуск команд (git, сборка, CLI-тулзы) | все |
| `Skill` | built-in | навыки | Вызов навыка (фактически не задействован — ADR-004) | concept-artist |
| `mcp__unreal__*` | MCP | UE-сервер | 20 тулзов редактора UE (см. §4) | game-lead, unreal-operator |
| `mcp__blender__*` | MCP | Blender-сервер | 20 тулзов Blender (см. §4) | modeler-3d |

Примечания (проверено):
- **game-lead** имеет `mcp__unreal__*` в frontmatter, но в живых сессиях инжекция MCP-тулзов в teammate-сессии флакки (см. §5 и `context/game-lead/context.md`).
- **qa** намеренно без `Write/Edit` — не правит код, только читает и запускает.
- **concept-artist** не имеет MCP; визуал — через `Bash`+Edge headless.
- В `settings.local.json` явно разрешён лишь ПОДНАБОР MCP-тулзов (для blender — 4: `get_objects_summary`, `get_object_detail_summary`, `execute_blender_code`, `render_viewport_to_path`; для unreal — 10 конкретных + `get_unreal_engine_path`), но frontmatter даёт wildcard `*`.

---

## 4. MCP-серверы

Конфигурация — `.mcp.json` (project scope), включение — `settings.local.json` → `enabledMcpjsonServers: ["blender", "unreal"]`. Привязка к агентам — через `mcpServers:` во frontmatter.

### 4.1 MCP `blender`
- **Название:** `blender` (пакет `blender-mcp` / модуль `blmcp` **v1.0.0**, Blender Lab; + `mcp` 1.27.2).
- **Способ запуска:** `stdio`, бинарь `C:\Users\pgr40\.local\bin\blender-mcp.exe` (установлен `uv tool install`, uv 0.11.17). Код — `C:\Users\pgr40\AppData\Roaming\uv\tools\blender-mcp\Lib\site-packages\blmcp`.
- **Конфигурация (`.mcp.json`):**
  ```json
  "blender": { "type": "stdio", "command": "C:\\Users\\pgr40\\.local\\bin\\blender-mcp.exe", "args": [], "env": {} }
  ```
- **Сторона Blender:** аддон Blender Lab v1.0.0, слушает `localhost:9876`, auto-start. **Один клиент на сокет** (ADR-011) — Desktop-коннектор держать выключенным.
- **Доступные инструменты (20, проверено по `blmcp/tools/*.py`):** `execute_blender_code`, `get_objects_summary`, `get_object_detail_summary`, `get_blendfile_summary_datablocks`, `get_blendfile_summary_missing_files`, `get_blendfile_summary_of_linked_libraries`, `get_blendfile_summary_path_info`, `get_blendfile_summary_usage_guess`, `get_python_api_docs`, `search_api_docs`, `search_manual_docs`, `get_screenshot_of_area_as_image`, `get_screenshot_of_window_as_image`, `get_screenshot_of_window_as_json`, `jump_to_tab_by_name`, `jump_to_tab_by_space_type`, `jump_to_view3d_object_by_name`, `jump_to_view3d_object_data_by_name`, `render_thumbnail_to_path`, `render_viewport_to_path`.
- **Использует:** `modeler-3d` (исключительно — правило CLAUDE.md).

### 4.2 MCP `unreal`
- **Название:** `unreal` (пакет `@runreal/unreal-mcp` **v0.1.4**).
- **Способ запуска:** `stdio` через абсолютный путь к Node (ADR-003, не голый `npx`): `node.exe` + `dist/bin.js` пакета.
- **Конфигурация (`.mcp.json`):**
  ```json
  "unreal": { "type": "stdio",
    "command": "C:\\Program Files\\nodejs\\node.exe",
    "args": ["C:\\Users\\pgr40\\AppData\\Roaming\\npm\\node_modules\\@runreal\\unreal-mcp\\dist\\bin.js"],
    "env": {} }
  ```
- **Сторона UE:** проект открыт в редакторе ДО старта claude; Python Editor Script Plugin + Enable Remote Execution; **Multicast Bind Address = `0.0.0.0`**; канал — UE Python Remote Execution (multicast 239.0.0.1:6766).
- **Доступные инструменты (20, проверено по `dist/index.js`):** `set_unreal_engine_path`, `get_unreal_engine_path`, `set_unreal_project_path`, `get_unreal_project_path`, `editor_run_python`, `editor_list_assets`, `editor_export_asset`, `editor_get_asset_info`, `editor_get_asset_references`, `editor_console_command`, `editor_project_info`, `editor_get_map_info`, `editor_search_assets`, `editor_get_world_outliner`, `editor_validate_assets`, `editor_create_object`, `editor_update_object`, `editor_delete_object`, `editor_take_screenshot`, `editor_move_camera`.
- **Использует:** `unreal-operator` (основной), `game-lead` (frontmatter; инжекция флакки — §5).

---

## 5. Unreal Engine

Проект игры — **отдельный репозиторий** `E:/ContrarySurvior/ContrarySurvivor/` (UE 5.5.4, GAS+Enhanced Input, ~7233 ассета). Оркестр взаимодействует с ним так:

- **MCP — ДА.** Сервер `@runreal/unreal-mcp` (см. §4.2). 20 тулзов `mcp__unreal__*`.
- **Python API — ДА, два пути:**
  1. **Live MCP:** `editor_run_python` исполняет `unreal`-Python в открытом редакторе (Remote Execution).
  2. **Headless (ADR-021):** `UnrealEditor-Cmd.exe "<uproject>" -ExecutePythonScript="<abs.py>" -unattended -nopause -nosplash` — работает с ЗАКРЫТЫМ редактором, MCP не нужен. Нюанс: stdout пуст на Windows → пруф из `Saved/Logs/<Project>.log`.
- **Editor Utility (EUW/EUB) — НЕ используется как отдельный механизм.** Всё через Python (live или headless) + Remote Execution. Явных Editor Utility Widget/Blueprint в пайплайне оркестра нет.
- **Удалённое управление — ДА.** UE Python **Remote Execution** (multicast `239.0.0.1:6766`, bind `0.0.0.0`) — транспорт MCP-канала. Полноценный Remote Control API (HTTP/WebSocket) отдельно не заведён.
- **Сборка проекта:** через `Bash` + `Build.bat`/`Rebuild.bat`/`Clean.bat` UBT (`E:\UnrealEngine\UE_5.5\...\BatchFiles\`), лог в `logs/` (cpp-dev/qa).
- **Computer Use — крайний случай** (только если программного пути нет).

**Список доступных действий (через MCP-тулзы + Python):** запуск произвольного Python в редакторе; листинг/поиск/инфо/референсы/валидация/экспорт ассетов; инфо о проекте и карте; чтение World Outliner; создание/обновление/удаление объектов на сцене; консольные команды; перемещение камеры; скриншоты (эфемерный и автономный high-res через `take_high_res_screenshot`); импорт FBX (static/skeletal/anim) через Interchange (headless); сборка/ребилд проекта (UBT). 

**Известный блокер (ПРОВЕРЕНО, открыт):** инжекция `mcp__unreal__*` в teammate-сессии нестабильна — сервер коннектится к процессу (`hasTools:true` в mcp-логе), но тулзы не пробрасываются в субагента; в части сессий `unreal-operator` получал только `{SendMessage,Read,Write,Edit,Glob,Grep,Bash}`. Гипотеза (НЕ ПРОВЕРЕНО) — связано с `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. Поэтому headless-коммандлет (ADR-021) — основной надёжный путь для детерминированных ассет-операций.

---

## 6. Blender

- **MCP — ДА.** Сервер `blender-mcp`/`blmcp` v1.0.0 (см. §4.1), сокет `localhost:9876`, аддон Blender Lab.
- **Blender Python API (`bpy`) — ДА, два пути:**
  1. **Live MCP:** тул `execute_blender_code` исполняет `bpy`-код в подключённом Blender. Приоритет — специализированные тулзы (`get_objects_summary` и т.д.), `execute_blender_code` — крайний случай (по инструкции сервера).
  2. **Headless CLI (аналог ADR-021):** `blender.exe -b --factory-startup --python <script.py>` — MCP-независимый путь (упомянут в ADR-021).
- **Доступные действия:** инспекция сцены (сводка объектов, детали объекта), сводки blend-файла (датаблоки, missing-files, линкованные библиотеки, инфо путей, usage-guess), исполнение произвольного `bpy`-кода, скриншоты области/окна (image/json), навигация по табам/вьюпорту, рендер вьюпорта/тумбочки в файл, поиск по bundled API-докам и user-manual (`data/api`, `data/manual`). Моделирование/ретопология/UV/материалы/анимация/экспорт FBX-glTF — реализуются через `execute_blender_code`/headless.
- **Нюанс (ADR-011):** `render_viewport_to_path` игнорирует `output_path` — пишет в серверный temp и возвращает фактический `filepath`; нужно копировать в целевую папку и подтверждать (протокол B).
- **Только `modeler-3d`** обращается к Blender; не спавнить двух экземпляров (один клиент на сокет).

---

## 7. Память

Модель памяти — файловая, Markdown, по слоям (CLAUDE.md задаёт дисциплину). Conversation-память сессии ведёт сам Claude Code; долговременная — в файлах репо.

| Агент | Отдельная память | Где | Формат | Объём (факт, `wc`) |
| --- | --- | --- | --- | --- |
| game-lead | да (+архив) | `context/game-lead/context.md` · `archive.md` | Markdown (блок «🧭 СЕЙЧАС» + история) | 63 стр / 19.6 КБ · архив 462 стр / 129 КБ |
| cpp-dev | да (+архив) | `context/cpp-dev/context.md` · `archive.md` | Markdown | 60 стр / 9.2 КБ · архив 389 стр / 145 КБ |
| unreal-operator | да | `context/unreal-operator/context.md` | Markdown | 107 стр / 45.9 КБ |
| modeler-3d | да | `context/modeler-3d/context.md` | Markdown | 169 стр / 55.8 КБ ⚠️ >150 стр (нужна чистка по СТОП-правилу) |
| concept-artist | да | `context/concept-artist/context.md` | Markdown | 34 стр / 7.1 КБ |
| qa | да | `context/qa/context.md` | Markdown | 10 стр / 0.58 КБ |

Общие/разделяемые слои памяти (единый источник на тип, не дублировать — CLAUDE.md):
- **Живая память агента:** `context/<agent>/context.md` (блок «🧭 СЕЙЧАС» ≤30 строк + директивы + текущая задача).
- **Прошлое:** `context/<agent>/archive.md` (read-on-demand, не в bootstrap).
- **Ключевые решения:** `docs/decisions.md` (24 ADR).
- **Общий слой:** `context/_shared.md` (43 стр / 4.3 КБ).
- **Корневые правила/протокол:** `CLAUDE.md` (≈19.5 КБ, грузится всем автоматически).
- **Дизайн-правда:** `docs/contrary-survivor/` (GDD, roadmap, tech-design, demo-plan и т.д.).
- **Полная история:** git.
- **Объём контекстного окна** — модель `inherit` (наследуется от модели сессии Claude Code); конкретное число токенов в репо не фиксировано, управляется дисциплиной bootstrap/дистилляции (правило H), а не настройкой.

---

## 8. Конфигурация

### Структура папок оркестра (репо `E:/game-dev-team`, отдельно от гейм-репо)
```
game-dev-team/
├── CLAUDE.md                      # корневые правила, GATE, анти-галл. протокол, bootstrap
├── .mcp.json                      # MCP-серверы (blender, unreal)
├── .gitattributes / .gitignore    # (QA_OK и settings.local.json — в ignore)
├── .claude/
│   ├── agents/*.md                # 6 определений агентов (frontmatter + промпт)
│   ├── hooks/*.ps1                # PowerShell-хуки (gate/protect/selfheal) + gate-inject.log
│   ├── settings.json              # env, permissions, hooks (в git)
│   └── settings.local.json        # allow-лист, enabledMcpjsonServers (НЕ в git)
├── .githooks/                     # git-native гейт: pre-push, pre-merge-commit (+ .ps1, README)
├── context/
│   ├── _shared.md                 # общий слой
│   ├── ARCHIVE-INDEX.md
│   ├── <agent>/context.md|archive.md   # память агентов
│   └── BugReports/                # скриншоты-баг-репорты от Рината
├── docs/
│   ├── architecture.md · decisions.md · ai-team-playbook.md
│   └── contrary-survivor/         # GDD, roadmap, tech-design, demo-plan, asset-contract …
├── assets/                        # каталог ассетов (ADR-022): <id>/{.blend,.png,.asset.md}, index.html
├── concept-art/                   # стайл-шиты concept-artist (html/png/pdf/md)
├── logs/ · renders/ · reports/ · backups/ · Screenshots/ · tmp/
```

### Основные конфигурационные файлы
- **`.claude/settings.json`** (в git): `env.CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`; `permissions.defaultMode=acceptEdits`, `additionalDirectories=[E:/ContrarySurvior/ContrarySurvivor]`, allow/deny-листы, `disableBypassPermissionsMode=disable`; блок `hooks` (см. ниже).
- **`.claude/settings.local.json`** (НЕ в git): расширенный allow-лист конкретных команд + `enabledMcpjsonServers:[blender,unreal]`.
- **`.mcp.json`**: 2 stdio-сервера.
- **`.claude/agents/*.md`**: агенты (роль, tools, mcpServers, model, промпт).
- **Хуки (`.claude/hooks/*.ps1`), все PowerShell:**
  - `inject-gate.ps1` — `UserPromptSubmit`: инъекция GATE-маяка в контекст каждого хода + лог-пруф.
  - `ensure-hookspath.ps1` — `SessionStart`(startup/resume)+`PreToolUse`(Bash|PowerShell): self-heal `core.hooksPath` → `.githooks` (worktree-спавн его сбивает).
  - `qa-gate.ps1` — `PreToolUse`(Bash|PowerShell): блок `git push`→master / `git merge`→master без маркера `.claude/QA_OK` (разбор по глаголу команды).
  - `protect-claude.ps1` — `PreToolUse`(Edit|Write|Bash|PowerShell): запрет субагенту писать в `.claude/**` и `.githooks/**` (детект по `agent_id`); карвут `.claude/QA_OK`.
- **`.githooks/`** (git-native, не зависят от Claude Code): `pre-push`, `pre-merge-commit` (+`.ps1`) — независимый слой защиты master.

### Зависимости (проверено: версии живые на машине)
| Компонент | Версия | Роль |
| --- | --- | --- |
| Claude Code CLI | (движок) | оркестратор, субагенты, хуки, MCP-клиент |
| Node.js | v24.16.0 | рантайм `@runreal/unreal-mcp`; запасной puppeteer/sharp |
| `@runreal/unreal-mcp` | 0.1.4 (npm global) | MCP-сервер UE |
| uv | 0.11.17 | установка/запуск blender-mcp |
| `blender-mcp`/`blmcp` | 1.0.0 (+ `mcp` 1.27.2) | MCP-сервер Blender |
| Blender + Blender Lab аддон | v1.0.0 | сторона Blender (сокет 9876) |
| Unreal Engine | 5.5.4 | целевой движок проекта |
| Visual Studio 2022 | Game Dev C++ | сборка C++ |
| Microsoft Edge (Chromium) | headless | code-render concept-artist |
| git / git-lfs | 2.52.0 / 3.7.1 | VCS; LFS для /Content гейм-репо (ADR-019) |
| PowerShell (Windows 5.1+) | — | все хуки |

---

## 9. Запуск

### Пошагово
1. **Поднять внешние сервисы ДО `claude`:**
   - Для UE-задач: открыть проект в **UE 5.5 редакторе и дождаться ПОЛНОЙ загрузки** (иначе MCP-сервер `unreal` стартует и сразу падает — ADR-003). Включены Python Remote Execution, bind `0.0.0.0`.
   - Для Blender-задач: запустить **Blender с аддоном Blender Lab** (сокет `localhost:9876`), Desktop-коннектор выключен.
2. **Старт главной сессии:** `claude --agent game-lead` в `E:/game-dev-team`.
3. **SessionStart-хук** `ensure-hookspath.ps1` чинит `core.hooksPath → .githooks`.
4. **Claude Code поднимает MCP-серверы** (stdio): `blender-mcp.exe`, `node dist/bin.js` (по `.mcp.json` + `enabledMcpjsonServers`).
5. **Bootstrap-грунтовка:** грузится `CLAUDE.md` + блок «🧭 СЕЙЧАС» памяти + нужный срез источника истины.
6. **Рабочий цикл:** Ринат ставит задачу → `game-lead` декомпозирует → `Agent` спавнит ≤3 специалистов (в worktree-ветках) → специалисты возвращают результат+пруф → `qa`-гейт → `game-lead` создаёт `.claude/QA_OK` → merge → удаляет маркер.
7. **На каждый ход** срабатывает `UserPromptSubmit` (инъекция GATE), на каждый Bash/Write — `PreToolUse` (selfheal + qa-gate + protect-claude).

### Какие процессы стартуют
- 1 процесс Claude Code (главная сессия) + дочерние субагент-сессии (teammates).
- 2 MCP-процесса (stdio): `blender-mcp.exe`, `node.exe (unreal-mcp)`.
- По требованию: `UnrealEditor-Cmd.exe` (headless), `UBT/Build.bat`, `msedge.exe --headless`, `blender.exe -b`.

### Обязательные сервисы
- **Всегда:** Claude Code CLI, git, PowerShell (хуки).
- **Под UE-задачи:** открытый и загруженный редактор UE 5.5 (для live-MCP) **или** UnrealEditor-Cmd (для headless) + Node.js.
- **Под Blender-задачи:** запущенный Blender с аддоном (сокет 9876) + uv/blender-mcp.
- **Под concept-art:** Microsoft Edge.

---

## 10. Миграция на OpenAI Agents SDK

> **Калибровка (важно):** ниже — ОЦЕНКА. Общая модель OpenAI Agents SDK (agents с `instructions`/`tools`/`model`, handoffs, function tools, guardrails, sessions, поддержка MCP-серверов) — по моим сведениям о фреймворке, но **конкретный API/версию обязательно сверить с актуальной докой OpenAI перед реализацией** (в этой сессии доку я не открывал → отдельные детали помечаю «НЕ ПРОВЕРЕНО»). Легенда: 🟢 без изменений · 🟡 адаптация · 🔴 замена.

| Компонент | Вердикт | Обоснование |
| --- | --- | --- |
| **MCP-серверы blender / unreal** | 🟢→🟡 | OpenAI Agents SDK поддерживает MCP (stdio) — серверы и их 40 тулзов переиспользуемы как есть. Адаптация — формат регистрации (вместо `.mcp.json`/`mcpServers:` — объекты MCP-сервера в коде SDK). НЕ ПРОВЕРЕНО: точный класс/способ привязки тула к агенту. |
| **Логика Unreal (Remote Exec, headless UnrealEditor-Cmd) и Blender (bpy, headless)** | 🟢 | OS-/движко-уровень, не зависит от фреймворка. Headless-коммандлеты и сокет Blender вызываются из любых function-tools без изменений. |
| **Системные промпты (тела `.md`)** | 🟡 | Текст переиспользуем по смыслу → переносится в `instructions=` агента. Адаптация: убрать Claude-Code-специфику (Agent/SendMessage/Skill, формулировки про субагентов), переписать ссылки на инструменты. |
| **Определения агентов (frontmatter)** | 🟡 | `name/description/model/tools` → конструктор `Agent(...)` в Python/JS. Семантика переносится, синтаксис — переписать. `model: inherit` → явная модель OpenAI. |
| **Делегирование (game-lead→специалисты)** | 🟡 | В OpenAI SDK — через **handoffs** или **agents-as-tools**. Плюс: ограничение «субагент не зовёт субагента» в OpenAI SDK **снимается** (handoffs многоуровневые) — архитектуру можно упростить/углубить. Переписать оркестрацию. |
| **Встроенные тулзы Read/Write/Edit/Glob/Grep/Bash** | 🔴 | Это инструменты Claude Code, в OpenAI SDK их НЕТ. Нужно реализовать как **custom function tools** (файловый IO, ripgrep-обёртка, shell-runner) с собственным контролем безопасности. Существенный объём. |
| **`Agent` / `SendMessage` / `Skill`** | 🔴 | Claude-Code-специфика. Заменяется механизмами SDK (handoffs/runner, общий стейт) и собственными тулзами. `Skill` фактически не использовался. |
| **Хуки `.claude/hooks/*.ps1` (gate/protect/selfheal/inject)** | 🔴 | Привязаны к событийной модели Claude Code (UserPromptSubmit/PreToolUse/SessionStart) и `agent_id`. Переписать на **guardrails / lifecycle-hooks** SDK + tool-wrappers. inject-gate → системная инструкция/guardrail; qa-gate/protect → input/tool guardrails. |
| **git-native гейт `.githooks/` (pre-push, pre-merge-commit)** | 🟢 | git-уровень, фреймворк-независим. Переносится без изменений (главный слой защиты master сохраняется). |
| **`settings.json` permissions (allow/deny, acceptEdits, additionalDirectories)** | 🔴 | Модель разрешений Claude Code. В OpenAI SDK аналога «из коробки» нет — реализовать в коде custom-тулзов (валидация путей, denylist, approve-логика). |
| **Память `context/*.md` + `CLAUDE.md` + `decisions.md`** | 🟢→🟡 | Файлы-данные (Markdown) переиспользуемы как есть. Адаптация — логика загрузки: автоподхват `CLAUDE.md` и bootstrap «СЕЙЧАС» в Claude Code надо **переписать** (грузить файлы в `instructions`/контекст вручную; для диалоговой памяти — **Sessions** SDK). |
| **MCP-инжекция в субагентов (текущий флакки-блокер)** | 🟢 (плюс миграции) | В OpenAI SDK привязка тулзов/MCP к агенту явная и детерминированная — текущий баг «тулзы не доходят до teammate» уходит. Потенциальный выигрыш надёжности. |
| **Концепт-арт (Edge headless), сборка UE (UBT), Blender-экспорт** | 🟢 | Внешние CLI; вызываются из function-tools без изменений. |
| **Запуск (`claude --agent game-lead`)** | 🔴 | Заменяется на Python/JS-скрипт-раннер (`Runner.run(...)`) с собственной точкой входа, циклом и оркестрацией. |

### Итог по миграции (оценка)
- **Переносится дёшево (🟢):** оба MCP-сервера и их 40 тулзов, все внешние CLI-интеграции (UnrealEditor-Cmd, bpy headless, UBT, Edge), git-native гейт, файлы памяти/ADR/диздок как данные.
- **Адаптация (🟡):** агенты и промпты (переписать в код SDK), оркестрация делегирования (handoffs/agents-as-tools — в т.ч. возможность убрать ограничение глубины), привязка MCP к агентам, логика загрузки памяти.
- **Замена/переписать с нуля (🔴):** весь слой инструментов файлов/оболочки (Read/Write/Edit/Glob/Grep/Bash) как custom function tools; вся система хуков и разрешений Claude Code → guardrails+собственные проверки; точка входа/раннер.
- **Главный риск/объём работ:** не модели и не MCP (там легко), а **воспроизведение «бесплатной» инфраструктуры Claude Code** — встроенных тулзов, permission-модели и событийных хуков. Это ядро трудозатрат миграции.
- **Перед реализацией обязательно (анти-галл.):** сверить с актуальной докой OpenAI Agents SDK классы Agent/Runner/handoffs/function_tool/guardrails/Sessions/MCP — детали API в этой сессии НЕ ПРОВЕРЕНЫ.

---

## Дерево файлов оркестра (конфиг/структура; обрезаны логи, баг-скрины, tmp)
```
game-dev-team/
├── CLAUDE.md
├── .mcp.json
├── .gitattributes
├── .gitignore
├── .claude/
│   ├── agents/
│   │   ├── game-lead.md
│   │   ├── cpp-dev.md
│   │   ├── unreal-operator.md
│   │   ├── modeler-3d.md
│   │   ├── concept-artist.md
│   │   └── qa.md
│   ├── hooks/
│   │   ├── inject-gate.ps1
│   │   ├── ensure-hookspath.ps1
│   │   ├── qa-gate.ps1
│   │   ├── protect-claude.ps1
│   │   └── gate-inject.log
│   ├── settings.json
│   └── settings.local.json        # (gitignored)
├── .githooks/
│   ├── pre-push  / pre-push.ps1
│   ├── pre-merge-commit / pre-merge-commit.ps1
│   └── README.md
├── context/
│   ├── _shared.md
│   ├── ARCHIVE-INDEX.md
│   ├── game-lead/      { context.md, archive.md, audit-2026-06-16.md, tmp/ }
│   ├── cpp-dev/        { context.md, archive.md, logs/ }
│   ├── unreal-operator/{ context.md }
│   ├── modeler-3d/     { context.md }
│   ├── concept-artist/ { context.md, tmp/ }
│   ├── qa/             { context.md, tmp/ }
│   ├── logs/           { protect-claude.log }
│   └── BugReports/     # скриншоты от Рината (1..17)
├── docs/
│   ├── architecture.md
│   ├── decisions.md            # 24 ADR
│   ├── ai-team-playbook.md
│   └── contrary-survivor/
│       ├── GDD.md
│       ├── roadmap.md
│       ├── tech-design.md
│       ├── asset-contract.md
│       ├── mobile-optimization.md
│       ├── demo-plan.{source.md,html,pdf,preview.png}
│       └── art/ { README.md, *.jpg }
├── assets/
│   ├── index.html
│   └── iron_barrel/ { iron_barrel_v1.blend, iron_barrel_preview_v1.png, iron_barrel.asset.md }
├── concept-art/      { contrarysurvivor-style-{notes.md,sheet.html,sheet.png,sheet.pdf} }
├── logs/             # прогоны UBT/headless/nav (множество .log/.py/.console)
├── renders/ · reports/ · backups/ · Screenshots/ · tmp/
└── Ответы1.txt · Ответы2.txt
```

---

### Сводка по разделам (что подтверждено артефактом)
- §1–4, §7–9 — **ПРОВЕРЕНО** по файлам репозитория и установленным пакетам (`.claude/agents/*`, `.mcp.json`, `settings*.json`, `hooks/*.ps1`, `blmcp/tools/*`, `unreal-mcp/dist/index.js`, `wc` по `context/*`, версии рантаймов).
- §5 (Unreal) — механизмы ПРОВЕРЕНЫ по ADR-003/012/021 + код тулзов; флакки-инжекция MCP в субагентов — ПОДТВЕРЖДЕНА логами (`context/game-lead/context.md`).
- §6 (Blender) — ПРОВЕРЕНО по ADR-002/011 + список тулзов из пакета `blmcp` 1.0.0.
- §10 (миграция) — **ОЦЕНКА**; общая модель OpenAI Agents SDK не сверена с докой в этой сессии (помечено НЕ ПРОВЕРЕНО), требует валидации перед работами.
```
