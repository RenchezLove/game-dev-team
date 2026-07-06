# context: cpp-dev

> Лёгкая рабочая память `cpp-dev` (правило H + Гигиена памяти из CLAUDE.md: стоп >150 строк, СЕЙЧАС вырезает прошлый). Закрытая история — в [archive.md](archive.md) (read-on-demand, НЕ для грунтовки). Build-логи — `logs/`, история — git.

## 🧭 СЕЙЧАС
**ЭТАП D — фидбек-пакет №2 (приёмка Рината 07-06): СОБРАН, ЗАКОММИЧЕН, ЗАПУШЕН.** Ветка `feature/stage-d-combat`, origin = `f45675e`. Оба пакета 07-06 в git.
- **Пруф сборки №2:** BUILD_EXIT=0, DLL слинкована (редактор закрыт, tasklist проверен). Лог: `logs/build-2026-07-06-stage-d-feedback-pack2.log`.
- **Коммиты №2:** `4a3215d` фикс погони (враг в бою не теряет цель по DetectionRange — только поводок, ADR-036; корень доказан логом PIE: idle-far-from-home, не leash), `5234601` маркер = текущая невыполненная цель (FQuest::KillObjectiveLabel/ItemObjectiveLabel + ElderNPC + DrawQuestTargetMarker), `f45675e` «Патроны 9мм» (AAmmoItem/торговец/фолбэк HUD; матчинг патронов по классу, сейв только class path). Push `483b230..f45675e` подтверждён.
- В рабочей копии остались ТОЛЬКО 3 бинарника Рината (НЕ коммитить, его указание): BP_PlayerCharacter.uasset, L_World_C.umap, BP_ContrarySurvivorHUD.uasset.
- **НЕ ПРОВЕРЕНО: PIE-поведение пакета №2** (погоня до поводка / смена текста метки / имя патронов в UI) — за лидом/Ринатом.
- ДОПУЩЕНИЕ (umap недоступен): пикап карты с явным PlacedItemDisplayName «Патроны» показал бы старое имя; по D8 патроны шли через PlacedAmmoAmount (имя из класса) — проверить оператору при случае.
- Патч-бэкап `logs/stage-d-feedback-pack.patch` устарел (всё в git) — удалить при чистке.
- Вариант B прицеливания (Modify Bone руки в общем ABP) — отложен лидом как полировка; разведка — в archive.md (сессия 07-05).

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
