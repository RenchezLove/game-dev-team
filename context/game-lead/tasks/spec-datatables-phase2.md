# Спека Фазы 2: таблицы данных (предметы, квесты) + правки UPROPERTY + конструктор брошенных авто

**Автор:** cpp-dev, 2026-08-22. **Основание:** ADR-075 (волна инструментов контента, решения Рината 22.08), инвентаризация Фазы 1 (`E:/ContrarySurvior/ContrarySurvivor/Saved/bp-audit-phase1.md`), решения лида по эскалациям (каталог торговца — вариант «таблица», типы расходников не трогаем).
**Статус:** проект на утверждение лида. Кода нет — рабочее дерево игры не трогалось (там qa).
**Проверено по файлам:** AMasterInventoryItem.h, AArmor.h, AArmorTiers.cpp, AConsumableItem.h, AAmmoItem.cpp, APistol.cpp, AMeleeWeapon.cpp, ShopTypes.h, MasterTrader.h/.cpp (RebuildCatalog:258-333), ElderNPC.h, QuestComponent.h/.cpp, EnemyCharacter.h/.cpp, WolfCharacter.h/.cpp, EnemyAIController.h, WolfAIController.cpp, Pickup.h, ContrarySaveGame.h (по loc-stage2-plan), ADR-050/069/075, loc-stage2-plan.md «Порция 0», список ассетов `Content/Environment/Props/AbandonedCar/` (Glob, 14 файлов).

---

## 0. Принцип владения данными (анти-дубль, п.5 ТЗ издателя)

Чтобы «Blueprint не дублирует значения, а читает их», у каждого числа — РОВНО ОДИН дом:

| Тип данных | Дом | Пример |
|---|---|---|
| Идентичность, витрина, экономика предмета | **таблица предметов** | ключ, название, иконка, меш, цена, категория, лимит стака |
| Поведение (боевые числа, тайминги) | **класс / BP-наследник** | урон ножа, разброс пистолета, интервалы деградации |
| Квест как контент | **таблица квестов** | цели, количества, награда, тексты |
| Раскладка на уровне | **экземпляр актора** | радиусы зон, число врагов, наполнение пикапа |

Служебные ключи ADR-050 (`ItemName`, `FQuest::RequiredItemName`, `KillTargetTag`, значения «Шкура волка»/«Ноутбук», сравнение QuestComponent.cpp:204,252) — **неприкосновенны**: рантайм продолжает сравнивать те же строки. Таблицы НЕ вводят новый механизм сравнения — только новое место хранения тех же значений (см. §1, поле `LegacyKey`).

---

## (а) Таблица предметов — реестр `DT_Items`

### Имя строки (RowName)

Латинский идентификатор в нижнем регистре. **Совпадает с уже существующими `AnalyticsId` каталога торговца** (MasterTrader.cpp: water_bottle, canned_food, bandage, ammo_9mm, knife, pistol, armor_t1_head … armor_t3_pants) — эти иды уже стабильны, уже в событиях аналитики, придумывать вторые не надо. Новые строки: `wolf_pelt`, `laptop`.

### Структура строки — `FContraryItemRow : public FTableRowBase`

Новый файл `Source/ContrarySurvivor/Data/ContraryItemRow.h`.

