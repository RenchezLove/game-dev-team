# context: cpp-dev

> Лёгкая рабочая память `cpp-dev` (правило H + Гигиена памяти из CLAUDE.md: стоп >150 строк, СЕЙЧАС вырезает прошлый). Закрытая история — в [archive.md](archive.md) (read-on-demand, НЕ для грунтовки). Build-логи — `logs/`, история — git.

## 🧭 СЕЙЧАС
**КОСТЁР настраиваемый (фидбек Рината, ветка feature/clean-village) — СБОРКА PASS + ЗАКОММИЧЕНО `1645bd9`** (`logs/campfire-settings-build.log`, BUILD_EXIT=0, -WarningsAsErrors, DLL релинк при закрытом редакторе, 2 файла Source/.../Actors/Campfire.{h,cpp}). Закоммитил ТОЛЬКО Source — ассеты оператора (BP_Campfire.uasset/L_World.umap и пр.) не трогал. STANDBY: game-lead в редакторе делает репарент BP_Campfire→ACampfire + чистку дублей компонентов + назначение SM_Campfire на унаследованный Mesh + УБИРАЕТ save-узлы из графа BP (сейв оставляем в C++, согласовано). Ждёт PIE-приёмку Рината + qa-гейт. Задача была: SafeZoneRadius у размещённого костра не двигал сферу (фикс) + поднять параметры наверх Details + настройка света.
- РЕШЕНИЕ: расширил СУЩЕСТВУЮЩИЙ `Source/.../Actors/Campfire.{h,cpp}` (`ACampfire:AActor`), НЕ создавал дубль-класс `ASafeZoneCampfire` — у ACampfire уже были нужные имена компонентов (SceneRoot/Mesh/SafeZoneTrigger) + C++ автосейв-overlap. game-lead думал, что C++-костра нет (смотрел дамп BP). Флагнул это в отчёте.
- Что добавил: компонент `FireLight` (UPointLightComponent, Movable, имя сабобъекта "FireLight" под репарент BP); параметры огня `FireLightIntensity/FireLightColor/FireLightAttenuationRadius`; ВСЕ тюнинг-поля → EditAnywhere+BlueprintReadWrite+meta DisplayPriority 1..5; `OnConstruction` синхронит `SafeZoneTrigger->SetSphereRadius(SafeZoneRadius)` (ФИКС бага) + применяет свет. SafeZoneRadius/AutoSaveCooldown: BlueprintReadOnly→ReadWrite.
- ВАЖНО (свет): SetIntensity/SetLightColor/SetAttenuationRadius гейтятся `AreDynamicDataChangesAllowed` → для Static-света в OnConstruction = no-op. Поэтому FireLight явно SetMobility(Movable). Сверено по UE5.5 хедерам (LightComponent.h:268/278, LocalLightComponent.h:52, SceneComponent.h:1289).
- БАГ-ХВОСТ для game-lead: C++ ACampfire уже делает автосейв на overlap; если репарентить BP_Campfire→ACampfire и НЕ убрать save-узлы из графа BP → двойной сейв (частично гасит антиспам 2с). Рекомендовал убрать save-узлы из BP, сейв оставить в C++.
- ЖДУ сигнала game-lead на сборку (он закроет редактор). Команда сборки — в LIVE-КОНВЕНЦИЯХ ниже.

---
**ФАЗА B доводка (PIE-фидбек Рината) — C++ ЗАКОММИЧЕН `f8c82ee`, сборка PASS** (`logs/phaseB-spawn-radius-details-build.log`, BUILD_EXIT=0, -WarningsAsErrors, релинк DLL при закрытом редакторе, 9 файлов). Ветка **feature/clean-village**, master НЕ тронут. STANDBY: ждёт qa-гейт (game-lead) + PIE-приёмку Рината. Дефолты в BP (NumToSpawn=4 в BP_WolfDen, 3 в BP_BanditBase) + расстановку ~7 точек делает оператор/game-lead в редакторе, НЕ я.
Что вошло в `f8c82ee` (3 правки):
- **ПРАВКА 2 (ADR-029, число врагов ≠ число точек):** `NumToSpawn` перенесён из Fallback-подкатегории в основную "EnemyBase", дефолт 1→3, EditAnywhere+ClampMin. `SpawnEnemies` (MasterEnemyBase.cpp): при наличии точек — Fisher–Yates перемешивание `SpawnTransforms` + спавн `min(NumToSpawn, число точек)` врагов в случайном подмножестве точек (было: 1 враг на каждую точку). Без точек — fallback круг NumToSpawn (как было). **Устройство точек:** 1 дефолтная `SpawnPoint0` в C++-ctor (образец) + дизайнер ДОБАВЛЯЕТ точки `UEnemySpawnPointComponent` вручную в BP; код берёт ВСЕ через `GetComponents<>()`. 7 точек в C++ НЕ хардкодил.
- **ПРАВКА 3 (ActivationRadius виден):** новый `USphereComponent* ActivationVisualizer` в `AMasterEnemyBase` (ctor: attach к SceneRoot, NoCollision, SetCanEverAffectNavigation(false), оранжевый ShapeColor). Каркас-сфера видна во вьюпорте редактора (UShapeComponent рисуется при `bDrawOnlyIfSelected=false` по умолч.) и скрыта в игре (`bHiddenInGame=true` по умолч. — проверено по движку 5.5). Радиус = ActivationRadius синхронизируется в новом `OnConstruction` (`SetSphereRadius`) — обновляется при правке в Details (превью BP и размещённый актор реконструируются).
- **ПРАВКА 4 (наши настройки выше в Details):** `meta=(DisplayPriority=N)` на лид-свойство каждой нашей top-level категории в 8 классах (EnemyBase/Humanoid/Trader/Elder/Wolf/Weapon/Enemy/Player). Механизм (проверен по PropertyEditor 5.5): категория сортируется по порядку регистрации = порядок DisplayPriority-отсортированного обхода свойств; Transform-tier (1000) всегда выше Default-tier (4000), наши с DP идут первыми в Default-tier → сразу после Transform. База Humanoid=DP 50+, наследники=1+ (специфика выше унаследованного). ВИЗУАЛ порядка — подтвердить в ЖИВОМ редакторе (UI-вещь, не доказывается сборкой); подкатегория-only "Weapon"/"Audio" — чуть ниже уверенность в позиции родителя.

