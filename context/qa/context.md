# context: qa

## 🧭 СЕЙЧАС
- 2026-08-01 мерж-гейт ветки `feature/build12-night` (HEAD `50ab6a6`, master `f9ee6c8`): **ГОДНО по всем 5 пунктам**, вердикт отдан game-lead.
- Артефакты в `logs/`: `build-2026-08-01-b12-rebuild.log` (чистка + unity-модули 1–11 + AddGripSocketCommandlet.cpp, обе DLL, EXIT=0); `tests-2026-08-01-b12.log` (Found 26 / Success 26 / Fail 0, GIsCriticalError=0, Movement оба зелёные); `verify-2026-08-01-b12-{wbp,animbp,gripsocket}.log` (10 окон «ошибок 0»; «ПРОВЕРКА ПРОЙДЕНА» граф; WeaponGripSocket на обоих скелетах, кость R_Hand, нулевой трансформ; все EXIT=0); `diff-2026-08-01-b12-{stat,files}.log` (63 файла, мусора/ключей нет: хекс-греп текстового диффа 0, папки keys нет); `lfs-2026-08-01-b12.log` (11 новых + все изменённые .uasset в LFS).
- Следующий шаг: за game-lead — маркер QA_OK и merge в master.

## Урок сессии: «EXIT=0» бывает пустым
`Build.bat` может вернуть 0 со строкой `Target is up to date`, не скомпилировав НИЧЕГО. Для гейта искать строки `Compile [x64] <файл>`; нет их — гнать `Rebuild.bat`. При unity-сборке отдельных имён .cpp игрового модуля в логе НЕТ — они внутри блоков `Module.ContrarySurvivor.N.cpp`; полная чистая пересборка всех N блоков покрывает все файлы модуля по построению.

## Урок сессии: проверять занятость проекта, а не верить вводной
`tasklist`/`Get-Process *Unreal*` + `git status` ДО начала; при чужой активности ждать. HEAD фиксировать в отчёте — может уехать.

## Как гонять полный набор (эталон Build 1.2: 26 тестов)
1. Проверить, что проект свободен.
2. Начисто: `Rebuild.bat ContrarySurvivorEditor Win64 Development -Project=<uproject> -WaitMutex` (~2.5 мин; при «paging file too small» добавить `-NoUBA -MaxParallelActions=6`).
3. Тесты: `UnrealEditor-Cmd.exe <uproject> -ExecCmds="Automation RunTests ContrarySurvivor; Quit" -unattended -nopause -nosplash -stdout -nullrhi -abslog=<лог>`.
4. Критерий: `Found 26 automation tests` + 26 `Result={Success}` + `GIsCriticalError=0`. Состав: Ads 6 (AdGating 3 + DeathLoss 3), Story 3, DailyReward 6, Combat 8, Movement 2, LimpHint 1.
5. Коммандлеты целостности, каждый свежим процессом: `-run=GenerateWbp -verify` (10 окон, «Итог проверки: ошибок 0»); `-run=PatchAnimBp -verify` («ПРОВЕРКА ПРОЙДЕНА»); `-run=AddGripSocket -verify` (оба скелета, кость R_Hand).

## Рецепты проверки
- **Мёртвая фича при зелёной сборке.** Пути на контент в C++ не проверяются компилятором: `grep -rhoE '"/Game/[^"]+"' Source/` и сверять с `Content/<путь>.uasset`.
- **Удаление класса с UCLASS.** Доказательство невключения — файл ответа линковщика `UnrealEditor-<Модуль>.dll.rsp`.
- **Git LFS.** `git lfs ls-files` — истина по HEAD; сверять ВСЕ .uasset из диффа против списка, не только новые.
- **Секреты в диффе.** Хекс-греп `[0-9a-fA-F]{32}` по текстовому диффу (`':(exclude)*.uasset'`); код возврата снимать с grep, не с head в конце конвейера.
- **Двоичный поиск** только через Bash, с позитивным и негативным контролем; ловушка префиксов (`MI_FogBand` ловит `MI_FogBandSoft`).
- **Цепочки с grep рвутся:** ноль совпадений даёт код 1 и обрывает `&&`.

## Ограничения
- Вердикт только с реальными логами (правило B). Логи qa — в `context/qa/logs/`.
- Headless не проверяет: проигрывание анимаций/монтажей, тач-жесты, живой PIE — это приёмка Рината.
