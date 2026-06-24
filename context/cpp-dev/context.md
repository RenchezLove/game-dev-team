# context: cpp-dev

> Лёгкая рабочая память `cpp-dev` (правило H + Гигиена памяти из CLAUDE.md: стоп >150 строк, СЕЙЧАС вырезает прошлый). Закрытая история — в [archive.md](archive.md) (read-on-demand, НЕ для грунтовки). Build-логи — `logs/`, история — git.

## 🧭 СЕЙЧАС
ФАЗА A демо-плана (перевод рабочего функционала на принятую архитектуру; механику НЕ переписываем).
Ветка **feature/clean-village**. НЕ коммичено (по правилу) — A2+A3 лежат в рабочем дереве вместе.

**A2 ЗАСЧИТАН game-lead** (магазин развязан от класса через интерфейс IShopVendor). Лог `logs/a2-shopvendor-build.log` (BUILD_EXIT=0). Суть: `Actors/ShopTypes.h` (FShopEntry/EShopEntryKind) + `Actors/ShopVendor.h` (UINTERFACE IShopVendor: GetCatalog/GetSellValue/GetAmmoSellPerRound, плейн-virtual). PC.NearbyTrader/HUD.ShopTrader → `TScriptInterface<IShopVendor>` (IsValid через `.GetObject()`, имя `GetNameSafe`, поиск `Implements<UShopVendor>()`). AMasterTrader реализует IShopVendor + overlap регистрирует `PC->SetNearbyTrader(this)`. ATraderNPC УДАЛЁН.

**A3 СДЕЛАН (2026-06-24), сборка PASS** — лог `context/cpp-dev/logs/a3-elder-build.log` (BUILD_EXIT=0, релинк DLL, редактор был закрыт). Файлы: `Actors/ElderNPC.h/.cpp`.
- База `AElderNPC : AActor` → `: AMasterHumanoidCharacter` (по образцу AMasterTrader): тонкий модульный гуманоид. УДАЛЕНЫ placeholder-визуал (CharMesh/MeshComponent/Beacon/PlaceholderColor) и тест-поле TestPingValue; убран C++ ABP-finder + SK-finder (меш/ABP теперь назначает BP_Elder, как BP_Trader).
- Добавлено `AutoPossessAI = EAutoPossessAI::Disabled` (риск авто-AIController из плана). InteractTrigger на капсуле-корне; PostInitializeComponents — Leader Pose Torso/Legs→Head (как у трейдера). Квест-данные перенесены как есть. Overlap (SetNearbyElder/ClearNearbyElder) без изменений. IShopVendor тут НЕ нужен — Elder не идёт через интерфейс, NearbyElder остался `AElderNPC*` (консьюмеры не трогал).
- A1: шкуры 5→3 (RequiredItemCount + текст Description «три … шкуры», чтобы UI не противоречил гейту).
ХВОСТ ДЛЯ unreal-operator (editor, НЕ моя часть, оба батчем):
  - A2: L_World держит placed СТАРЫЙ ATraderNPC (станет missing-class); BP_Trader (AMasterTrader) НЕ размещён → снять старый + поставить BP_Trader.
  - A3: BP_Elder НЕ существует (есть только SK_Elder.uasset); placed AElderNPC стоит прямо на L_World (станет missing-class после reparent на ACharacter). C++ Elder теперь БЕЗ визуала → нужно СОЗДАТЬ BP_Elder (модульные меши Head/Torso/Legs + ABP, как BP_Trader) и поставить, снять старую болванку. Риск PIE: капсула Character'а твёрдая (может загородить проход) — проверить.
Доп. правка 2026-06-24 (comment-only, БЕЗ сборки): ElderNPC.h:22-24 шапка приведена к факту («Collect-квест „3 шкуры“, без kill-цели»).

