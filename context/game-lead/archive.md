# archive: game-lead

> **ПРОШЛОЕ game-lead — read-on-demand.** НЕ входит в грунтовку сессии (правило «Гигиена памяти» в CLAUDE.md). Читать ТОЛЬКО по поводу: чистка / онбординг свежей сессии / «как мы пришли к X». Единственный источник правды на «сейчас» — блок «🧭 СЕЙЧАС» в `context.md`. Полная история изменений — git; ключевые решения — `docs/decisions.md` (ADR); дизайн-правда — `docs/contrary-survivor/`.

## Оглавление (что где)
- **Инфра Ш7–Ш9 (смержено в master, закрыто):** qa-гейт хук (Ш8), автономия/worktree/укрепление гейта (Ш9 T1–T7), concept-artist native-render (Ш7). Состояние инфры на 2026-06-11.
- **Игра — истории фаз:** Фаза 0 (осмотр + диздок v2), Фаза 1 (бой с бандитом + раунды визуала 1–5), Фаза 2 (выживание/сейв), Фаза 3 (нож/броня/волк), Фаза 4 (инвентарь/экип/торговец), Фаза 5 старт (квесты/диалог/староста).
- **END-OF-DAY:** 2026-06-13 (00:30) и 2026-06-13 (~20:20).
- **Демка 2026-06-14:** контент-направление (2 квеста, зоны, звук, оружие в руке, камера LDoE).
- **ПЛЕЙБУК для будущих ИИ-команд** (наказ Рината).
- **УРОКИ UE** (vertex-color/Rotator/Color BGRA и пр.) — в конце файла.

> ⚠️ Из живой памяти УДАЛЕНЫ (не архивировались — перетёрты, итог в «СЕЙЧАС»): 4 промежуточных SAVE-снимка 2026-06-14/15 и отметённые слои WASD-саги (NavWalking / камера-yaw / MaxWalkSpeed / friction / root motion — все опровергнуты; корень WASD см. «СЕЙЧАС»).

---

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
- **Проводка ДОВЕДЕНА (раунд wiring):** HUDClass=AContrarySurvivorHUD в GameMode, DefaultWeaponClass=BP_Pistol игроку, навмеш строится (путь PlayerStart→бандит валиден), **реальный меш бандита импортирован** (/Game/Characters/Bandit/SK_Bandit_*, на общий скелет) и назначен слотам BP_EnemyBandit.

## ФАЗА 1 — Play-баг-репорты Рината (2026-06-12 вечер) + правки
Ринат прогнал Play, скрины в `context/BugReports/` (имена = описания). Разбор:
- **БАГ 1 (критич.) — бандит не умирал от стрельбы.** Причина (грунт. по ARangedWeapon.cpp): трейс `LineTraceSingleByChannel(...,ECC_Visibility)` от оружия к центру цели; капсула врага (Pawn) Visibility=Ignore, меши без коллизии → пуля сквозь, нет `Hit`/`Health now` в логах. **ИСПРАВЛЕНО (cpp, коммит d86b324, сборка PASS `logs/phase1-cpp-fix-28b67d0.log`):** AEnemyCharacter конструктор `Capsule->SetCollisionResponseToChannel(ECC_Visibility,ECR_Block)`. Цепочка урон→смерть в коде УЖЕ была верна (TakeDamage→Stats.ApplyDamage→OnDeath→HandleDeath рэгдолл), не хватало попадания.
- **БАГ 2 — бандит «серый + перевёрнутый».** (а) Серый: vertex-color флэт-материал из Blender не импортирован → дефолт серый (поэтому «изменений не видно» — облик гопника цветовой). (б) Поза/ориентация: модульный риг (Leader Pose+AnimBP+трансформы) живёт в BP игрока, не в C++; BP бандита его не имел. **ЧАСТИЧНО (cpp d86b324, enemy-only):** PostInitializeComponents `Torso/Legs SetLeaderPoseComponent(Head)`; конструктор `GetMesh()->SetRelativeLocationAndRotation((0,0,-90),(0,-90,0))`.

## ✅ PLAY-ПРОВЕРКА РАУНДА ПРАВОК (Ринат, 2026-06-12 22:38) — `context/BugReports/2. BugReport120620262238/`
- **БАГ 1 (бой) — ПОДТВЕРЖДЁН ИСПРАВЛЕННЫМ.** Хелсбар врага есть и уменьшается от попаданий, бандит умирает, всё в логах. C++ HUD-хелсбар работает.
- **Урон ПРАВИЛЬНЫЙ.** Логи: `Hit BP_EnemyBandit for 25.0 damage` / `took 5.0 damage. Health: 0.0/80.0` / `died`. 80HP/25 = 4 выстрела (25+25+25+5). «took 5.0» = добивающий хит, обрезан по остатку HP. НЕ баг. (Опц. мелочь: причесать формулировку лога StatsComponent — логировать и запрошенный, и применённый.)
- **БАГ 2 ОРИЕНТАЦИЯ — НЕ выправилась: бандит стоит НА ГОЛОВЕ (перевёрнут на 180°).** C++ −90/−90 поднял из-под земли (позиция ок), но переворот остался → причина НЕ в трансформе компонента, а в **ОСИ ЭКСПОРТА Blender→UE** (меш/скелет перевёрнут относительно проектного скелета). **→ ЗАДАЧА modeler:** переэкспорт SK_Bandit_{Head,Torso,Legs} с верными осями (Forward/Up как в пайплайн-docx, что даёт корректные меши игрока); проверить, что round-trip в UE даёт вертикального бандита на общем скелете. Затем unreal переимпортирует.
- **БАГ 2 ЦВЕТ — серый, не сделано** (нужен unreal MCP, раунд 3).
- **НЕ баги (ожидаемо Фаза 1):** ближний бой без анимации (логика есть, визуал — Фаза 3); серое окружение/яркий пол = плейсхолдеры + свет не построен; камень=сфера, дерево=конус. Лок только по клику = по дизайну (ADR-017 клик-захват). Игрок не поворачивается к цели = ок этой фазы.

## ⛔ БЛОКЕР СЕССИИ: unreal-MCP не инжектируется в субагентов
- После серии перезапусков редактора тулзы `mcp__unreal__*` ПЕРЕСТАЛИ доходить до свежих спавнов unreal-operator («No such tool available», сервер `unreal` отсутствует в MCP-инструкциях спавна), ХОТЯ `claude mcp list` → `unreal: ✔ Connected`. На РАННИХ спавнах этой сессии тулзы были (работали). Это флакки-инжект MCP в субагентов.
- **ЛЕЧЕНИЕ:** рестарт сессии game-lead (`claude --agent game-lead`) с УЖЕ ОТКРЫТЫМ редактором (ADR-003: редактор полностью загружен ДО старта claude). Редактор сейчас ОТКРЫТ со свежим fix-DLL (d86b324) — НЕ закрывать перед рестартом сессии.
- **NB про рестарт редактора при правках C++:** редактор держит старый DLL если запущен до сборки → после каждой cpp-сборки нужен перезапуск редактора (делал через taskkill+start, ждал ~210с). Это нормальный цикл.

## NEXT (для свежей сессии game-lead, старт отсюда) — РАУНД 3 (визуал бандита)
Бой подтверждён рабочим. Осталось ТОЛЬКО визуал бандита (цвет + ориентация + анимация). Два напарника параллельно (Blender ≠ Unreal, не конфликтуют):
1. **modeler-3d:** переэкспорт SK_Bandit_{Head,Torso,Legs} из `bandit-work/bandit_work.blend` с ВЕРНОЙ ОСЬЮ (бандит на Play стоит на голове — ось экспорта Blender→UE). Свериться с пайплайн-docx (настройки, дающие корректные меши игрока). Цель: после импорта бандит вертикальный на общем скелете. NB: Blender запущен (его не закрывать перед рестартом сессии, если modeler нужен сразу).
2. **unreal-operator** (тулзы должны инжектнуться в свежей сессии — ОБЯЗАТЕЛЬНО проверить mcp__unreal__* на Шаге 0): переимпорт исправленных FBX бандита; назначить Head AnimBP (ABP_HumanoidCharacter); материал M_Bandit_VColor (VertexColor→BaseColor) + vertex-color; проверить ориентацию вертикальная; скрин. Ветка `feature/phase1-enemy-stats`.
3. (Опц.) Build Lighting — убрать «ярко-зелёный unlit» вид сцены.
4. (Опц. мелочь) причесать лог урона в UStatsComponent (запрошенный vs применённый).
5. **qa-ревью ветки** `feature/phase1-enemy-stats` (независимая сборка + аттест с артефактом) → merge в master ГЕЙМ-репо (вручную, своего хука-гейта там нет). Перед этим — РЕШЕНИЕ Рината по версионированию Content/ (сейчас /Content в .gitignore — ассеты не в git; вариант A=Git LFS рек., B=диск+бэкап).
6. Старт Фазы 2 по роудмапу.
ПОРЯДОК раунда 3: сначала modeler чинит ориентацию (переэкспорт) → потом unreal переимпортирует+материал+AnimBP (иначе придётся импортировать дважды). Либо параллельно, но unreal импортирует ПОСЛЕ готовности исправленных FBX.
- Гейм-репо ветка Фазы 1: `feature/phase1-enemy-stats`, HEAD=`d86b324`, master=`f7542ad` (НЕ тронут). Логи сборок: phase1-cpp-build-f7542ad / phase1-cpp-hud-ea5b201 / phase1-cpp-fix-28b67d0 (все PASS). Бэкап орфанов: `backups/orphans-20260612/`. Бандит FBX: `E:/ForGameLead(Materials)/bandit-work/`.

## РАУНД 3 (визуал бандита) — 2026-06-12, частично: находки + БЛОКЕР MCP-канала
- **modeler НАХОДКА (анти-галлюцинация, переэкспорт НЕ делал — правильно):** гипотеза «ось экспорта Blender→UE» **ОПРОВЕРГНУТА** байт-в-байт. Сравнил свой FBX (torso) с пайплайн-эталоном `SK_BanditTorsoArmor3.fbx` (даёт вертикальные меши в UE): GlobalSettings (UpAxis=Y,FrontAxis=Z,CoordAxis=X, знаки +1, FBX7400), Model-узлы (RootAnim Lcl Rot[-90,0,0] scale100; меш[-90,0,0]; кость C_Root) — ИДЕНТИЧНЫ. Round-trip собственного экспорта в чистую factory-сцену → скелет вертикальный (Z=1.569, ноги на полу), меш rot[0,0,0], vertex-color «Col» (CORNER/BYTE_COLOR) + материал M_Bandit_Flat НА МЕСТЕ. В Blender бандит вертикальный (rot[0,0,0]). **В Blender чинить НЕЧЕГО.** FBX не тронуты (раунд-2 экспорт): Head 62828B, Torso 72332B, Legs 62860B (2026-06-12 12:55-12:56).
- **→ ФЛИП 180° «на голове» — на СТОРОНЕ UE, не Blender.** Подтверждено и по C++: `AEnemyCharacter` ПРАВКА C задаёт `GetMesh()->SetRelativeLocationAndRotation((0,0,-90), FRotator(0,-90,0))` — это Yaw −90 (штатный yaw персонажа), физически НЕ даёт переворот на 180° (180°=pitch/roll). База `AMasterHumanoidCharacter` НЕ задаёт relative-трансформ меша вообще (Torso/Legs SetupAttachment к HeadMesh) — у ИГРОКА трансформ меша задан в BP_PlayerCharacter. **ДЕТЕРМИНИРОВАННЫЙ ФИКС (когда канал вернётся):** прочитать relative-трансформ Mesh у рабочего BP_PlayerCharacter + настройки импорта его мешей (Import Rotation/skeleton) → повторить 1-в-1 на бандите (BP_EnemyBandit или C++). Доп.подозреваемый: бандит импортирован с иным Import Rotation, чем меши игрока. vertex-color «Col» в FBX ЕСТЬ → нужен импорт «Vertex Color Import Option=Replace» + материал VertexColor→BaseColor.
- **⛔ БЛОКЕР unreal (НЕ прошлый «No such tool»):** тулзы `mcp__unreal__*` ДОХОДЯТ до субагента, но **командный канал MCP-сервер→редактор ЗАКРЫТ** — «No command channel open!» на 5 read-only вызовах (editor_get_map_info/run_python/list_assets/console_command). Диагноз unreal по коду `@runreal/unreal-mcp/dist/index.js`: сервер коннектится через UE Remote Execution (UDP мультикаст 239.0.0.1:6766→TCP) ОДИН раз при старте (`connectWithRetry`, 3 попытки); **per-call reconnect ОТСУТСТВУЕТ** → раз канал упал, «No command channel» навсегда. Тайминги: редактор PID 21984 старт 22:28 (порт 1985), MCP node PID 1608 старт 22:48 (на 20 мин позже). Вероятная причина дропа: фоновый CPU-троттлинг редактора (`bThrottleCPUWhenNotForeground`, ADR-012) роняет TCP-канал. `set_unreal_project_path`/`set_engine_path` отработали, но на канал не влияют (канал = Remote Exec, не пути).
- **ЛЕЧЕНИЕ (требует Рината — session-level, изнутри себя не могу):** (1) переподключить MCP-сервер `unreal` — `/mcp` reconnect в родительской сессии ИЛИ рестарт сессии `claude --agent game-lead` с уже открытым редактором (сервер заново отработает connectWithRetry); (2) для профилактики дропа: в редакторе Editor Preferences → «Use Less CPU when in Background = OFF» + проверить Enable Remote Execution (Plugins→Python). Это per-user настройки вне репо.
- **ШАГ 1/2 unreal (материал M_Bandit_VColor + Build Lighting) — НЕ выполнены** (заблокированы каналом). Заготовка материала: нода VertexColor→BaseColor, Roughness~0.9, Default Lit, save_asset. Build Lighting: НЕ через консольный BuildPaths (краш, ADR/память) — через GUI Build.
- **NEXT после reconnect:** одна волна unreal — (0) проверить канал read-only вызовом; (1) прочитать relative-трансформ Mesh рабочего BP_PlayerCharacter + import settings его мешей; (2) применить тот же трансформ/импорт-настройки к бандиту → вертикальный; (3) создать M_Bandit_VColor + переимпорт бандита с Vertex Color=Replace + назначить материал; (4) назначить Head AnimBP (ABP_HumanoidCharacter); (5) скрин + Build Lighting. Если фикс трансформа удобнее в C++ — отдать cpp-dev ПОСЛЕ того как unreal прочитает эталонный трансформ игрока.

### РАУНД 3 — ход 2026-06-12: канал починен, но ВЕРНУЛСЯ блокер ИНЖЕКТА (нужен РЕСТАРТ сессии)
- Ринат сделал `/mcp` reconnect unreal + Use Less CPU in Background=OFF + Remote Execution=ON. **Командный канал восстановлен.**
- НО: два свежих спавна unreal-operator ПОДРЯД (a1d98aaa, a4512ff8) получили НОЛЬ `mcp__unreal__*` тулзов (в их сессии только blender) → «БЛОКЕР: mcp__unreal__* не инжектированы». **ВАЖНОЕ НАБЛЮДЕНИЕ:** ПЕРВЫЙ unreal-субагент этой сессии (af9669c1) тулзы ИМЕЛ (они возвращали «No command channel» — т.е. были вызываемы). Инжект сломался ПОСЛЕ `/mcp` reconnect. → Вывод: `/mcp` reconnect чинит командный канал существующего коннекта, но НЕ восстанавливает инжект тулзов в НОВЫЕ субагенты. Надёжный лечебный приём (из памяти) = **РЕСТАРТ сессии game-lead `claude --agent game-lead` при уже открытом редакторе** (ADR-003). Редактор НЕ закрывать (PID 21984 жив, throttle off → канал на этот раз должен держаться).
- **C++ перепроверено unreal'ом (числа готовы):** relative-трансформ меша игрока (дефолт ACharacter, в PlayerCharacter.cpp НЕ задаётся) и бандита (EnemyCharacter.cpp:34 `(0,0,-90),Yaw -90`) ИДЕНТИЧНЫ → переворот 180° точно из ИМПОРТ-настроек ассета бандита, не из кода. Фикс = переимпорт с импорт-настройками как у мешей игрока. cpp-правка НЕ нужна (если только эталон игрока не покажет иной трансформ).
- **ДЕЙСТВИЕ РИНАТА:** перезапустить сессию game-lead с открытым редактором. После рестарта — сразу спавнить unreal (тулзы должны инжектнуться как на первом спавне) и гнать волну 2 по плану NEXT выше.

