# context: cpp-dev

> Персональная память агента `cpp-dev`. Сюда агент дистиллирует решения, ограничения и текущее состояние (правило H). Новые сессии стартуют с этого файла.

## Решения
- Миграция Health: база `AMasterHumanoidCharacter` сохраняет инлайн Health/TakeDamage (игрок + пайплайн оружия не трогаем). Новый враг `AEnemyCharacter` несёт `UStatsComponent` и переопределяет `TakeDamage` БЕЗ вызова Super — единственный источник истины по HP врага = компонент. Стратегия миграции игрока на компонент отложена (Фаза 2), в Фазе 1 не требуется.
- `HandleDeath()` сделан virtual в базе; враг переопределяет (override, БЕЗ повтора UFUNCTION-спецификатора — UHT это запрещает для override, см. ниже).

## Ограничения
- UHT-правило (подтверждено ошибкой сборки): override UFUNCTION НЕЛЬЗЯ снабжать новым `UFUNCTION()` макросом — «Override of UFUNCTION ... cannot have a UFUNCTION() declaration above it». Reflection наследуется от базовой virtual UFUNCTION; этого достаточно для AddDynamic.
- Include-пути внутри модуля: использовать префикс `ContrarySurvivor/<Subdir>/Header.h` (как в существующих файлах). Относительный `Components/Header.h` из другой подпапки НЕ резолвится (C1083). Это конвенция проекта.

## Текущее состояние

### Фаза 1 C++-фундамент (2026-06-12, реальный лог сборки)
- Ветка гейм-репо: `feature/phase1-enemy-stats` (от master f7542ad). master НЕ тронут. 2 коммита: 6faccca (stats+death stub), ea5b201 (enemy+AI+target-lock+Build.cs).
- СБОРКА: PASS. `Build.bat ContrarySurvivorEditor Win64 Development`, exit 0. Лог: `E:\game-dev-team\logs\phase1-cpp-build-f7542ad.log` (имя по HEAD-хешу на момент старта; перезаписывался между прогонами, итог — успешный). Собран `UnrealEditor-ContrarySurvivor-0003.dll`. Скомпилированы все 5 cpp (Enemy/Stats/AI/Master/PlayerController), adaptive non-unity.
- Создано: `Source/ContrarySurvivor/Components/StatsComponent.{h,cpp}`, `Characters/EnemyCharacter.{h,cpp}`, `Controllers/EnemyAIController.{h,cpp}`. Изменено: `MasterHumanoidCharacter.{h,cpp}`, `ContrarySurvivorPlayerController.{h,cpp}`, `ContrarySurvivor.Build.cs` (+AIModule,+GameplayTasks).
- API подтверждён по заголовкам UE 5.5.4 (`E:\UnrealEngine\UE_5.5\...AIModule\Classes\AIController.h`): MoveToActor, LineOfSightTo, SetFocus(default prio), ClearFocus(EAIFocusPriority::Type), StopMovement, OnPossess override. `EAutoPossessAI::PlacedInWorldOrSpawned` — EngineTypes.h. Все существуют.
- ДОПУЩЕНИЯ: рэгдолл при смерти врага сработает только если у скелет-меша назначен Physics Asset (иначе тихо без эффекта, не краш) — назначение меша/физики на стороне unreal-operator. AttackDamage врага = 10/удар, AttackCooldown 1.5с, DetectionRange 1500, AttackRange 175 — все тюнингуемые UPROPERTY, числа черновые.
- Остаётся на BP/редактор (unreal-operator): BP-наследник AEnemyCharacter с мешами Head/Torso/Legs + AnimBP; назначить AIControllerClass=AEnemyAIController в BP врага (или проверить, что AutoPossessAI берёт его); виджет хелсбара на OnHealthChanged/OnDeath; разместить бандита на карте; назначить игроку оружие APistol (если ещё не в BP).