| Поле | Тип | Откуда переезжает (сегодняшний дом) |
|---|---|---|
| `LegacyKey` | `FString` | служебный ключ ADR-050 как есть: «Pistol», «Knife», «Патроны 9мм», «Броня Т1 — голова», «Шкура волка», «Ноутбук», ключи расходников из `AConsumableItem::GetDefaultDisplayName`. Рантайм-сравнения продолжают ходить по нему; для НОВЫХ предметов = имени строки. Это и есть «не плодить новую связку по ключам» (ADR-069): единственное место, где ид строки сходится со старым ключом — эта колонка |
| `DisplayText` | `FText` | конструкторы предметов (`ItemDisplayText`), `GetDefaultDisplayText` расходников, `QuestItemText`/`QuestLootItemText` |
| `Icon` | `TSoftObjectPtr<UTexture2D>` | пути из конструкторов: AArmorTiers.cpp (9 иконок), APistol.cpp:46, AMeleeWeapon.cpp:68, AAmmoItem.cpp:13, статики `AConsumableItem::GetDefaultIcon`, иконки шкуры/ноутбука из `AQuestItem::GetItemIcon` |
| `WorldMesh` | `TSoftObjectPtr<UStaticMesh>` | меш предмета в мире/в руке: SM_Pistol, SM_Knife (сейчас FObjectFinder в конструкторах) |
| `EquipMesh` | `TSoftObjectPtr<USkeletalMesh>` | слотовый меш брони SK_Armor_T{1..3}_{Head,Torso,Legs} (сейчас FObjectFinder в AArmorTiers.cpp) |
| `ItemClass` | `TSoftClassPtr<AMasterInventoryItem>` | класс актора (C++ или BP). Для брони после Фазы 2 может указывать на один базовый BP брони — строка сама несёт слот/защиту |
| `Category` | `EItemCategory` | конструкторы (Resource/Consumable/Armor/Weapon/Quest) |
| `MaxStackCount` | `int32` | конструкторы (999 у стакаемых, 1 у брони/оружия) |
| `Price` | `float` | RebuildCatalog: вода 5, еда/бинт 12, патрон 2, нож 40, пистолет 150, броня — из PriceArmorT1/T2/T3 (50/120/250). 0 = у торговца не продаётся |
| `ConsumableType` | `EConsumableType` | каталожное `bApplyConsumableType`+`ConsumableType`; действует только на расходники |
| `HealRestoreAmount` | `float` | `AConsumableItem::HealRestoreAmount` (25) — граница спорная: это поведение; предлагаю ОСТАВИТЬ на классе, в таблице НЕ дублировать (п.0). В таблице держим только витрину/экономику |
| `ArmorSlot` | `EArmorSlot` | конструкторы AArmorTiers |
| `ArmorProtection` | `float` | конструкторы AArmorTiers (0.05/0.10/0.16). Для брони защита — суть ПРЕДМЕТА, а не поведения, и «новый тир без кода» без неё невозможен → живёт в таблице; поле класса становится VisibleAnywhere-зеркалом (заполняется из строки при спавне), чтобы не было двух редактируемых копий |

Что в таблицу НЕ переезжает (остаётся на классах/BP): боевые числа оружия (Damage/FireRate/Range/патроны/разброс/звуки/вспышка), эффекты расходников (величины восстановления — на UStatsComponent потребителя и классе расходника), всё поведение. Новый ТИП расходника — не в этой волне (решение лида по эскалации №2).

### Доступ к таблицам

Новый класс `UContraryDataSettings : public UDeveloperSettings` (файл `Source/ContrarySurvivor/Data/ContraryDataSettings.h`): два поля `TSoftObjectPtr<UDataTable> ItemTable, QuestTable` с `config=Game`. Задаются один раз в Project Settings (пишутся в DefaultGame.ini), читаются отовсюду без синглтонов и без BP. Пустая ссылка = фолбэк на сегодняшние конструкторные дефолты (игра обязана работать и без таблиц — мягкая деградация, как везде в проекте).

### Точки потребления (спавн из строки)

Хелпер в новом файле `Data/ContraryItemLibrary.{h,cpp}` (статики, `UBlueprintFunctionLibrary`):
- `FindRowByLegacyKey(Key)` — обратный поиск (нужен выкупу торговца и стыковке старых сейвов);
- `SpawnItemFromRow(World, RowName, StackCount)` — спавнит `ItemClass`, проставляет `ItemName=LegacyKey`, `ItemDisplayText`, `ItemIcon`, стак, для брони — слот/защиту/меш; используется покупкой (PlayerCharacter.cpp:894) и, опционально, пикапом (`APickup` получает поле `PlacedItemRow` (FName) рядом со старыми полями — старые не удаляем, они уже расставлены на карте).

---

