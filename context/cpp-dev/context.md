# context: cpp-dev

> Лёгкая рабочая память `cpp-dev` (правило H + Гигиена памяти из CLAUDE.md: стоп >150 строк, СЕЙЧАС вырезает прошлый). Закрытая история — в [archive.md](archive.md) (read-on-demand, НЕ для грунтовки). Build-логи — `logs/`, история — git.

## 🧭 СЕЙЧАС
**ЭТАП D — БАГ «броня из занятого слота пропадает»: ДОФИКС СОБРАН (BUILD_EXIT=0) и ЗАКОММИЧЕН `5f76218`, НЕ ЗАПУШЕН (лид пушит с Content). Ждёт финальный PIE Рината.** Ветка `feature/stage-d-combat`. Логи сборок: `logs/build-2026-07-09-armor-loss-fix.log` (v1 ef515fe), `logs/build-2026-07-09-armor-loss-fix-v2.log` (v2 5f76218). Первый фикс `ef515fe` (гейт по IsItemEquipped) закрыл только shop-броню; PIE Рината показал: ДЕФОЛТНАЯ стартовая броня всё равно пропадала — дофикс `5f76218` убрал гейт.
- **Разбор по живому логу** `Saved/Logs/ContrarySurvivor.log`: при старте `EquipDefaultArmor()` (BeginPlay, стр.220) надевает AHeadArmor/ATorsoArmor/APantsArmor (ItemName «Head/Torso/Pants Armor», меши SK_Armor_*_01, защита 0.10/0.25/0.15) голым EquipArmor — БЕЗ пометки equipped и БЕЗ AddItem. Это НЕ путь сейва (ApplySaveData броню не переэкипирует — подтверждено). Мой прежний гейт `IsItemEquipped(PrevArmor)` возвращал false для дефолт-брони → она терялась.
- **МОЯ ОШИБКА (исправлена):** назвал дефолт-броню «одеждой Т0» и не возвращал. Факт: дефолт = РЕАЛЬНАЯ броня. Настоящая «Т0/одежда» = базовый меш тела (HeadAndSkeletonfbx_Head / SK_Cloth_T0_*), снимок CacheBaseSlotMeshes, восстанавливается UnequipArmor; НЕ предмет брони, через EquipArmor не проходит → PrevArmor быть не может → исключать нечего.
- **Дофикс (вариант «б», незакоммичен, поверх ef515fe):** в `PlayerCharacter.cpp` Inv_UseBackpackItem убрал из условия `&& Inventory->IsItemEquipped(PrevArmor)` → возвращаем ЛЮБУЮ броню из занятого слота. Inv_UnequipSlot уже добавляет предмет, которого нет в инвентаре (guard `if(!Contains)AddItem`, дубля нет). Оба сценария (дефолт→T1; T1→T2) проверены логикой.
- **Допущение (лиду):** дефолт-броня теперь падает в рюкзак при замене. Если Ринат не хочет её существования/возврата — отдельный дизайн-таск.
- По «собирай»: Build.bat → BUILD_EXIT=0 → новый коммит ТОЛЬКО `Source/ContrarySurvivor/Characters/PlayerCharacter.cpp`. Первая сборка была зелёная: `logs/build-2026-07-09-armor-loss-fix.log`.
- **Первопричина:** `PlayerCharacter.cpp` `Inv_UseBackpackItem` (case Armor) звал `EquipArmor` напрямую → база `MasterHumanoidCharacter::EquipArmor` просто ПЕРЕЗАПИСЫВАЕТ ссылку слота (`EquippedHeadArmor=Armor`), старый предмет не снимается. Старая броня выпадает и из paper-doll (`HUD:393` берёт `GetEquippedArmor`), и из списка рюкзака (`HUD:444` пропускает `IsItemEquipped`) → «сирота» = исчезает.
- **Фикс (1 файл):** `Source/ContrarySurvivor/Characters/PlayerCharacter.cpp` `Inv_UseBackpackItem`, case `Armor` — перед `EquipArmor` проверка: если слот занят ДРУГИМ бронепредметом И он `Inventory->IsItemEquipped` (реальный, надетый из рюкзака) → сперва `Inv_UnequipSlot(slot)` (тот же путь, что ручное снятие F4) → предмет вернулся в рюкзак. Стартовую одежду Т0 (НЕ помечена equipped, нет в рюкзаке из EquipDefaultArmor) не трогаем — штатная перезапись, чтобы не захламлять рюкзак. Новых include не нужно (все символы уже в файле).
- **Допущение (озвучено лиду):** Т0-одежда при первом надевании реальной брони в рюкзак НЕ возвращается (осознанно). Если Ринат захочет иначе — снять гейт `IsItemEquipped`.
- Ручное снятие F4/`Inv_UnequipSlot`, выброс `Inv_DropItem`, продажа `Shop_SellItem`, загрузка сейва `ApplySaveData` (броню НЕ переэкипирует) — НЕ тронуты. Других путей equip-в-занятый-слот нет (проверено grep по Source).
- После «собирай»: Build.bat → BUILD_EXIT=0 → коммит ТОЛЬКО `Source/ContrarySurvivor/Characters/PlayerCharacter.cpp` в stage-d-combat.
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