**A5 — РАЗВЕДКА СДЕЛАНА (2026-06-24), план принят game-lead, кода НЕ трогал. РЕАЛИЗАЦИЮ НЕ НАЧИНАТЬ до отмашки** (после приёмки A2+A3 Ринатом в PIE; редактор ДОЛЖЕН быть ЗАКРЫТ к сборке).
✅ РЕШЕНИЯ game-lead по 4 вопросам (зафиксировано): (1) активация — ОСТАВИТЬ проверенный таймер+XY-дист (НЕ sphere-overlap: перенос без смены поведения), локация из GetActorLocation() placed-актора, параметризовать; (2) SpawnDelay — EditAnywhere дефолт ~0.5с, тюнинг в BP; (3) NumToSpawn — нейтральный C++-дефолт (1), 4/3 ставят BP_WolfDen/BP_BanditBase (ADR-024); (4) EnemyAIController QA-хуки — НЕ ТРОГАТЬ (боевой контроллер, урок 06-16), мёртвый код оставить.
Сверенные факты A5 (line актуальны 06-24): удалить Subsystems/WolfSpawnSubsystem.{h,cpp} + BanditSpawnSubsystem.{h,cpp}; SpawnPlacementUtils.h ОСТАВИТЬ (переиспользует новый AMasterEnemyBase). «5 волков» = WolfSpawnSubsystem.h:68 (уйдёт с файлом; «4» → BP_WolfDen.NumToSpawn). Debug-хуки удалить: PC.cpp функции OnQATeleportToWolfDen(454-491)/OnQATeleportToBanditBase(493-531)/QA_RunWolfChaseTest(550-593)/QA_WolfChaseSample(595-700)/QA_FinalizeWolfChaseTest(702-751); инклуды PC.cpp:29-30; биндинги PC.cpp:158(V)/161(Z); PC.h декларации :92/:292/:298 + поля QAChase* ≈:425-441; удалить Debug/QAChaseTest.cpp целиком; DefaultInput.ini:60(V)/64(Z) снять (B :54 остаётся). AMasterEnemyBase (новый placed AActor): EnemyClass `TSubclassOf<ACharacter>` (оба врага — ACharacter), NumToSpawn/ActivationRadius/SpreadRadius/SpawnDelay + опц.квест (QuestItemClass/PickupClass/QuestItemName). Оператор: BP_WolfDen(4,север)/BP_BanditBase(3+ноутбук,юг)/BP_Wolf:AWolfCharacter. Проверено: сабсистемы нигде в Content/Config; cs.TestWolfChase только QAChaseTest.cpp+2 коммента.

**A4 — РАЗВЕДКА СДЕЛАНА (2026-06-24), план принят. РЕАЛИЗАЦИЮ НЕ НАЧИНАТЬ** (редактор ОТКРЫТ под A2+A3; ждать: PIE-приёмка → редактор закрыт → отмашка). Очередь: сначала A5, потом A4.
✅ РЕШЕНИЯ game-lead: Q1 «вне деревни» = вариант (a): флаг bInSafeZone на игроке, тоггл Campfire Begin/EndOverlap (сейчас только BeginOverlap — добавить EndOverlap + флаг); штраф ТОЛЬКО если умер вне safe-zone. Q3 мешок = ОДИН мульти-предметный (расширить APickup списком предметов; если расширение начнёт разрастаться/рисковать — СТОП+флаг game-lead). Q4 = −40% ПОСЛЕ LoadGame + ПЕРЕ-СОХРАНИТЬ игру (штраф переживает quit/reload, анти-эксплойт). Q5 попап = на существующем DrawDeathScreen (показать −40% монет + «расходники остались на месте гибели»), НЕ новый toast. ⏳ ЖДУ от Рината: Q2 (доля дропа — реком game-lead ВСЕ неэкип. Consumable) + текст/формулировку попапа.
Сверенные факты: текущий штраф ApplyDeathInventoryPenalty() PlayerCharacter.cpp:1129-1160 (удаляет 0.25 от Consumable+Resource через RemoveItem, без мешка; DeathItemLossPercent decl .h:179). HandleDeath() :1162 (экран смерти, подписка Stats->OnDeath :209). Respawn() :1200 порядок: penalty(шаг1,до телепорта)→LoadGame(шаг2,перезаписывает деньги/позицию из сейва костра)→форс HP/голод/жажда. Респаун-точка=Save->PlayerLocation (автосейв костра Campfire.cpp:33-56→SaveGame→PlayerLocation :1043). ⚠️ «вне деревни» рантайм-проверки НЕТ (village = только нав-область UNavArea_Village). Деньги: UStatsComponent::Money (StatsComponent.h:104), −40%=`SpendMoney(GetMoney()*0.40f)` (всегда ок, broadcast HUD); ⚠️ применять ПОСЛЕ LoadGame (иначе перезатрётся). Дроп-мешок: APickup несёт 1 предмет (Pickup.h:74); Inv_DropItem PlayerCharacter.cpp:588-640 уже роняет инстанс мировым пикапом (паттерн готов); «мешок N» = N пикапов ИЛИ расширить APickup списком. Категория фильтр Consumable: GetUnequippedItemsOfCategory (UInventoryComponent.h:49); Quest никогда не теряется. UI: transient-toast в HUD НЕТ; есть DrawDeathScreen HUD.cpp:1237 (хост для текста штрафа). Тех-долг сейва (ItemName/StackCount) — отложен к E2 (ContrarySaveGame.h только class-paths :51), НЕ чиню. Открытые вопросы Q1(вне деревни?) Q2(доля дропа?) Q3(мешок 1 vs N?) Q4(база −40% + переписывать сейв?) Q5(попап где? текст ждёт Рината) — в треде game-lead.

