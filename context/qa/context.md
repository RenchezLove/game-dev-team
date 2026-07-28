# context: qa

## 🧭 СЕЙЧАС
- Фаза: доводка Build 1 (ADR-051), ветка feature/build1-intro.
- 2026-07-28, interim №4 (HEAD 03d1c1c, волна 2: WorldBorder WallOffset/слои тумана + канвас-первые WBP_Dialog/WBP_Death): сборка EXIT=0 (`logs/build-2026-07-28-wave2.log`), тесты 17/17 Success, GIsCriticalError=0 (`logs/tests-2026-07-28-interim.log`).
- Пересборка окон: `-run=GenerateWbp -rebuild` EXIT=0, 5/5 ассетов ОК (`logs/genwbp-rebuild-2026-07-28.log`). Перенос стилизации: Shop 0, Inventory 0, PlayerStats 14, Dialog 4, Death — чистый. Warnings по старым контейнерам Dialog (PanelSize и др.) — по проекту, не ошибка.
- `-verify` после rebuild: EXIT=0, «Итог проверки: ошибок 0», 9 ассетов VERIFY OK (`logs/genwbp-verify-2026-07-28.log`).
- 5 изменённых .uasset в Content/UI НЕ закоммичены — коммит за лидом (его указание).
- Это interim, НЕ мерж-гейт; гейтовый прогон будет отдельно по команде лида.
- Замечание (не блокер): RetentionAutomationTests.cpp:26 — имя `Base` в анонимном namespace даёт ворох warning C4459 при инстанцировании делегатов UE.
- Урок машины: UBA-сборка нестабильна (paging file) — гонять с `-NoUBA -MaxParallelActions=6`.

## Как гонять полный набор (эталон, теперь 17 тестов)
1. Редактор UE закрыт (tasklist | grep -i unreal).
2. Сборка: `E:\UnrealEngine\UE_5.5\Engine\Build\BatchFiles\Build.bat ContrarySurvivorEditor Win64 Development -Project=E:/ContrarySurvior/ContrarySurvivor/ContrarySurvivor.uproject -WaitMutex -NoHotReload -NoUBA -MaxParallelActions=6` (UBA на этой машине падает по paging file).
3. Тесты: `E:\UnrealEngine\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe <uproject> -ExecCmds="Automation RunTests ContrarySurvivor; Quit" -unattended -nopause -nosplash -stdout -nullrhi -abslog=<лог>`.
4. Критерий: `Found 17 automation tests` и 17 строк `Result={Success}`; любой Fail → «Setting GIsCriticalError due to test failures» и exit != 0. Плюс сверить состав путей тестов с эталоном ниже.
5. Набор: Combat.Armor x2, Combat.Player x1, Combat.Quest x1, Combat.Stats x3, Combat.Weapon x1, Movement x2, Retention.DailyReward x6, Retention.LimpHint x1.
6. Окна: `-run=GenerateWbp -rebuild` (сначала), потом `-run=GenerateWbp -verify` (0 ошибок); verify ДО rebuild красный по замкам — ожидаемо.

## Ограничения
- Вердикт только с реальными логами (правило B). Логи qa — в `context/qa/logs/`.
- Тач-жесты живьём на ПК не проверяются (bUseMouseForTouch=False) — только код+тесты, жест — на устройстве при следующем APK.
