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
- **Push волны A+B в origin — ВЫПОЛНЕН (2026-06-11, авторизовано Ринатом).** Легитимный гейт-проход: `.claude/QA_OK` создан ОТДЕЛЬНЫМ вызовом (лежал на диске ДО push) → `git push origin master` (`72b39f8..2b11275`) → маркер снят СРАЗУ. Итог: `master == origin/master == 2b11275`, ahead/behind = 0/0. Висячего QA_OK нет, гейт активен (hooksPath=абс .githooks). Примечание: сам этот docs-коммит (`docs/context-sync`) в origin ещё не уехал — уйдёт следующим бэкапом.

### СЛЕДУЮЩИЙ ШАГ — РАЗВИЛКА ДЛЯ РИНАТА (инфра-каркас практически собран)
Открытые ветки решения (ждём выбор):
1. **T6 (qa-testbed)** — последний инфра-хвост. Дать qa изолированный стенд для самостоятельного прогона матрицы гейта.
2. **Старт фазы разработки игры** — подключение диздока ContrarySurvivor (Фаза подключения проекта) + первая игровая задача. Первой игровой задачи ещё не было.
- (Push волн A+B в origin — ВЫПОЛНЕН 2026-06-11, см. выше; из развилки убран.)
- Рестарт сессии, который требовался для активации T3 `tools:`/самохила T7/сброса кеша — судя по git-состоянию и активному hooksPath, уже произошёл (гейт git-native активен). Доп. рестарт не требуется.
