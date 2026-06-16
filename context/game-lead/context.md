# context: game-lead

> Персональная (живая) память агента `game-lead`. Грунтовка сессии — ТОЛЬКО блок «🧭 СЕЙЧАС» ниже (правило bootstrap CLAUDE.md). Прошлое — `archive.md` (read-on-demand). Решения — `docs/decisions.md` (ADR). История — git. Дизайн-правда — `docs/contrary-survivor/`.
> СТОП-правило гигиены: >150 строк ИЛИ Read обрезается → СНАЧАЛА чистка (вынос закрытого в archive.md, удаление перетёртого), потом работа. Дистилляция ВЫРЕЗАЕТ прошлый «СЕЙЧАС», не только дописывает.

## 🧭 СЕЙЧАС (2026-06-16, конец сессии)
**РЕЖИМ (новое, ВАЖНО):** доверие Рината просело за сессию. Теперь — **НИЧЕГО не делать без его явной команды** (ни делегирования, ни правок). Визуальный контроль — **Ринат сам** (я headless-скрины НЕ делаю). Это перекрывает прежнюю «полную автономию»: действовать только по команде.

**Репо:** game `feature/clean-village` = **d35126f** (запушен origin RenchezLove/ContrarySurvivor). master=627d243. Team `docs/phase0-gdd` = **f36f136** (запушен).

**ЗАЩИТА ОТ ДРЕЙФА внедрена (f36f136):** CLAUDE.md — GATE-«маяк» в самом верху + ПРАВИЛА №0.1 (логика/причинный порядок + анти-«тупизм») после №0. Хук `UserPromptSubmit` (`.claude/hooks/inject-gate.ps1`) инъектит маяк в контекст КАЖДЫЙ ход — доказано артефактом (лог + видимый эффект). Лог хука `gate-inject.log` в .gitignore.

**ЭТАП 3b (L_World) — рабочее состояние, закоммичено d35126f (детали/координаты — в коммите и logs/build_village.log):**
- Земля: `SM_GroundGrid` (Geometry Script AppendRectangleXY, 121×121=14641 верш, UV0, ±6000) вместо 4-верш Plane. Материал `M_GroundBlend` = Lerp(трава 0.18,0.30,0.12 ↔ грунт 0.32,0.22,0.12) по VertexColor.R, Roughness 0.9. Плагин `GeometryScripting` включён в .uproject.
- Дорога: **vertex-paint** (427 верш R=1, коридор X[−3000,3000] Y[−300,300]) — НЕ отдельный меш. Прямая улица восток↔запад через центр.
- Деревня (схема Рината: context/BugReports/Bug Report 16): 6× `SM_VillageHouse` (550×498×460), север Y+900 / юг Y−900, X=−1400/0/+1400, BlockAll, **yaw=0 (фасады НЕ выверены — нужен глаз Рината)**. Трава 2800→2046 (вырезана под домами/дорогой).
- NPC: **ВРЕМЕННО** C++-актёры `ElderNPC_1`(450,600)/`TraderNPC_1`(1000,1000) — ПЕРЕДЕЛАТЬ (см. след. задача).
- `TestFloor` (коллизия ходьбы, ±6000, BlockAll) НЕ тронут. PlayerStart(0,0,98), камера arm 3000.

**СЛЕДУЮЩАЯ ЗАДАЧА (план согласован, ЖДЁТ «го» Рината):** торговец/староста → **BP-наследники `MasterHumanoidCharacter`**.
- Архитектура (направление от Рината): `MasterHumanoidCharacter` (C++, ACharacter, Abstract) → `AMasterTrader`/`AMasterElder` (C++, логика магазина/квестов) → `BP_Trader`/`BP_Elder` (меш/анима/тюнинг, на уровень). Староста — мой выбор = симметрия торговцу.
- ⚠ КРИТИЧНО: MasterHumanoidCharacter — Pawn с TakeDamage/Health → чтобы NPC не стали мишенями: БЕЗ `UStatsComponent` (авто-лок/хелсбары фильтруют по StatsComponent — проверено), override `TakeDamage`→no-op, капсула игнорит трассу оружия (пули сквозь), но блок прохода. Общую NPC-механику (сфера-триггер/регистрация у PlayerController) — в переиспользуемый КОМПОНЕНТ (композиция, оба прямые наследники MasterHumanoidCharacter).
- Декомпозиция: cpp-dev (классы + перенос логики из старых AActor `ATraderNPC`/`AElderNPC` + обновить ссылки PlayerController/HUD/тесты + убрать старые) → сборка + qa (компиляция зелёная, лог) → unreal-operator (BP-дети + меши/AnimBP `ABP_HumanoidCharacter` + расстановка + удалить врем. C++-актёры) → Ринат PIE (торговля/квест/не-мишень/блок прохода).

