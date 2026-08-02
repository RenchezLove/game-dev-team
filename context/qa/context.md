# context: qa

## 🧭 СЕЙЧАС
- 2026-08-02 мерж-гейт ветки `feature/build121-fixes` (HEAD `188b5fd`, база `feature/build12-night`): **ГОДНО по всем 5 пунктам ТЗ Build 1.2.1**, вердикт отдан game-lead. Мерж в master — только после живой приёмки Рината (условие ТЗ волны).
- Артефакты в `logs/` (префикс `b121-gate`): `b121-gate-rebuild.log` (без «Target is up to date», unity-блоки 1–11, обе DLL, EXIT=0); `b121-gate-tests.log` (Found 32 / Success 32 / Fail 0, чистый выход «Test Queue Empty»); `b121-gate-wbp-verify.log` (VERIFY OK по всем 12 WBP, вкл. новые WBP_EndOfStory и WBP_CorpseLoot); `b121-gate-wbp-dumpslots.log` (срез SLOTS по всем 12, ошибок загрузки 0); `b121-gate-diff-stat.log` + `b121-gate-diff-text.log` (58 файлов, hex-секретов 0, позитивный контроль 85 UPROPERTY); `b121-gate-lfs.log` (17/17 бинарников диффа в LFS).
- Следующий шаг: за game-lead — живая приёмка Рината, затем маркер QA_OK и merge в master.

## Урок сессии: «EXIT=0» бывает пустым
`Build.bat` может вернуть 0 со строкой `Target is up to date`, не скомпилировав НИЧЕГО. Для гейта искать строки `Compile [x64] <файл>`; нет их — гнать `Rebuild.bat`. При unity-сборке отдельных имён .cpp игрового модуля в логе НЕТ — они внутри блоков `Module.ContrarySurvivor.N.cpp`; полная чистая пересборка всех N блоков покрывает все файлы модуля по построению.

## Урок сессии: проверять занятость проекта, а не верить вводной
`tasklist`/`Get-Process *Unreal*` + `git status` ДО начала; при чужой активности ждать. HEAD фиксировать в отчёте — может уехать.

## Как гонять полный набор (эталон Build 1.2.1: 32 теста)
1. Проверить, что проект свободен.
2. Начисто: `Rebuild.bat ContrarySurvivorEditor Win64 Development -Project=<uproject> -WaitMutex` (~1–2.5 мин; при «paging file too small» добавить `-NoUBA -MaxParallelActions=6`). Движок: `E:/UnrealEngine/UE_5.5`.
3. Тесты: `UnrealEditor-Cmd.exe <uproject> -ExecCmds="Automation RunTests ContrarySurvivor" -TestExit="Automation Test Queue Empty" -unattended -nopause -nosplash -stdout -nullrhi -abslog=<лог>`.
4. Критерий: `Found 32 automation tests` + 32 `Result={Success}`, падений 0, чистый выход `TestExit: Automation Test Queue Empty`. Build 1.2.1 добавил к 26 старым: трупы/лут (WolfDeathLootStaysInCorpse, BanditDeathLootStaysInCorpse, ContainerTakeAndExpire), реклама PlaytimeGate6Min, стаки (InventoryMerge, ConsumeOneFromStack). Строки `GIsCriticalError` в логе UE 5.5 может не быть — чистоту выхода смотреть по хвосту лога.
5. Коммандлеты целостности, каждый свежим процессом: `-run=GenerateWbp -verify` (12 WBP, «VERIFY OK» у каждого); `-run=GenerateWbp -dumpslots` (срез `SLOTS WBP_*` по всем 12); при затронутых анимациях/скелетах — `-run=PatchAnimBp -verify`, `-run=AddGripSocket -verify`.

## Рецепты проверки
- **Мёртвая фича при зелёной сборке.** Пути на контент в C++ не проверяются компилятором: `grep -rhoE '"/Game/[^"]+"' Source/` и сверять с `Content/<путь>.uasset`.
- **Удаление класса с UCLASS.** Доказательство невключения — файл ответа линковщика `UnrealEditor-<Модуль>.dll.rsp`.
- **Git LFS.** `git lfs ls-files` — истина по HEAD; сверять ВСЕ .uasset/.umap из диффа против списка, не только новые.
- **Секреты в диффе.** Хекс-греп `[0-9a-fA-F]{32}` по текстовому диффу (`':(exclude)*.uasset' ':(exclude)*.umap'`); код возврата снимать с grep, не с head в конце конвейера; рядом позитивный контроль (греп заведомо частой строки).
- **Двоичный поиск** только через Bash, с позитивным и негативным контролем; ловушка префиксов (`MI_FogBand` ловит `MI_FogBandSoft`).
- **Цепочки с grep рвутся:** ноль совпадений даёт код 1 и обрывает `&&`.
- **Безобидный шум в логах UE:** `Failed to load 'WinPixGpuCapturer.dll'` — отладочная библиотека PIX, не ошибка.

## Ограничения
- Вердикт только с реальными логами (правило B). Логи qa — в `context/qa/logs/`.
- Headless не проверяет: проигрывание анимаций/монтажей, тач-жесты, визуал (материалы/масштаб/торговец) — это живой PIE и приёмка Рината.
