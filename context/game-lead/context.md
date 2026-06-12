# context: game-lead

> Персональная память агента `game-lead`. Сюда агент дистиллирует решения, ограничения и текущее состояние (правило H). Новые сессии стартуют с этого файла.

## Решения
- Все решения по инструментам/архитектуре — в `docs/decisions.md` (ADR-001..013 + ADR-004 пересмотрен).
- Инструменты команды заведены и проверены живыми вызовами: Blender MCP (modeler-3d), unreal-mcp (unreal-operator, 20 тулзов), **нативный code-render через headless Edge (concept-artist)**, Google Drive (бэкап). cpp-dev/qa — нативный Claude Code, MCP не нужен.
- concept-artist: canvas-design ОТКЛОНЁН (вне скоупа роли, ADR-004 пересмотрен). Инструмент роли = HTML/CSS+SVG → PNG/PDF через `msedge --headless`. Фигуративный концепт-арт роль НЕ делает.

## Ограничения
- QA-гейт: маркер `.claude/QA_OK` создаётся game-lead'ом ВРУЧНУЮ только после «добро» от qa (с артефактом) и удаляется СРАЗУ после merge. Не коммитится. ВАЖНО: при обрыве сессии маркер может остаться висячим — проверять при старте.
- Параллелизм ≤3 агента. Субагенты не порождают субагентов (дерево плоское, глубина 1).
- Напарники — только фича-ветки, не master. Merge в master — после QA.

