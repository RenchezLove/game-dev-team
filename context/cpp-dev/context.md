# context: cpp-dev

> Лёгкая рабочая память `cpp-dev` (правило H + Гигиена памяти из CLAUDE.md: стоп >150 строк, СЕЙЧАС вырезает прошлый). Закрытая история — в [archive.md](archive.md) (read-on-demand, НЕ для грунтовки). Build-логи — `logs/`, история — git.

## 🧭 СЕЙЧАС
WASD-баг ЗАКРЫТ: корень был в ДАННЫХ уровня (не в коде) — персонаж ходит в чистом L_World.
Ветка **feature/clean-village** (от phase5-quests). Этап 2 «чистка» СОБРАН (база DLL, 50s, OK), коммит acaba92:
- Камера: ApplyCameraSettings убран из BeginPlay → применяется 1 раз в OnConstruction (knob Camera-категории
  живой, без рантайм-перетирания); CameraArmLength деф. 3000. Дизайнер крутит Camera Arm Length в Class Defaults BP.
- Репликация OFF (одиночная): bReplicates=false, SetReplicateMovement(false), NetworkSmoothingMode=Disabled —
  митигация «резинового» отката; КОРЕНЬ не подтверждён PIE (нужен прогон).
- Удалены UTraderSpawnSubsystem/UElderSpawnSubsystem (авто-спавн NPC). Классы ATraderNPC/AElderNPC живы (оператор ставит актёрами).
- Этап 1 (коллизия надетого оружия Equip/Unequip + диаг floorActor/OVERLAPLIST в BLOCK) вошёл в этот же коммит.
ОТКРЫТО: двойной экип пистолета (C_0→Unequip→C_1) — НЕ C++ (EquipDefaultWeapon спавнит 1 раз, лог-док в отчёте),
дубль в EventGraph BP_PlayerCharacter (BeginPlay-ноды спавн+экип) → правка за unreal-operator.
ДЁРГАНЬЕ РЕШЕНО (коммит 9ef9261): причина = per-0.5s диаг-спам в Move() (overlap-проба+рефлексия+bScreen)
давал фрейм-хитч в ритм дёрганья. ВСЕ TEMP-диаги BugReport12 сняты (Move-блок целиком; BeginPlay-логи;
осиротевшие члены LastMoveDiag* + 5 инклудов). Функциональное оставлено: базис/AddMovementInput,
ResetIgnoreMoveInput, спавн-relocate, NavWalking->Walking. Собрано (8.4s, OK). Репликация OFF из прошлого
коммита к дёрганью, видимо, не относилась — оставил (для одиночной корректно), но причиной была не она.

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
