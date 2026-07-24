# context: qa

## 🧭 СЕЙЧАС
- Фаза: доводка Build 1 (ADR-051), ветка feature/build1-intro.
- 2026-07-24: два полных прогона тестов на этой ветке — interim (после фикса DailyRewardComponent 0cbac2e + коммандлета PatchWbpDialog 028f129) и ГЕЙТОВЫЙ (после канвас-перегенерации WBP_Shop/WBP_Inventory, коммит 94f8575). Оба: 16/16 Success, GIsCriticalError=0, exit 0.
- Логи: `context/qa/logs/tests-2026-07-24-interim.log` и `tests-2026-07-24-gate.log`.
- Вердикт лиду по гейту: ДОБРО на merge-гейт. Merge — после живой приёмки Рината (маркер QA_OK ставит лид).
- В рабочей копии незакоммиченные правки Рината (4 файла, включая WBP_Dialog) — НЕ трогать, НЕ откатывать.
- Урок машины: UBA-сборка нестабильна (paging file) — гонять с `-NoUBA -MaxParallelActions=6`.

## Как гонять полный набор (эталон, 16 тестов)
1. Редактор UE закрыт (tasklist | grep -i unreal).
2. Сборка: `E:\UnrealEngine\UE_5.5\Engine\Build\BatchFiles\Build.bat ContrarySurvivorEditor Win64 Development -Project=E:/ContrarySurvior/ContrarySurvivor/ContrarySurvivor.uproject -WaitMutex -NoHotReload -NoUBA -MaxParallelActions=6` (UBA на этой машине падает по paging file).
3. Тесты: `E:\UnrealEngine\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe <uproject> -ExecCmds="Automation RunTests ContrarySurvivor; Quit" -unattended -nopause -nosplash -stdout -nullrhi -abslog=<лог>`.
4. Критерий: `Found 16 automation tests` и 16 строк `Result={Success}`; любой Fail → «Setting GIsCriticalError due to test failures» и exit != 0. Плюс сверить состав путей тестов с эталоном ниже.
5. Набор: Combat.Armor x2, Combat.Player x1, Combat.Quest x1, Combat.Stats x3, Combat.Weapon x1, Movement x2, Retention.DailyReward x6.

## Ограничения
- Вердикт только с реальными логами (правило B). Логи qa — в `context/qa/logs/`.
- Тач-жесты живьём на ПК не проверяются (bUseMouseForTouch=False) — только код+тесты, жест — на устройстве при следующем APK.