## Текущее состояние (на 2026-06-11, конец сессии)
- **Фаза:** инфраструктура/инструменты + валидация окружения — каркас команды ИНСТРУМЕНТАЛЬНО СОБРАН.
- **Вся команда из 6 агентов провалидирована живыми вызовами** (game-lead, cpp-dev, unreal-operator, modeler-3d, concept-artist, qa).
- **Ш8 СМЕРЖЕН в master (2026-06-11).** Решение Рината — вариант 1 (стандартный мёрж). master = `b44e42e` (merge commit, `--no-ff`). Ветка `fix/qa-gate-delete` удалена. Маркер `QA_OK` создан→мёрж→удалён сразу (проверено gone). Висячего маркера нет.
- **master запушен в origin (2026-06-11): master = origin/master = `93b9c18`.** Push сделан легитимно через гейт (создать QA_OK ОТДЕЛЬНЫМ вызовом → push → удалить маркер; маркер обязан лежать на диске ДО запуска push-команды, т.к. PreToolUse-хук проверяет его до выполнения).
- Untracked: `context/concept-artist/tmp/` (PNG мини-палитры Ш7) + `context/game-lead/tmp/` (артефакты ревью Ш8: `hooktest.ps1` оракул + `qa-matrix-61bda9b.log`; Ш8 закрыт — можно хранить как референс гейта или подчистить).
- cpp-dev: C++-сборка UE провалидирована — `ContrarySurvivorEditor` PASS + полный ребилд (28 TU) PASS. Логи в `E:\game-dev-team\logs\`. Детали — `context/cpp-dev/context.md`.
- Проект ContrarySurvivor: `E:/ContrarySurvior/ContrarySurvivor/`, UE 5.5.4, GAS + Enhanced Input, 7233 ассета.

### Ш8 — фикс qa-gate хука: СМЕРЖЕН (master b44e42e, 2026-06-11)
- **Баг:** хук считал ЛЮБОЙ `git push` пушем в master, если HEAD=master и в команде нет слова «master» (старая стр.54) → `git push origin --delete <ветка>` и `git push origin <feature>` ложно блокировались.
- **Фикс (ветка `fix/qa-gate-delete`):** 2 коммита. `d30e022` — детект push разбирает рефспеки и смотрит на ЦЕЛЬ пуша (нет рефспека → текущая ветка; `src:dst`/`:master`/`HEAD:master` → dst; `--delete`/`-d`: удаление master блокируем, чужой ветки — пропускаем). `61bda9b` — фикс регрессии, найденной qa: subshell с приклеенным трейлинг-метасимволом (`(git push origin master)` → токен `master)` ≠ `master`) утекал мимо гейта. Правки: сегментация теперь режет и по `( ) < >` (стр.42) + дочистка трейлинг-метасимволов у `$dst` (стр.83).
- **QA:** qa дал **ATTEST PASS**. Раунд 1 — независимо поймал реальную регрессию (вердикт FAIL). Раунд 2 — построчный аудит диффа `61bda9b` (фикс корректен и полон) + аудит оракула `hooktest.ps1` (честный, проверил cwd/branch/marker-резолв и отсутствие маскированных крашей) + лог **37/37 OK, fails=0** против `HEAD=61bda9b`.
- **Структурное ограничение (важно для Ш9):** qa из инструментов имеет только Bash; Bash тут гейтится самим хуком-под-тестом И режется permission-гардрейлом на синтетические push-to-master payloadы (нет PowerShell/Write). Поэтому qa НЕ смог сам выполнить матрицу — «run» нажал game-lead через инструмент PowerShell (Start-Process, реальные exit-коды). qa заверил артефакт, но не самовыполнил — qa поступил верно (не обфусцировал обход, не фабриковал).
- **Артефакты ревью (НЕ УДАЛЯТЬ — нужны, если Ринат выберет «прогоню сам»):** `context/game-lead/tmp/hooktest.ps1` (оракул), `context/game-lead/tmp/qa-matrix-61bda9b.log` (выхлоп 37/37).
- **РАЗВИЛКА ЗАКРЫТА:** Ринат выбрал вариант 1 — принять связку «рантайм-артефакт game-lead + независимый аудит qa (дифф+оракул+лог) + раунд-1 кэтч» → стандартный мёрж. Выполнено 2026-06-11.
- ВАЖНО на будущее: при коммите/мерже не помещать в Bash-команду сегменты, начинающиеся с `git push ... master` — живой хук их режет (в т.ч. синтетику в логах команды).

### Ш9 — автономия: ВОЛНА A смёржена (T3+T1+T4), 2026-06-11
- **T3** (`fix/agent-tools-lockdown`, merge `5d1f86b`): прописан явный `tools: Read,Write,Edit,Glob,Grep,Bash` у `modeler-3d` и `unreal-operator` (раньше строки не было → наследовали ВЕСЬ тулсет). Живой тулсет-чек — ПОСЛЕ рестарта (frontmatter кешируется на старте).
- **T1** (`fix/qa-gate-tool-agnostic`, merge `9970c31`): **git-native qa-гейт = АВТОРИТЕТ.** `.githooks/pre-push`+`pre-merge-commit` (sh→ps1) через `core.hooksPath .githooks` (ЛОКАЛЬНЫЙ конфиг, бутстрап `git config core.hooksPath .githooks` на каждой машине — см. `.githooks/README.md`). Решают по реальным git-рефам → инструмент-агностично. Claude-хук matcher `Bash`→`Bash|PowerShell` (ранний фильтр). Дыра-1 (обход через PowerShell) ЗАКРЫТА. Пруфы: git-native 6/6, оракул 7/7, живой блок, qa независимый 6/6. ff-вектор закрыт правилом «merge в master всегда `--no-ff`» + pre-push.
- **T4** (`chore/settings-local-revision`, merge `ca7adf6`): `settings.json` (коммит) — `additionalDirectories: E:/ContrarySurvior/ContrarySurvivor` + Read/Write/Edit на тот же путь. `settings.local.json` (gitignored) — убраны опасно-широкие allow (powershell/cmd/node/python/pwsh/* + winget/dotnet/npm/tasklist/taskkill/Get-Content*/Read(//e//**)). **Static deny НЕ вводим** (решение Рината).
- **КЛЮЧЕВАЯ НАХОДКА (на проверке в части 2):** удаление allow НЕ закрывает запись в `.claude/` под текущим поведением сессии. Главная сессия: `node -e` и Bash-запись в `.claude/hooks` проходили свободно. НО: после удаления `Bash(node *)` свежеспавненный субагент (qa) получил ОТКАЗ гейта на node → **allow ВСЁ-ТАКИ гейтит для свежего субагента**. Две гипотезы (Ринат, разбираем эмпирически после рестарта): (1) **stale-кеш** правил прав в главной сессии (как frontmatter); (2) **acceptEdits** штатно авто-принимает правки в cwd, а `.claude/` в cwd → запись проходит не из-за bypass. Вывод-of-record — после теста режима (часть 2).
- **Дыра-2 (.claude) закрывается ТОЛЬКО хуком T2 (agent_id), НЕ удалением allow.** T2 — приоритет, идёт сразу после теста режима, ДО T5/T6. `agent_id` есть только у субагентов (дока) → хук не блокирует game-lead.
- **ИНЦИДЕНТ (урок):** тест-зонд дописал 1 символ в боевой `qa-gate.ps1` при проверке гейтинга. Восстановлено из git (`git diff HEAD` пуст), проба удалена, гейт перепроверен живьём (блокирует). УРОК: тестировать гейтинг на throwaway-путях, НЕ на боевом хуке.
- **Артефакты волны A (НЕ удалять):** `context/game-lead/tmp/gitnative-test.ps1`+`gitnative-matrix.log` (6/6), `claudelayer-oracle.ps1`+`claudelayer-oracle.log` (7/7).
- **НУЖЕН РЕСТАРТ** сессии game-lead: активировать `tools:` из T3 + сбросить кеш прав для теста режима (часть 2 файла 004).

### Ш9 T5 — изоляция напарников через git-worktree (ПРОЦЕДУРА)
- **Механизм = НАТИВНЫЙ.** Инструмент `Agent` с параметром `isolation:"worktree"` даёт напарнику СВОЙ git-worktree + СВОЮ ветку `worktree-agent-<id>`, его cwd = этот worktree. Подтверждено живьём (2026-06-11): отдельный каталог, отдельная ветка, запись без промптов, `git worktree list` показывает все активные worktree (locked) одновременно.
- **Где лежат:** Claude Code кладёт worktree в `E:/game-dev-team/.claude/worktrees/agent-<id>/` (ВНУТРИ репо, под `.claude/`). Добавлено в `.gitignore` (`.claude/worktrees/`), чтобы не засорять статус.
- **Параллель:** двух+ напарников можно спавнить ОДНОВРЕМЕННО, каждый в своём worktree/ветке — НЕ конфликтуют (доказано: wt-A `f1ac07e` + wt-B `6ad5c10`, разные деревья, оба коммитят независимо). Потолок ≤3. **Blender — ОДИН клиент: не спавнить двух `modeler-3d` разом даже в разных worktree** (сокет `localhost:9876` держит одного).
- **master недосягаем из worktree:** `git push origin HEAD:master` / merge из worktree режется гейтом (qa-gate.ps1 + git-native pre-push/merge + маркер QA_OK). Подтверждено живьём. Напарник коммитит только в свою ветку (без push).
- **Имена напарников — по роли** (`modeler`, `cpp`, `unreal`, `concept`, `qa`; суффикс-номер для нескольких: `modeler-2`). Ветка авто-именуется `worktree-agent-<id>`.
- **Уборка:** worktree «auto-cleaned if unchanged» НЕ срабатывает, если напарник оставил файлы/коммиты. game-lead убирает вручную: `git worktree remove --force .claude/worktrees/agent-<id>` + `git branch -D worktree-agent-<id>` (+ при нужде `git worktree prune`). Подтверждено.
- **Проход в master:** ветку напарника game-lead отдаёт qa → ATTEST с артефактом → `.claude/QA_OK` → `git merge --no-ff <ветка>` → снять QA_OK. Гейт сериализует (один маркер) — ветки заходят ПО ОЧЕРЕДИ.
- **(T7c, РЕШЕНО)** карвут `.claude/worktrees/**` в protect-claude добавлен (см. ниже Ш9 T7) — напарник теперь пишет в свой worktree и абсолютными путями.
- **НАХОДКА:** `logs/` целиком в `.gitignore` → коммит файла из `logs/` требует `git add -f`.

### Ш9 T7 — укрепление гейта после инцидента T5 (СМЁРЖЕНО, master `c5032fa`, 2026-06-11)
- **КОРЕНЬ слёта гейта (подтверждено живьём):** `isolation:"worktree"` Claude Code пишет `core.hooksPath=<repo>/.git/hooks` в ОБЩИЙ `.git/config` при КАЖДОМ спавне worktree → git-native гейт (`.githooks`) гаснет на весь репо до ре-ассерта. Это и был корень инцидента T5 (непрошеный merge без QA_OK).
- **T7a самохил:** `.claude/hooks/ensure-hookspath.ps1` форсит `core.hooksPath` в АБСОЛЮТНЫЙ `E:\game-dev-team\.githooks`. Зарегистрирован в `settings.json` на `SessionStart`(startup+resume) И `PreToolUse(Bash|PowerShell)` ПЕРВЫМ хуком (чинит и мид-сессийный слёт). Идемпотентен, лог `logs/gate-selfheal.log`. **АКТИВируется ПОСЛЕ РЕСТАРТА** (settings кешируется на старте).
- **T7b:** `qa-gate.ps1` теперь ловит склейку `git checkout master && git merge/push` (пред-скан `switchToMaster`). Регрессии целы (feature push/merge, Ш8 `--delete`, `checkout -b master2`). ЖИВОЕ (хук читается заново).
- **T7c:** `protect-claude.ps1` — карвут `.claude/worktrees/**` (своя копия напарника) с traversal-guard (нет `..`). Главные рельсы вне worktrees → не ослаблены. ЖИВОЕ.
- **qa РЕ-ATTEST PASS:** T7b 8/8, T7c 10/10, heal-лог+идемпотентность. Ветка `fix/gate-hardening` → QA_OK → merge `c5032fa` → маркер снят.
- **ВАЖНО — РЕСТАРТ:** до рестарта самохил-регистрация НЕ активна → game-lead ВРУЧНУЮ `git config core.hooksPath .githooks` после спавна worktree и ПЕРЕД любым merge. После рестарта — авто.
- **ОПЕРАЦИОННАЯ ПАМЯТКА (живой хук на master):** находясь на master, НЕ помещать в Bash-команду (включая echo-обёртки и коммит-сообщения) текст, начинающий сегмент с `git merge`/`git push`/`git checkout master` — живой qa-gate режет (branch=master). Для коммитов использовать `git commit -F -` с телом без триггер-фраз.
- **Классификатор:** правки security-рельсов (`settings.json`, хуки) auto-mode-классификатор пропускает ТОЛЬКО при ПРЯМОЙ авторизации Рината в его сообщении (не из файла-задания). Создание НОВОГО файла-хука и git-коммиты — проходят.

### Ш7 — concept-artist: ЗАКРЫТ (нативный code-render)
- canvas-design ОТКЛОНЁН (навыка нет в установке + вне скоупа роли). Инструмент роли = HTML/CSS+SVG → PNG/PDF через headless Edge. ADR-004 пересмотрен. Скоуп сужен (ADR-004 доп.). Обе ветки (`feat/concept-artist-native-render`, `feat/concept-artist-scope-narrow`) СМЕРЖЕНЫ в master.
- **Хвост 2 (этой сессией): concept-artist рендерит САМ — ПОДТВЕРЖДЕНО.** После рестарта сессии `Bash` у concept доступен (прошлый `No such tool: Bash` не воспроизводится). Спавн concept сам: HTML → `msedge --headless=new --screenshot` → PNG `context/concept-artist/tmp/mini-palette.png` (16330 B), подтверждено `ls -l`. Палитра — тестовый семпл, НЕ из диздока, не утверждена.
- Рендерер: `msedge --headless=new --disable-gpu --hide-scrollbars --no-sandbox --window-size=W,H --screenshot=OUT.png "file:///ABS.html"`.
- **УРОК (важно):** правка frontmatter `tools:` в дефиниции агента в середине сессии НЕ подхватывается — дефиниция кешируется на старте game-lead-сессии. После правки дефиниций агентов → ПЕРЕЗАПУСК сессии game-lead, иначе новый тулсет не вступает в силу. (Подтверждено: в прошлой сессии concept без Bash, в этой — с Bash после рестарта.)

### Осталось (инфра-хвосты) — АКТУАЛИЗИРОВАНО 2026-06-11 (сверка с git-логом)
- **Ш8** — ЗАКРЫТ ПОЛНОСТЬЮ: смёржен (b44e42e) + запушен (master=origin=93b9c18). Хвостов нет.
- **Ш9 волна A** — СМЁРЖЕНА локально (T3+T1+T4, master `ca7adf6`).
- **Ш9 волна B — СМЁРЖЕНА локально (сверено по git-логу):**
  - **T2** (protect-claude guard, ADR-014) — merge `19d90ec`. Дыра-2 (.claude от субагентов) закрыта хуком (best-effort, не airtight — см. ADR-014). Зарегистрирован в settings.json PreToolUse.
  - **T5** (worktree-изоляция, нативная процедура) — merge `adae0de`.
  - **T7** (укрепление гейта после инцидента T5: самохил hooksPath + bundle-bypass + worktree carve-out) — merge `c5032fa`/`2b11275`.
  - **«Тест режима, часть 2»** — субсумирован T2: Дыру-2 закрыл хук protect-claude, не разрешение вопроса stale-cache vs permissive. Отдельного вывода-of-record по режиму не фиксировали; практически неактуально, т.к. рельсы держит хук.
- **T6 (qa-testbed)** — НЕ ДЕЛАЛСЯ (коммитов нет). Единственный незакрытый инфра-хвост Ш9. Назначение: изолированный стенд для qa, чтобы qa мог сам прогонять матрицу гейта (сейчас qa заверяет, но «run» жмёт game-lead — см. структурное ограничение Ш8). Опционально/nice-to-have.
- **Push волны A+B в origin — ВЫПОЛНЕН (2026-06-11, авторизовано Ринатом).** Легитимный гейт-проход: `.claude/QA_OK` создан ОТДЕЛЬНЫМ вызовом (лежал на диске ДО push) → `git push origin master` (`72b39f8..2b11275`) → маркер снят СРАЗУ. Итог: `master == origin/master == 2b11275`, ahead/behind = 0/0. Висячего QA_OK нет, гейт активен (hooksPath=абс .githooks). Примечание (обновлено 2026-06-11): docs/context-sync смёржен (`99be7fd`) и запушен; инфра-master == origin == `99be7fd`.

### Инфра-хвост (на потом)
- **T6 (qa-testbed)** — единственный незакрытый инфра-хвост, опционально. Не блокирует разработку игры.

---

# === РАЗРАБОТКА ИГРЫ ContrarySurvivor — Сессия 2026-06-11 (Фаза 0 + диздок v2) ===

## РЕЖИМ
Ринат перевёл команду в режим **разработки игры**. game-lead ведёт разработку **напрямую с Ринатом** (архитектор-сборщик — только при сбоях). Работаем фазами: диздок (источник правды) → техдиздок-сверка → роудмап (утв. 1 раз) → фазы (каждая = играбельный инкремент с пруфом). Принципы: **вертикальный срез сначала** (узкий сквозной цикл поверх существующего), диздок=правда (дыры эскалировать, не выдумывать), каждая фаза реально запускается, автономию на рутине гнать без вопросов, анти-фабрикация с пруфами.

## ПУТИ / ОКРУЖЕНИЕ
- Проект игры: `E:/ContrarySurvior/ContrarySurvivor/` (UE **5.5.4**), `.uproject`, Source/Content/Config. Доступ есть (в settings.json additionalDirectories Read/Write/Edit).
- Папка материалов: `E:/ForGameLead(Materials)/` — диздок `Новый Дизайн документ Survior.docx`, `ИерархияКлассов(...).svg` (техдиздок), пайплайн ассетов (WIP .blend/.fbx меша+анимаций+брони бандита), `ФотоРеференсы/` (1.jpg,2.webp,3.webp).
- **UE-редактор запуск:** `/e/UnrealEngine/UE_5.5/Engine/Binaries/Win64/UnrealEditor.exe "E:/ContrarySurvior/ContrarySurvivor/ContrarySurvivor.uproject"` (фоном). unreal-operator MCP/Remote работает ТОЛЬКО когда редактор открыт (иначе «Remote node is not available»). На конец сессии редактор ЗАКРЫТ (освободил ресурсы).
- Диздок извлечён в текст: `context/game-lead/tmp/dd/dizdok.txt` (gitignored). Палитра: `context/concept-artist/tmp/cs-palette.png`+`.html`.

## ФАЗА 0 ОСМОТР — ЗАВЕРШЕНА (с пруфами, файлы + живой редактор)
- **Играбельно сейчас:** тонкий тех-прототип — управляемый персонаж (изометрия, WASD, спринт), hitscan-стрельба `LineTrace` по цели под курсором с уроном/патронами/перезарядкой, инвентарь-данные. PlayerStart+GameMode настроены, при Play игрок спавнится.
- **ВАЖНО (поправка к вводной Рината):** у боевого персонажа **МОДЕЛЬ И АНИМАЦИИ ЕСТЬ** — модульный меш Head/Torso/Legs + `ABP_HumanoidCharacter` (из `TestContentAndCode/PreProduction`) вшиты в `BP_PlayerCharacter`. Препродакшн-качество, не финал.
- **Нет:** врагов, AI (AIModule не подключён), логики выживания, HUD/инвентарь-UI (UMG-виджетов 0), диалогов, квестов, экономики/торговли, сейва/смерти/респауна, ближнего боя, World Partition, моб.управления, влияния брони на урон.
- **C++ (14 классов, скомпилирован):** `ACharacter→AMasterHumanoidCharacter→APlayerCharacter`; `AContrarySurvivorPlayerController`; `UInventoryComponent`; `AMasterInventoryItem→AMasterWeapon→ARangedWeapon→APistol` (пистолет 25 урона/маг 12/2 в сек); `AArmor→{Head,Torso,Pants}Armor` (пустые заглушки). **GAS НЕТ** (статы=голые float). GameMode/HUD/PlayerState/Enemy/AIController в C++ нет. Linetrace: `ARangedWeapon::PerformLineTrace` (есть урон+DrawDebugLine; смерть=только лог "I am dead").
- **Сцена `L_MainLevel`** (единственная карта, стартовая): пол, Cube, DirectionalLight, PlayerStart, +лишний дубль `BP_PlayerCharacter`. GameMode override=`BP_ContrarySurviorGameMode`(на движковом GameModeBase)→Pawn=BP_PlayerCharacter, Controller=BP_..PlayerController, HUD=движковый дефолт. Enhanced Input: IA_Move(WASD)/Sprint(Shift)/Fire(ЛКМ)/Reload(R)+IMC_Default; код ждёт ещё Interact/Inventory (нет IA).
- **Аудит TestContentAndCode (19 ассетов):** 9 USED (цепочка персонажа — НЕ трогать), **10 ORPHAN** (кандидаты на уборку, удалять кластерами): BP_MyTestGameMode+BP_TestCharacterSeparated2906252047; BP_TestItem+red-cross-icon; папка WrokingCorrectly2906252034/ (Try6_Cube+скелет+аним+мат); BS_HumanoidCharacter_Walk_Idle; SK_BanditTorsoArmor3__Torso. Тех-долг: блендспейс орфан — AnimBP играет анимации напрямую (нет сглаживания по скорости).

## РЕШЕНИЯ РИНАТА (зафиксированы, нужно оформить ADR-015..017)
1. **БЕЗ GAS** → лёгкий кастомный `UStatsComponent` на float (Health/Hunger/Thirst/Money). (ADR-015)
2. **World Partition — отложен**, старт на одной малой карте. (ADR-016)
3. **Деньги** — добавить в статы персонажа.
4. **Наведение:** ПК — цель=актор под курсором, клик ЛКМ=имитация тапа; **архитектура ввода абстрактная под тач Android** (реализация тача — позже). Первый срез — **клик-захват** цели (авто-захват ≤5м — позже). (ADR-017)
5. **Модульный меш персонажа — by-design под броню** (смена меша по слотам). НЕ плейсхолдер. Технадо: части шарят скелет через **Leader/Master Pose Component**. ВРАГОВ — единым склеенным мешем (Android: меньше draw call); модульный только игрок.
6. **Первый вертикальный срез УТВЕРЖДЁН:** игрок (готовое движение+стрельба) vs один **бандит** с примитивным AI (заметил→подошёл→атакует), у врага хелсбар, корректная смерть, маленькая тест-арена.
7. **Палитра УТВЕРЖДЕНА** (cs-palette.png, 16 цветов). Референс = **Last Day on Earth (Kefir)**.
8. Бюджет Android: 1.5–4k трисов/перс ок; главный рычаг — draw calls/материалы/кости; финал — профилирование на устройстве (tech-artist/qa).

## ДЕЛИВЕРАБЛЫ СЕССИИ
- **Черновик диздока v2:** `docs/contrary-survivor/GDD.md` — 11 частей + Приложения A(состояние)/B(уборка)/C(тех-долги)/D(8 откр.вопросов)/E(4 промпта артов). Источник правды по игре. Метки [ОТКРЫТО]/[РЕШЕНО]/[ЕСТЬ]/[ДЫРА].
- **concept-artist:** палитра(утв.)+арт-дирекция(в GDD ч.2)+4 EN-промпта (GDD прил.E). Ринат генерит арты в Bing Image Creator / Google ImageFX / Leonardo.ai, вернёт — вставить в диздок (на 1й срез не блокер).

## БЛОКЕР ПЕРЕД ФИНАЛИЗАЦИЕЙ — 8 ОТКРЫТЫХ ВОПРОСОВ (ждём Рината, GDD прил.D)
Ринат на конец сессии НЕ ответил на них (ответил только по визуалу/трисам/рефу/тулзам + утвердил палитру/срез/решения 1-7 выше):
1. Враги MVP: бандиты-да; зомби/мутанты/волки — кто MVP, кто пост-MVP?
2. Первый срез: тест-арена (рек.) или кусок окрестностей деревни?
3. Числа выживания (предложить черновые на тюнинг?).
4. Числа экономики (предложить черновые?).
5. Квесты MVP: набор (из примеров диздока)?
6. Сейв/смерть: костры в точках сейва? что теряется при смерти?
7. Ближний бой в MVP? стволы MVP (дробовик?)?
8. Прогрессия только через снаряжение (без XP) — подтвердить?
9. (мелочь) Кровь — оставить условным акцентом или убрать?

## СЛЕДУЮЩИЙ ШАГ (ЗАВТРА, старт отсюда)
1. Получить ответы Рината на 8(+1) вопросов выше → **финализировать `docs/contrary-survivor/GDD.md`** (снять [ОТКРЫТО]).
2. Написать **ADR-015..017** в `docs/decisions.md` (нет GAS / WP отложен / абстракция ввода-наведения).
3. **Тонкая сверка техдиздока** (иерархия классов) под первые 1-2 фазы: добавить плановые `AEnemyCharacter`+`AEnemyAIController`, `UStatsComponent`, при нужде C++ GameMode/HUD.
4. **Роудмап по фазам с Definition of Done** (прицел — играбельный MVP к фазе 2-4) → Ринат утверждает ОДИН раз.
5. Старт Фазы 1 = первый вертикальный срез (бандит+AI). Делегирование: cpp-dev (EnemyCharacter+AIController+StatsComponent+смерть), unreal-operator (тест-арена, разместить, BP, хелсбар-виджет), modeler-3d (склеенный меш бандита по арту), qa (сборка+проверка). Прогон через qa-гейт перед merge.
- ВАЖНО: финальный Word-рендер диздока (pandoc или вручную) — когда содержание залочено. Сейчас pandoc/LibreOffice/python-docx НЕ установлены.
- Прогресс сессии сохранён в ветке `docs/phase0-gdd` (+push origin). Тех-состояние master инфры = `99be7fd`.

# === Сессия 2026-06-12: финализация диздока + СТАРТ ФАЗЫ 1 ===

## Диздок/решения финализированы (ветка docs/phase0-gdd, коммиты dfb8355..2b9c21c)
- Все 9 вопросов закрыты Ринатом. GDD v2.0 финал. ADR-015 (без GAS, UStatsComponent), ADR-016 (WP отложен), ADR-017 (абстракция ввода/наведения), **ADR-018 (модульность у ВСЕХ гуманоидов + runtime mesh merge при спавне; Skeletal Merging в 5.5 — на проверке cpp; фолбэк живые компоненты+LOD)**.
- Решения MVP: враги = бандиты+волки; локация = кусок деревни (кубы); один Kill-квест + расширяемый каркас; сейв = гибрид зоны+костры, респаун, потеря % неэкип. рюкзака; бой = нож+пистолет (ближний есть); прогрессия только снаряжение; кровь = скупые партиклы. Черновые числа выживания/экономики — утв. на тюнинг.
- Арты (4) получены, утв., в `docs/contrary-survivor/art/` (hero/bandit/village/styleframe .png.jpg). Арт=ориентир. Герой: в ТЗ моделеру НЕ писать ватник/кирзачи (наказ Рината). Style frame «островок-диорама» — артефакт, не цель.
- Роудмап утверждён Ринатом (7 фаз с DoD): `docs/contrary-survivor/roadmap.md`. Техдизайн: `docs/contrary-survivor/tech-design.md`.

## ФАЗА 1 (срез: бой с бандитом) — В РАБОТЕ, гейм-репо `E:/ContrarySurvior/ContrarySurvivor`
- **Гейм-репо отдельный** (github RenchezLove/ContrarySurvivor), **своего qa-гейта НЕТ** (хуки только в team-репо) → политику веток держу вручную. **`Content/` в .gitignore** → .uasset/.umap НЕ версионируются (ассет-работу qa ревьюит в редакторе, не по git). master гейм-репо = `f7542ad`, НЕ тронут.
- Вся работа Фазы 1 — ветка гейм-репо **`feature/phase1-enemy-stats`**.
- **cpp-dev (СДЕЛАНО, сборки PASS):** UStatsComponent (Health+смерть, делегаты OnHealthChanged/OnDeath, GetHealthPercent, задел-модификаторы), AEnemyCharacter:AMasterHumanoidCharacter (бандит 80HP, GetStats()), AEnemyAIController (Idle→Chase→Attack, MoveToActor, AIModule+GameplayTasks в Build.cs), клик-захват в PlayerController (GetCurrentTarget), заглушка смерти игрока (HandleDeath). +Автоэкип пистолета (DefaultWeaponClass+спавн в BeginPlay APlayerCharacter). +**AContrarySurvivorHUD:AHUD** (DrawHUD рисует хелсбар врага над залоч./ближней целью ≤1500). Логи: phase1-cpp-build-f7542ad.log, phase1-cpp-hud-ea5b201.log. Коммиты ea5b201,6faccca,18339cf,28b67d0.
- **modeler-3d (СДЕЛАНО):** реальный модульный бандит-гопник на общем скелете RootAnim(21 кость), 590 трисов (Head156/Torso332/Legs102), 1 материал M_Bandit_Flat (vertex-color), UV ок, заскинен, round-trip проверен. FBX: `E:/ForGameLead(Materials)/bandit-work/SK_Bandit_{Head,Torso,Legs}.fbx` (+bandit_work.blend). NB: Blender v5.1, FBX7400 — unreal проверит импорт в 5.5. База-пайплайн: `MasterHumanoidCharacterSeparatedMesh.blend1`.
- **unreal-operator (ЧАСТИЧНО):** уборка 10 орфанов ВЫПОЛНЕНА (бэкап `E:/game-dev-team/backups/orphans-20260612/` + перепроверка референсеров + удаление + целостность). BP_EnemyBandit (база AEnemyCharacter, AIControllerClass задан, плейсхолдер-визуал = меши игрока). Карта L_MainLevel: 2 дома-куба/2 дерева/2 камня + NavMeshBoundsVolume + бандит размещён + BP_Pistol в мире. Скриншоты в Saved/Screenshots (phase1_village_combat_overview.png, phase1_combat_zone_closeup.png).
  - **УРОК/ИНЦИДЕНТ:** консольная `BuildPaths` через Python КРАШИТ редактор (access violation) — НЕ использовать; навмеш строить через GUI Build или авто на загрузке статик-навмеша.
  - **УРОК:** UMG WidgetTree и BP Event Graph НЕ редактируются через unreal-MCP Python в 5.5 → хелсбар/автоэкип сделали через C++ (HUD-draw + DefaultWeaponClass), а не UMG/BP-граф. Назначение HUDClass/DefaultWeaponClass — это property-set (Python может).
  - **УРОК:** при правке C++ редактор держит СТАРЫЙ DLL в памяти если был запущен до сборки → перезапуск редактора обязателен после cpp-сборки (или Live Coding, но для НОВЫХ классов ненадёжно). MCP переподцепляется к новому редактору после рестарта (подтверждено).
- **ОСТАЛОСЬ в Фазе 1 (после рестарта редактора):** unreal — выставить HUDClass=AContrarySurvivorHUD в BP GameMode + DefaultWeaponClass=BP_Pistol в BP игрока (property-set); достроить навмеш безопасно; verify find_path; скриншот. Опционально — импорт реальных FBX бандита вместо плейсхолдера. Затем **qa-ревью ветки** (сборка+проверка) и отчёт Ринату. **Боевой цикл в PIE — финально подтверждает ручной Play (Ринат/qa), автономно PIE не верифицируется.**