## (б) Таблица квестов — `DT_Quests`

### Что НЕ меняется (важно для сейва)

Рантайм-структура `FQuest` и `UQuestComponent` не трогаются: журнал, сейв (в слоте лежат ПОЛНЫЕ FQuest — RestoreQuests), сравнение по `RequiredItemName` — всё как есть. Таблица — источник ДЕФОЛТОВ квеста при выдаче, а не новый рантайм. Старые сейвы совместимы без миграции.

### Имя строки

`RowName == QuestId` (уже латиница: `KillWolves`, `ClearBanditBase` — сверить точные значения по ElderNPC.cpp при реализации).

### Структура строки — `FContraryQuestRow : public FTableRowBase`

Новый файл `Source/ContrarySurvivor/Data/ContraryQuestRow.h`. Поля повторяют редактируемую часть FQuest (VisibleAnywhere-прогресс и State в таблицу не идут):

| Поле | Тип | Примечание |
|---|---|---|
| `Title`, `Description` | `FText` | тексты; собираются штатным gather (ADR-050) — FText в строках DataTable движок собирает |
| `Type` | `EQuestType` | описательный |
| `KillTargetTag` | `FName` | цель убийств; сходится с полем `QuestKillTag` врага (группа 2 правок ниже) |
| `TargetCount` | `int32` | 0 = kill-цели нет |
| `KillObjectiveLabel` | `FText` | подпись метки |
| `RequiredItemRow` | `FName` | **ссылка на строку таблицы предметов** (wolf_pelt, laptop). При выдаче квеста разрешается в `LegacyKey` строки и кладётся в `FQuest::RequiredItemName` — сравнение остаётся посимвольным по старому ключу, НОВОЙ связки по ключам не появляется (требование ADR-069/075 п.3): связь «квест→предмет» существует ровно в одном месте — этой колонке |
| `RequiredItemCount` | `int32` | 0 = item-цели нет |
| `ItemObjectiveLabel` | `FText` | подпись метки |
| `MapMarkerTag` | `FName` | тег актора-цели (QuestMarkerTag базы врагов) |
| `RewardMoney` | `float` | награда |
| `AcceptReplyText`, `TurnInReplyText`, `CloseReplyText` | `FText` | реплики героя на кнопках |
| `NextQuestRow` | `FName` | следующий квест цепочки (сейчас порядок «кв.1 → кв.2» зашит в `GetQuestForPlayer`); NAME_None = терминальный |

Реплики СТАРОСТЫ (интро, намёк ноутбука, FirstQuestCompletedText) остаются полями BP_Elder — это контент NPC, не квеста; в таблицу не тянем (иначе дубль и потеря правок Рината на экземпляре).

### Потребление

`AElderNPC` получает поля `FName FirstQuestRow, SecondQuestRow` (EditAnywhere) и наполняет `OfferedQuest`/`SecondQuest` из таблицы (PostInitializeComponents; конструкторные дефолты — фолбэк при пустой таблице). Существующие поля `OfferedQuest`/`SecondQuest` переводятся EditAnywhere → **VisibleAnywhere** — видны для отладки, но редактировать их больше нельзя (иначе две редактируемые копии одного квеста = запрещённый дубль). ⚠ Это перетрёт возможные правки квестов, сделанные Ринатом на BP_Elder, — перед реализацией сверить дефолты BP_Elder с конструктором (вопрос лиду №3).

---

## (в) Точный план правок Фазы 2 по файлам

Порядок причинный: сначала независимые мелочи (группы 1–3), потом реестр (4), на нём торговец (5) и квесты (6), машина (7) — независима, можно параллельно. Все правки — в новой ветке от master ПОСЛЕ отмашки лида. Одна сборка на группу + финальная; автотесты не запускаю (правило Рината), на каждую группу пишу headless-проверяемый тест в НОВЫЙ файл — прогонит лид/qa.