### Фаза 1 — автоэкип + C++ хелсбар (2026-06-12, реальный лог)
- Ветка `feature/phase1-enemy-stats` (от master f7542ad, не тронут). +2 коммита: 18339cf (player auto-equip), 28b67d0 (C++ HUD). working tree clean. HEAD=28b67d0.
- СБОРКА: PASS. `Build.bat ContrarySurvivorEditor Win64 Development`, exit 0, линк `UnrealEditor-ContrarySurvivor.dll`. Лог: `E:\game-dev-team\logs\phase1-cpp-hud-ea5b201.log` (tee перезаписал первый ПРОВАЛЬНЫЙ прогон; итог — успешный).
- ЗАДАЧА 1: APlayerCharacter +UPROPERTY `DefaultWeaponClass` (TSubclassOf<AMasterWeapon>, EditDefaultsOnly), BeginPlay→`EquipDefaultWeapon()` спавнит (SpawnActor, Owner/Instigator=this, AlwaysSpawn) и зовёт `EquipWeapon`. EquipWeapon крепит к WeaponSocketName на TorsoMesh — НЕ HeadMesh (проверено в .cpp). Значение BP_Pistol ставит unreal-operator в BP игрока.
- ЗАДАЧА 2: новый класс `Source/ContrarySurvivor/HUD/ContrarySurvivorHUD.{h,cpp}` : AHUD. DrawHUD: TActorIterator<AEnemyCharacter>, показ если жив (GetStats()->IsDead()==false) И (залочен через PC->GetCurrentTarget() ИЛИ DistSq<=1500^2 до пешки игрока). Project(worldAnchor,false): Z>0=перед камерой. DrawRect фон+заполнение по GetHealthPercent. HUDClass=AContrarySurvivorHUD ставит unreal-operator в BP GameMode.
- ВАЖНО (новое ограничение): `GetCurrentTarget()` в контроллере был под `protected:` (хотя UFUNCTION) → C2248 при чтении из HUD. UFUNCTION-спецификатор НЕ делает метод публичным; access-модификатор C++ действует. Вынес в public-секцию.
- API подтверждён по HUD.h/Canvas.h UE 5.5.4: AHUD::Canvas (TObjectPtr<UCanvas>), Project(FVector,bool)->FVector, DrawRect(FLinearColor,X,Y,W,H), DrawText(...), GetOwningPlayerController()->APlayerController*, UCanvas::SizeX/SizeY (int32). HUD/Canvas/EngineUtils — модуль Engine (уже в deps, Build.cs НЕ менял).
- ДОПУЩЕНИЕ: радиус показа 1500 ед (GDD ч.8 «~5м»=~500ед, взял с запасом под top-down обзор) — тюнингуемый UPROPERTY. Хелсбар без текста/иконки, простые DrawRect (фон чёрный полупрозрачный + красное заполнение) — Фаза 1 достаточно. Project с bClampToZeroPlane=false чтобы корректно отсекать за-камерой по Z<=0.

### Инвентаризация среды сборки UE C++ (2026-06-07, только факты из вывода команд)
- VS 2022 Professional 17.14.36811.4, путь `C:\Program Files\Microsoft Visual Studio\2022\Professional`.
- Workload `Microsoft.VisualStudio.Workload.NativeGame` (Game Dev C++) установлен. Также VC.Tools.x86.x64, Windows10SDK, Windows11SDK.26100.
- MSVC toolset 14.44.35207, cl.exe: `...\VC\Tools\MSVC\14.44.35207\bin\Hostx64\x64\cl.exe`.
- MSBuild 17.14.23: `...\2022\Professional\MSBuild\Current\Bin\MSBuild.exe`.
- Движок UE 5.5.4 (5.5.4-40574608): `E:\UnrealEngine\UE_5.5` (из LauncherInstalled.dat). UBT: `E:\UnrealEngine\UE_5.5\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.exe` (есть).
- .NET: глобально только SDK/runtime 3.1.426 (старый), НО движок несёт свой `Engine\Binaries\ThirdParty\DotNet\8.0.300` — UBT использует bundled .NET 8, поэтому глобальный 3.1 не блокер.
- Проект ContrarySurvivor: `E:\ContrarySurvior\ContrarySurvivor\ContrarySurvivor.uproject` (EngineAssociation "5.5"). C++ проект: модуль `ContrarySurvivor` (Runtime), есть `ContrarySurvivor.Build.cs`, `ContrarySurvivor.Target.cs`, `ContrarySurvivorEditor.Target.cs`. Папки Characters/Controllers/Public/Private с .h/.cpp. Plugin: ModelingToolsEditorMode (Editor).
- Вывод: машина к сборке UE C++ готова. Сборку НЕ запускал (задача — только инвентаризация).
- pwsh (PowerShell 7) отсутствует; Windows-команды гнать через `powershell.exe -NoProfile`. Bash-тул = git-bash, `&`/`${env:..}` синтаксис там не работает напрямую.

