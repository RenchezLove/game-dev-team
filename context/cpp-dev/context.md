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
