# context: cpp-dev

> Лёгкая рабочая память `cpp-dev` (правило H + Гигиена памяти из CLAUDE.md: стоп >150 строк, СЕЙЧАС вырезает прошлый). Закрытая история — в [archive.md](archive.md) (read-on-demand, НЕ для грунтовки). Build-логи — `logs/`, история — git.

## 🧭 СЕЙЧАС
**ЭТАП F «Удержание» (ADR-038/044) — КОД ГОТОВ, ветка `feature/stage-f-retention` запушена (HEAD `748430a`, от master a8ec8fd). Ждёт QA-гейт/приёмку.**
- Статус по пунктам ТЗ:
  - Спайк GameAnalytics: ✅ СОБИРАЕТСЯ с UE 5.5. Плагин 6.1.2 в `Plugins/GameAnalytics` (коммит `cc78bae`, установка разрешена Ринатом 07-11), пруф `logs/build-2026-07-11-ga-plugin-spike.log`.
  - F2 ежедневка: ✅. UDailyRewardComponent на игроке (25/+10/потолок 75, всё EditAnywhere), окно UDailyRewardWidget (чистый C++ UMG, без BP), поля даты/серии в UContrarySaveGame.
  - F1 онбординг: ✅. UOnboardingComponent + UOnboardingHintWidget: 5 одноразовых подсказок (старт-движение WASD/ЛКМ/Q, подбор E, староста, инвентарь, смерть — текст СТРОГО ADR-044 п.3), флаги в сейве, автоскрытие ~7 c + гашение любым вводом (AnyKey-биндинг, bConsumeInput=false).
  - Q3 крючок: ✅. ThirdQuest в AElderNPC (после сдачи Q2; Collect 3 «Шкура волка», 100 монет, MapMarkerTag=WolfDen2 — пока актора с тегом нет, метка мягко не рисуется, проверено кодом HUD). Диалог получил перенос строк (DrawWrappedText).
  - F3 события: ✅. UAnalyticsSubsystem (GameInstanceSubsystem, Config=Game): смерть / взятие+сдача квеста (id) / покупка (предмет+цена value) / убийство врага (тип через новый параметр RegisterEnemyKill) / ежедневный вход (value=день серии); старт сессии SDK сам. Ключи ТОЛЬКО из локальных файлов `E:/game-dev-team/keys/{GameKey,SecretKey}.txt` (KeysFolder — UPROPERTY(Config), переопределяется в DefaultGame.ini; значения в публичное репо НЕ попадают, ADR-013). Нет ключей/плагина → тихо выключено (одна строка в лог).
  - Попап смерти: ✅ фраза «их можно забрать» убрана (ADR-044 п.3 доп., DrawDeathScreen).
- Коммиты этапа: `cc78bae` спайк-плагин → `c89e050` чистка → `e8ca7aa`+`72c3161` WIP (спас game-lead при обрыве лимита) → `b7c93d5` связка F1/F2+попап → `748430a` F3+тесты.
- Пруфы: сборки `logs/build-2026-07-11-stage-f-mid-f1f2q3.log` и `logs/build-2026-07-11-stage-f-f3-analytics.log` (оба BUILD_EXIT=0); тесты `logs/tests-2026-07-11-stage-f-full.log` — 14 зелёных (8 Combat + 6 новых Retention.DailyReward), 2 красных Movement = известный пре-существующий фон (падают на чистом master, пруф `logs/tests-2026-07-11-movement-baseline-MASTER-fail-proof.log`).
- НЕ ПРОВЕРЕНО (нужен живой PIE): показ окна награды и тостов, клик «Забрать», сценарий Q2→Q3 в диалоге, живая инициализация GA с ключами.
- ⚠️ Заметка для этапа G (Android-пак): ключи GA придётся внести в конфиг локально перед пакетованием (на устройстве папки E:/ нет) — решаем на G.

