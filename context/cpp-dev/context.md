# context: cpp-dev

> Лёгкая рабочая память `cpp-dev` (правило H + Гигиена памяти из CLAUDE.md: стоп >150 строк, СЕЙЧАС вырезает прошлый). Закрытая история — в [archive.md](archive.md) (read-on-demand, НЕ для грунтовки). Build-логи — `logs/`, история — git.

## 🧭 СЕЙЧАС
**ЭТАП D — БАГ «броня из занятого слота пропадает» ЗАКРЫТ: сборка BUILD_EXIT=0, ЗАКОММИЧЕНО `ef515fe` в `feature/stage-d-combat` (1 файл PlayerCharacter.cpp, 16 строк).** НЕ ЗАПУШЕНО — лид пушит сам вместе с Content при закрытии этапа D. PIE-проверка (надеть в занятый слот -> старая в рюкзак) — за лидом/Ринатом. Лог: `logs/build-2026-07-09-armor-loss-fix.log`. Свободен под следующую задачу.
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