КАРТА ФАЗЫ A (факты с пруфом, на старт реализации):
- **A2 (старт):** `IShopVendor` НЕ существует. Контроллер/HUD жёстко под `ATraderNPC*`
  (ContrarySurvivorPlayerController.cpp:1343 `Cast<ATraderNPC>`→OpenShop; HUD SetShopOpen(ATraderNPC*)).
  Рабочий магазин в PIE = placed `ATraderNPC` (НЕ MasterTrader: его overlap не регистрируется, MasterTrader.cpp:120).
  План: вынести `FShopEntry`/`EShopEntryKind` из TraderNPC.h:20-62 в нейтральный заголовок (3 потребителя:
  MasterTrader.h:8, PlayerCharacter.cpp:28, HUD .cpp:21) → создать `IShopVendor`(GetCatalog/GetSellValue/
  GetAmmoSellPerRound) → ретипизировать PlayerController+HUD → `AMasterTrader` реализует+регистрируется →
  удалить ATraderNPC. `AMasterTrader` уже создан/собран (HP-порог TakeDamage без Super, без StatsComponent).
- **A3 (староста):** `AElderNPC:AActor` (ElderNPC.h:32), квест-данные в конструкторе (cpp:89-112) портируемы.
  Сменить базу на `AMasterHumanoidCharacter` по образцу MasterTrader.cpp:23-66. Риск: капсула блокирует, авто-AIController.
- **A5 (спавн):** `AMasterEnemyBase`/`BP_Wolf`/`BP_WolfDen`/`BP_BanditBase` НЕ существуют. Подсистемы
  Wolf/BanditSpawnSubsystem завязаны на QA-хуки контроллера (PC.cpp:465/505/565 — V/Z/cs.TestWolfChase) —
  удаление сломает сборку, переписать/выпилить.
- **A1 (числа, хардкод, DataTable нет):** менять 2 — шкуры 5→3 (ElderNPC.cpp:96), волки 5→4 (WolfSpawnSubsystem.h:68).
  Бандиты(3)/награды(150/250) уже верны. Числа вшивать ВНУТРЬ A3/A5, не отдельным проходом.
- **A4 (сейв/респаун):** защита квест-предметов УЖЕ работает (категория Quest; шкура+ноутбук = AQuestItem).
  НЕТ: штраф −40% денег, дроп-мешком, UI-попап. Текущий штраф = удаление 25% Consumable/Resource (PlayerCharacter.cpp:1129).
