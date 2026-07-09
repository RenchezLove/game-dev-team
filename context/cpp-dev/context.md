# context: cpp-dev

> Лёгкая рабочая память `cpp-dev` (правило H + Гигиена памяти из CLAUDE.md: стоп >150 строк, СЕЙЧАС вырезает прошлый). Закрытая история — в [archive.md](archive.md) (read-on-demand, НЕ для грунтовки). Build-логи — `logs/`, история — git.

## 🧭 СЕЙЧАС
**ЭТАП D — броня Т1-Т3 в магазин (решение Рината 07-07): КОД НАПИСАН, ЖДЁТ КОМАНДЫ «СОБИРАЙ» от лида.** Ветка `feature/stage-d-combat` (база f45675e). СБОРКА НЕ ЗАПУСКАЛАСЬ (редактор открыт у Рината — запрет лида). НЕ ЗАКОММИЧЕНО.
- **Файлы:** новые `Public/AArmorTiers.h` + `Private/AArmorTiers.cpp` (9 классов A{Head,Torso,Pants}ArmorT{1,2,3}: слот+защита 0.05/0.10/0.16+русское ItemName+FObjectFinder на /Game/Characters/Shared/Armor/SK_Armor_T*_*); `Characters/MasterTrader.cpp` +14 строк (include + 9 FShopEntry, Price=5, через MakeItem). Ассеты (9 uasset) и имена объектов в них сверены с диском.
- **Прокрутка магазина СДЕЛАНА** (переполнение: 18 позиций против ~12 видимых; решение лида — реюз экшенов ShopQtyInc/Dec, колесо УЖЕ в DefaultInput.ini:77-84, моё «обработки колеса нет» было неверно). `ContrarySurvivorHUD.h/.cpp`: ScrollShopList(Delta) + ShopListScrollOffset/MaxScroll (кламп в DrawShop от фактической высоты панели, сброс в SetShopOpen), цикл BUY стартует с offset, счётчик «X-Y из N (колесо — листать)» справа от заголовка при переполнении; `ContrarySurvivorPlayerController.cpp` OnShopQtyDec/Inc: else (слайдер неактивен) → ScrollShopList(+1/-1). Колесо вниз = список вниз. SELL-колонку не трогал.
- После «собирай»: Build.bat → BUILD_EXIT=0 → коммит ТОЛЬКО Source/** (6 файлов: AArmorTiers.h/.cpp новые + MasterTrader.cpp + ContrarySurvivorHUD.h/.cpp + ContrarySurvivorPlayerController.cpp) в stage-d-combat.
- **Пруф прошлой сборки:** пакет №2 BUILD_EXIT=0, лог `logs/build-2026-07-06-stage-d-feedback-pack2.log`; push `483b230..f45675e` подтверждён. PIE-проверка пакета №2 — за лидом/Ринатом.
- В рабочей копии бинарники Рината/оператора (BP_*, umap, новые uasset экипировки) — НЕ коммитить с моим кодом.
- Вариант B прицеливания (Modify Bone) — отложен лидом; разведка в archive.md (07-05).

## LIVE-КОНВЕНЦИИ (как работаю в этом проекте)
- **Include внутри модуля**: префикс `ContrarySurvivor/<Subdir>/Header.h`. Относительный `Components/Header.h` из другой подпапки НЕ резолвится (C1083).
- **override UFUNCTION** — БЕЗ повтора макроса `UFUNCTION()` над override (UHT запрещает; reflection наследуется от базовой virtual UFUNCTION, AddDynamic работает).
- **Сборка `-WarningsAsErrors`**: нельзя шэдоуить члены базы (напр. `APawn* Pawn` → C4458; локальную переменную не называть `Mesh` в наследниках ACharacter).
- **Команда сборки**: `Build.bat ContrarySurvivorEditor Win64 Development -Project=E:/ContrarySurvior/ContrarySurvivor/ContrarySurvivor.uproject -WaitMutex -NoHotReload`. Запускать НАПРЯМУЮ с `2>&1 | tee log`, НЕ через `cmd /c` (вложенный cmd не редиректит → пустой лог, ложный exit 0).
- **Релинк DLL только при ЗАКРЫТОМ редакторе** (иначе LNK1104 на `UnrealEditor-ContrarySurvivor.dll`). Проверять tasklist. Компиляция .cpp+.lib проходит и при открытом — «компиляция PASS, релинк отложен».
- **Среда**: проект `E:/ContrarySurvior/ContrarySurvivor/` (UE 5.5.4), движок `E:/UnrealEngine/UE_5.5`, VS2022 MSVC 14.44. API сверять по заголовкам движка, не по памяти.
- **Не коммитить ассеты оператора** (BP_*.uasset, *.umap) — только свои Source/. Работаю в фича-ветке, master/merge не трогаю. Новые параметры — EditAnywhere+BlueprintReadWrite+meta DisplayPriority наверх (директива Рината 06-25).

## Решения
- Health: игрок И враги — через `UStatsComponent` (TakeDamage БЕЗ Super). Инлайн-Health базы `AMasterHumanoidCharacter` — легаси для оружейной системы.
- `HandleDeath()` virtual в базе; враг/игрок override. `ReloadCurrentWeapon` virtual; игрок тянет патроны из рюкзака (AAmmoItem-стак).
- `GetMesh()==HeadMesh==Leader` модульного гуманоида; Torso/Legs — followers через SetLeaderPoseComponent. Оружие крепится к кости `R_Hand` лидер-меша (сокетов в ассетах нет), офсеты грипа — параметры WeaponGripLocation/Rotation.
- Волк — НЕ гуманоид: ACharacter + единый меш SK_Wolf + Single Node анимации (без AnimBP); его ИИ = AWolfAIController(AEnemyAIController).
- **SetFocus сам по себе пешку НЕ вращает** (сверено с UE 5.5: APawn::FaceRotation, Pawn.cpp:1049 — no-op при выключенных bUseControllerRotation*, дефолт false; ACharacter не переопределяет; orient-to-movement у бандита тоже выключен). Доворот корпуса на цель — наш StartAimTurnTo (MasterHumanoidCharacter, вариант A).
- ИИ погони: state-machine Idle/Chase/Attack в AEnemyAIController, nav-погоня + direct-fallback (AddMovementInput) при недоступном навмеше; QA-лог дросселирован.

## Ограничения / тех-долги (DRAFT, на тюнинг/добивку)
- Save/Load НЕ сохраняет `ItemName`/`StackCount` (только class path) → после reload имена предметов/прогресс item-целей квестов и стак патронов теряются. Пре-существующее, не трогаю (риск кору).
- Атака врага в Attack-стейте без LineOfSight-гейта → теоретически удар через тонкую стену в упор.
- Числа баланса — DRAFT UPROPERTY: walk≈600/sprint≈1200, пистолет 25@2/с, нож 35, бандит HP80/650, волк HP40/780, кап брони 0.75 (текущая суммарная защита игрока упирается в кап → эффективный урон по игроку ×0.25 — учитывать при тюнинге урона бандитов).
- invoker-навмеш требует RecastNavMesh `RuntimeGeneration=Dynamic` в уровне.