### Ш6 — контрольная сборка (2026-06-07, реальный лог)
- РЕЗУЛЬТАТ: PASS. UBT exit code 0. Таргет `ContrarySurvivorEditor`, Development Win64.
- Лог: `E:\game-dev-team\logs\build_ContrarySurvivorEditor.log`. Собраны `UnrealEditor-ContrarySurvivor-0079.dll`/`.lib` в `Binaries\Win64`. Время: 27.21s (UBA local 5.94s). Скомпилирован `ContrarySurvivorPlayerController.cpp` (adaptive non-unity по git working set).
- Editor target name подтверждён чтением: класс `ContrarySurvivorEditorTarget`, `Type=TargetType.Editor`, `ExtraModuleNames=ContrarySurvivor`.
- ИЗВЕСТНЫЙ НЕ-БЛОКЕР (зафиксировано): MSVC 14.44.35222 вместо предпочитаемого UE 5.5 14.38.33130 → UBT печатает варнинг «not a preferred version». Это ТОЛЬКО варнинг, сборка чистая (exit 0, ошибок нет). Действие — доустановить MSVC 14.38 side-by-side toolset — выполнять ТОЛЬКО если в будущем всплывут ICE (internal compiler error) или странные крэши компилятора. Сейчас ничего делать не нужно.
- ВАЖНО про запуск .bat из Bash-тула: НЕ оборачивать в `cmd.exe /c '...'` с редиректами — quoting ломается, команда не выполняется (получишь ложный exit 0 от echo). Запускать Build.bat напрямую, редирект `> log 2>&1` отдавать самому bash. Запускать в background (первая сборка может превысить лимит вызова).
- Перед C++-сборкой убедиться, что `UnrealEditor.exe` не запущен (иначе DLL модуля залочена). В этот раз процесса не было.

### FULL REBUILD ContrarySurvivorEditor (2026-06-07, реальный лог)
- РЕЗУЛЬТАТ: PASS. exit code 0. Команда: `Rebuild.bat ContrarySurvivorEditor Win64 Development -Project=... -WaitMutex -FromMsBuild`. Лог: `E:\game-dev-team\logs\rebuild_ContrarySurvivorEditor.log`.
- ПОЛНОТА: Clean прошёл («Cleaning ContrarySurvivorEditor binaries...», «no existing makefile»). 32 action: 28 `Compile [x64]` (все 13 .cpp модуля + .gen.cpp + init.gen + PerModuleInline.gen + SharedPCH), 2 Link (.lib/.dll), WriteMetadata. Собран `UnrealEditor-ContrarySurvivor-0001.dll/.lib`.
- Toolchain: MSVC 14.44.35222 (соответствует 14.44 на машине). Ошибок 0. Единственный «Warning» — VS compiler not preferred version (информационный, НЕ warning-as-error). Время: 111.47s (UBA local 45.52s).
- ЗАМЕЧАНИЕ по правам: запуск Rebuild.bat в background (`run_in_background`) был DENY 3 раза; foreground-запуск с timeout 600000 прошёл. Rebuild только модуля проекта укладывается в ~111s, foreground приемлем.
