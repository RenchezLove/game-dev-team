# context: cpp-dev

> Персональная память агента `cpp-dev`. Сюда агент дистиллирует решения, ограничения и текущее состояние (правило H). Новые сессии стартуют с этого файла.

## Решения

## Ограничения

## Текущее состояние

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