**Группа 1. Броня: меш в редактор.**
- `Public/AArmor.h` — `ArmorMesh_Equipped`: `VisibleAnywhere` → `EditAnywhere` (тип не меняю — минимальный дифф; перевод на мягкую ссылку не в эту волну).
- Проверка: EquipArmor читает поле через GetMesh() — семантика не меняется.

**Группа 2. Квест-теги врагов в поля.**
- `Characters/EnemyCharacter.h/.cpp` — новое `UPROPERTY(EditAnywhere, Category="Quest") FName QuestKillTag = "Bandit";` HandleDeath (сейчас EnemyCharacter.cpp:239) шлёт поле.
- `Characters/WolfCharacter.h/.cpp` — то же, `= "Wolf"` (сейчас WolfCharacter.cpp:286).
- Тот же FName идёт и в аналитику киллов (рядом в тех же функциях) — единый источник.

**Группа 3. AI-параметры доступны без кода.**
- `Controllers/EnemyAIController.h` — DetectionRange, AttackRange, AttackDamage, AttackCooldown, MoveAcceptanceRadius: `EditDefaultsOnly` → `EditAnywhere` (остальные группы уже EditAnywhere).
- Кода больше не нужно: BP_EnemyAIController и BP_WolfAIController создаёт оператор (волчьи дефолты уже в конструкторе AWolfAIController.cpp:14-23: урон 10, дальность 70, кулдаун 1.0, детекция 1800 — BP их унаследует), в BP_EnemyBandit/BP_Wolf назначается AIControllerClass. «Урон укуса в поле» уже выполнен архитектурно — это поле базы `AttackDamage`; BP контроллера волка делает его настраиваемым.

**Группа 4. Реестр предметов (новые файлы, старое поведение не ломается).**
- НОВЫЕ: `Data/ContraryItemRow.h`, `Data/ContraryDataSettings.{h,cpp}`, `Data/ContraryItemLibrary.{h,cpp}` (структура §а, настройки, поиск/спавн из строки).
- `Public/AArmor.h` — `ArmorProtection` остаётся EditAnywhere до заведения таблицы оператором; после наполнения DT_Items строками брони — отдельным коммитом в VisibleAnywhere (см. §а). Двумя шагами, чтобы не оставить окно, где защиту нельзя править нигде.
- Заполнение DT_Items (19 строк: 3 расходника, патроны, нож, пистолет, 9 брони, шкура, ноутбук, +резерв) — работа оператора в редакторе, значения по табличке §а.

**Группа 5. Торговец на таблицу.**
- `Actors/ShopTypes.h` — в `FShopEntry` добавляется `FName ItemRow` (пустое = старое поведение записи).
- `Characters/MasterTrader.h/.cpp` — новый `UPROPERTY(EditAnywhere) TArray<FShopCatalogRef> CatalogRows` (`{FName ItemRow; float PriceOverride = -1;}`); `RebuildCatalog()`: если CatalogRows непуст — каталог строится ИЗ НЕГО по таблице (цена из строки, override главнее) и правки редактора больше не перетираются; пуст — прежний C++-состав как фолбэк. Дефолт CatalogRows в конструкторе = сегодняшний прайс (те же 15 позиций). PriceArmorT1/T2/T3 остаются на переходный период, помечаются устаревшими в подсказке.
- `Characters/PlayerCharacter.cpp` (~894, покупка) — если у позиции есть ItemRow → `SpawnItemFromRow`; иначе старый путь.
- `Characters/MasterTrader.cpp` — `FindCatalogEntryForItem`: сопоставление сначала по `LegacyKey` (== ItemName предмета), потом прежний классовый путь (выкуп BP-предметов, которых нет в классовой цепочке).

**Группа 6. Квесты на таблицу.**
- НОВЫЙ: `Data/ContraryQuestRow.h` (структура §б).
- `Actors/ElderNPC.h/.cpp` — поля FirstQuestRow/SecondQuestRow, загрузка строк в PostInitializeComponents, OfferedQuest/SecondQuest → VisibleAnywhere; конструкторные дефолты — фолбэк.
- `UQuestComponent`, сейв — БЕЗ правок.
- Наполнение DT_Quests (2 строки) — оператор, значения из конструктора ElderNPC.cpp.

