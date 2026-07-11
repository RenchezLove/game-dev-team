# context: cpp-dev

> Лёгкая рабочая память `cpp-dev` (правило H + Гигиена памяти из CLAUDE.md: стоп >150 строк, СЕЙЧАС вырезает прошлый). Закрытая история — в [archive.md](archive.md) (read-on-demand, НЕ для грунтовки). Build-логи — `logs/`, история — git.

## 🧭 СЕЙЧАС
**ЭТАП E «Прогрессия: броня» (ADR-042/043) — КОД ГОТОВ, 5 коммитов в `feature/stage-e-armor` (от master aee975d), НЕ запушено/не мёржено. Ждёт QA-гейт/приёмку.**
- Коммиты: `b90b31f` старт без брони+одежда Т0+F3=Т3; `cd34572` магазин (без _01, цены 50/120/250 полями, RebuildCatalog в BeginPlay); `ea601e0` ArmorProtection EditAnywhere + ItemIcon мягкой ссылкой в БАЗЕ AMasterInventoryItem (UHT запрещает шэдоуить имя базы в AArmor — сборка падала, пруф в build-логе v1); `bbc827a` HUD (иконки слотов, «Защита: N%» через новый GetEffectiveArmorFraction базы, русские подписи, «+N% защиты» в каталоге); `dfd483d` автотест нулевой защиты старта.
- Пруфы: сборка `logs/build-2026-07-11-stage-e-armor-final.log` (18/18, EXIT=0); тесты `logs/tests-2026-07-11-stage-e-armor.log` — 8/10 зелёные (7 старых Combat + новый).
- **Movement.NavWalkingFixed и Movement.TranslatesOnInput КРАСНЫЕ, но ПРЕ-СУЩЕСТВУЮЩЕЕ:** падают и на чистом master (git stash → сборка master → прогон; пруф `logs/tests-2026-07-11-movement-baseline-MASTER-fail-proof.log`). Не регрессия этапа E. Причина падения на master НЕ РАССЛЕДОВАНА — отдельная задача.
- Механизм Т0: `ApplyStartClothing()` в `PostInitializeComponents` игрока ставит SK_Cloth_T0_* в слоты ДО `CacheBaseSlotMeshes` (BeginPlay базы) → UnequipArmor возвращает одежду, не белое тело. Мягкая загрузка, фолбэк = меш из BP.
- Иконки: текстур НЕТ (папки /Game/UI/Icons нет; ждём художника). HUD ResolveIcon кэширует и успех, и неудачу (одна попытка на путь) → без спама; фолбэк = текст. Имена: T_Icon_Armor_T{1..3}_{Head,Torso,Legs}, T_Icon_Slot_{Head,Torso,Legs}.
- Сейвы проверены ЧТЕНИЕМ кода: SaveGame пишет пустые пути брони, ApplySaveData броню не читает → старт без брони/старые сейвы краш-путей не имеют. Живой PIE-прогон НЕ делался.
- В рабочей копии чужое: `Content/Maps/L_World_C.umap` (правка Рината) + `Content/_DIAG_ElderLegs/` — НЕ трогать, НЕ коммитить.

## LIVE-КОНВЕНЦИИ (как работаю в этом проекте)
- **Include внутри модуля**: префикс `ContrarySurvivor/<Subdir>/Header.h`. Относительный `Components/Header.h` из другой подпапки НЕ резолвится (C1083).
- **override UFUNCTION** — БЕЗ повтора макроса `UFUNCTION()` над override (UHT запрещает; reflection наследуется от базовой virtual UFUNCTION, AddDynamic работает).
- **Сборка `-WarningsAsErrors`**: нельзя шэдоуить члены базы (напр. `APawn* Pawn` → C4458; локальную переменную не называть `Mesh` в наследниках ACharacter).
- **Команда сборки**: `Build.bat ContrarySurvivorEditor Win64 Development -Project=E:/ContrarySurvior/ContrarySurvivor/ContrarySurvivor.uproject -WaitMutex -NoHotReload`. Запускать НАПРЯМУЮ с `2>&1 | tee log`, НЕ через `cmd /c` (вложенный cmd не редиректит → пустой лог, ложный exit 0).
- **Релинк DLL только при ЗАКРЫТОМ редакторе** (иначе LNK1104 на `UnrealEditor-ContrarySurvivor.dll`). Проверять tasklist. Компиляция .cpp+.lib проходит и при открытом — «компиляция PASS, релинк отложен».
- **Среда**: проект `E:/ContrarySurvior/ContrarySurvivor/` (UE 5.5.4), движок `E:/UnrealEngine/UE_5.5`, VS2022 MSVC 14.44. API сверять по заголовкам движка, не по памяти.
- **Не коммитить ассеты оператора** (BP_*.uasset, *.umap) — только свои Source/. Работаю в фича-ветке, master/merge не трогаю. Новые параметры — EditAnywhere+BlueprintReadWrite+meta DisplayPriority наверх (директива Рината 06-25).

## Решения
- Health: игрок И враги — через `UStatsComponent` (TakeDamage БЕЗ Super). Инлайн-Health базы `AMasterHumanoidCharacter` — легаси для оружейной системы.
- `HandleDeath()` virtual в базе; враг/игрок override. `ReloadCurrentWeapon` virtual; игрок тянет патроны из рюкзака (AAmmoItem-стак).
- `GetMesh()==HeadMesh==Leader` модульного гуманоида; Torso/Legs — followers через SetLeaderPoseComponent. Оружие крепится к кости `R_Hand` лидер-меша (сокетов в ассетах нет), офсеты грипа — параметры WeaponGripLocation/Rotation.
- Волк — НЕ гуманоид: ACharacter + единый меш SK_Wolf + Single Node анимации (без AnimBP); его ИИ = AWolfAIController(AEnemyAIController).
- **SetFocus сам по себе пешку НЕ вращает** (сверено с UE 5.5: APawn::FaceRotation, Pawn.cpp:1049 — no-op при выключенных bUseControllerRotation*, дефолт false; ACharacter не переопределяет; orient-to-movement у бандита тоже выключен). Доворот корпуса на цель — наш StartAimTurnTo (MasterHumanoidCharacter, вариант A).
- ИИ погони: state-machine Idle/Chase/Attack в AEnemyAIController, nav-погоня + direct-fallback (AddMovementInput) при недоступном навмеше; QA-лог дросселирован.

## Ограничения / тех-долги (DRAFT, на тюнинг/добивку)
- Save/Load НЕ сохраняет `ItemName`/`StackCount` (только class path) → после reload имена предметов/прогресс item-целей квестов и стак патронов теряются. Пре-существующее, не трогаю (риск кору).
- Атака врага в Attack-стейте без LineOfSight-гейта → теоретически удар через тонкую стену в упор.
- Числа баланса — DRAFT UPROPERTY: walk≈600/sprint≈1200, пистолет 25@2/с, нож 35, бандит HP80/650, волк HP40/780, кап брони 0.75 (текущая суммарная защита игрока упирается в кап → эффективный урон по игроку ×0.25 — учитывать при тюнинге урона бандитов).
- invoker-навмеш требует RecastNavMesh `RuntimeGeneration=Dynamic` в уровне.