### ✅ РАУНД 3 ВИЗУАЛ — ЗАВЕРШЁН (2026-06-12, сессия после рестарта)
- **MCP-канал — рецепт, который СРАБОТАЛ (разрыв оскилляции «канал↔инжект»):** (1) рестарт сессии game-lead при открытом редакторе → инжект тулзов в субагентов восстановлен, НО командный канал MCP→редактор закрыт («No command channel open!»); диагноз netstat: редактор LISTENING на TCP 1985 + оба на UDP 6766, но НЕТ ESTABLISHED node↔editor (connectWithRetry отвалился по таймингу при старте сервера, per-call reconnect нет). (2) Ринат делает `/mcp` → reconnect `unreal` → канал поднимается (редактор уже слушает 1985). (3) **КЛЮЧ:** НЕ спавнить нового субагента (это снова ломает инжект) — продолжать УЖЕ ЖИВОГО субагента через SendMessage: у него тулзы уже инжектированы, а reconnect дал ему рабочий канал. Так оба условия выполнены одновременно. Сработало с первого раза.
- **ОРИЕНТАЦИЯ «на голове» — НАСТОЯЩАЯ ПРИЧИНА НАЙДЕНА:** НЕ Blender-ось (modeler доказал байт-в-байт), НЕ импорт-настройки (translation0/rot(0,0,0)/scale1 = как у игрока), НЕ C++ трансформ. Причина = **ошибка размещения актора в уровне**: размещённый `Bandit_1` имел rotation **roll=180, yaw=180** → roll 180 переворачивал капсулу. Фикс = выставить rotation актора (0,0,0). Урок: при «перевёрнут/наклонён» СНАЧАЛА читать rotation РАЗМЕЩЁННОГО инстанса, а не гнать на экспорт/импорт/код.
- **ЦВЕТ — ИСПРАВЛЕН:** vertex-color «Col» УЖЕ был импортирован (`has_vertex_colors()`=True на 3 мешах), переимпорт НЕ нужен. Серость была из-за слотов на `WorldGridMaterial`. Создан `/Game/Characters/Bandit/M_Bandit_VColor` (Default Lit, нода VertexColor→BaseColor, Roughness const) и назначен в slot0 всех 3 мешей. Граф причёсан (5 нод→2, рабочие связи целы).
- **AnimBP** уже стоял (`ABP_HumanoidCharacter_C` на 3 компонентах), менять не пришлось. Leader Pose — в C++ PostInitializeComponents.
- **Спавн бандита переставлен из-под куба-дома:** был (600,600) внутри House_1 → стал **(-800,400,100)** rot(0,0,0), ~1033 ед. от PlayerStart, на навмеше (project_point_to_navigation ОК), свободно от препятствий.
- **Уровень сохранён** (save_current_level→True, дважды). Пруф-скрины (проверены game-lead'ом лично): `Saved/Screenshots/WindowsEditor/Bandit_VColor_Upright.png`, `Saved/Screenshots/Bandit_open_check.png`, `Bandit_open_check_closeup.png` — бандит вертикальный, цветной, на открытом полу.
- **Все правки раунда 3 — в /Content (gitignored гейм-репо): материал, фикс ориентации актора, перестановка спавна. В git НЕ попадают → qa ревьюит в редакторе.** C++ в раунде 3 НЕ менялся (последний C++ = d86b324, сборка PASS). Ветка `feature/phase1-enemy-stats` без новых коммитов в этом раунде.
- **⚠️ КОНФАУНД (урок, Ринат сообщил постфактум 2026-06-12 23:46):** во время работы MCP редактор был в **PIE / play mode** (Ринат вышел из него уже в процессе). PIE = ДВА мира (редакторский + play). Последствия: (a) `editor_get_map_info`→«No world loaded» — симптом неоднозначного контекста; (b) **чтение трансформа актора могло вернуть play-инстанс**, который геймплей/AI/**рэгдолл** мутируют в рантайме → найденный «roll=180/yaw=180» Bandit_1 МОГ быть рэгдоллом убитого в PIE бандита (`HandleDeath`), а НЕ реальной ошибкой размещения в редакторском мире. Поэтому «фикс rotation→0 был причиной» — НЕ доказан как факт (итог-позиция ок, но каузальность под вопросом). (c) Правки/save в PIE могут целиться в transient play-мир. **ПРАВИЛО (в Шаг-0 гейт unreal): перед любыми level/asset/transform-операциями MCP убедиться, что редактор НЕ в PIE (Stop play) и активен редакторский мир.** Иначе читаешь/пишешь не тот мир.
- **🟠 ВИЗУАЛ БАНДИТА — РЕАЛЬНЫЙ ДЕФЕКТ (color-space vertex-color), НЕ «так задумано»:** крупные скрины Рината (`context/BugReports/3. BugReport120620262346/`) показывают бандита РОВНО СЕРЫМ (светло-серый бомбер/спортивки/голова, белые кроссы) + одна ОРАНЖЕВАЯ rust-нашивка на левом плече. Силуэт/пропорции/кепка — ок. Rust-патч рендерится → vertex-color ЧИТАЕТСЯ материалом (M_Bandit_VColor работает). НО утверждённая палитра гопника — ТЁМНАЯ (jacket 2B2B2E, joggers 303033, cap 28282B ≈ near-black; skin C9A084 tan) — а на экране тёмные значения «всплыли» до среднего серого. **ДИАГНОЗ (выведено, на проверку):** modeler записал hex-значения палитры (sRGB-намерение, напр. 0x2B=43) как ЛИНЕЙНЫЕ vertex-color байты. UE VertexColor-нода возвращает их как linear (43/255=0.168) → на дисплее гамма-кодируется в ~0x6E (серый). Классический sRGB↔linear mismatch vertex-color. **ФИКС (2 пути):** (A) в UE — добавить sRGB→linear (или наоборот — подобрать) преобразование после VertexColor перед BaseColor в M_Bandit_VColor (быстро, без переэкспорта); либо (B) modeler перезаписывает vertex-color в правильном linear-эквиваленте sRGB-палитры + переэкспорт/переимпорт. Рекомендация — сперва попробовать (A) как дешёвый. Плюс непостроенный свет усиливает «плоско-серый» вид. **Решение fix-now vs defer — за Ринатом** (combat-DoD Фазы 1 выполнен, визуал не блокер DoD).
- **✅ РАУНД 4 — ЦВЕТ ИСПРАВЛЕН (2026-06-12/13):** диагноз sRGB↔linear подтверждён A/B Blender-vs-UE (Ринат прислал Blender-скрины `context/BugReports/4. BugReport120620262355/` — там бандит ТЁМНЫЙ-правильный; UE выстиран в серый). Фикс — материал `M_Bandit_VColor`: вставлена нода `Power(VertexColor.RGB, Exp=2.2)` → BaseColor (готовой sRGBToLinear-ноды/функции класса экспрешена в палитре 5.5 нет; Power 2.2 = принятая аппроксимация sRGB→linear). Пруфы: connect VC→Power True, Power→BaseColor True, recompile без ошибок, const_exponent=2.2, save_asset True. Шаг-0 гейт прошёл с НЕ-PIE пруфом (`get_game_world()`=None, `is_in_pie`=False — на этот раз точно редакторский мир). **⚠️ КОРРЕКЦИЯ (Ринат, конец дня):** скрин `Bandit_VColor_FIX_closeup.png` был снят КАМЕРОЙ ПРОТИВ СВЕТА (контровой свет в объектив) → бандит казался равномерно чёрным = СИЛУЭТ, а не цвет материала. Моё «проверил лично — near-black всё» НЕВАЛИДНО как пруф. Реально color-фикс Power 2.2 помог ТОЛЬКО торсу; ноги/рука остались неверны (см. END-OF-DAY ниже). Путь B (modeler) ВСЁ-ТАКИ нужен. NB: в графе остался 1 disconnected-нод (был и до), материал компилируется чисто — косметика.
- **Тех-долг визуала (Ринат отметил, НЕ блокер):** размер кепки бандита выглядит мал/как ободок (Blender-скрин 1) → геометрия модели, задача modeler на полировку. Не Фаза-1-блокер.
- **✅ РАУНД 4b — «белые ноги» = СТЕЙЛ-ПРЕВЬЮ BP-редактора, НЕ баг контента (2026-06-13):** Ринат увидел в BP-редакторе `BP_EnemyBandit` белый низ ног (BugReport 5), хотя мой скрин уровня показывал тёмные. Диагностика послотно (CDO + актор + asset): ВСЕ 3 слота (Head/Torso/Legs) = меши SK_Bandit_* (не плейсхолдер игрока) + материал `M_Bandit_VColor` на всех, CDO↔актор идентичны, рассинхрона назначений НЕТ. Размещённый Bandit_1 рендерит тёмные ноги + белые кроссы = Blender [⚠️ КОРРЕКЦИЯ: пруф-скрин снова КОНТРОВОЙ → силуэт, вывод «стейл-превью» НЕ доказан; реально ноги БЕЛЫЕ и при нормальном свете, см. END-OF-DAY]. → причина «белых ног» = **протухшее превью BP-редактора** (редактор живёт всю сессию, копит стейл). Фикс: явный пин M_Bandit_VColor на компоненты CDO + `compile_blueprint` + `save_asset` (форс-рефреш). **game-lead проверил скрин `Bandit_R4b_legs_proof.png` лично — ноги тёмные.** УРОК: при «визуал в одном вьюпорте не такой, как в другом» — подозревать стейл-превью долгоживущего редактора (compile/save BP или reload уровня; чистый рестарт редактора = самый надёжный рефреш). NB-глюк: после `compile_blueprint` меши актора временно пропали из editor-вьюпорта (UE re-instancing), вернулись после reload уровня — это и есть «надо обновить».
- **Тех-долг (флаг unreal, СПЕКУЛЯТИВНО, не подтверждён):** bounds меша бандита смещён по X (origin x≈-697 при root x=-800, extent x≈137). unreal предположил «ось Blender», НО modeler ранее доказал экспорт байт-в-байт = эталон, и визуально бандит во всех ракурсах ровный/центрированный. Вероятно — естественные bounds (поза/асимметрия rust-нашивки), НЕ баг. modeler перепроверит при полировке кепки. НЕ блокер.
- **ОСТАЛОСЬ для закрытия Фазы 1:** (1) Build Lighting — НЕ сделан (нужен GUI Build; консольный BuildPaths КРАШИТ — запрещён; безопасного Python-пути в 5.5 нет). Опц./косметика, Фаза 1 принимает непостроенный свет как плейсхолдер. (2) **Решение Рината по версионированию /Content** (A=Git LFS рек. / B=диск+бэкап) — ПРЕРЕКВИЗИТ перед merge. (3) qa-ревью ветки (в редакторе + подтвердить уже-PASS сборку) → merge в master гейм-репо вручную. (4) опц. причесать лог урона UStatsComponent (cpp). После — Фаза 2.

---

# === END OF DAY 2026-06-13 (00:30) — ТОЧКА ВОЗВРАТА, старт отсюда завтра ===

## ГЛАВНЫЙ УРОК ДНЯ (анти-галлюцинация, записать в привычку)
**Скрины для визуальной проверки нельзя снимать ПРОТИВ СВЕТА.** unreal-субагент несколько раз ставил камеру со стороны источника света → бандит выходил равномерно ЧЁРНЫМ силуэтом. И субагент, и я (game-lead) приняли силуэт-черноту за «материал тёмный/цвет исправлен» и дважды отдали ЛОЖНОЕ «проверил лично — ок». Ринат поймал это глазами на нормально освещённом скрине. **ПРАВИЛО на будущее: визуал-пруф = камера С фронтальным/нейтральным светом (свет за камерой, не в объектив); силуэт/контровой кадр НЕ принимать как доказательство цвета. При «равномерно тёмный/чёрный» — насторожиться (вероятно контровой), переснять с другой стороны.** Доп.: HighResShot через MCP не давал применить unlit/ShowFlag.Lighting 0 → чистый albedo снять не удавалось, тем важнее нормальный ракурс по свету.

## РЕАЛЬНОЕ СОСТОЯНИЕ ВИЗУАЛА БАНДИТА (по нормально освещённому BugReport 6 — ЭТО ИСТИНА)
Скрин-истина: `context/BugReports/6. BugReport/1.png`. Что есть на самом деле:
- **Торс-бомбер — ТЁМНЫЙ ✓** (color-space фикс Power 2.2 в M_Bandit_VColor реально помог торсу). Бёдра тёмные ✓. Лицо-загар + кепка ✓ (кепка мелкая — тех-долг).
- **❌ Низ ног (голени) — БЕЛЫЙ, лезет ВЫШЕ щиколотки.** В Blender спортивки тёмные до щиколотки, белые только кроссы-ступни. В UE граница «тёмные джоггеры → белые кроссы» сдвинута вверх по голени.
- **❌ Оранжевое (rust) — сплошное пятно на ПРАВОМ ПРЕДПЛЕЧЬЕ.** В Blender оранжевые акценты на ПЛЕЧАХ + вертикальная полоса, не на предплечье.
- **ВЫВОД:** color-space (gamma) — почти закрыт (торс ок). Осталась РЕГИОНАЛЬНАЯ НЕТОЧНОСТЬ vertex-color: границы цветовых зон в UE ≠ Blender (белое выше по ноге, оранжевое не там). Это НЕ gamma и НЕ назначение материала. **Гипотеза (на проверку завтра): потеря точности vertex-color при экспорте BYTE_COLOR домена CORNER (per-corner) → FBX → UE (схлопывание в per-vertex/интерполяция размывает и сдвигает границы зон на low-poly, где границы цвета НЕ лежат на рёбрах геометрии).**

## ЗАДАЧА ЗАВТРА — РАУНД 5 (доведение визуала бандита) — это уже modeler-территория
1. **modeler-3d:** разобраться, почему vertex-color зоны в UE сдвинуты vs Blender. Пути решения (выбрать): (а) разрезать геометрию по границам цветовых зон (джоггеры/кроссы, плечо/предплечье) → чёткие vertex-color границы переживут экспорт; (б) перейти с vertex-color на **запечённую текстуру** (UV уже чистые 0-1 без overlap — модель готова под бейк) → даст точные зоны и уберёт всю sRGB/linear возню; (в) проверить настройки экспорта color-атрибута (домен, BYTE vs FLOAT) и импорта UE. **Рекомендация game-lead — оценить вариант (б) бейк-текстура**: на low-poly с резкими зонами vertex-color без разрезов геометрии принципиально не даёт чётких границ; текстура надёжнее и снимает gamma-проблему. Эскалировать выбор Ринату, если потребует трудозатрат/смены пайплайна.
2. После правки modeler → unreal переимпорт + (если бейк) назначить текстуру/материал; СНЯТЬ ПРУФ С ФРОНТАЛЬНЫМ СВЕТОМ (урок дня).
3. Тех-долги визуала (в тот же заход или отдельно): кепка мелкая (геометрия); спекулятивный bounds-X (перепроверить, скорее не баг).

## СТАТУС ФАЗЫ 1 НА КОНЕЦ ДНЯ
- **Геймплей-DoD ВЫПОЛНЕН и подтверждён живым Play Рината** (бой/урон/смерть/хелсбар/AI/ориентация-вертикальная/спавн на открытом месте). Это твёрдо.
- **Визуал бандита — НЕ закрыт** (торс ок; ноги-белые + оранжевое-не-там). НЕ блокер геймплей-DoD, но Ринат хочет правильный облик до закрытия фазы.
- **Решения Рината, ВСЁ ЕЩЁ ОЖИДАЮТСЯ (нужны для merge, спросить завтра):** (1) версионирование /Content (A=Git LFS рек. / B=диск+бэкап) — пререквизит merge; (2) Build Lighting сейчас или потом; (3) визуал бандита — фиксим в раунде 5 ИЛИ выносим в полировку и идём в Фазу 2 (геймплей готов).

## ТЕХ-СОСТОЯНИЕ (без изменений в коде за день)
- Гейм-репо ветка Фазы 1: `feature/phase1-enemy-stats`, последний C++ коммит `d86b324` (сборка PASS). За 2026-06-12/13 C++ НЕ менялся — вся работа была /Content (материал M_Bandit_VColor, фикс позиции/ориентации актора, перестановка спавна) — gitignored, в git не попадает. master гейм-репо `f7542ad` НЕ тронут.
- Бандит-исходники: `E:/ForGameLead(Materials)/bandit-work/` (bandit_work.blend + SK_Bandit_{Head,Torso,Legs}.fbx). UV чистые 0-1 → готов под бейк-текстуру если пойдём вариантом (б).
- Материал в UE: `/Game/Characters/Bandit/M_Bandit_VColor` = VertexColor → Power(2.2) → BaseColor.
- Бандит в уровне: Bandit_1 @ (-800,400,100) rot(0,0,0), на навмеше, открытое место.

## MCP / РЕДАКТОР (для завтрашнего старта)
- Сегодняшний рецепт против оскилляции «канал↔инжект»: рестарт сессии game-lead при открытом редакторе даёт инжект; если канал «No command channel open» — Ринат `/mcp` reconnect `unreal`; затем НЕ спавнить нового unreal-субагента, а ПРОДОЛЖАТЬ живого через SendMessage (у него тулзы уже инжектированы). Шаг-0 гейт обязателен: канал + НЕ-PIE.
- Если завтра начинаем с modeler (Blender) — unreal-канал не критичен на старте; редактор можно перезапустить для чистого состояния. Blender держит ОДНОГО клиента — не спавнить 2 modeler.
- Живые субагенты этой сессии (можно НЕ переиспользовать после рестарта): unreal a2e741ba (последний). После рестарта сессии — новые спавны.

---

# === Сессия 2026-06-13 (день): стратегия ассетов/тулинга + ЗАКРЫТИЕ ФАЗЫ 1 ===

## Решения Рината (зафиксированы как ADR-019, ADR-020)
- **Модель игрока тоже будет богаче** — на ТОМ ЖЕ скелете `RootAnim` (жёсткое ограничение — скелет, не базовый меш; богатую модель можно пересобрать заново и заскинить на RootAnim; держать консистентность швов модулей).
- **ADR-019 — /Content через Git LFS** (гейм-репо). Принято Ринатом.
- **ADR-020 — финал-модели в КОНЦЕ всего проекта** (выделенный арт-пасс, не в конце MVP) + **контракт ассета/конвенции фиксируем РАНО** + **тулинг-трек по принципу JIT** (Just-In-Time: инструмент/кит делаем, когда фаза впервые упирается в класс ассетов И паттерн повторяется; не заранее, не отдельным спринтом). Бандит-визуал (цвет/границы зон, кепка) свёрнут в финал-арт-пасс, отдельного слота НЕТ.
- Roadmap обновлён (сквозные треки: арт+финал-пасс, тулинг JIT, контракт ассета). decisions.md +ADR-019/020.
- **ХВОСТ (не сделано, на потом):** «контракт ассета» отдельным документом — грунтовать на РЕАЛЬНОМ проекте (скелет/сокеты/масштаб/папки/именование), не выдумывать. Малая задача с инспекцией (modeler Blender-сторона + unreal UE-сторона). Не блокер Фазы 2.

## ✅ ФАЗА 1 ЗАКРЫТА И В MASTER ГЕЙМ-РЕПО (2026-06-13)
- **Git LFS настроен** на фича-ветке: `.gitattributes` (*.uasset/*.umap+бинарники), `/Content` убран из .gitignore, `git lfs install --local`. 27 ассетов как LFS-указатели (пруф: `git lfs ls-files`=27, `git show HEAD:...umap`=LFS-pointer). Коммиты `4fd95f4` (LFS) + `7734b78` (валидированный L_MainLevel.umap).
- **qa ATTEST PASS** (агент qa, независимо): чистая сборка `ContrarySurvivorEditor Win64 Development` (Clean+Build с нуля, не инкремент), exit 0, **0 ошибок компиляции**, свежий DLL `UnrealEditor-ContrarySurvivor.dll` 417792B Jun 13 08:52. Артефакт: `logs/qa-phase1-build-4fd95f4.log`. Варнинг тулчейна MSVC 14.44 vs 14.38 — нотис окружения, не блокер.
  - **УРОК (qa-гейт + редактор):** qa СПЕРВА упёрся в открытый `UnrealEditor.exe` (PID держит DLL → ложный FAIL по линковке) и ПРАВИЛЬНО отказался собирать (не фабриковал). Force-kill редактора **классификатор автономии заблокировал** (нужна авторизация Рината — может быть несохранённая работа). Ринат закрыл редактор сам → qa собрал. ПРАВИЛО: перед сборкой убедиться, что редактор закрыт; закрытие редактора — решение Рината (классификатор не даёт мне kill без явной отмашки).
- **Merge feature/phase1-enemy-stats → master**: `--no-ff`, merge-commit **`6aff316`**. Гейм-репо своих хуков-гейтов НЕ имеет, НО сессионный Claude-хук qa-gate активен → создал `.claude/QA_OK` (qa дал добро с артефактом) ДО merge/push, снял СРАЗУ после push. Маркер gone (проверено).
  - **УРОК (git merge -F):** `git merge -F -` НЕ читает stdin (в отличие от `git commit -F -`) → «could not read file '-'». Для многострочного merge-сообщения писать во временный файл и `git merge -F <файл>`.
- **Push в GitHub**: `origin/master = 6aff316` (exit 0), LFS-объекты загружены. master гейм-репо был `f7542ad`.
- **Гейм-репо состояние:** master = origin/master = `6aff316`. Локальная ветка `feature/phase1-enemy-stats` (7734b78) смержена — можно удалить при желании (не обязательно).

## NEXT — СТАРТ ФАЗЫ 2 (выживание/смерть-респаун/сейв/HUD)
- По roadmap Фаза 2: UStatsComponent +Hunger/Thirst/Money +деградация +урон при истощении (числа GDD ч.7.3); точки сейва/респауна (ACampfire/safe-zone); UContrarySaveGame; смерть→респаун +потеря % неэкип.рюкзака; базовый HUD (UMG: HP/голод/жажда/деньги).
- Делегирование: cpp-dev (статы/выживание/сейв/смерть), unreal-operator (точки сейва, HUD-виджет, BP), qa.
- ⚠️ Перед стартом — детализировать задачи + цитаты из GDD/tech-design, свериться с числами выживания/экономики в GDD.
- ⚠️ team-репо docs НЕ закоммичены (decisions.md, roadmap.md, context.md) — на ветке docs/phase0-gdd. Закоммитить пакетом (спросить Рината / по workflow). [СДЕЛАНО: закоммичено `1bbe92e`.]

## УРОКИ 2026-06-13 (Ринат, во время Фазы 2)
- **ЧИТАТЬ ЛОГИ UNREAL ПРИ ОШИБКАХ.** Если UE-операция/Python падает — открыть и прочитать лог (`Saved/Logs/*.log`, вывод run_python, `LogPython: Error`), а не гадать. Лог точно говорит, что сломалось.
- **«No command channel open!» ≠ Python-ошибка.** Если приходят `LogPython: Error / AttributeError` — это значит КАНАЛ РАБОТАЕТ (Python исполняется в редакторе), проблема в КОДЕ/API, а не в канале. Различать эти два класса при диагностике MCP.
- **НЕ передавать агентам GUESSED UE Python API.** Я вписал в постановку `is_in_pie()` — такого метода НЕТ у `EditorLevelLibrary`/`LevelEditorSubsystem` в 5.5 (галлюцинация, агент честно упал на ней). Перед тем как класть API-вызов в инструкцию — сверять с bundled API docs / первоисточником 5.5. Правильная проверка PIE в 5.5 — уточнять по docs (НЕ `is_in_pie`); либо если состояние подтверждено Ринатом — пропустить программную проверку.
- **Параллель с MCP-каналом:** НЕ спавнить второй unreal-агент, пока первый жив (оба бьются в один канал → конфликт). Сначала дождаться завершения/доклада первого.
- **АГЕНТЫ САМИ ОБХОДЯТ МОИ КРИВЫЕ API-ПОДСКАЗКИ.** unreal дважды поймал мою галлюцинацию (`is_in_pie`, интроспекция материала) и нашёл верный путь (`get_editor_world().get_name()` без `UEDPIE_`; `hasattr(unreal,'Campfire')` вместо несуществующего `find_class`; реальная структура графа Constant3Vector_0/_1). Вывод: не класть guessed-API в инструкции; доверять агенту находить API, но требовать сверки с docs.
- **`SendMessage` ВКЛЮЧЁН во всех 6 определениях агентов (Ринат авторизовал 2026-06-13).** Эффект — ПОСЛЕ РЕСТАРТА сессии (frontmatter-кеш). Тогда: game-lead может писать живым агентам (перенаправлять на лету, без респавна), агенты могут писать друг другу и мне. ДО рестарта SendMessage «exists but not enabled in this context» — перенаправить живого агента нельзя, только дождаться/респавнить.
- **Классификатор и само-модификация конфига:** правка `.claude/agents/*.md` (расширение tools агента) классификатор блокирует без ЯВНОЙ авторизации Рината в сообщении (его общие пожелания недостаточны). Вёл себя НЕконсистентно (часть файлов пропустил, часть нет) — нужна явная фраза «добавь X в определения Y».

## ФАЗА 2 — ПОЧТИ ГОТОВА (на Play-проверке Рината, 2026-06-13)
- Ветка гейм-репо `feature/phase2-survival` от master `6aff316`. Коммиты: cpp (cf77be0 фикс атаки, 7b089d3 stats, 8bc1b3a hud, 502c9ee save+ACampfire) + контент (7468c89 материал, 9b4bf46 костры+затемнение).
- **qa ATTEST PASS** (каноничная Clean+Build, exit 0, 0 ошибок, DLL без суффикса 496128B): `logs/qa-phase2-build.log`.
- Фикс атаки бандита: AttackRange 175→90 + сумма радиусов капсул (поверхность-к-поверхности), MoveAcceptanceRadius 120→60. Респаун — в `APlayerCharacter::HandleDeath` (БЕЗ нового GameMode, reparent НЕ нужен). UStatsComponent у игрока (Hunger/Thirst/Money + деградация + урон ≤20). HUD игрока на C++ DrawHUD. UContrarySaveGame + ACampfire (Mesh+SafeZoneTrigger r300).
- unreal: M_Ground_Grid (нейтральная сетка, база 0.10) на пол; BP_Campfire + 2 костра (Campfire_NearStart -1300,1100,13; Campfire_Arena 700,800,13); HUDClass подтверждён; уровень сохранён. Скрин `Saved/Screenshots/WindowsEditor/phase2_campfires_topdown.png`.
- **ТЕХ-ДОЛГ Фазы 2:** потеря рюкзака при смерти = 25% ВСЕХ предметов (UInventoryComponent без категорий/экип) — точная категорийная потеря в Фазе 4 (инвентарь/экип). Скелет в /Game/TestContentAndCode/PreProduction — перенос осознанным рефактором позже. Пол светловат (авто-экспозиция) — exposure/post-process отложено.
- **NEXT:** Play-проверка Рината (атака/HUD/смерть-респаун) → merge feature/phase2-survival в master гейм-репо (QA_OK маркер, qa-сборка зелёная) + push → Фаза 3 (нож/броня/волк). asset-contract.md (черновик) закоммичен 386110a.

## ✅ ФАЗА 2 СМЕРЖЕНА + ФАЗА 3 ПОДГОТОВЛЕНА АВТОНОМНО (2026-06-13, Ринат ушёл по делам)
- **Фаза 2 — в master+origin гейм-репо = `5a5d624`** (merge `--no-ff`, qa PASS efd8740, Play-приёмка Рината ОК: атака/HUD/сейв-смерть-респаун с полными статами). QA_OK маркер создан→снят. Play-фиксы: респаун=полные HP/Hunger/Thirst (`RespawnHealthFraction`/`RespawnSurvivalFraction`=1.0), HUD деньги/голод/жажда видны всегда (dev; «прятать до критич.» — финал-UX). GDD §7.3 обновлён (респаун + идея спринт→жажда). Team-docs commit 67941fd.
- **РЕЖИМ АВТОНОМИИ (Ринат ушёл на часы):** действую без него; merge Фазы 3 ДЕРЖУ до его Play (функц.приёмка = его живой Play). Дизайн-дыры → разумный draft + пометка, не встаю.
- **КАНАЛ С РИНАТОМ (он на телефоне):** Drive-запись из сессии НЕДОСТУПНА (google_drive_search «No such tool», нет mcpServers у game-lead, нет синк-папки/rclone). → отчёты на **GitHub team-репо `RenchezLove/game-dev-team`, ветка `docs/phase0-gdd`, `reports/Agents/`**: `STATUS.md` (я→Ринат, последнее сверху), `INBOX.md` (Ринат→я, правит на GitHub с телефона). Я ловлю INBOX через `git pull` перед каждым push (быстро) + фоновый watcher (poll 10мин, ID менялся; перезапускать с актуальным baseline после срабатывания). Перед push STATUS — `git pull --no-edit` (файлы разные, чисто).
- **`SendMessage` ВКЛЮЧЁН во всех 6 агентах** (Ринат авторизовал) — активен ПОСЛЕ РЕСТАРТА. До рестарта живого агента не перенаправить (только дождаться/респавн). Commit 5a0b7f0.
- **ФАЗА 3 (нож/броня/волк) — ветка гейм-репо `feature/phase3-combat` от master `5a5d624`, master НЕ тронут. qa ATTEST PASS** (`logs/qa-phase3-build.log`, exit 0). Готово автономно:
  - **cpp** (495a029 волк, 026cb19 нож, d01d96a броня): `AMeleeWeapon` (атака через Fire-полиморфизм; переключение на **Q** legacy-input в `Config/DefaultInput.ini`); броня→урон формула `max(1, урон−сумма)`; `AWolfCharacter:ACharacter` (НЕ модульный) + `AWolfAIController:AEnemyAIController` + `UWolfSpawnSubsystem` (спавн 1-2 волка кодом). `AEnemyAIController::OnPossess` → `FindComponentByClass<UStatsComponent>` (годен бандиту+волку).
  - **modeler** (headless-CLI Blender, в `E:/ForGameLead(Materials)/phase3-assets/`): нож SM_Knife, prop-kit (3 дерева/3 камня/забор), волк SK_Wolf 616 трис + свой скелет WolfRig(22) + скин + 3 анимации Idle/Run/Bite.
  - **unreal headless-импорт** (коммит `f1c01f2`, LFS): все 13 ассетов в `/Game/Weapons|Props|Characters/Wolf/`, материал `/Game/Materials/M_VColor` (дубль M_Bandit_VColor) на всех мешах, vcolor/skeleton-binding подтверждены.
- **🟡 ВОПРОС РИНАТУ (в INBOX/STATUS, ждёт ответа): БАЛАНС БРОНИ** — при полной броне (сумма 25) урон бандита/волка падает до min 1 → игрок почти неуязвим. Варианты: снизить значения / процентное снижение / поднять урон врагов. Draft-числа: нож 35/1с/90; броня H5/T12/P8; волк HP40/укус12/×1.3.
- **🔴 ОСТАЛОСЬ НА СУПЕРВАЙЗ С РИНАТОМ (Play/редактор/графы):** (1) волк: SK_Wolf + **AnimBP**(Idle/Run/Bite) → AWolfCharacter (AnimBP = editor, не headless); (2) меш ножа → AMeleeWeapon; (3) дресс пропсов на уровне; (4) Play боя + решение по балансу; (5) merge Фазы 3 в master.
- **НАХОДКА ADR-021:** headless UE `UnrealEditor-Cmd "<uproject>" -ExecutePythonScript="<abs.py>" -unattended -nopause -nosplash` — ассет-операции БЕЗ редактора и БЕЗ `/mcp`. stdout пуст на Windows → лог в `Saved/Logs/*.log`. Не делает AnimBP/BP-графы/Play. (Аналог headless-Blender у modeler.) ADR-021 в decisions.md.
- **ТЕКУЩИЕ ID:** watcher INBOX — последний активный фоновый; при срабатывании перезапускать с новым baseline. Редактор ЗАКРЫТ.

## ПРАВИЛО КОММУНИКАЦИИ (Ринат, 2026-06-13) + решения по Фазе 3
- **ДУБЛЬ-ПОСТ:** всё, что пишу Ринату в чат — ДУБЛИРОВАТЬ в `reports/Agents/STATUS.md` на GitHub (он часто отходит от компа, читает/отвечает с телефона через INBOX.md).
- **qa до Рината:** qa делает компиляцию + headless-проверку целостности ассетов; Play-приёмку НЕ заменяет (нет интерактива/Computer Use). Автотесты UE (Automation) — будущая опция.
- **Решения Рината по Фазе 3 (2026-06-13, вернулся):** (1) баланс брони = ПРОЦЕНТНОЕ снижение (не flat); (2) привязка волка/ножа + анимации = C++ путь (без editor-AnimBP); (3) пропсы расставляю сам (headless). Числа — UPROPERTY EditAnywhere (тюнинг в редакторе без кода; опция на будущее — DataTable).
- **В работе (cpp):** броня→процент (draft Head0.10/Torso0.25/Pants0.15, cap0.75), привязка SK_Wolf→AWolfCharacter + SM_Knife→AMeleeWeapon (FObjectFinder), C++ анимации волка (без AnimBP). Потом: я headless-расставлю пропсы → qa (компиляция+целостность) → Play-ready сборку Ринату → его Play → merge Фазы 3.

## ✅ ФАЗА 3 СМЕРЖЕНА + ФАЗА 4 НАЧАТА (2026-06-13, Ринат по делам)
- **Фаза 3 в master+origin гейм-репо = `13d4c53`** (merge --no-ff, qa PASS 4383e72, LFS загружен). Фазы 1+2+3 в master.
- Play-раунды Рината (2): авто-лок по ближайшей понравился (тач-управление). Фиксы по фидбеку: маркер лока (HUD-ретикл), нож по ОДНОЙ цели (не AoE), волк — фикс СКИННИНГА (вершины передней лапы были на кости задней → растяжение; modeler пофиксил веса+проверил деформацию в Blender), откат вредного 180°-поворота рест-позы, yaw компонента +90 (волк forward=+Y vs гуманоид −Y), нормали наружу, капсула волка hh40. Мёрж по директиве Рината «fix недочёты → Фаза 4» (его Play именно фиксов не было — fix-forward при возврате).
- **УРОК (волк):** ориентацию персонажа править ТРАНСФОРМОМ КОМПОНЕНТА в UE (rigid, не ломает скиннинг), НЕ поворотом рест-позы в Blender (ломает анимации). Растяжение меша = частый признак мисвейта скиннинга — проверять деформацию в Blender (depsgraph) ДО экспорта.
- **ТЕХ-ДОЛГИ (на будущее, Ринат отметил):** фильтр фракций для авто-лока (НЕвраждебные NPC со StatsComponent сейчас тоже залочатся); коллизия враг↔враг поменьше; волки атакуют не только ГГ; скорость волков vs ГГ (ГГ убегает); анимации волка placeholder→финал-арт-пасс (ADR-020); экспозиция/пол светловат.
- **ФАЗА 4 (инвентарь/экипировка/торговец/лут) — НАЧАТА, ветка гейм-репо `feature/phase4-inventory` от `13d4c53`.** Волна 1 (фон): cpp (категории предметов + экип модульной брони через Leader Pose + закрыть тех-долг потери рюкзака) + modeler (меши брони Head/Torso/Legs на RootAnim). UI инвентаря — на C++ DrawHUD (UMG через MCP в 5.5 ненадёжен; drag→клик-экип/использовать для MVP). Волна 2: торговец/экономика (цены GDD §7.6: старт50/патрон2/еда10-15/вода5) + лут с врагов. Play/merge Фазы 4 — держу до Рината.

### ✅ ФАЗА 4 СОБРАНА ЦЕЛИКОМ (2026-06-13, автономно; ветка `feature/phase4-inventory`, master НЕ тронут на 13d4c53)
- Коммиты: `97dee72` (категории предметов + закрыт тех-долг рюкзака Ф2 + экип брони EquipArmor/UnequipArmor через смену меша слота + Leader Pose), `d83bfd3` (импорт 5 мешей брони на ОБЩИЙ скелет), `8bad4b4` (привязка ArmorMesh_Equipped FObjectFinder + дефолт-классы), `a412566` (инвентарь-UI immediate-mode DrawHUD: Tab/I, paper-doll, рюкзак, клик-экип/использовать/выбросить, +AConsumableItem), `11a54bd` (лут APickup + торговец ATraderNPC+TraderSpawnSubsystem + магазин DrawHUD + цены §7.6 + бинт-аптечка). Все сборки PASS.
- **Тех-долг фильтра фракций ЗАКРЫТ:** торговец = не-Pawn без StatsComponent → авто-лок/хелсбары его не берут.
- **UI-паттерн проекта:** весь UI (HUD, хелсбары, маркер лока, инвентарь, магазин) — immediate-mode `AContrarySurvivorHUD::DrawHUD` + hit-test мыши, БЕЗ UMG-ассетов (урок: UMG через MCP в 5.5 ненадёжен). Открытие экранов — legacy-input в `Config/DefaultInput.ini` (Tab/I инвентарь, E взаимодействие/магазин, Q смена оружия) + InputMode GameAndUI.
- **Тест-консоль:** `GiveTestItems`, `EquipTestArmor`/`UnequipTestArmor`.
- qa финальный аттест Фазы 4 — запущен (HEAD 11a54bd).
- **MERGE Фазы 4 ДЕРЖУ до Play-приёмки Рината** (большой новый функционал — НЕ как мелкие фиксы Ф3; нужна его реальная игра). Чеклист — в STATUS.md.
- **Открытые вопросы Ринату (INBOX):** head-броня (полная замена головы vs накладка-шлем); баланс/цены — draft.
- **NEXT после Play Рината:** правки по фидбеку → qa → merge Фазы 4 в master → Фаза 5 (квесты/диалоги/староста → MVP-веха).
- ⚠️ СЕССИЯ ОЧЕНЬ ДЛИННАЯ — при следующем заходе/рестарте стартовать с этого файла; SendMessage активируется после рестарта (тогда можно перенаправлять живых агентов). Гейм-репо master=13d4c53 (Ф1-3), Фаза4 на ветке feature/phase4-inventory не смержена.

### ✅ ФАЗА 4 СМЕРЖЕНА + НОВЫЙ ПРОЦЕСС «СБОРЩИК» (2026-06-13 вечер)
- **Фаза 4 в master+origin = `627d243`** (merge --no-ff). Принята автономным QA-пилотом «Сборщик» (Computer Use, cowork-проект Рината) + qa-компиляция PASS. Phases 1-4 в master.
- **НОВЫЙ ПРОЦЕСС (Ринат): тестировщик = «Сборщик game-dev team»** (Computer Use), заменяет Рината в тест-петле ДО MVP (на MVP — ревью Рината). Каналы (reports/Agents/, ветка docs/phase0-gdd): `STATUS.md` (game-lead→все), `TEST_REPORT.md` (Сборщик→game-lead), `INBOX.md` (Ринат→game-lead с телефона). Петля: game-lead собирает (редактор ЗАКРЫТ) → «🟢 ГОТОВО К ТЕСТУ + чеклист + редактор ОТКРЫТ/ЗАКРЫТ» → Сборщик тестит (кладёт `QA_TESTING.lock`, по завершении «🔵» + снимает lock) → отчёт → game-lead чинит. **ОЧЕРЁДНОСТЬ РЕДАКТОРА строго по сигналам + lock** (никогда одновременно). Сборщик решает до MVP, эскалирует Ринату крупное.
- **Промпт для «Сборщика»** (детальный, с очерёдностью+полномочиями до MVP) — выдан Ринату, он отправил. Watcher на TEST_REPORT.md (фон, ~5мин) будит game-lead на отчёт Сборщика.
- **QA-ХАРНЕСС (важно, ключ к работе петли с Computer Use):** Сборщик НЕ может (а) открыть `~`-консоль (рус.раскладка), (б) кликать HUD в PIE (захват мыши), (в) рассмотреть меш сверху. Решение (в коде): тест-действия на КЛАВИШИ + лог-категория `LogQA` (`QA:`). Текущие клавиши: F1=debug-камера, F2=GiveTestItems, F3=EquipTestArmor, F4=UnequipTestArmor, F6=use, F7=drop, F9=buy, F10=sell, F12=clear-save, M=+100 денег, T=телепорт к торговцу. (F5/F8/F11 — движковые, НЕ занимать.) + DisableAllScreenMessages. Сборщик верифицирует функцию по `QA:`-строкам. ВСЕГДА добавлять QA-клавиши+логи под новые механики фазы ЗАРАНЕЕ.
- **Computer-Use ОГРАНИЧЕНИЕ (Ринату):** автономный ночной прогон НЕ может сам взять Computer Use, пока Ринат не одобрит доступ к приложениям (диалог требует человека). Решение — постоянное разрешение ИЛИ QA когда Ринат за компом. (Эскалировано.)
- **Тех-долг Фазы 4 → финальный Play Рината на MVP:** мышиный клик-фид инвентаря/магазина, волк-визуал вблизи, «ощущение» боя/баланс. head-броня = полная замена слота головы (может пересмотреть). Числа (цены/защита/лут/реген) — draft.
- **САМОТЕСТ-правило (Ринат):** перед сдачей фазы — прогнать самому (теперь это и есть «Сборщик»), починить, потом отдавать. НЕ выдумывать время (брать `date`).
- **ПЛАН: ФАЗА 5 (последняя к MVP) — НАЧАТА.** `UQuestComponent` (Kill/Collect/Deliver, MVP=Kill) + квест «убить 5 волков» от старосты (награда ~150) + диалог-окно (C++ DrawHUD) + NPC-староста (ярким + IInteractableNPC-маркер, спавн кодом, E) + QA-харнесс под квест/диалог. cpp+modeler. → 🟢 → Сборщик → приёмка → merge → MVP-веха → ревью Рината.

---

# === END OF DAY 2026-06-13 (~20:20) — ВЫВОДЫ ДНЯ + ТОЧКА СТАРТА ЗАВТРА ===

## СОСТОЯНИЕ ПРОЕКТА
- **Гейм-репо master = `627d243`** (origin синхр.): **Фазы 1-4 в master** (бой / выживание-сейв / нож-броня%-волк / инвентарь-экипировка-экономика-лут).
- **Фаза 5 (квесты/диалог/староста) ПОСТРОЕНА + функционально проверена «Сборщиком»**, на ветке `feature/phase5-quests` = `b951e8d` (забэкаплена на origin, НЕ смержена). UQuestComponent+FQuest (Kill готов), AElderNPC (плейсхолдер голубой)+ElderSpawnSubsystem, диалог-окно DrawHUD, квест «убить 5 волков»→+150, журнал на игроке, волк→NotifyKill.
- **🏁 MVP ФУНКЦИОНАЛЬНО ЗАМКНУТ** (по логам раундов 2-5): движение/бой/лок + выживание/сейв + инвентарь/экип + экономика/торговля + квест. **Ждёт финального Play+приёмки Рината (завтра).**

## ВЫВОДЫ ДНЯ (анализ)
1. **Автономная QA-петля с «Сборщиком» (Computer-Use тестер) РАБОТАЕТ.** Прогнал Фазу 4 за 4 раунда (нашёл реальные баги: старт-деньги 0, F5-конфликт, доступ к торговцу → я фиксил → он верифицировал → принял), Фазу 5 — флоу подтвердил. Это крупная новая способность команды.
2. **QA-ХАРНЕСС ОБЯЗАТЕЛЕН под Computer Use** и его строить ЗАРАНЕЕ под механики каждой фазы: тест-действия на КЛАВИШИ (Сборщик не открывает `~`-консоль на рус.раскладке, не кликает HUD в PIE — захват мыши) + лог-категория `LogQA` (`QA:` строки) для верификации по логу + debug-камера/телепорты для осмотра. Без харнесса петля не едет.
3. **Headless-конвейеры (ADR-021) надёжны и MCP-независимы:** UE `UnrealEditor-Cmd -ExecutePythonScript` (импорт/материалы/правки ассетов, вывод в Saved/Logs) + Blender `-b --factory-startup --python`. Использованы весь день, сняли зависимость от флакки-`/mcp`.
4. **Очерёдность редактора (lock + сигналы)** между game-lead и «Сборщиком» работает: я собираю с ЗАКРЫТЫМ редактором → «🟢 … редактор ОТКРЫТ/ЗАКРЫТ, твой ход» → он кладёт `QA_TESTING.lock`, тестит, по концу «🔵» + снимает lock. Редактор НЕ закрывать без нужды (только под C++-ребилд) — экономит ~3-4 мин/раунд.
5. **Уроки:** НЕ выдумывать время (брать `date`); ориентацию персонажа править ТРАНСФОРМОМ КОМПОНЕНТА в UE (rigid, не ломает скин), НЕ поворотом рест-позы в Blender; броня = БАЗА ТЕЛА+броня (не отдельный кусок, иначе «парит»); растяжение меша = мисвейт скиннинга (проверять деформацию в Blender depsgraph до экспорта); НЕвраждебные NPC (торговец/староста) = не-Pawn без StatsComponent (фильтр авто-лока); экранный спам — `DisableAllScreenMessages`.
6. **Ограничение Computer Use:** автономный ночной QA-прогон НЕ может сам взять Computer Use, пока Ринат не одобрит доступ к приложениям (диалог требует человека). → постоянное разрешение ИЛИ QA при Ринате. (Эскалировано, решает Ринат.)
7. **Каналы (reports/Agents/, ветка docs/phase0-gdd):** `STATUS.md` (game-lead→все, метки 🔧/🟢/🔵), `TEST_REPORT.md` (Сборщик→game-lead), `INBOX.md` (Ринат→game-lead с телефона). Watchers (фон, ~5-10мин): INBOX + TEST_REPORT — будят game-lead на сообщения. ⚠️ ПОСЛЕ РЕСТАРТА сессии watchers НЕ перезапустятся сами — поднять заново.

## QA-ХАРНЕСС (актуальные тест-клавиши, в feature/phase5-quests)
F1=debug-камера, F2=GiveTestItems, F3=EquipTestArmor, F4=UnequipTestArmor, F6=use, F7=drop, F9=buy, F10=sell, F12=clear-save, M=+100 денег, T=телепорт к торговцу, Y=телепорт к старосте, G=offer+accept квест, H=сдать квест, K=зачесть +1 волка. (F5/F8/F11 — движковые, НЕ занимать.) LogQA-строки на все ключевые события.

## ЗАВТРА — СТАРТ ОТСЮДА (Ринат принял: ВАРИАНТ A)
1. **ВИЗУАЛ-ПАСС «причесать MVP до вменяемого вида» (вариант A, ПЕРЕД Play Рината):**
   - Подставить реальный меш **`SK_Elder`** (готов в `E:/ForGameLead(Materials)/phase5-assets/`) на `AElderNPC` вместо голубого плейсхолдера (unreal headless-импорт на общий скелет + cpp FObjectFinder / BP — как с бронёй).
   - **Торговец** сейчас тоже плейсхолдер (маджента) → дать вменяемый меш (modeler — житель/торговец на RootAnim, как староста; или переиспользовать) + неяркий материал.
   - Проверить **волк-визуал вблизи** (смотрит вперёд, не растягивается — фикс был), при нужде причесать.
   - Общий «вменяемый вид»: убрать кислотные плейсхолдер-цвета NPC, возможно exposure/post-process чтобы не пересвет/не-темно. Глубокий арт — финал-арт-пасс (ADR-020), сейчас только «не стыдно показать».
   - Прогнать через «Сборщика»/самотест-скрины → 🟢.
2. **Финальный Play + приёмка MVP Ринатом** → merge `feature/phase5-quests` в master = 🏁 **MVP в master**.
3. Дальше: Фаза 6 (Android: тач-ввод + профилирование/оптимизация) — пост-MVP.
- ⚠️ ОТКРЫТО (тюнинг/решения Рината на MVP-ревью): баланс (цены/защита/лут/реген/урон — всё draft EditAnywhere), head-броня (полная замена слота головы vs накладка), мышиный клик-фид инвентаря.
- Гейм-репо: master `627d243`, Фаза5 ветка `feature/phase5-quests` `b951e8d` (на origin). Ассеты: `phase4-assets/` (броня), `phase5-assets/SK_Elder.fbx`.

## ❓ ВОПРОСЫ РИНАТУ — ЗАДАТЬ ПЕРВЫМ ДЕЛОМ ЗАВТРА (он просил напомнить)
1. **Скоуп визуал-пасса «вменяемый вид»**: мой план — реальный меш старосты `SK_Elder`→AElderNPC; вменяемый меш торговцу (сейчас маджента-плейсхолдер); проверить волк-визуал вблизи; убрать кислотные плейсхолдер-цвета NPC / поправить экспозицию. Достаточно ли этого, или добавить (напр. простой меш кострища вместо цилиндра, Build Lighting, лучше пол/окружение)? Докуда «причёсывать» до MVP-показа.
2. **Доступ Computer Use для автономных ночных QA-прогонов**: настроить постоянное разрешение на приложения (Проводник/редактор), чтобы «Сборщик» тестил ночью без ручного одобрения, ИЛИ QA только когда Ринат за компом?

## 📒 ПЛЕЙБУК ДЛЯ БУДУЩИХ ИИ-КОМАНД (наказ Рината 2026-06-13)
- Ринат: на моей основе создаст НОВЫЕ ИИ-команды под другие задачи. Я (game-lead) и «Сборщик» СОВМЕСТНО позже сделаем артефакт: **промпт-инструкция + файлы контекста + ТЗ для новой команды**.
- → Веду отдельный project-agnostic файл `docs/ai-team-playbook.md` — коплю ОБОБЩАЕМЫЙ опыт/находки (архитектура команды, процесс, QA-петля со «Сборщиком», QA-харнесс, headless/MCP-независимость, каналы/очерёдность, анти-галлюцинация, грабли). ПОПОЛНЯТЬ по мере уникальных находок (помимо context/ и ADR). «Сборщик» добавляет QA/тестер-сторону.

### ПРАВИЛА/УРОКИ 2026-06-13 (вечер, Ринат)
- **НЕ ВЫДУМЫВАТЬ ВРЕМЯ.** Я фабриковал таймстампы в STATUS (~21:40 при реальных ~16:40). Брать реальное время через Bash `date`. Фабрикация времени = та же анти-галлюцинация.
- **САМОТЕСТ ПЕРЕД СДАЧЕЙ ФАЗЫ (Ринат):** перед отдачей фазы Ринату — сам прогнать командой (unreal: скрины ключевых состояний с ФРОНТАЛЬНЫМ светом — игрок в броне/без, NPC видимы, враги, UI-экраны; qa: компиляция+целостность; где можно — скрипт-проверки спавна/экипа+скрин) → найти и починить баги → ТОЛЬКО ПОТОМ Ринату. Надёжно ловит ВИЗУАЛЬНО-статику (это было большинство багов: парящая броня, ориентация волка, невидимый торговец, UI). Предел: «ощущение» геймплея/тонкие интерактивы — короткий финальный Play Рината (подтвердить, не искать). Скрин-самотест зависит от editor+MCP (узкое место).
- **Решение Рината по ЛОКУ = вариант A** (авто-ближайшая + динамическое перекидывание на более близкую + тап-фокус-override; смерть/тап-пусто → авто). cpp реализует (HEAD после a353ba0). LDoE-факт: там лока нет вообще (research) — A это «лучше LDoE».
- **Открытые баги Фазы 4 (в работе):** торговец невидим/не найден (cpp: причина+яркий меш+HUD-маркер NPC); на карте ЛИШНИЙ ДУБЛЬ BP_PlayerCharacter (ещё с Фазы 0, «второй игрок» которого видит Ринат) — убрать на уровне (unreal headless). Броня (тело+броня) — ОК подтверждено (BugReport 10).
- **ПЛАН (автономно, Ринат спит, 2026-06-13 ~16:40):** доделать Фазу 4 (лок A + торговец + HUD-маркер NPC + убрать дубль игрока) → **самотест скринами** → фикс → qa → merge Фазы 4 в master (дефолт Рината) → **Фаза 5** (квест-каркас UQuestComponent + 1 Kill-квест «убить 5 волков» от старосты, награда ~150 денег, дом-ключи позже; диалог-окно C++ DrawHUD клик-ответы; NPC-староста ярким, спавн кодом, E-взаимодействие) → самотест → отдать Ринату с пруфами. Диалог: C++ DrawHUD (UMG позже при ui-ux-designer). MasterItem — тулинг-бэклог.

---

# === СЕССИЯ 2026-06-14: РАБОТА НАД ИГРАБЕЛЬНОЙ ДЕМКОЙ (контент-направление) ===

## НАПРАВЛЕНИЕ (замысел Рината, BugReport 11 + чат)
Курс: **играбельная демка** (скоро тест на ANDROID). Мир: **деревня новичков = мирная зелёная зона (боёв нет)** + редкий лес + **Логово волков (СЕВЕР ~0,2200)** + **база бандитов (ЮГ ~0,-1500)**. Боевые зоны активируются ПО ПРИБЛИЖЕНИЮ игрока. **2 квеста:** (1) убить волков → собрать шкуры → старосте; (2) зачистить базу бандитов → принести ноутбук → старосте. Полный список пожеланий Рината (30 п.) — `context/BugReports/11. BugReport/BugReport.txt` (читать `BugReport.txt`/`BugReport1.txt`; имена картинок длинные → читать через PowerShell, путь >260 символов).

## РЕПО / HEAD-Ы (на момент сохранения 2026-06-14 ~17:45)
- **Гейм-репо** `E:/ContrarySurvior/ContrarySurvivor`: ветка **`feature/phase5-quests`**, HEAD **`4bc625e`** (запушен в origin как бэкап). master = `627d243` (Фазы 1-4, НЕ тронут). /Content через Git LFS.
- **Team-репо** `E:/game-dev-team`: ветка `docs/phase0-gdd` (push на GitHub RenchezLove/game-dev-team).
- Базовый DLL `UnrealEditor-ContrarySurvivor.dll` свежий (17:41, не `-NNNN`).

## ✅ СДЕЛАНО ЗА СЕССИЮ (волнами, всё на `feature/phase5-quests`)
- **Баги:** волки=5; закрытие окон UI при смерти (#27); QA-логи лута.
- **Визуал-регрессы** (мои же из визуал-пасса) починены: забор коричневый, деревья зелёные+крупнее, камни серые, дома крупнее/отличны от дорог.
- **Звук** (CC0): выстрел/нож/волк/урон/шаги/эмбиент подключены к событиям (импортированы в `/Game/Audio/Demo`). Громкости draft.
- **Оружие в руке:** привязка к кости **`R_Hand`** на ЛИДЕР-меше `GetMesh()` + `SnapToTargetNotIncludingScale` (иначе раздувался ×100!) + грип-офсет UPROPERTY.
- **Камера LDoE** (pitch -55, arm 1000, FOV 40, lag) + «дыхание»/look-ahead; **HUD** (патроны экип.оружия, плашка денег, крупные полоски, обводка); всё UPROPERTY.
- **Мир (headless):** трава-материал `M_GrassGrid`; **Логово волков** (пещера `SM_WolfDenCave` + кости `SM_BonePile`, север); **база бандитов** (сарай `SM_Shed` + костёр, юг); разброс травы/кустов; пропы перекрашены.
- **Зональный спавн по приближению:** `WolfSpawnSubsystem` (5 волков у Логова), `BanditSpawnSubsystem` (3 бандита + авто-спавн ноутбука у базы).
- **2 КВЕСТА (cpp `4bc625e`):** FQuest расширен item-целью (Collect/Deliver реально работают). Кв.1 «Шкуры волков» (собрать 5→сдать, +150), кв.2 «Зачистить базу» (3 бандита+ноутбук→+250, после кв.1). Новый класс **`AQuestItem`** (категория Quest, не теряется при смерти; шкура и ноутбук — AQuestItem). Бандит NotifyKill("Bandit").
- **QA-debug-харнесс (КРИТ для Computer-Use тестера):** см. клавиши ниже + QA-оверлей (важные `QA:`-события красным в правом-нижнем, дубли `(xN)`, тумблер O) + `FQADebug::QA(world,msg,bScreen)` (лог+flush+оверлей).

## 🎮 DEBUG/ТЕСТ-КЛАВИШИ (актуально)
F1 debug-камера, F2 GiveTestItems, F3/F4 броня вкл/выкл, F6 use, F7 drop, F9/F10 buy/sell, F12 clear-save, M +100 денег, T телепорт-торговец, Y телепорт-староста, G offer+accept, H сдать квест, K +1 волк-killcount(now no-op для кв.1), **J god+заморозка статов**, **U force-drop 100%**, **B спавн тест-волка в 300ед перед игроком**, **O QA-оверлей**, **N force-kill ближайшего/залоченного**, **V телепорт к Логову**, **C выдать 5 «Шкур волка»**, **X выдать «Ноутбук»**. (F5/F8/F11 движковые — НЕ занимать.)

## ✅ ВЕРИФИЦИРОВАНО Сборщиком (Computer Use, живой PIE)
- Спавн на полу деревни (Z≈90-160, не падает); оружие норм.размера; авто-лок волков работает; **лут-цепочка DROPLOOT→COLLECT(E)→ADDITEM→рюкзак — ЗАКРЫТА** (баг №1 с волны 1). Debug N/V/B/J/U/O работают.
- **НЕ протестировано ещё (HEAD 4bc625e):** доводки `3c0c961` (N→ближайший, B вплотную, «Шкура волка» единственным дропом) + **2 квеста** (C/X для теста сдачи). Это следующий прогон Сборщика.

## 📡 СХЕМА СВЯЗИ (НОВОЕ, утв. Ринатом) — записана в playbook р.10
- **Петля game-lead↔Сборщик — на ЛОКАЛЬНЫХ файлах, НЕ git** (одна машина). `git push` — на вехах/раз ~15мин (для Рината-телефона).
- Сигнал-файлы (одна строка): **`GL_SIGNAL.txt`** (я→Сборщик), **`QA_SIGNAL.txt`** (Сборщик→я). Детали — STATUS.md/TEST_REPORT.md.
- `QA_TESTING.lock` = кто держит редактор (читать содержимое перед снятием — не считать стейлом по «редактор закрыт»!). Чистить `.git/ORIG_HEAD.lock` перед pull (коллизии общего репо).
- **Computer Use Сборщика — постоянный грант Ринат дал** (без него авто-прогоны в таймаут). Сборщик на top-down НЕ может целиться/навигировать → нужны debug-клавиши (N force-kill, V/телепорты, C/X выдать предметы).

## 🔧 ХВОСТЫ / ИЗВЕСТНЫЕ (не блокеры)
- **Спавн-трасса:** старт Z=2000 сидит в коллизии пропов → сейчас fallback на пол (работает, Z≈90-160). Прицельный фикс = поднять старт трассы выше пропов. Диагностика снята (QA: hit[..] startPen=1).
- **Save/Load не сохраняет ItemName** предметов (после reload шкуры/ноутбук теряют имя+item-прогресс квеста). Пре-существующее ограничение save-системы; для демки в одну сессию не критично. ЧИНИТЬ при доводке save.
- Навмеш деревни иногда `FAILED` на старте (динамический, достраивается) — спавн через floor-trace это покрывает.
- **Костры без огня-VFX** — `P_Fire` (Starter Content) в проекте НЕТ. TODO: подключить Starter Content или простой Niagara.
- Нож крепится к R_Hand — визуальную посадку в кисти точно не проверяли (грип-офсет UPROPERTY на подбор).
- Награды квестов 150/250 — draft (UPROPERTY).

## 🎯 NEXT (старт следующей сессии отсюда)
1. **Отдать Сборщику HEAD `4bc625e` на прогон:** 2 квеста (взять у старосты G→ выдать предметы C/X → сдать H; кв.2 после кв.1; бандиты+ноутбук на базе) + подтвердить доводки `3c0c961` (N ближний, B вплотную, «Шкура волка»). Сигнал в GL_SIGNAL.txt.
2. По фидбеку — фиксы. Потом полировка из 30-п. списка Рината: огонь костра (P_Fire/Niagara), экран смерти #26, спринт-расход голода/жажды #2, патроны-предмет+слайдер магазина #3, читаемость/иконки HUD #18, лица NPC #22, по 1 броне на слот (прогресс) #21, и пр.
3. **DT_Quests / DT_Items (конструкторы)** — РЕШЕНО с Ринатом: делать **ближе к КОНЦУ демки**, когда механики/типы квестов устаканятся (JIT; не в разгар). Тогда чистый рефактор: определения квестов/предметов → строки таблиц, староста читает по RowName. Новый квест существующего типа = строка без кода.
4. **Android-порт — ПОСЛЕДНИМ, с Ринатом** (мобильный рендер, без Lumen/Nanite, Vulkan, scalability, тач-ввод, профиль). Данные разведки — в трёх отчётах (камера/UI/Android, ассеты/звук/VFX, аудит кода) этой сессии.

## АССЕТЫ (исходники)
`E:/ForGameLead(Materials)/demo-assets/` (SM_Pistol, SM_CampfireLogs, SM_Shed, SM_GrassTuft, SM_Bush, SM_BonePile, SM_WolfDenCave); `demo-audio/` (12 CC0-звуков + LICENSES.txt); `phase4-assets/` (броня); `phase5-assets/SK_Elder.fbx`. headless-скрипты — `E:/ContrarySurvior/ContrarySurvivor/Saved/qa_scripts/`.

## ПРОЦЕСС-НАПОМИНАНИЯ
- Сборка: `Build.bat ContrarySurvivorEditor Win64 Development` при ЗАКРЫТОМ редакторе; убедиться что обновлён БАЗОВЫЙ DLL (не `-NNNN` патч — иначе свежий старт грузит старый код).
- Headless ассеты/уровень: `UnrealEditor-Cmd "<uproject>" -ExecutePythonScript="<abs.py>" -unattended -nopause -nosplash`, результат в файл-лог (stdout пуст). Импорт FBX модельера: **import_uniform_scale=1** (выверено по bounds; ×100 = в 100 раз больше!).
- Watchers (фон bash) поднимать заново после рестарта сессии; реагируют на изменение `QA_SIGNAL.txt`/`TEST_REPORT.md`.

---
# === УРОКИ UE + статус визуал-демки (из SAVE 2026-06-16, перетёртая WASD-сага удалена) ===

## ВИЗУАЛ демки (Этап визуала, сделан с UE-скринами; геймплей — приоритет, см. СЕЙЧАС)
- ✅ Костёр тёплый (был синий — `unreal.Color` BGRA переставил R↔B), кровь-лужи (были розовые плиты — `unreal.Rotator` roll вместо pitch), SkyLight+SkyAtmosphere+экспозиция, дорога→декаль. Все с реальными UE-скринами (S3_FINAL_*.png в Saved/Screenshots/WindowsEditor).
- 🟠 ХВОСТ: дом на UE-скрине мутно-серый (vcol слабо тянет, вероятно Power(2.2) пере-обесцвечивает коричневый под небом) — доводка на этапе визуала.
- Модели приняты+экспортированы: дом-изба, забор, колодец, кости+кровь, трава зелёная, одежда L1/L2, кепка бандита v2.

## УРОКИ UE (записать накрепко)
- `unreal.Rotator(a,b,c)` = (roll, pitch, yaw) — для наклона декали/объекта использовать keyword `pitch=`.
- `unreal.Color(r,g,b)` — BGRA, переставляет R↔B; для цвета света использовать `LinearColor(...)`.
- Цвет моделей для UE — только VERTEX-COLOR, не материал-слоты Blender (теряются при MESH-only FBX экспорте). Импорт с «Vertex Color = Replace» + материал VertexColor→Power(2.2)→BaseColor.

## Уроки июня 2026 (вынесены из живого context.md 2026-07-12, давно усвоены — детали здесь)

**▶ УРОКИ 06-28 (чтобы не повторять):**
- **idle-пинг teammate ≠ «завис».** Уведомления `idle/available` приходят МЕЖДУ фазами работы напарника — он может в этот момент работать. НЕ паниковать, НЕ плодить дубль. Запустил `modeler-2` решив, что первый modeler завис на колоде, — а тот РАБОТАЛ; оба прогнали колоду в одни файлы. Спасло то, что работа идентична (вариант «а») и файл вышел цел (проверил FBX-заголовок). **Правило: прежде чем дублировать агента — проверить РЕЗУЛЬТАТ на диске (файлы/время) и дать явную короткую команду, а не запускать второй экземпляр.**
- **MCP `mcp__blender__*` в СУБАГЕНТОВ не пробрасывается** (проверено на 3 свежих экземплярах — «No such tool»). modeler работает ТОЛЬКО headless CLI. Не тратить цикл на «проверь нативный MCP» — сразу headless.
- **Команды teammate'у разъезжаются в очереди** (мои сообщения про канал/headless пришли вперемешку → modeler запутался, повторял старый вопрос). Давать ОДНУ чёткую задачу за раз + просить подтверждение приёма; не слать «кашу» команд подряд.
- **`context/**/tmp/` игнорируется git** — concept держит иконки в `tmp/hud-icons/` → утверждённые иконки НЕ попадают в репо. Проверять gitignore ПЕРЕД тем как сказать «сохранено в git».

**▶ УРОКИ 06-29 (чтобы не повторять):**
- **НЕ СДАВАТЬСЯ на «protected/закрыто».** Сказал «доступ к нодам материала закрыт» после первой ошибки — Ринат: «соберись, всё можешь». Граф материала ЧИТАЕТСЯ: `MaterialEditingLibrary.get_material_property_input_node(m, MaterialProperty.MP_BASE_COLOR)` + `get_inputs_for_material_expression` + `get_material_expression_input_names` — обход дерева нод. Перед «не могу» — искать рабочий API (правило D).
- **Vertex paint ПРОГРАММНО работает** (Geometry Script): `GeometryScript_AssetUtils.copy_mesh_from_static_mesh` → правка цветов → `GeometryScript_List.convert_array_to_color_list(py_list)` → `GeometryScript_VertexColors.set_mesh_per_vertex_colors` (нужен ColorList, НЕ py-list) → `copy_mesh_to_static_mesh` → save_asset. Сброс: `set_mesh_constant_vertex_color`. Цвет вершин под координаты считать в МИРОВЫХ (vertex local + actor offset).
- **НЕ масштабировать плоскость пола** (Ринат): scale на меше-сетке растягивает UV + разъезжает вершины (ломает vertex paint). Правильно — заменить корректным мешем нужного размера/плотности (modeler). Для текстур world-mapped scale некритичен, но для vertex paint плотность критична.
- **Сверять детали со схемой, не перебарщивать** (Ринат: «слишком извилисто, перестарался»). Дорога на `scheme-map` — почти прямая с лёгкой органикой, не синусоида. Перечитывать референс ПЕРЕД параметрами.
- **`set_material` для StaticMesh-ассета — РАБОЧИЙ метод** (`sm.set_material(idx, mat)`); `set_editor_property('static_materials', ...)` тихо НЕ применяется. И НЕ удалять материалы ДО проверки что переназначение прижилось (удалил импортные M_* до верификации → слоты стали None).
- **Перед удалением чего-либо в UE — фильтровать аккуратно** (standalone акторы vs компоненты внутри BP): удалял пропсы по метке/папке/мешу, BP-базы/костёр не задеты (их класс `BP_*_C`, не `StaticMeshActor`).

**▶ УРОКИ 06-26 (чтобы не повторять):**
- **git -C <path> для разных репо — НЕ полагаться на `cd` в составной команде** (`cd A && git…; git…`: второй git ушёл не в тот репо — cd не вернулся → обе проверки показали ОДИН репо; поймал при закрытии 06-26, перепроверил через `git -C`).
- **Догадку за факт НЕ выдавать (повтор №0.1):** заявил «HUD-иконки — работа concept» БЕЗ проверки → Ринат поймал. Про найденный на диске файл: СНАЧАЛА происхождение (git log/дата/подпись в файле), ПОТОМ утверждение.
- **СВЕРЯТЬ КАЖДУЮ деталь правки с ПОСЛЕДНИМ требованием Рината — не копировать старую формулировку.** В этой сессии дважды вернул «~45°» в промптах ПОСЛЕ явного «вид строго сверху», и «дома вокруг перекрёстка» ПОСЛЕ явного «дома НЕ вокруг костра». Это невнимательность при редактировании спеков/промптов (Ринат заметил «что с тобой происходит»). Перед отправкой правки — перечитать последнее требование и сверить дословно.
- **Нумерацию этапов плана держать КАНОНИЧНОЙ (0/A/B/C…), не плодить лишние буквы.** Ввёл «Этап R» → потерялась «B» → путаница у Рината. Сделанное помечать явно (✅), буквы по порядку, без переименований середины.
- **Не коммитить WIP-код без проверки сборки** (render-distance был закоммичен в `0e2660c` без сборки → всплыл C4458 при первой реальной сборке). Подтверждено снова.

**▶ УРОКИ 06-25 (чтобы не повторять):**
- **Анимацию/тонкий визуал в дневной сцене скриншотом НЕ оценить** — судит Ринат вживую (Realtime во вьюпорте / PIE). Аддитивное пламя днём «вымывается» → translucent+emissive читается лучше.
- **Материал через Python — ВЕРИФИЦИРОВАТЬ кадром:** flipbook-узел сэмплил криво (мелкое пламя) → одиночная текстура решила; декаль-проектор бил вскользь (прямоугольник) → pitch −90 вниз + тонкий size.x. Не считать материал готовым без осмотра рендера.
- **BP↔инстанс рассинхрон:** удаление/замена компонента в BP не всегда чисто доходит до размещённого инстанса (зависал старый компонент; `set_material` на старом не прижился). СВЕЖИЙ add компонента берёт материал надёжнее; проверять на ИНСТАНСЕ (`get_material`), не на BP.
- **Не переусложнять очевидное** (Ринат: «переусложнил» про траву под базы): очевидное делать сразу, не оформлять как развилку А/Б (№0.2-2).

---

## Этап F «Удержание» — ЗАКРЫТ (вынесено из context.md при чистке 2026-07-19)
Закрыт 07-17 (merge `4ae63b9`+`664150f`, тесты 16/16, приёмка Рината) — детали в git и ADR-044/045.
Что было в живой памяти и стало историей: ветка `feature/stage-f-retention` HEAD `42d8e7d` (слита); квест Q3 «шкуры для торговца» + второе логово BP_WolfDen2; панель диалога с высотой от числа строк (`dc2d111`); тон диалога Q3 (`f0d3992`); мои PIE-пруфы 07-12 (метка Q3 рисуется, дроп бандитов = баланс не поломка, попап смерти без «можно забрать»); решения по луту (русские имена расходников, шанс 35%, цвет пикапов); незакрытая работа по F (qa-прогон, таблица, GDD) — всё выполнено при закрытии этапа.
**Нерасследованная странность (перенесена как хвост):** волк спавнится у логова при num_to_spawn=0 на экземпляре; волк уходил в погоню на dist=23457 через полкарты (leash возвращал). Не блокер.
**Разведка Android 07-13 — УСТАРЕЛА:** на тот момент на машине не было ничего Android. Тулчейн поставлен 07-17, рабочий конвейер зафиксирован в ADR-047.
**Инфра-фикс 07-12:** относительные пути PreToolUse-хуков в settings.json заменены на `${CLAUDE_PROJECT_DIR}` (падали при cwd=гейм-репо).
**Белые дома** — закрыто Ринатом 07-12 («дома нормальные пока»).

## Уроки 07-04..07-11 (вынесено из context.md 2026-07-19; усвоены, читать по поводу)
- **07-11:** пункты плана сверять с КОДОМ перед постановкой задач (F1+ уже была сделана в D); **push проверять `git ls-remote`**, а не верить «Everything up-to-date» (лечение: `git config http.postBuffer 524288000`); оборванную работу напарника спасать WIP-чекпоинтом с честной пометкой; Python-имена перечислений UE сверять по факту (правильно `TC_EDITOR_ICON`); установка стороннего кода — только явное слово Рината, отказ классификатора напарнику не обходить своими руками (permission laundering).
- **07-09:** Excel COM — `.Text` для эмодзи врёт, брать `.Value2`, запись ✅ через `ConvertFromUtf32(0x2705)` + шрифт Segoe UI Emoji, верификация кодами символов; `save_dirty_packages` пишет на диск и «удалённое» из реестра — после delete_asset проверять диск; PIE Рината блокирует editor-Python — сериализовать; Blender-ре-импорт FBX ≠ слепок UE, цвет судить только в UE/PIE; «12/12 готово» = проверял наличие, не качество — визуал принимать только по кадру; интерпретацию данных не выдавать за вывод (нужен РАЗЛИЧАЮЩИЙ тест); держать команду загруженной.
- **07-06:** лог живой сессии бьёт гипотезы (корень погони — DetectionRange, не камера); UE-FBX выгрузка даёт кости ×100 — обязателен позовый чек; диагностика визуала данными, не глазами; Interchange игнорирует legacy-опции импорта; сбои валили агентов 3 раза — рецепт «проверь диск → доделай, не переписывай»; сообщения teammate разъезжаются хронически — после пересечения слать ОДНУ сверочную с явным «выполняй/отбой»; `rename_asset` в живом редакторе переносит ассет чисто.
- **07-05:** правка СВОЙСТВ существующих нод материала headless РАБОТАЕТ (обход графа от корня); самостоятельный PIE-прогон — рабочий набор (`editor_request_begin_play` → `get_game_world` → телепорты → BlueprintCallable); плейтест-фидбек закрывать «фактом кода», не обещанием (половина хотелок уже была в коде).
- **07-04:** `unreal.Rotator(roll, pitch, yaw)` — yaw ТРЕТИЙ аргумент; FBX-импорт UE зеркалит ось Y (attach-схемы только в UE-координатах); изоляция одной переменной находит корень за 2 шага; лимит подписки валит ВСЮ команду разом — прогресс переживает на диске и в чекпоинт-коммитах; PowerShell из Git Bash — только через `-EncodedCommand` (UTF-16LE+base64); `taskkill /F` — с `MSYS_NO_PATHCONV=1`.

## Вынесено из context.md при закрытии сессии 2026-07-20 (СЕЙЧАС-блоки 07-19 и 07-20 день)
## 🧭 ПРЕДЫДУЩЕЕ (2026-07-20 день — локализация закрыта в коде)
**⛔ ПЕРВОЕ ДЕЛО СЛЕДУЮЩЕЙ СЕССИИ:** (1) **ЖИВОЙ ОСМОТР РИНАТА** — ни одна панель НЕ ВИДЕНА в игре, всё подтверждено только сборкой/тестами. Порядок осмотра: панель статов (обязателен контейнер `AmmoRow` вокруг строки патронов, иначе подпись «Патроны» повиснет при ноже), метки над старостой/торговцем (если в BP_Elder/BP_Trader сохранены старые значения — правка кода их НЕ перебьёт, стирать вручную), инвентарь (строку статов надо ПЕРЕЛОЖИТЬ заново — кубик StatsText разобран на 6), магазин. Инструкции: `docs/contrary-survivor/umg-layout-guide.md`. (2) **3 ОТВЕТА РИНАТА** ждут: реплики издателя для интро/диалога (сюжет — утверждает он; лежат в `docs/contrary-survivor/publisher-2026-07-20/TZ-intro-i-knopki-dlya-gamelead.md` §3); конфликт по броне (в журнале издателя ОБА варианта чисел помечены «утверждено Ринатом» — снять может только он, в коде менять НЕЧЕГО, действует ADR-042); постобработка кадра (визуал уровня = его территория по правилу, поручать ли оператору). (3) После приёмки — выпил старого Canvas-пути HUD (31 поле + 19 литералов, ADR-048); до приёмки НЕЛЬЗЯ (останемся без отката). (4) Издатель ждёт: удобный формат передачи текстов (ответить ПОСЛЕ показа реального примера из Game.po) + замеры FPS на realme.
**✅ СДЕЛАНО 07-20 (ADR-050, все пруфы проверены мною лично по коду/логам):** локализация интерфейса и игровых текстов на штатную систему UE — 9 порций, ветка `feature/localization` от `161a3cc`. Сборка+тесты зелёные СЕМЬ раз подряд (16/16 каждый, квестовый тест проходит), логи `logs/2026-07-20-*`. Закрыто: панель статов, названия предметов, магазин, диалог, трекер, инвентарь, экран смерти, меню паузы, ежедневка, обучение, тач-кнопки, тексты квестов, метки NPC. Устранены в КОРНЕ служебные имена (`BP_Pistol_C_1` в инвентаре — `InventoryScreenWidget.cpp:117`, и на экране смерти — `PlayerCharacter.cpp:504`). 27 английских надписей заменены. **Первый реальный сбор переводов ПРОВЕДЁН** (unreal, `96557a8`): 170 текстов (107 код / 63 ассеты), `Content/Localization/Game/ru/Game.po` + `.locres`; **обратная проверка пройдена — служебные ключи НЕ утекли (0 в манифесте)** → квесты останутся проходимыми при смене языка. Издатель прислал ответ: журнал «РИ» признан ВНУТРЕННИМ (источник истины = наш ADR), ошибка по броне СНЯТА (ADR-042 верен), схема кнопок получена с размерами в dp, приоритет Build 1 = диалог+интро+постобработка, ветвление ответов и полная хромота ОТЛОЖЕНЫ.
**▶ В РАБОТЕ:** `unreal` проверяет, ПРИМЕНЯЕТ ли игра перевод (временная культура-пустышка → смена языка → доказать подмену строк; культуру потом убрать). Собранный файл ≠ работающий перевод — это разные вещи, родной ru совпадает с исходником и разницы не видно.
**▶ ГЛАВНЫЙ УРОК 07-20 (записан в ADR-050 как приёмочное правило):** обход по СПИСКУ ПАНЕЛЕЙ структурно НЕ находит строки, живущие в игровых классах и попадающие на экран через геттер — так выпали ОБЕ дыры (метки NPC, имя убийцы), причём из всех 7 порций И из моего контроля. Лечение в два шага: (1) прямой поиск по всему `Source/` полей, чьё значение уходит игроку; (2) **ОБРАТНАЯ ПРОВЕРКА — искать ожидаемые слова в СОБРАННОМ файле перевода и смотреть, чего там НЕТ.** Второй способ сильнее: поиск по коду находит то, о чём догадался спросить, сверка с собранным файлом показывает пропуск САМА. Обе дыры нашлись именно так. Отдельно: обёртка `FText::FromString` вокруг готового текста ОБНУЛЯЕТ перевод (culture-invariant), искать такие при приёмке.
**▶ УРОК ПРО СЕБЯ 07-20 (процессный, исправлен):** дважды отправил cpp претензию «ты не сделал», пока он делал эту работу — проверял диск и сразу писал упрёк. Данные были верны, но порядок неверен: агент тратил ответы на оборону вместо кода. НОВОЕ ПРАВИЛО: пока задача может быть в работе — НЕ писать «ты не сделал», а ждать отчёта либо спрашивать «на чём ты сейчас». Претензия только если работа ОБЪЯВЛЕНА законченной, а на диске её нет. Встречно cpp шлёт короткое «взял, делаю то-то» в начале задачи.
**▶ ПАРАЛЛЕЛЬНАЯ РАБОТА ДВУХ cpp — РАБОТАЕТ, приём записан:** два программиста в ОДНОЙ рабочей копии на непересекающихся файлах; коммит СТРОГО явными путями `git commit -m "..." -- <пути>` (без `git add .` / `-a`) — чужую незаконченную работу не забирает. Проверено: ни одного конфликта за сессию. Файл-исключение `GenerateWbpCommandlet.cpp` закреплять за ОДНИМ агентом (его правят все порции).
**▶ ХВОСТЫ 07-20:** заглушка «Квест: Шкуры волков — Шкура волка 1/3» в WBP_QuestTracker (текст Рината в дизайнере, переводчик будет переводить впустую — стереть при случае); два предупреждения сбора о дублях-ассетах (`SM_Knife` в двух папках — известный хвост; `HeadAndSkeletonfbx_Head_Skeleton` в Shared/Humanoid + TestContentAndCode) — текстов в них нет, разобрать при чистке дублей.

## 🧭 ПРЕДЫДУЩЕЕ (2026-07-19 — панели в UMG, ревью publisher)
**⛔ ПЕРВОЕ ДЕЛО СЛЕДУЮЩЕЙ СЕССИИ (по приоритету):** (1) **ПАКЕТ РУСИФИКАЦИИ для cpp** — главный вывод publisher (ADR-049): весь интерфейс на русский (HUD `HP/Hunger/Thirst/Ammo`; магазин `TRADER (E to close)`/`FOR SALE`/`SELL FROM BACKPACK`/`Buy`/`Close`; товары `Knife`/`Pistol`), «Пистолет» вместо `BP_Pistol_C_1` + греп ВСЕХ протечек имён BP в интерфейс, кнопки диалога без квадратных скобок, «Защита: 0%» нейтральным цветом (не зелёным), «Не хватает монет» ТЕКСТОМ (не только красной кнопкой), `Ammo 12/48 (bag 0)` → «Патроны 12 / 48» (расшифровать или убрать «bag»); (2) **ранний крючок** — ОДНА фраза-намёк «кто-то охотится за героем» в ПЕРВЫЙ диалог старосты (ADR-049-б, текст утверждает Ринат); (3) **первая минута** — явная цель «Подойди к старосте у костра» + маркер от спавна; фикс бага: онбординг-подсказка движения рисуется частично ЗА верхом вьюпорта (кадры 00010/00016); (4) иконки в HUD/магазин (нарисованы, лежат в `docs/contrary-survivor/ui/hud-icons/`); (5) ТОЛЬКО ПОТОМ — витринные скрины/видео из ЧИСТОЙ сборки (RuStore запрещает элементы не из игры) + видео с ветром 15-30 с (главный козырь, на стоп-кадрах не виден).
**✅ СДЕЛАНО 07-19 (все пруфы проверены мною лично):** (1) фикс самопрячущихся виджетов собран и зелёный: сборка 9/9, тесты 16/16 EXIT 0 (логи `2026-07-19-build-umg-selfhiding-fix.log` / `-tests-`), подсказка «E — торговать» подтверждена живым кадром PIE. (2) Ринат удалил свои 4 пустых WBP (`2754045`) → генерируем САМИ: cpp расширил коммандлет (`e88fb0f`), сгенерированы 4 панели (`d9109c1`, verify 10/10 ВТОРЫМ процессом, тесты 16/16), назначены в слоты HUD мною headless (`2773325`, verify вторым процессом). **ИТОГ: все 7 панелей ADR-048 в UMG-режиме.** (3) Иконка текущего оружия: иконки импортированы (`ICONIMPORT_OK[2]`), кубик WeaponIconImage добавлен в WBP_TouchControls режимом AUGMENT без перезаписи стилизации Рината (`AUGMENT OK` в логе), сборка 13/13 без ошибок — спасено чекпоинтом `161a3cc` (cpp упал по лимиту). ⚠️ **НЕ ПРОВЕРЕНО: 16 тестов после иконки НЕ гонялись; вид иконки в игре НЕ осмотрен.** (4) Пакет publisher (`1744316`) отправлен Ринатом, **ОТВЕТ ПОЛУЧЕН и сохранён** — `docs/contrary-survivor/publisher-response-visual-review-2026-07-19.md`, решения Рината в **ADR-049**. (5) Таблица: G и I «в работе» (`d3364eb`).
**▶ ГЛАВНОЕ ИЗ РЕВЬЮ PUBLISHER (полный текст — в файле выше, НЕ пересказывать по памяти):** графика УЖЕ проходит планку «прилично»; вниз тянут ТЕКСТЫ интерфейса — это и самый громкий сигнал «самоделки», и самое дешёвое в починке. Экран смерти назван самой законченной панелью. Требования витрины RuStore (иконка 512×512 без прозрачности, 1-10 скринов 16:9 без элементов не из игры, тексты 30/80/4000 символов, рейтинг честно 16+/18+) — с источниками в том же файле. Досъёмка для publisher — 8 пунктов там же. ⚠️ Publisher ссылался на несуществующую у нас запись «РИ-19» с чужими числами брони — снято Ринатом (ADR-049-а: верны наши ADR-042); при следующем контакте сообщить publisher. Его пункт 6 про «эксперимент за монеты» — такой фичи у нас НЕТ, уточнить откуда.
**▶ НЕЗАКОНЧЕННОЕ У НАПАРНИКОВ (оба упали по лимиту подписки, работа спасена на диске):** (а) **cpp** — тесты после иконки оружия не прогнаны, живой осмотр не делался; (б) **modeler — ЗАДАЧА ЗАКРЫТА, ПРИНЯТО мною по логу и личному осмотру рендеров.** `assets/loot_bag/`: SM_LootSack (мешок, 180 трис) и SM_LootBackpack (рюкзак, 160 трис); в логе `_build.log` **`palette_check=PASS off_palette={}` у ОБОИХ** (моя прежняя запись про FAIL относилась к первому прогону — исправлено), tri_budget PASS, nonmanifold=0, dup_faces=0, origin в нуле, низ на Z=0. 24 рендера в `renders/`. Я лично смотрел `LootPair_top.png` (мешок сверху НЕ читается шаром — неровный контур + золотое кольцо горловины; рюкзак читается с пряжками и ручкой) и `LootPair_gameplay_scale.png` (реальные параметры камеры из PlayerCharacter.h: наклон −60°, штанга 3000, FOV 40 → пикап ~30 пикселей; янтарное пятно делает предмет заметным). **ОСТАЛОСЬ: выбор варианта за Ринатом + его вкусовое решение — у мешка янтарным закрашены 84 грани из 180 («нарядновато», правится одной покраской без переделки геометрии); затем импорт в UE и замена шара-плейсхолдера.**
**▶ ЖДЁТ РИНАТА:** приёмка и СТИЛИЗАЦИЯ 4 новых панелей в UMG-дизайнере (магазин/строка/диалог/статы — раскладка-дефолт снята с Canvas-вида, он правит стиль); выбор варианта лут-пропа (мешок или рюкзак) по рендерам; текст ранней фразы-крючка; иконка RuStore отложена им же (ADR-049-в).
**▶ ХВОСТЫ СЪЁМКИ:** кадр трекера квеста НЕ снят; кадры ежедневной награды и брони «до/после» — просит publisher.
**▶ УРОКИ 07-19:** (1) `tasklist //FI` из Git Bash БИТ (ошибка глотается → пустота = ложное «процесса нет») — процессы проверять PowerShell Get-Process (готовый /tmp/check-ue.ps1); (2) `Shot showui` снимает ВСЁ ОКНО редактора с панелями — кроп готов (/tmp/crop-batch.ps1: 2582×1550→rect 18,176,1973,1053; 2265×1425→14,170,1730,962); (3) открывающих UFUNCTION у окон НЕТ (только close_*/show_death_screen; interact/inventory_action — это СВОЙСТВА Enhanced Input) — окна только живым вводом; ЕСТЬ offer_quest/accept_quest на QuestComponent и OnboardingComponent с текстами подсказок; (4) боевые кадры: телепорт в стаю = смерть за 12 с; рецепт — `slomo 0.1` перед Shot, потом slomo 1; (5) после заказа Shot НЕ трогать игру до появления файла (задержка записи ~2-3 с — дважды словил кадр «после смерти»); (6) фоновые git-мониторы запускать с `git -C <путь>` (cwd уплывает → ложные срабатывания).
**▶ УРОКИ СМОУКА 07-18 (ВАЖНО, не переоткрывать):** (1) editor_request_begin_play в свежем редакторе стартует Simulate (SpectatorPawn+базовый PC при нашем GameMode, «PIE: Server logged in» В ЛОГЕ ЕСТЬ И У SIMULATE!) — лечение: LastExecutedPlayModeType=PlayMode_InViewPort в Saved/Config/WindowsEditor/EditorPerProjectUserSettings.ini секция [/Script/UnrealEd.LevelEditorPlaySettings] (уже прописано) при ЗАКРЫТОМ редакторе; (2) /mcp-канал умирает вместе с процессом редактора — перезапустил редактор = проси /mcp заново; все правки конфигов делать ДО открытия; (3) editor_take_screenshot НЕ видит UMG/Slate (видит Canvas) — кадры с UI: execute_console_command(world,"Shot showui") → Saved/Screenshots/WindowsEditor/ScreenShotNNNNN.png, пишется с ЗАДЕРЖКОЙ на заказ; (4) Collapsed-корень UUserWidget = его NativeTick мёртв (виджет не может сам показаться) — паттерн: прятать содержимое; (5) unreal.WidgetLibrary.get_all_widgets_of_class — рабочий способ проверить UMG-режим; методы игры приватные (UFUNCTION-обработчики клавиш из Python не дёргаются — открытие окон только живым вводом); (6) рабочая карта = /Game/Maps/L_World_C (НЕ L_World).
**▶ ХВОСТ АНДРОИДА (без изменений, по команде «собирай APK»):** контрольный Development-пак из worktree E:/ContrarySurvior/pack-android (ПЕРЕКЛЮЧИТЬ worktree на master!), конвейер ADR-047; критерии: 6 строк SK_Cloth_T0_* в манифесте ДО установки; USB + pm grant WRITE/READ; на телефоне — без диалога Storage, игрок в Т0, свайп магазина живьём.
**▶ РЕШЕНИЯ РИНАТА 07-18:** размер APK (650 МБ на телефоне) — НЕ трогаем до завершающей фазы (Shipping+ужимка там же); APK собирать ТОЛЬКО после его настройки BP; скан диска C — папки читать можно, чистка за ним (hiberfil 12,7 ГБ — кандидат №1; Program Files 28,3 / ProgramData 12,5 / x86 5,2 ГБ; Users+Windows досчитываются фоном ~80 ГБ где-то там; кэш UE на C всего 626 МБ — НЕ наш виновник).
**▶ ХВОСТЫ ЭТАПА G (без изменений):** ключи GameAnalytics в пак (безопасность — репо публичный); торговец не надет на BP_Trader (визуал без команды Рината не трогать); ассеты торговца ae3c00a на ветке stage-g-touch ХВОСТОМ — в master НЕ слиты (qa не покрывал); таблица DemoPlanTemplateRec.xlsx — обновить за 07-17 (этап G) И за сегодня к закрытию сессии.
**▶ УРОКИ 07-18:** (1) qa-гейт-хук проверяет маркер ДО команды — touch QA_OK и merge должны быть РАЗНЫМИ вызовами Bash; (2) idle-сигналы разъезжались 3 раза за день (cpp дважды, unreal дважды) — рецепт «проверь диск → одна сверочная с "выполняй"» отработал все разы, дублей не было; (3) сборка с UBA падала «paging file too small» и у qa — `-NoUBA -MaxParallelActions=6` теперь ШТАТНЫЙ режим гейтов (qa записал себе; альтернатива — Ринату увеличить файл подкачки); (4) du по всему C из Git Bash виснет на системных папках — сканировать частями, системные файлы корня (hiberfil/pagefile) смотреть ls-ом.
**Фаза:** этапы G (Android, ADR-046/047) и I (интерфейс на UMG, ADR-048) — оба «в работе» в плановой таблице. Этапы 0/A/B/C/D/E/F ЗАКРЫТЫ (история — archive.md и git).
**▶ ЦЕНЫ ТОРГОВЦА (справка):** Вода 5 / Консервы 12 / Бинт 12 / патроны 2 / нож 40 / пистолет 150 / броня Т1-Т3 по 50/120/250 за слот (ADR-042). У волка generic-поля лута МЁРТВЫЕ (DropLoot роняет только шкуру + деньги 5-15).
**▶ КЛЮЧИ GA:** `E:/game-dev-team/keys/{GameKey,SecretKey}.txt`, папка в .gitignore (check-ignore подтверждён). Значения в гейм-репо НЕ попадают (git grep полными значениями + git log -S по всем веткам = 0, проверено мною и qa). Для Android-пакета (этап G) ключи вносить в конфиг ЛОКАЛЬНО перед пакетованием.
**▶ БЭКЛОГ ЭТАПА G:** MCP-сервер GameAnalytics (находка Рината, Screenshots/11/1.png) — подключать когда появятся реальные данные; спайк + ADR; делаю я. Плюс ключи в пакет локально (выше).
**▶ ХВОСТЫ (старые, при случае):** дубль SM_Knife; внешность ТОРГОВЦА (референсы Рината УЖЕ ЕСТЬ: `concept-art/TraiderReference/1.png` — можно запускать modeler по пайплайну старосты `assets/npc_elder/10_build_elder.py`); SK_Elder_Head без PhysicsAsset; красные Movement-тесты на master (НЕ РАССЛЕДОВАНО); броня `_01` — жителям деревни (ADR-042); paper-doll — позже (ADR-043).
**▶ ИНФРА (на конец 07-19):** редактор ЗАКРЫТ штатным quit_editor, несохранённых пакетов НЕ было (проверено get_dirty_*), процессов нет (Get-Process → NO_PROCESS). Оба репо чисты и запушены. Маркер .claude/QA_OK НЕ висит (проверено). ВЕТКИ: гейм-репо `feature/umg-hud` HEAD `161a3cc` = origin (ls-remote); team-репо `docs/phase0-gdd` HEAD `5d1cfdd` = origin. master НЕ трогался — merge только после qa-гейта. MCP: после перезапуска редактора мост сам НЕ поднимается: если сессия стартовала при закрытом редакторе — нужен `/mcp` Рината после открытия и полной загрузки, затем set-пути (project/engine). Запуск редактора: `powershell Start-Process` с картой в аргументах. Монитор сообщений Рината — перезапустить при старте. Сборки cpp: при «paging file too small» — флаги `-NoUBA -MaxParallelActions=6` (заметка cpp). Пути: проект `E:\ContrarySurvior\ContrarySurvivor\ContrarySurvivor.uproject`, движок `E:\UnrealEngine\UE_5.5`.
**▶ ПРАВИЛО ЯЗЫКА №0.2-3 (Ринат 07-11, полный текст в CLAUDE.md):** только законченные предложения; без телеграфных обрубков и чисел через дробь в ответах Ринату.
**▶ УРОКИ 07-04..07-11 — вынесены в archive.md** (усвоены; читать по поводу). Урок 07-07 в силе: лимит валит напарников молча — при воскрешении проверять ДИСК (git status, файлы по времени), не искать «недоделки» по памяти.
**▶ КАНАЛ СВЯЗИ С РИНАТОМ (работает):** корень team-репо: «Отчёты по фазе D.md» (5 отчётов там) + «Для сообщений от Рината.md» — фоновый монитор (git fetch кажд. 2,5 мин) ПЕРЕЗАПУСКАТЬ при старте сессии и после каждого срабатывания. Рендеры — коммитить, давать ссылки.
**⛔ СТОРОНЫ СВЕТА = ПО КАМЕРЕ: верх кадра при спауне ГГ = север. Факт карты: логово — ЗАПАД, база бандитов — СЕВЕР.**
**▶ Хвосты плана:** миникарта — этап I; L/M — полиш после Build 1; **красная линия L/M: политика/война/госсимволы/религия — НЕТ**; дубль SM_Knife в /Game/Weapons и /Game/Weapons/Knife (заметил при инвентаризации — разобрать при случае, НЕ трогал).
**▶ ЖДЁТ РЕШЕНИЯ РИНАТА:** лор героя в GDD ч.3 («разочарованный в подавлении демонстраций») задевает красную линию «политика — НЕТ» (ADR-040) и модерацию RuStore. Спросил 07-02 (переписать мотив на нейтральный или оставить как фон) — ответа НЕТ. При старте работ по текстам/онбордингу (F1) — переспросить.
**▶ ОТКРЫТЫЕ СПАЙКИ:** первый Android-пак (риск №1, этап G); ad-плагин VK/myTarget (Build 2); GameAnalytics×UE5.5 (F3).


---

# Перенесено из context.md 2026-08-06 (дистилляция после волны Б5/Б8/Б9, пак Shipping)

## 🗄️ ПРОШЛОЕ СОСТОЯНИЕ (2026-08-05, вечер — работа по заданию издателя Б1–Б10)

**ФАЗА:** доводка перед первым выходом на RuStore. Ветка `feature/build122`, в master не вливалось. Задание издателя — ADR-059, порядок Б1–Б10.

**ЗАКРЫТО И ПРОВЕРЕНО МНОЙ ЛИЧНО:**
- **Б1** (291c049) — пропавшие ассеты в пакете; на телефоне ЖИВЬЁМ подтверждена анимация смерти (журнал: «анимация смерти Anim_Death_Humanoid запущена»).
- **Б2, Б7** (01b5323…261ec5e) — продажа стопками, экономика, старт с ножом. **Старт с одним ножом ПОДТВЕРЖДЁН ГЛАЗАМИ** на телефоне: в рюкзаке слот огнестрела пуст, есть только нож (`Screenshots/phone-b6-05-inventory.png`).
- **Замер времён кадра** (97837c5) — своя строка на экране: время кадра / логика / отрисовка / видеочип. В публикационной сборке выключается на уровне компиляции (часть Б5).
- **Б3** (f5bae10) — загрузка сейва при старте, экран «Продолжить»/«Новая игра», вступление только при новой игре. Тесты 47/47. Велено добавить переспрос перед стиранием.
- **Б9 + опыт с разрешением** (369d683) — `MaxAspectRatio=2.4`, новый `Config/DefaultDeviceProfiles.ini` с `r.MobileContentScaleFactor=0.8`.

**▶ ГЛАВНАЯ НАХОДКА СЕССИИ: УПИРАЕМСЯ В ВИДЕОЧИП.** Замер на живом телефоне, три места: поле кадр 36,5 / видеочип 35,6; деревня 43,8 / 43,2; рюкзак 51,6 / 51,1. Логика везде 8-9 мс, отрисовка 7-9. Значит группировка отрисовок, упрощение моделей и правки кода бесполезны — резать надо нагрузку на картинку (разрешение, материалы, освещение). Три прошлые гипотезы (тени, полигоны, дальность) закрыты окончательно.

**▶ НАЙДЕННЫЙ БАГ:** на боевом экране висят патроны «12/48» и картинка пистолета при ПУСТОМ слоте огнестрела — обманывает игрока. Отдан cpp.

**▶ В РАБОТЕ:** cpp — обманный счётчик патронов, затем Б8 (вёрстка магазина). unreal — собирает пакет 7 с правками Б9/разрешения. Я — установка и замер «было/стало» на телефоне.

**▶ ЖДЁТ РИНАТА:** (1) как вшивать ключи аналитики (Б4) — вне моей автономии; рекомендую вшивать при сборке, чтобы ключи не попали в git; (2) русское название игры для RuStore (сейчас приложение подписано латиницей `ContrarySurvivor`); (3) три боевых блока рекламы — список для кабинета отдан, `docs/contrary-survivor/reklama-kabinet-spisok.md`.

**⛔ УРОК ЭТОЙ СЕССИИ (мой прокол):** доложил Ринату как ФАКТ «старт с ножом не работает», опираясь на строки журнала. Оказалось неверно — строка выдачи оружия у игрока и у врага ОДИНАКОВАЯ (`EnemyCharacter.cpp:143-146` на успехе не логирует своего). Правда выяснилась за 30 секунд прямым взглядом в рюкзак. **Состояние проверять прямым взглядом, а не выводом по косвенным строкам.**

**⚠️ ФОНОВЫЙ ЗАПУСК СБОРКИ ВРЁТ КОДОМ ВОЗВРАТА:** получил «успех» при упавшей компоновке, которая ещё и стёрла библиотеку редактора. Проверять ЛОГ (строки Compile/Link/error), а не код возврата.
**⚠️ Счётчики времён кадра требуют модулей `RenderCore` и `RHI` в сборочных правилах** — без них падает компоновка.
**⚠️ `adb shell cat` ЛОМАЕТ КИРИЛЛИЦУ** в выгружаемом журнале — брать только `adb pull`. Пути к телефону в Git Bash — с `MSYS_NO_PATHCONV=1`.

## 🗄️ ПРОШЛОЕ СОСТОЯНИЕ (2026-08-05, день — РЕВИЗИЯ ПЕРЕД ПУБЛИКАЦИЕЙ отдана издателю)

**ФАЗА:** доводка перед первым выходом на RuStore. Ветка `feature/build122`, в master не вливалось. Отчёт ревизии — `reports/2026-08-05-audit/otchet.md` (+ копия у издателя), разбор — **ADR-058**.

**ЧТО ДОКАЗАНО ЛИЧНО (телефон + журнал + код):** реклама Яндекса 8.2.0 работает на живом Android целиком (ролик → награда → возрождение), идентификатор пока демонстрационный; сохранение пишется, но при старте НЕ читается (загрузка есть только при возрождении, `PlayerCharacter.cpp:1960`); продажа в магазине ограничена одной штукой (`ShopScreenWidget.cpp:355`) и из-за этого не появляется золотая кнопка; анимация смерти людей и материал сектора ножа НЕ попали в пакет (мягкие ссылки, третий/четвёртый случай ADR-057); аналитика молча выключена (ключи ищутся по пути на моём компьютере); кадры 19-28 при цели 30; меню/настроек/согласия/Telegram/карточки конца нет.

**ЗАДАНИЕ ИЗДАТЕЛЯ ПОЛУЧЕНО (ADR-059):** порядок Б1–Б10. Решения Рината: выкладываемся с БОЕВОЙ рекламой (ИП + кабинет заводит сам), пистолет на старте не выдаётся, Telegram из объёма убран, НО кнопку «Написать мне» оставить (поправка против издателя). РИ-30: свой плагин рекламы остаётся.

**ЗАКРЫТО И ПРОВЕРЕНО ЛИЧНО (вечер 08-05):**
- **Б1 — оператор, 291c049.** Ассеты вернулись в пакет: в манифесте `Anim_Death_Humanoid` 3 файла, `Anim_FirePistol_Humanoid` 3, `Anim_MeleeSlash_Humanoid` 3, `MI_MeleeSectorSoft` 2, `M_MeleeSector` 2 (было по 0), список 2891→2909 строк. Материалы сектора попали БЕЗ добавления `/Game/Materials` — только через ссылку из BP_PlayerCharacter (приём подтверждён). `M_VColor` пересохранён (флаг чинился в памяти, на диске его не было); касалось 770 камней SM_Rock_01..03.
- **Б2 и Б7 — cpp, коммиты 01b5323, c297a9b, d206b56, 83c50d1, 261ec5e.** Тесты 41/41, 0 провалов (проверено лично `grep`), 4 новых теста. Выкуп теперь считается ОТ цены покупки (поле `BuybackPriceFraction`, дефолт 0.5, потолок 0.9) — дыра структурно закрыта; второй перекос: нож 40/выкуп 70 → 40/20. Шкура 15. Старт: только нож, сразу в руках; **купленный огнестрел теперь занимает слот оружия** (раньше покупка была мертва — ствол лежал в рюкзаке, вооружиться из рюкзака игра не умеет).

**▶ ФАКТЫ ПО КАДРАМ (оператор измерил, три гипотезы СНЯТЫ):** теней нет вовсе и мы за них НЕ платим — у стационарного солнца `dynamic_shadow_distance_stationary_light=0`, запечённого света нет (нет `L_World_C_BuiltData.uasset`), на мобиле отдельные тени от стационарного света выключены умолчанием. Упрощать модели нечего: у всех 22 мешей одна ступень, вся деревня ~8700 треугольников. Дальность при виде сверху ни при чём (камера 3000 ед., −60°). Отрисовок в деревне 47, из них 42 — однотипная мелочь; сбор в группы даст всего 2-4 кадра. `r.MobileContentScaleFactor` = движковое умолчание 1.0, менять в новом `Config/DefaultDeviceProfiles.ini`. **НАСТОЯЩАЯ ПРИЧИНА 19-28 кадров НЕ НАЙДЕНА** — идёт дешёвый различающий замер: cpp выводит на экран время игровой логики / отрисовки / видеочипа, дальше меряем на телефоне.

**▶ СЛЕДУЮЩИЙ ШАГ:** cpp коммитит замер → дерево передаю оператору на полный APK → сам проверяю на телефоне: падение бандита, сектор ножа, золотая кнопка на сделке ≥50, старт с ножом, реплика старосты, замер кадров. Дальше cpp: Б3 (загрузка сейва при старте), пороги рекламы по РИ-29, экран смерти, запрет продажи ноутбука.

**⚠️ ДВА АГЕНТА В ОДНОМ ДЕРЕВЕ МЕШАЮТ ДРУГ ДРУГУ** — оператор правильно отказался собирать APK поверх чужого незакоммиченного кода. Правило на будущее: сборку пакета делать только при чистом дереве, работу кодера на это время останавливать.

**ПРИЁМ (важно, экономит часы):** телефоном можно управлять с компьютера — `adb shell input tap X Y` по координатам кадра 1600×720, `input swipe` двигает стик, `exec-out screencap -p` снимает кадр, `input keyevent 82` снимает блокировку, `svc power stayon usb` держит экран. Отладочные клавиши через `input keyevent` в UE НЕ доходят. Журнал и сейв: `/sdcard/Android/data/com.renchezlove.contrarysurvivor/files/UnrealGame/ContrarySurvivor/ContrarySurvivor/Saved/`.

**⚠️ УРОК ЭТОЙ СЕССИИ:** трое помощников (cpp, cpp-2, unreal) ушли в простой и не прислали отчёты — все ключевые причины нашёл сам грепом по коду и по манифесту пакета за считанные минуты. Вывод: короткую проверку фактов быстрее делать самому, помощников звать на объёмную работу.

## 🗄️ ПРОШЛОЕ СОСТОЯНИЕ (2026-08-02, ночь — установка APK на телефон Рината)

**ФАЗА:** Build 1.2.2, ветка `feature/build122`, **HEAD `fe54252`**, ветка ЗАПУШЕНА (пруф: `origin/feature/build122` = `fe54252`, рабочее дерево чистое). В master НЕ вливалось: qa-гейта по волне 1.2.2 ещё не было, маркера `.claude/QA_OK` нет (проверено).

**СОСТАВ ВОЛНЫ 1.2.2 — что закрыто (каждое с пруфом, проверено лидом лично):**
- Сокет хвата оружия (f19bee2, тесты 35/35); иконки предметов 18/18 импортированы (`Saved/b122-icons-import.txt`); тайловый UI (d976ba3); доводка инвентаря — слоты брони, зазоры плиток, два слота оружия (a014935 + 07a6036, тесты 37/37, verify 11 OK/0 FAIL); пикап обыскивается как труп (2b98e7a, тесты 37/37). Разбор — ADR-056.
- Правки Рината из редактора закоммичены: 13378e9, e20b5ee, 00d6197.
- **Постобработка кадра: СДЕЛАНА И ОТКАЧЕНА по решению Рината** («раньше была лучше»), откат `b33d3c6`, содержимое файлов сверено с 00d6197 — совпадает один в один. Знания про мобильный рендер сохранены в **ADR-057** (там же правило про упаковку мягких ссылок). Вступление (чёрный экран → плавное осветление за 2 с) проверено серией кадров живой игры `Saved/Screenshots/IntroSeries/`, кадры смотрел лично.
- **Иконки не попадали в пак** (мягкие ссылки из C++ не видны cook): починено `fe54252` (`+DirectoriesToAlwaysCook=(Path="/Game/UI/Icons")`), после пересборки в манифесте 18 иконок поимённо.

**APK НА ТЕЛЕФОНЕ (последнее состояние):** собран из отдельной копии `E:/ContrarySurvior/pack-android` (worktree на `fe54252`), лог `Saved/b122-android-pack5.log`, EXIT 0; установлен — ответ `Success`, `lastUpdateTime=2026-08-02 22:37:46`, разрешения на хранилище выданы. Размер вырос 221 → 289 МБ (иконки несжатые, по 1 МБ — хвост на ужатие перед публикацией).

**▶ СЛЕДУЮЩИЙ ШАГ:** дождаться живой проверки Рината на телефоне (иконки, инвентарь, обыск мешка, реклама-заглушки) → qa-гейт волны 1.2.2 → мерж 1.2.1 + 1.2.2 в master одной операцией → плановая таблица.

**НЕ ПРОВЕРЕНО (честные границы):** реклама Yandex на живом Android (Win64-плагин линкуется, APK собирается, но живого показа заглушки никто не видел); резкость тонмаппера на устройстве; вид плиток/инвентаря в PIE глазами (за Ринатом).

**▶ ЖДЁТ РИНАТА:** живая приёмка 1.2.1 и 1.2.2 (потом мерж); ответ издателя про согласие на рекламу (bUserConsent=True временно); ссылка на телеграм-канал; удвоение ежедневки со 2-го дня; замена двух шаров лута на BP_Pickup.

**▶ ХВОСТЫ (не блокеры):** ужать иконки (сжатие или 256 px); тост-системы нет; вторые параметры GA-событий в QA-лог; BP_BanditBase без pickup_class; музыка интро; RuStore/VK; свечение материалов костра/окон (множитель 5–15) — если когда-нибудь вернёмся к свечению.

**ИНФРА (стартовая точка):** редактор ЗАКРЫТ, движковых процессов 0 (проверено tasklist). Гейм-репо `E:/ContrarySurvior/ContrarySurvivor` (ветка feature/build122, дерево чистое), пак-копия `E:/ContrarySurvior/pack-android` (detached на fe54252). Движок `E:/UnrealEngine/UE_5.5`. Team-репо `E:/game-dev-team`, ветка `docs/phase0-gdd`.
**📱 ANDROID:** adb = `E:/Android/sdk/platform-tools/adb.exe`, телефон realme RMX3938 виден как `device`. Пак: `RunUAT.bat BuildCookRun -platform=Android -cookflavor=ASTC -clientconfig=Development -build -cook -stage -pak -package -archive` из pack-android с env JAVA_HOME/ANDROID_HOME/NDKROOT; повторный пак ~1–1,5 мин. Установка: `adb install -r` с ВИНДОВЫМ путём + `pm grant ... WRITE_EXTERNAL_STORAGE`.

**▶ УРОКИ ЭТОЙ СЕССИИ (08-02, ночь):**
1. **Показывать кадр ДО реализации.** Полный цикл постобработки (3 коммита, сборки, тесты, числа художника) ушёл в мусор, потому что вкус владельца не был снят с одного кадра заранее. Визуальные задачи начинать с одного-двух кадров на согласование.
2. **Не судить о чужой работе по срезу диска, не сверив время.** Дважды упрекнул cpp в невыполненном пункте, а расходились почта и коммит. Перед упрёком — `git log` по ветке, а не только `grep` по файлу.
3. **Материал ≠ постобработка.** Назвал белую крышу пересветом, а она белая по материалу. Прежде чем звать дефект дефектом — проверить сам ассет.
4. **Кадр вступления не годится для оценки грейда** — вступление намеренно затемняет (alpha 0 → 1). Оценивать только после `QA: intro control handed to player`.
5. **Новый ассет из кода — проверять по манифесту пакета** (ADR-057), а не по редактору. Иконки уехали в пустоту ровно так же, как раньше одежда Т0.
6. **PS1 с кириллицей — только с BOM**, иначе PowerShell падает на разборе строк (повтор старого урока, снова наступил).
7. Ринат может смотреть постобработку сам: она видна ТОЛЬКО в Play (сидит на камере игрока), ручки — в `BP_PlayerCharacter` → Class Defaults → категория `Camera|PostProcess`.


## 2026-08-09 (день) — волна главного меню: подходы 2 и 3, брак раскладки, переделка
- Подход 2 (экран настроек + автовыбор качества) `c5769c8`,`77c5325`; подход 3 (надпись «Прогресс сохранён», выход в меню из паузы, вибрация) `fda5a33`,`3fcd9c4`; мои прогоны генератора `5bb0b35`,`c4b6753`,`a86e70d`. Тесты 108/0.
- ⛔ БРАК: меню завёрнуто Ринатом живьём («всё поехало»). Причина моя — гнал точечную пересборку с ВКЛЮЧЁННЫМ переносом значений владельца, старая геометрия перетёрла новую раскладку (`Saved/gl-startscreen-rebuild.log:214-216`). Урок вошёл в ADR-064 доп.12 и в правило «перенос выключать у окон, где правок владельца нет».
- Переделка меню сдана коммитами `ee20959`,`cdf2ec8`,`5740256`,`aae7bb2`,`c1dd5d7`; печать геометрии в проверке окон `a688d25`; название «Марево» утверждено; фон — статичная картинка с волком (видео отклонено).
- QA-«добро» на `a86e70d` (тесты 108/0, 30 окон без провалов) — устарело, ветка ушла далеко вперёд, нужен новый гейт.
- Задача Г (полоса голода) СНЯТА как несуществующая: вечером выяснилось, что полос не было вовсе из-за виджета, спрятавшего сам себя (ADR-066 п.1), а не из-за полосы голода.
