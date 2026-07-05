# context: cpp-dev

> Лёгкая рабочая память `cpp-dev` (правило H + Гигиена памяти из CLAUDE.md: стоп >150 строк, СЕЙЧАС вырезает прошлый). Закрытая история — в [archive.md](archive.md) (read-on-demand, НЕ для грунтовки). Build-логи — `logs/`, история — git.

## 🧭 СЕЙЧАС
**ЭТАП D — фидбек-пакет 07-05 + вариант A прицеливания: КОД ГОТОВ НА ДИСКЕ, НЕ СОБРАН, НЕ ЗАКОММИЧЕН** (сборки в сессии 07-05 не было — редактор у Рината был открыт всю сессию). Ветка `feature/stage-d-combat` (база 5228245), 14 файлов Source в рабочей копии; страховка лида — патч `context/cpp-dev/logs/stage-d-feedback-pack.patch`. BP_PlayerCharacter.uasset в git status — не мой (лида/Рината), не коммитить.
- **ПЕРВОЕ ДЕЙСТВИЕ следующей сессии:** Build.bat при ЗАКРЫТОМ редакторе (команда — LIVE-КОНВЕНЦИИ, проверить tasklist), лог в `context/cpp-dev/logs/`, починить ошибки → логические коммиты в `feature/stage-d-combat`.
- **БАГ-РИСК: компиляция пакета НЕ ПРОВЕРЕНА** (ни одного прогона компилятора за сессию). PIE-поведение (маркер/камера/доворот) — тоже НЕ ПРОВЕРЕНО.
- **Состав пакета (файл → задача):**
  1. MasterTrader.cpp — «Pistol Ammo» → «Патроны» (единое имя с ItemName AAmmoItem).
  2. ContrarySurvivorHUD.{h,cpp} — квест-маркер: State==Completed → метка на старосту («Сдать: <квест>», якорь +120 над его NPC-ромбом), иначе на базу по тегу; + кэш цели (слабый указатель, инвалидация тег/фаза/гибель, дроссель неудачного поиска 0.5с).
  3. MasterEnemyBase.{h,cpp} — LeashVisualizer: фиолетовая каркас-сфера радиуса LeashRadius, синк в OnConstruction, БЕЗ отдельного параметра (паттерн ActivationVisualizer).
  4. PlayerCharacter.{h,cpp} — CombatCameraExitInterpSpeed=1.0 + флаг bCombatCameraRecovering: мягкий выход камеры из боя до схождения офсета; при выключенном look-ahead — мягкий увод к нулю вместо скачка.
  5. AMeleeWeapon.{h,cpp} — hitstop-страховка: bHitStopPending + EndPlay восстанавливает дилатацию 1.0 и чистит таймер.
  6. EnemyAIController.cpp — удалён устаревший комментарий (ПРОБА nav/AbortMove); + хуки варианта A: PerformAttack (:154), PerformRangedAttack (:196).
  7. ARangedWeapon.{h,cpp} — .h: завершающий CRLF; .cpp: хук варианта A в Fire() (:221) + include MasterHumanoidCharacter.h.
  8. MasterHumanoidCharacter.{h,cpp} — вариант A: StartAimTurnTo/UpdateAimTurn (плавный yaw FMath::RInterpTo в Tick; окно AimTurnHoldTime=1.0 продлевается выстрелом; save/restore bOrientRotationToMovement — BP игрока держит true; гейт трупа MOVE_None); параметры bAimTurnToTarget / AimTurnInterpSpeed=10 / AimTurnHoldTime (EditAnywhere+BRW, DisplayPriority 55-57). Снап-доворот ножа не тронут; волк не гуманоид — no-op.
- Цифры урона (задача 4 фидбека) — код был готов ранее (6800dce); пробел «негде крутить» закрыл лид: /Game/System/BP_ContrarySurvivorHUD + HUDClass в BP_ContrarySurviorGameMode.
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