## LIVE-КОНВЕНЦИИ (как работаю в этом проекте)
- **Include внутри модуля**: префикс `ContrarySurvivor/<Subdir>/Header.h`. Относительный `Components/Header.h` из другой подпапки НЕ резолвится (C1083).
- **override UFUNCTION** — БЕЗ повтора макроса `UFUNCTION()` над override (UHT запрещает; reflection наследуется, AddDynamic работает).
- **Сборка `-WarningsAsErrors`**: нельзя шэдоуить члены базы (C4458; не называть локальную `Mesh` в наследниках ACharacter).
- **Команда сборки**: `Build.bat ContrarySurvivorEditor Win64 Development -Project=E:/ContrarySurvior/ContrarySurvivor/ContrarySurvivor.uproject -WaitMutex -NoHotReload` напрямую с `2>&1 | tee log` (НЕ через `cmd /c`). **НОВОЕ 07-11: если UBA падает «paging file too small» и лог обрывается без итога — добавить `-NoUBA -MaxParallelActions=6`, лечит.**
- **Релинк DLL только при ЗАКРЫТОМ редакторе** (LNK1104), проверять tasklist.
- **Среда**: проект `E:/ContrarySurvior/ContrarySurvivor/` (UE 5.5.4), движок `E:/UnrealEngine/UE_5.5`, VS2022 MSVC 14.44. API сверять по заголовкам движка, не по памяти.
- **Не коммитить ассеты оператора** (BP_*.uasset, *.umap) — только свои Source/. Фича-ветки, master/merge не трогаю. Новые параметры — EditAnywhere+BlueprintReadWrite+DisplayPriority (директива Рината 06-25).
- **UMG из чистого C++ (этап F)**: дерево в NativeOnInitialized (WidgetTree->ConstructWidget, RootWidget=CanvasPanel), CreateWidget<T>(PC, T::StaticClass()) без BP-наследника — работает. Модули: UMG (public) + Slate/SlateCore (private).
- **Плагин GameAnalytics подключён УСЛОВНО** в Build.cs: WITH_GAMEANALYTICS=1 только если есть Plugins/GameAnalytics/GameAnalytics.uplugin — копия без плагина остаётся собираемой.

## Решения
- Health: игрок И враги — через `UStatsComponent` (TakeDamage БЕЗ Super). `HandleDeath()` virtual; `ReloadCurrentWeapon` virtual (патроны из рюкзака, AAmmoItem-стак).
- `GetMesh()==HeadMesh==Leader` модульного гуманоида; Torso/Legs — followers (SetLeaderPoseComponent). Оружие к кости `R_Hand`, офсеты — параметры.
- Волк — НЕ гуманоид: ACharacter + SK_Wolf + Single Node анимации; ИИ = AWolfAIController(AEnemyAIController).
- **SetFocus сам пешку НЕ вращает** (UE 5.5 Pawn.cpp:1049) — доворот наш StartAimTurnTo.
- ИИ погони: state-machine Idle/Chase/Attack, nav + direct-fallback; QA-лог дросселирован.
- **Сейв-слот один (`ContrarySave`), retention-поля в нём же (этап F):** `SaveGame()` игрока создаёт свежий объект → ПЕРЕНОСИТ retention-поля из прежнего сейва (`UContrarySaveGame::CopyRetentionData`), иначе автосейв костра обнулял бы серию/подсказки. Компоненты удержания правят ТОЛЬКО свои поля через `LoadOrCreateSaveObject`/`WriteSaveObject`. Игра при ЗАПУСКЕ сейв НЕ грузит (LoadGame только при смерти) → награда ежедневки зеркалится и в живые статы, и в `Save->Money`.
- Чистая логика серии ежедневки — `Retention/DailyRewardLogic.h` (DailyReward::Compute, без UObject) — гоняется headless-автотестом; перевод часов назад = награды нет, серия цела.

## Ограничения / тех-долги (DRAFT, на тюнинг/добивку)
- Save/Load НЕ сохраняет `ItemName`/`StackCount` (только class path) — пре-существующее, не трогаю (риск кору).
- Атака врага без LineOfSight-гейта → теоретически удар через тонкую стену в упор.
- Числа баланса — DRAFT UPROPERTY: пистолет 25@2/с, нож 35, бандит HP80/650, волк HP40/780, кап брони 0.75.
- invoker-навмеш требует RecastNavMesh `RuntimeGeneration=Dynamic` в уровне.
- Movement.NavWalkingFixed / TranslatesOnInput красные и на master — причина НЕ РАССЛЕДОВАНА (отдельная задача).
- GA-плагин: 2 warning C4996 (FEditorStyle deprecated) в коде САМОГО плагина — не наш код, не блокирует.