---
ИСТОРИЯ ФАЗЫ A (read-on-demand; A2/A3/A5 закоммичены ранее, A4-код теперь внутри `4bf8d07`):
- **A2 ✅ ЗАКОММИЧЕНО** (`c317d97`, PIE-принято): магазин развязан от класса через интерфейс `IShopVendor` (`Actors/ShopTypes.h`+`ShopVendor.h`; PC/HUD на `TScriptInterface<IShopVendor>`; `ATraderNPC` удалён). Детали — git.
- **A3 ✅ ЗАКОММИЧЕНО** (`c317d97`, PIE-принято): `AElderNPC` → база `AMasterHumanoidCharacter`; убран C++ ABP/SK-finder + placeholder-визуал; `AutoPossessAI=Disabled`; A1 шкуры 5→3. Детали — git.
- **A5 ✅ ЗАКОММИЧЕНО** game-lead (лог `logs/a5-enemybase-build.log` BUILD_EXIT=0): сабсистемы спавна → `Actors/MasterEnemyBase` (placed AActor, таймер+XY-активация, navmesh+floor-trace, опц.ноутбук); удалены Wolf/BanditSpawnSubsystem + QAChaseTest.cpp; выпилены debug V/Z + cs.TestWolfChase (PC.cpp/.h + DefaultInput.ini). EnemyAIController НЕ тронут (мёртвые комменты cs.TestWolfChase в нём + CombatAutomationTests.cpp:11 — безвредны). Оператор сейчас ставит BP_Wolf/BP_WolfDen(4,север)/BP_BanditBase(3+ноутбук,юг) — BP_* уже в дереве.

**A4 — СДЕЛАН + ПРАВКА «БЕЗУСЛОВНЫЙ ШТРАФ» (2026-06-25), сборка PASS** (`logs/a4-unconditional-build.log`, BUILD_EXIT=0, релинк DLL, редактор закрыт). НЕ коммичено. По **ADR-027** (фикс Рината 06-25: штраф при ЛЮБОЙ смерти, БЕЗ гейта safe-зоны):
- Штраф БЕЗУСЛОВНЫЙ в `Respawn` (PlayerCharacter.cpp): (1) `DropConsumablesAsBag(DeathDropLocation)` ДО телепорта — ВСЕ неэкип. Consumable одним мешком; (2) LoadGame; (3) `ApplyMoneyDeathPenalty` = `SpendMoney(GetMoney()*0.40f)` + `SaveGame()` (пере-сейв, анти-reload). Гейты `if(bDiedOutsideVillage)` УБРАНЫ. `HandleDeath` фиксирует только `DeathDropLocation`. Старый `ApplyDeathInventoryPenalty`/`DeathItemLossPercent` удалены.
- УБРАНЫ (фикс): `bInSafeZone`/`bDiedOutsideVillage`/`SetInSafeZone`/`DiedOutsideVillage` (PlayerCharacter) + `Campfire::OnSafeZoneEndOverlap` + bind + SetInSafeZone-вызовы. **Campfire НЕТТО без изменений** (A4 их добавил, фикс убрал → git не видит diff Campfire; автосейв BeginOverlap→SaveGame НЕ тронут).
- «Мешок» = мульти-предмет `APickup`: `CarriedItems` + `InitLootBag()`; Collect/EndPlay/HasLoot обрабатывают список (одиночный CarriedItem сохранён).
- Попап на `DrawDeathScreen` (HUD.cpp) — теперь БЕЗУСЛОВНО (гейт DiedOutsideVillage убран); финальный текст ADR-027 (ВЫ ПОГИБЛИ/−40% монет/расходники мешком/снаряжение цело).
- Валюта HUD `Money`/`Деньги`→«Монеты» (status/shop/persistent/death-stat). Иконка-монета — НЕ в C++ (нужна текстура, за оператором).
- Боевой код НЕ тронут; тех-долг сейва НЕ чинил (E2).
МОИ файлы A4 (Source, НЕ коммичено): Pickup.{h,cpp}, PlayerCharacter.{h,cpp}, HUD/ContrarySurvivorHUD.cpp, Public/AQuestItem.h. (Campfire нетто без изменений.) Content/* (L_World, BP_Campfire) = оператор, НЕ трогаю.

STANDBY — A4 ждёт PIE-приёмки Рината → коммит game-lead. Фаза A C++ почти закрыта (A2/A3/A5 закоммичены). Следующая C++-работа = **Этап E** (DT_Quests/DT_Items, DataTable) ПОСЛЕ Этапов B/C. Если Ринат найдёт баг A4 в PIE — позовут чинить.

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
