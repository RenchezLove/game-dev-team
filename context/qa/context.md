# context: qa

## 🧭 СЕЙЧАС
- Фаза: доводка Build 1 (ADR-051), ветка feature/build1-intro.
- 2026-07-27, interim №2 (HEAD a915dc6, после WorldBorder 161cd97 + канвас WBP_PlayerStats f347ea4): сборка EXIT=0 (`logs/build-2026-07-27-border-stats.log`), тесты 17/17 Success, GIsCriticalError=0 (`context/qa/logs/tests-2026-07-27-interim2.log`).
- Interim №1 того же дня (HEAD cac86f9, хромота+замки): тоже зелёный — `logs/build-2026-07-27-limp-locks.log`, `context/qa/logs/tests-2026-07-27-interim.log`, там же появился 17-й тест Retention.LimpHint.FirstShowOnce.
- Это interim'ы, НЕ мерж-гейт: после меня оператор гонит -run=GenerateWbp (rebuild трёх окон), гейтовый прогон будет позже.
- Замечание (не блокер): RetentionAutomationTests.cpp:26 — имя `Base` в анонимном namespace даёт ворох warning C4459 при инстанцировании делегатов UE.
- В рабочей копии незакоммиченные правки Рината — НЕ трогать, НЕ откатывать.
- Урок машины: UBA-сборка нестабильна (paging file) — гонять с `-NoUBA -MaxParallelActions=6`.

## Как гонять полный набор (эталон, теперь 17 тестов)
1. Редактор UE закрыт (tasklist | grep -i unreal).
2. Сборка: `E:\UnrealEngine\UE_5.5\Engine\Build\BatchFiles\Build.bat ContrarySurvivorEditor Win64 Development -Project=E:/ContrarySurvior/ContrarySurvivor/ContrarySurvivor.uproject -WaitMutex -NoHotReload -NoUBA -MaxParallelActions=6` (UBA на этой машине падает по paging file).
3. Тесты: `E:\UnrealEngine\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe <uproject> -ExecCmds="Automation RunTests ContrarySurvivor; Quit" -unattended -nopause -nosplash -stdout -nullrhi -abslog=<лог>`.
4. Критерий: `Found 17 automation tests` и 17 строк `Result={Success}`; любой Fail → «Setting GIsCriticalError due to test failures» и exit != 0. Плюс сверить состав путей тестов с эталоном ниже.
5. Набор: Combat.Armor x2, Combat.Player x1, Combat.Quest x1, Combat.Stats x3, Combat.Weapon x1, Movement x2, Retention.DailyReward x6, Retention.LimpHint x1.

## Ограничения
- Вердикт только с реальными логами (правило B). Логи qa — в `context/qa/logs/`.
- Тач-жесты живьём на ПК не проверяются (bUseMouseForTouch=False) — только код+тесты, жест — на устройстве при следующем APK.