**Группа 7. Конструктор брошенных авто (ADR-075 п.4).**
- НОВЫЙ: `Actors/AbandonedCar.h/.cpp`, класс `AAbandonedCar : AActor`, `UCLASS(Blueprintable)`, паттерн OnConstruction как у ACampfire/AWorldBorder (правка галочки видна во вьюпорте сразу). Один BP_AbandonedCar (ADR-028).
- Детали в проекте (проверено списком файлов `Content/Environment/Props/AbandonedCar/`, 14 ассетов): SM_AbandonedCar_Body, _Door_FL/_FR/_RL/_RR, _Hood, _Trunk, _Wheel (один меш — ставится 4 раза), _Glass, _Scratches, _Block; материалы M_CarPaint + MI_CarPaint, M_CarGlass.
- Компоненты (все — UStaticMeshComponent с дефолтным мешем из папки, меши переопределяемы в BP): Body (корень-меш), DoorFL/FR/RL/RR, Hood, Trunk, WheelFL/FR/RL/RR, Glass, Scratches, + опц. Block (по имени — подпорка/блок; назначение уточнит оператор в редакторе, поле в классе завожу, дефолт скрыт).
- Поля (все `EditAnywhere, BlueprintReadWrite`, русские DisplayName/подсказки — паттерн APickup):
  - галочки наличия: `bDoorFL/bDoorFR/bDoorRL/bDoorRR`, `bHood`, `bTrunk`, `bWheelFL/FR/RL/RR`, `bScratches`, `bBlock` — прячут/показывают компонент;
  - стёкла: `bGlass` (есть/сняты) + `bGlassBroken` (целые/битые). Битость: отдельного меша битого стекла в папке НЕТ (проверено) → решаю материалом: MID от M_CarGlass с параметром «битости», а если у материала параметра не окажется — деградация до «битые = стекло скрыто» (оговорка ADR-075 «решение за исполнителем по факту»); имя параметра — настраиваемое поле `GlassBrokenParamName`, не хардкод;
  - цвет кузова: `FLinearColor BodyColor` + `FName PaintColorParamName` (дефолт подберу по факту из MI_CarPaint в редакторе оператора; поле настраиваемое — контракт с материалом не зашивается в код);
  - углы створок (предлагаю, в ТЗ нет — решение лида): `DoorFLOpenAngle` и т.д., градусы, 0 = закрыто — «брошенность» читается позой машины; дёшево (RelativeRotation в OnConstruction);
  - коллизия: кузов Block по Pawn и Visibility (машина — укрытие: и путь врагам режет, и линию атаки — фикс 08-07 это учитывает автоматически), детали — без отдельной коллизии (дёшево для Android).

**Оценка объёма:** группы 1–3 — мелочь, один день с сборкой и тестами; группы 4–6 — основная работа, ~6 новых файлов + 4 правленных, два-три дня с проверками; группа 7 — один день. Наполнение таблиц и BP — оператор, после моих структур.

---

## Открытые вопросы лиду (нужны решения до/в ходе реализации)

1. **RowName таблицы предметов = существующие AnalyticsId** (латиница, уже стабильны) — подтверждить. Альтернатива «RowName = старый служебный ключ с кириллицей» отвергнута мной: кириллические FName в именах строк — нетипичный путь, а связка со старыми ключами и так есть через `LegacyKey`.
2. **Углы открытия створок машины** — делать ли (в ТЗ только галочки; углы дешёвые и сильно добавляют «брошенности»).
3. **BP_Elder:** перед переводом OfferedQuest/SecondQuest в VisibleAnywhere сверить, не правил ли Ринат квесты на экземпляре/дефолтах BP (если правил — его значения переносятся в DT_Quests, а не теряются).
4. **Судьба 9 классов AArmorTiers** после переезда брони в таблицу (кандидаты на выпил вместе со старой бронёй _01) — НЕ в эту волну, но зафиксировать в бэклоге.
