# context: qa

## 🧭 СЕЙЧАС
- Build 1 в master (e567e92). 2026-07-28 закрыт гейт ветки уборки `chore/cleanup-dead-assets`, финальный HEAD a03f44c (4 коммита поверх master). Вердикт: ДОБРО НА MERGE, слияние перемоткой вперёд.
- Догоняющий прогон на a03f44c: сборка EXIT=0 ошибок 0 (`logs/build-2026-07-28-cleanup2.log`), тесты 17/17 Success `GIsCriticalError=0` (`logs/tests-2026-07-28-cleanup2.log`), окна 10 VERIFY OK «ошибок 0» (`logs/genwbp-verify-2026-07-28-cleanup2.log`).
- Оба моих замечания закрыты и это ПРОВЕРЕНО, а не принято на слово: папка `dev/` теперь помечается `!!` (игнорируется), `git add -n dev/` её отвергает; параметр `FlipU` из нового комментария реально есть в M_FogSoft, MI_FogBandSoft и MI_FogCurtainSoft, а `FlipVertical` — ни в одном (негативный контроль).
- Итог ветки против master: 10 файлов, +43/−316. Удалены 3 материала тумана и 2 файла коммандлета PatchWbpDialog; остальное — комментарии и `.gitignore`. Исполняемых строк не менялось.

## Как гонять полный набор (эталон, 17 тестов)
1. Редактор UE закрыт (`tasklist | grep -i unreal`).
2. Сборка: `E:\UnrealEngine\UE_5.5\Engine\Build\BatchFiles\Build.bat ContrarySurvivorEditor Win64 Development -Project=E:/ContrarySurvior/ContrarySurvivor/ContrarySurvivor.uproject -WaitMutex -NoHotReload -NoUBA -MaxParallelActions=6` (UBA на этой машине падает по paging file). Полная пересборка — тот же вызов через `Rebuild.bat`, всего ~2.5 минуты.
3. Тесты: `UnrealEditor-Cmd.exe <uproject> -ExecCmds="Automation RunTests ContrarySurvivor; Quit" -unattended -nopause -nosplash -stdout -nullrhi -abslog=<лог>`.
4. Критерий: `Found 17 automation tests` + 17 строк `Result={Success}` + `GIsCriticalError=0`.
5. Окна: `-run=GenerateWbp -verify` (0 ошибок). Verify проверяет кубики, замки дизайнера и классы строк списков; при успехе пишет «VERIFY <окно>: замки на месте — ...» (GenerateWbpCommandlet.cpp, блок GLockContracts ~строка 2860). Прогон ~40 секунд — дешевле, чем рассуждать, нужен ли он.

## Рецепты проверки (проверено на практике)
- **Правка комментария — тоже предмет проверки.** Дважды подряд комментарий ссылался на несуществующую сущность. Имена материалов/параметров из комментариев проверять поиском по ассету, с негативным контролем на старое имя.
- **Удаление класса с UCLASS.** UHT сам убирает сгенерированные файлы из `Intermediate/.../Inc/.../UHT/`. НО старые `.obj` остаются в `Intermediate/Build/Win64/x64/...`; чтобы доказать, что они не попали в библиотеку, смотреть файл ответа линковщика `UnrealEditor-<Модуль>.dll.rsp` (дата = дата сборки): удалённого имени нет, живое есть.
- **Git LFS.** Контент (`*.uasset`, `*.umap`) в LFS, поэтому `git show HEAD:<файл>` отдаёт указатель на 132 байта — это норма. Сверять `sha256sum` файла со строкой `oid sha256:` указателя.
- **Двоичный поиск.** Grep-инструмент Claude молча пропускает бинарники — только через Bash: `grep -a -o -E "токен" файл.umap | sort | uniq -c`, всегда с позитивным (`PlayerStart`) и негативным контролем.
- **Ловушка префиксов:** `MI_FogBand` ловит `MI_FogBandSoft`, `M_FogWall` ловит `M_FogWall2`. Точная ссылка: `grep -rlaE "/Game/Materials/ИМЯ[^A-Za-z0-9_]"`.
- **Игнор в git не проверять через `check-ignore -v`** — он может указать на пустую строку .gitignore и вернуть 0. Правда: `git status --porcelain --ignored` (`!!` = игнорируется, `??` = нет) и сухой прогон `git add -n <путь>`.
- **Цепочки с grep рвутся:** ноль совпадений даёт код возврата 1 и обрывает `&&`. Негативный контроль ставить последним или через `;`.

## Ограничения
- Вердикт только с реальными логами (правило B). Логи qa — в `context/qa/logs/`.
- Тач-жесты живьём на ПК не проверяются (`bUseMouseForTouch=False`) — только код+тесты, жест проверяется на устройстве при следующем APK.
