# context: qa

## 🧭 СЕЙЧАС
- 2026-08-06 мерж-гейт волны Б4–Б9 ветки `feature/build122` (HEAD `7cf4f01`, 8 коммитов bc39673..7cf4f01): **ДОБРО НА МЕРЖ**, вердикт отдан game-lead. Пруфы (в `Saved/` гейм-репозитория): `b122-wave3-build2.log` — реальная компиляция всех файлов волны + Link .lib/.dll, 0 ошибок; `b122-wave3-tests2.log` — 65 Success / 0 Fail, EXIT CODE 0, все 4 новых теста волны прошли (строки 1451/1618/1754/2220); манифест Shipping-пакета через aapt — без EXTERNAL_STORAGE и RemoteFileManager; `b122-wave3-augment1.log:1198` — SAFEZONE-строка, коммит 179664a = ровно один WBP_PlayerStats.uasset; дифф глазами чистый, все 21+1 отладочная привязка под `CONTRARY_WITH_QA_CHEATS`, игровые снаружи.
- Замечание не-блокер: таймаут ~30 с ожидания экрана согласия оставляет рекламный SDK неподнятым на этот запуск (при нормальном старте недостижимо). Известное ограничение лида: живой прогон магазина Б8 на телефоне не делался.
- Следующий шаг: за game-lead — маркер QA_OK и merge в master.

## Урок сессии: «EXIT=0» бывает пустым
`Build.bat` может вернуть 0 со строкой `Target is up to date`, не скомпилировав НИЧЕГО. Для гейта искать строки `Compile [x64] <файл>`; нет их — гнать `Rebuild.bat`. При unity-сборке отдельных имён .cpp игрового модуля в логе НЕТ — они внутри блоков `Module.ContrarySurvivor.N.cpp`; полная чистая пересборка всех N блоков покрывает все файлы модуля по построению.

## Урок сессии: проверять занятость проекта, а не верить вводной
`tasklist`/`Get-Process *Unreal*` + `git status` ДО начала; при чужой активности ждать. HEAD фиксировать в отчёте — может уехать.

## Урок сессии (08-06): число тестов сверять со счётом макросов на КОНКРЕТНОМ коммите
Старый лог мог сниматься с рабочей копии, где уже лежали ещё не закоммиченные тесты (b6-consent-tests1.log: 63 успеха при 61 макросе на bc39673). Арифметика «было + добавили = стало» сходится только через `git grep -c IMPLEMENT_SIMPLE_AUTOMATION_TEST <коммит>`, а не по числам из сообщений коммитов.

## Как гонять полный набор (эталон Build 1.2.1: 32 теста; на 08-06 в наборе уже 65)
1. Проверить, что проект свободен.
2. Начисто: `Rebuild.bat ContrarySurvivorEditor Win64 Development -Project=<uproject> -WaitMutex` (~1–2.5 мин; при «paging file too small» добавить `-NoUBA -MaxParallelActions=6`). Движок: `E:/UnrealEngine/UE_5.5`.
3. Тесты: `UnrealEditor-Cmd.exe <uproject> -ExecCmds="Automation RunTests ContrarySurvivor" -TestExit="Automation Test Queue Empty" -unattended -nopause -nosplash -stdout -nullrhi -abslog=<лог>`.
4. Критерий: число `Result={Success}` = числу макросов `IMPLEMENT_SIMPLE_AUTOMATION_TEST` в `Source/ContrarySurvivor/Tests/` на проверяемом коммите, падений 0, чистый выход `TestExit: Automation Test Queue Empty` и `TEST COMPLETE. EXIT CODE: 0`. Строки `GIsCriticalError` в логе UE 5.5 может не быть — чистоту выхода смотреть по хвосту лога.
5. Коммандлеты целостности, каждый свежим процессом: `-run=GenerateWbp -verify` (12 WBP, «VERIFY OK» у каждого); `-run=GenerateWbp -dumpslots` (срез `SLOTS WBP_*` по всем 12); при затронутых анимациях/скелетах — `-run=PatchAnimBp -verify`, `-run=AddGripSocket -verify`.

## Рецепты проверки
- **Мёртвая фича при зелёной сборке.** Пути на контент в C++ не проверяются компилятором: `grep -rhoE '"/Game/[^"]+"' Source/` и сверять с `Content/<путь>.uasset`.
- **Удаление класса с UCLASS.** Доказательство невключения — файл ответа линковщика `UnrealEditor-<Модуль>.dll.rsp`.
- **Git LFS.** `git lfs ls-files` — истина по HEAD; сверять ВСЕ .uasset/.umap из диффа против списка, не только новые.
- **Секреты в диффе.** Хекс-греп `[0-9a-fA-F]{32}` по текстовому диффу (`':(exclude)*.uasset' ':(exclude)*.umap'`); код возврата снимать с grep, не с head в конце конвейера; рядом позитивный контроль (греп заведомо частой строки).
- **Двоичный поиск** только через Bash, с позитивным и негативным контролем; ловушка префиксов (`MI_FogBand` ловит `MI_FogBandSoft`).
- **Цепочки с grep рвутся:** ноль совпадений даёт код 1 и обрывает `&&`.
- **Безобидный шум в логах UE:** `Failed to load 'WinPixGpuCapturer.dll'` — отладочная библиотека PIX, не ошибка.
- **Манифест Android-пакета:** `E:/Android/sdk/build-tools/34.0.0/aapt.exe dump permissions <apk>` и `dump xmltree <apk> AndroidManifest.xml`; сверять дату пакета с датой последнего коммита волны.

## Ограничения
- Вердикт только с реальными логами (правило B). Логи qa — в `context/qa/logs/`.
- Headless не проверяет: проигрывание анимаций/монтажей, тач-жесты, визуал (материалы/масштаб/торговец) — это живой PIE и приёмка Рината.
