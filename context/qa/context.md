# context: qa

## 🧭 СЕЙЧАС
- Фаза: Build 1 сдан. 2026-07-28 проведён ФИНАЛЬНЫЙ мерж-гейт ветки `feature/build1-intro` (HEAD e567e92). Вердикт: ДОБРО НА MERGE.
- Сборка с нуля (`Rebuild.bat` ContrarySurvivorEditor Win64 Development): EXIT=0, ошибок 0, лог `logs/build-2026-07-28-gate.log`. В логе видно `Cleaning ContrarySurvivorEditor binaries...` и `no existing makefile` — чистка была настоящей, 32 действия, 147 сек.
- Тесты: `Found 17 automation tests`, 17 Success / 0 Fail, `GIsCriticalError=0`, `TEST COMPLETE. EXIT CODE: 0`. Лог `logs/tests-2026-07-28-gate.log`. Состав совпал с эталоном (Armor 2, Player 1, Quest 1, Stats 3, Weapon 1, Movement 2, DailyReward 6, LimpHint 1).
- Контракты окон: `-run=GenerateWbp -verify` EXIT=0, «Итог проверки: ошибок 0», 10 окон VERIFY OK. Лог `logs/genwbp-verify-2026-07-28-gate.log`.
- Карта: в `Content/Maps/L_World_C.umap` есть экземпляр актора `PersistentLevel.BP_WorldBorder_C_2` (позитивный контроль `PersistentLevel.PlayerStart_0`, негативный — 0). Работа Рината на месте.
- Не закрыто лидом: коммит e567e92 и его LFS-объект карты ещё НЕ на origin. Перед/после merge нужен push, иначе на другой машине карта не восстановится.

## Как гонять полный набор (эталон, 17 тестов)
1. Редактор UE закрыт (`tasklist | grep -i unreal`).
2. Сборка: `E:\UnrealEngine\UE_5.5\Engine\Build\BatchFiles\Build.bat ContrarySurvivorEditor Win64 Development -Project=E:/ContrarySurvior/ContrarySurvivor/ContrarySurvivor.uproject -WaitMutex -NoHotReload -NoUBA -MaxParallelActions=6` (UBA на этой машине падает по paging file). Для гейта — тот же вызов через `Rebuild.bat` (чистка + сборка), это ~2.5 минуты, не бойся запускать.
3. Тесты: `E:\UnrealEngine\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe <uproject> -ExecCmds="Automation RunTests ContrarySurvivor; Quit" -unattended -nopause -nosplash -stdout -nullrhi -abslog=<лог>`.
4. Критерий: `Found 17 automation tests` + 17 строк `Result={Success}`; сверить `GIsCriticalError=0` в строке `LogAutomationCommandLine: Shutting down`.
5. Окна: `-run=GenerateWbp -rebuild` (сначала), потом `-verify` (0 ошибок). Verify проверяет НЕ только кубики, но и замки дизайнера — при успехе пишет строку «VERIFY <окно>: замки на месте — замкнутой начинки N, свободных верхнеуровневых виджетов M» (код: GenerateWbpCommandlet.cpp, блок GLockContracts ~строка 2860).

## Рецепт: как проверять содержимое карты и ассетов
- Контент проекта в **Git LFS** (`.gitattributes`: `*.uasset`, `*.umap`). Поэтому `git show HEAD:<файл.umap>` отдаёт указатель на 132 байта, а НЕ карту — это норма, не потеря данных. Сверять надо так: `sha256sum` рабочего файла против строки `oid sha256:` в указателе; `git lfs ls-files -l` покажет тот же хеш.
- Grep-инструмент Claude молча пропускает двоичные файлы — искать только через Bash: `grep -a -o -E "токен" файл.umap | sort | uniq -c`. Всегда с позитивным контролем (`PlayerStart`) и негативным (заведомо несуществующая строка).
- Ловушка префиксов: `grep "MI_FogBand"` ловит и `MI_FogBandSoft`. Для точной ссылки использовать границу: `grep -rlaE "/Game/Materials/ИМЯ[^A-Za-z0-9_]"`.

## Ограничения
- Вердикт только с реальными логами (правило B). Логи qa — в `context/qa/logs/`.
- Тач-жесты живьём на ПК не проверяются (`bUseMouseForTouch=False`) — только код+тесты, жест проверяется на устройстве при следующем APK.