- **Хардкод-пути:** 2 ABP-finder (TraderNPC.cpp:52, ElderNPC.cpp:44 → `/Game/TestContentAndCode/PreProduction/
  ABP_HumanoidCharacter`) УЖЕ СЛОМАНЫ (ассет переехал в Characters/Shared/Humanoid/) → закроются фазой A.
  Armor×3/Knife/Pistol/Bandit-BP пока резолвятся, но есть дубли в feature-first папках (зависит от реорга).

## LIVE-КОНВЕНЦИИ (как работаю в этом проекте)
- **Include внутри модуля**: префикс `ContrarySurvivor/<Subdir>/Header.h`. Относительный `Components/Header.h` из другой подпапки НЕ резолвится (C1083).
- **override UFUNCTION** — БЕЗ повтора макроса `UFUNCTION()` над override (UHT запрещает; reflection наследуется от базовой virtual UFUNCTION, AddDynamic работает).
- **Сборка `-WarningsAsErrors`**: нельзя шэдоуить члены базы (напр. `APawn* Pawn` → C4458 на `AController::Pawn`, переименовывать в `ControlledPawn`).
- **Команда сборки**: `Build.bat ContrarySurvivorEditor Win64 Development -Project=E:/ContrarySurvior/ContrarySurvivor/ContrarySurvivor.uproject -WaitMutex -NoHotReload`. Запускать НАПРЯМУЮ с `2>&1 | tee log`, НЕ через `cmd /c` (вложенный cmd не редиректит → пустой лог, ложный exit 0).
- **Релинк DLL только при ЗАКРЫТОМ редакторе** (иначе LNK1104 на `UnrealEditor-ContrarySurvivor.dll`). Проверять tasklist. Компиляция .cpp+.lib проходит и при открытом — «компиляция PASS, релинк отложен».
- **Среда**: проект `E:/ContrarySurvior/ContrarySurvivor/` (UE 5.5.4), движок `E:/UnrealEngine/UE_5.5` (реестр HKLM\SOFTWARE\EpicGames\Unreal Engine\5.5), VS2022 MSVC 14.44. API сверять по заголовкам движка, не по памяти.
- **Не коммитить ассеты оператора** (BP_*.uasset, *.umap) — только свои Source/. Работаю в фича-ветке, master/merge не трогаю.

## Решения
- Health: база `AMasterHumanoidCharacter` держит инлайн Health/TakeDamage (игрок+оружие). Враг `AEnemyCharacter` несёт `UStatsComponent`, переопределяет `TakeDamage` БЕЗ Super (источник истины HP врага = компонент). Миграция игрока на компонент отложена.
- `HandleDeath()` virtual в базе; враг override. `ReloadCurrentWeapon` virtual в базе; игрок override (тянет патроны из рюкзака перед штатной перезарядкой).
- `GetMesh()==HeadMesh==Leader` модульного гуманоида; Torso/Legs — followers через SetLeaderPoseComponent. Оружие крепится к кости `R_Hand` лидер-меша (не к сокету — сокетов в ассетах нет).

## Ограничения / тех-долги (DRAFT, на тюнинг/добивку)
- Save/Load НЕ сохраняет `ItemName`/`StackCount` (только class path) → после reload имена предметов/прогресс item-целей квестов и стак патронов теряются. Пре-существующее, save-систему не трогал (риск кору).
- Атака врага в Attack-стейте без LineOfSight-гейта → теоретически удар через тонкую стену в упор (на открытых зонах демки не проявляется).
- Числа баланса/камеры/звуков — DRAFT UPROPERTY (EditAnywhere): walk≈600/sprint≈1200, пистолет 25@2с, нож 35, бандит HP80/650 walk, волк HP40/780, броня 0.50 (кап 0.75), награды квестов 150/250.
- invoker-навмеш требует RecastNavMesh `RuntimeGeneration=Dynamic` в уровне (если оператор сменит на Static — погоня сломается).
- TEMP диаг-цепочка движения (MOVE/VELKILL/PIPELINE/BLOCK + BeginPlay-диаг) — снять после подтверждения WASD в PIE.
