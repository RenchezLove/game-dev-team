# context: qa

## 🧭 СЕЙЧАС
- 2026-08-08 мерж-гейт `fix/shop-pause-bones-0808` (4 коммита d7291fb..963b1a6 поверх master 0ec0a43): **ДОБРО НА МЕРЖ** — вердикт отдан game-lead. Прошлый гейт night-0807 вынесен в archive.md.
- Сборка (`Saved/qa-gate3-build.log`): touch 4 правленых .cpp + новый тест, реальная компиляция `Module.ContrarySurvivor.10/12.cpp`, линк .lib и .dll, DLL перелинкована 10:58:54 (была 10:49:12), 0 ошибок, exit 0.
- Тесты (`Saved/qa-gate3-tests.log`): 82 Success / 0 Fail (макросов ветка 82, master 81 = +1 новый ShopBackpackWeapon), TEST COMPLETE EXIT CODE 0, GIsCriticalError=0. Регрессии оружия зелёные: StartWithoutFirearm, WeaponSlotDesync.*(3), WeaponUiGating.RangedGate; новый PurchasedFirearmGoesToBackpackThenTapEquips=Success.
- Логика проверена глазами: TryAdoptRangedWeapon при не-огнестреле/занятом слоте возвращает false, предмет остаётся в рюкзаке (ветка HandleTileUse для любой категории Weapon безопасна, потерь/дублей нет). Пауза: убрано только согласие, строка политики и номер версии сохранены (RefreshConsentAndVersion цел). L_World_C.umap — LFS-указатель. Дифф/секреты чистые (позитивный контроль сработал).
- Следующий шаг: за game-lead — маркер QA_OK и merge в master. Дерево чистое, HEAD d7291fb, замок сборки снят.
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
