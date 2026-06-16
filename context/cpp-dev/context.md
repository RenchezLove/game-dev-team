# context: cpp-dev

> Лёгкая рабочая память `cpp-dev` (правило H + Гигиена памяти из CLAUDE.md: стоп >150 строк, СЕЙЧАС вырезает прошлый). Закрытая история — в [archive.md](archive.md) (read-on-demand, НЕ для грунтовки). Build-логи — `logs/`, история — git.

## 🧭 СЕЙЧАС
WASD vel=0 — КОРЕНЬ+ФИКС f10835c (feature/phase5-quests). Капсула утоплена в пол ~34см
(floorDist=-34, floorPen=1) → свип CMC упирается в depenetration → Velocity=0 при accel=2048.
Корень — спавн-Z/размещение, НЕ код движения. Нижние слои отметены (в архиве):
MaxWalkSpeed/NavWalking/камера-yaw/IsMoveInputIgnored/root motion/friction.
ФИКС: relocate в PlayerCharacter::BeginPlay — floor-trace TraceFloorZ, центр капсулы на
floorImpact+halfHeight+10 если игрок под картой ИЛИ утоплен. СОБРАН (релинк PASS), ждёт PIE+W.
После подтверждения СНЯТЬ TEMP-диаги MOVE/VELKILL/PIPELINE/BLOCK (PlayerController.{cpp,h})
+ BeginPlay-диаг (PlayerCharacter.cpp:~206).

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