**УРОКИ сессии 06-16:**
- Дисциплина (после провалов): НЕ действовать без команды Рината; STOP=немедленно стоп; самоотчёт напарника СВЕРЯТЬ по артефакту (лог/mtime/дамп) САМ, не транслировать на слово.
- Headless-скрин: строго top-down (pitch −90) выходит ЧЁРНЫЙ; рабочий — УГЛОВОЙ loc(1700,1700,1200) rot(−33,−135,0). НО Ринат запретил мне скрины — смотрит сам.
- Geometry Script headless рабочий: AppendRectangleXY (верш = steps на сторону) + create_new_static_mesh_asset_from_mesh (Python-класс `GeometryScript_NewAssetUtils`); плагин включить в .uproject.
- Болванки вышли из-за того, что NPC искали как BP, а это C++-классы → урок: сверять архитектуру с кодом ДО постановки.

**Долги:** фасады домов (yaw); финал-арт NPC (меша торговца нет, SK_Elder — черновик); далее базы бандитов/логово волков + спавнеры + навмеш; оптимизация под мобилки — отдельная фаза (docs/contrary-survivor/mobile-optimization.md).

## ⚡ ПОСТОЯННЫЕ ДИРЕКТИВЫ (Ринат)
- **НИЧЕГО без явной команды** (новое, 06-16) — пока доверие не восстановлено. Не «золотить», не лезть за рамки задачи.
- **Визуал смотрит РИНАТ сам** (06-16): game-lead headless-скрины НЕ делает; приёмка визуала/геймплея = живой PIE Рината.
- **ЛУЧШИЕ практики** UE/кода, оптимально; статика на уровень, не сабсистемы. Editor open/close — на game-lead (не дёргать Рината). ПОЯСНЯТЬ термины (Ринат не UE-технарь). План крупного — на утверждение. Каждый этап = тест Ринатом.
- **ПРУФ (анти-фабрикация):** «собралось/тест прошёл» — только с логом; «закоммичено» — только после git status/log; факт ≠ догадка (GATE/№0).

## Решения / Инструменты
- Все решения — `docs/decisions.md` (ADR-001..021). Инструменты: Blender MCP (modeler-3d), unreal-mcp (unreal-operator), code-render (concept-artist), GDrive (бэкап). cpp-dev/qa — нативный Claude Code.
- Headless-конвейеры: UE `UnrealEditor-Cmd "<uproject>" -ExecutePythonScript="<abs.py>" -unattended -nopause -nosplash` (лог в Saved/Logs или -abslog). Импорт FBX uniform_scale=1. Навмеш-бейк: `-run=ResavePackages -MAPSONLY -PACKAGE=<map> -BuildNavigationData`. Консольный in-editor BuildPaths КРАШИТ.
- НОВОЕ: Geometry Script headless (см. УРОКИ). Защита от дрейфа: GATE-маяк + хук UserPromptSubmit + №0.1.

## Ограничения
- QA-гейт: маркер `.claude/QA_OK` создаёт game-lead вручную только после «добро» qa (с артефактом), снимает сразу после merge; не коммитится. Проверять висячий при старте.
- Напарники — только фича-ветки, не master. Merge в master — после QA. ≤3 агента, субагенты не порождают субагентов.
- Гейм-репо своего хука-гейта НЕ имеет → политику веток держу вручную. /Content через Git LFS (ADR-019).

## РЕПО / HEAD
- **Гейм-репо** `E:/ContrarySurvior/ContrarySurvivor` (UE 5.5.4), origin RenchezLove/ContrarySurvivor. Рабочая ветка `feature/clean-village` = d35126f (запушена). master=627d243 (Фазы 1-4). Сборка: `Build.bat ContrarySurvivorEditor Win64 Development` при ЗАКРЫТОМ редакторе.
- **Team/инфра-репо** `E:/game-dev-team`: ветка `docs/phase0-gdd` = f36f136 (push GitHub RenchezLove/game-dev-team).

## 🎮 DEBUG/ТЕСТ-КЛАВИШИ (LogQA-строки на ключевые события)
F1 debug-камера · F2 GiveTestItems · F3/F4 броня вкл/выкл · F6 use · F7 drop · F9/F10 buy/sell · F12 clear-save · M +100 денег · T телепорт-торговец · Y телепорт-староста · G offer+accept квест · H сдать квест · K +1 волк · J god+заморозка статов · U force-drop 100% · B тест-волк вплотную · O QA-оверлей · N force-kill ближнего · V телепорт-Логово · Z телепорт-база · C выдать 5 «Шкур волка» · X выдать «Ноутбук» · P убить игрока. Магазин: стрелки/колесо ±1, Shift ±10, Enter подтвердить. **(F5/F8/F11 движковые — НЕ занимать.)**
