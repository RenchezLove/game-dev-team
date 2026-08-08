# context: qa

## 🧭 СЕЙЧАС
- 2026-08-08 мерж-гейт ветки `feature/night-0807` (7 коммитов 1ea5e2d..0181111 поверх master `86274ad`): **ДОБРО НА МЕРЖ с одним замечанием**, вердикт отдан game-lead. Пруфы (в `Saved/` гейм-репозитория): `qa-gate2-build.log` — после touch 21 правленого .cpp реальная компиляция Module.ContrarySurvivor.9–12 + GenerateWbpCommandlet.cpp, линк обеих DLL (08-08 09:01), 0 ошибок; `qa-gate2-tests.log` — 81 Success / 0 Fail (= 81 макрос на ветке, master 74, +7 новых: 3 ContinueSpawn + 4 AttackLos/LootName; все 7 сверены по полным именам), TEST COMPLETE EXIT CODE 0, GIsCriticalError=0; `qa-gate2-wbp.log` — 19 WBP «VERIFY OK» (11 старых + 8 новых), 13 слотов HUD и 3 слота контроллера заполнены, «Итог проверки: ошибок 0». Дифф глазами чистый, LFS покрывает все 17 ассетов, хекс-греп секретов пуст (позитивный контроль 117), пустой документирующий коммит cd27744 подтверждён.
- ЗАМЕЧАНИЕ (не регрессия, передано лиду): `PlayerCharacter.cpp:524` создаёт индикатор хромоты жёстко из `ULimpIndicatorWidget::StaticClass()` — слот `LimpIndicatorWidgetClass` объявлен на HUD, заполнен генератором и «VERIFY OK», но НЕ ЧИТАЕТСЯ; правки Рината в WBP_LimpIndicator в игре не проявятся. -verify этот случай не ловит (проверяет заполненность слота, не чтение).
- В корне гейм-репо посторонняя нетрекаемая папка `scratchpad/` (poi_dump.py, poi_rename.py) — в мерж не попадает, прибрать.
- Следующий шаг: за game-lead — решение по замечанию (хвост или дофикс), маркер QA_OK и merge.

## Урок сессии: «EXIT=0» бывает пустым
`Build.bat` может вернуть 0 со строкой `Target is up to date`, не скомпилировав НИЧЕГО. Для гейта искать строки `Compile [x64] <файл>`; нет их — touch правленых .cpp и пересобрать (срабатывало 08-07 и 08-08). При unity-сборке отдельных имён .cpp игрового модуля в логе НЕТ — они внутри блоков `Module.ContrarySurvivor.N.cpp`.

## Урок сессии (08-08): ловушка «объявлено, но не читается» — проверять ОБЕ стороны
Слот WBP-класса — это пара «объявлен+заполнен» И «читается в CreateWidget». Верификация коммандлета проверяет только первую половину. Греп по всем `CreateWidget<`: каждый жёсткий `::StaticClass()` без выбора из слота — кандидат на пробел (08-08: LimpIndicator).

## Урок сессии: проверять занятость проекта, а не верить вводной
`tasklist`/`Get-Process *Unreal*` + `git status` ДО начала; при чужой активности ждать. HEAD фиксировать в отчёте — может уехать. Замок `.build-lock` в корне гейм-репо ставить на время сборки, снимать после.

## Урок сессии (08-06): число тестов сверять со счётом макросов на КОНКРЕТНОМ коммите
Арифметика «было + добавили = стало» сходится только через `git grep -c IMPLEMENT_SIMPLE_AUTOMATION_TEST <коммит> -- Source/ContrarySurvivor/Tests/`. 08-08: ветка 81, master 74 — сошлось с прогоном 81/0. Лист-имена тестов в логе могут совпадать между сьютами (HealsPoisonedSaveToCampfire есть и в Respawn, и в ContinueSpawn) — сверять по ПОЛНОМУ имени.

## Как гонять полный набор (на 08-08 в наборе 81 тест)
1. Проверить, что проект свободен.
2. Сборка: `Build.bat ContrarySurvivorEditor Win64 Development -Project=<uproject> -WaitMutex -NoHotReload -NoUBA -MaxParallelActions=6` (движок `E:/UnrealEngine/UE_5.5`; `-NoUBA` обязателен). «Target is up to date» — touch и заново.
3. Тесты: `UnrealEditor-Cmd.exe <uproject> -ExecCmds="Automation RunTests ContrarySurvivor; Quit" -unattended -nopause -nosplash -nullrhi -abslog=<лог>` (из Git Bash — префикс `MSYS_NO_PATHCONV=1`).
4. Критерий: число `Result={Success}` = числу макросов на проверяемом коммите, падений 0, хвост `TEST COMPLETE. EXIT CODE: 0`, `GIsCriticalError=0`.
5. Коммандлеты целостности свежим процессом: `-run=GenerateWbp -verify` — на 08-08 это 19 WBP «VERIFY OK» + 9 контрактов слотов CDO (6 HUD + 3 контроллера) + печать всех 13 слотов HUD; `-run=GenerateWbp -dumpslots`; при затронутых анимациях/скелетах — `-run=PatchAnimBp -verify`, `-run=AddGripSocket -verify`.

## Рецепты проверки
- **Мёртвая фича при зелёной сборке.** Пути на контент в C++ не проверяются компилятором: `grep -rhoE '"/Game/[^"]+"' Source/` и сверять с `Content/<путь>.uasset`.
- **Удаление класса с UCLASS.** Доказательство невключения — файл ответа линковщика `UnrealEditor-<Модуль>.dll.rsp`.
- **Git LFS.** `git lfs ls-files` — истина по HEAD; сверять ВСЕ .uasset/.umap из диффа против списка, не только новые.
- **Секреты в диффе.** Хекс-греп `[0-9a-fA-F]{32}` по текстовому диффу (`':(exclude)*.uasset' ':(exclude)*.umap'`); код возврата снимать с grep; рядом позитивный контроль.
- **Двоичный поиск** только через Bash, с позитивным и негативным контролем; ловушка префиксов (`MI_FogBand` ловит `MI_FogBandSoft`).
- **Цепочки с grep рвутся:** ноль совпадений даёт код 1 и обрывает `&&`.
- **Безобидный шум в логах UE:** `Failed to load 'WinPixGpuCapturer.dll'` — отладочная библиотека PIX, не ошибка; строка Build.cs про ключ статистики из `E:/game-dev-team/keys` — штатная, ключ вне репозитория.
- **Манифест Android-пакета:** `E:/Android/sdk/build-tools/34.0.0/aapt.exe dump permissions <apk>` и `dump xmltree <apk> AndroidManifest.xml`; сверять дату пакета с датой последнего коммита волны.

## Ограничения
- Вердикт только с реальными логами (правило B). Логи qa — в `context/qa/logs/`.
- Headless не проверяет: проигрывание анимаций/монтажей, тач-жесты, визуал (материалы/масштаб/торговец), Z у пола (трасса вне PIE невалидна) — это живой PIE и приёмка Рината.
