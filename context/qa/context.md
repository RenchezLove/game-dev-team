# context: qa

## 🧭 СЕЙЧАС
- Фаза: этап G, интеграционный гейт двух веток перед merge в master (d94064c).
- 2026-07-18 (вечерний гейт): `feature/ui-bp-and-shop-scroll` (97b416b) + `fix/android-storage-and-cloth` (79ca38b) слиты в ЛОКАЛЬНУЮ ветку `qa/integration-gate-2026-07-18` БЕЗ конфликтов, не пушилась.
- Сборка на объединении: первая попытка с UBA УПАЛА («paging file too small» + CLR fatal, exit 139) → `context/qa/logs/build-2026-07-18-qa-integration-gate.log`; повтор `-NoUBA -MaxParallelActions=6` — exit 0 → `...-noUBA.log`.
- Тесты: 16/16 Success, exit 0 → `context/qa/logs/tests-2026-07-18-qa-integration-gate.log`.
- Ревью: 20+ вынесенных дефолтов сверены ДОСЛОВНО со старыми зашитыми; игровая логика не задета; у operator ровно 2 конфига; путь cook одежды существует.
- Вердикт лиду: ДОБРО на merge обеих веток. Рабочая копия оставлена на `qa/integration-gate-2026-07-18` — после merge ветку можно удалить.
- Урок машины: UBA-сборка на этой машине нестабильна (paging file) — по умолчанию гонять с `-NoUBA -MaxParallelActions=6`.

## Как гонять полный набор (эталон, 16 тестов)
1. Редактор UE закрыт (tasklist | grep -i unreal).
2. Сборка: `E:\UnrealEngine\UE_5.5\Engine\Build\BatchFiles\Build.bat ContrarySurvivorEditor Win64 Development -Project=E:/ContrarySurvior/ContrarySurvivor/ContrarySurvivor.uproject -WaitMutex -NoHotReload -NoUBA -MaxParallelActions=6` (UBA на этой машине падает по paging file).
3. Тесты: `E:\UnrealEngine\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe <uproject> -ExecCmds="Automation RunTests ContrarySurvivor; Quit" -unattended -nopause -nosplash -stdout -nullrhi -abslog=<лог>`.
4. Критерий: `Found 16 automation tests` и 16 строк `Result={Success}`; любой Fail → «Setting GIsCriticalError due to test failures» и exit != 0.
5. Набор: Combat.Armor x2, Combat.Player x1, Combat.Quest x1, Combat.Stats x3, Combat.Weapon x1, Movement x2, Retention.DailyReward x6.

## Ограничения
- Вердикт только с реальными логами (правило B). Логи qa — в `context/qa/logs/`.
- Тач-жесты живьём на ПК не проверяются (bUseMouseForTouch=False) — только код+тесты, жест — на устройстве при следующем APK.
