# Задача unreal-operator: наполнение волны инструментов (ADR-075) — таблицы и BP

**От:** game-lead, 22.08.2026. **Ветка:** рабочее дерево игры уже на `feature/tools-0822` (C++ часть готова и собрана, 7 коммитов). **Основание:** ADR-075; спека `E:/game-dev-team/context/game-lead/tasks/spec-datatables-phase2.md` (читай §а, §б и группу 7 — там точные структуры и значения).

## Что сделать (по порядку)

### 1. Таблица предметов DT_Items
- Создать Data Table на строке `FContraryItemRow` в `Content/Data/DT_Items` (папку Data создать).
- 19 строк, имена строк латиницей = AnalyticsId (water_bottle, canned_food, bandage, ammo_9mm, knife, pistol, armor_t1_head … armor_t3_pants, wolf_pelt, laptop). Значения полей — по таблице соответствия спеки §а: LegacyKey = старый служебный ключ (кириллица там, где она в коде), названия, иконки, меши, категории, стаки, цены (вода 5, еда/бинт 12, патрон 2, нож 40, пистолет 150, броня 50/120/250 по тирам, у шкуры/ноутбука цена 0). Источники значений — реальные конструкторы (AArmorTiers.cpp, APistol.cpp, AMeleeWeapon.cpp, AAmmoItem.cpp, AConsumableItem.cpp) — сверяйся с кодом, не выдумывай.

### 2. Таблица квестов DT_Quests
- Data Table на строке `FContraryQuestRow` в `Content/Data/DT_Quests`, 2 строки:
  - `KillWolves`: «Шкуры волков», kill-цели нет, RequiredItemRow=wolf_pelt ×3, маркер WolfDen, награда 200;
  - `ClearBanditBase`: «Зачистить базу бандитов», KillTargetTag=Bandit ×3, RequiredItemRow=laptop ×1, маркер BanditBase, награда 250.
  - Тексты (title/description/реплики) — дословно из дампа `Saved/elder_quests_dump.txt` (лежит готовый).

### 3. Назначить таблицы
Project Settings → Game → «Contrary Survivor: таблицы данных» (класс UContraryDataSettings): ItemTable=DT_Items, QuestTable=DT_Quests. Изменения уходят в `Config/DefaultGame.ini` — этот файл закоммитить.

### 4. Blueprint-ассеты
- `Content/System/AI/BP_EnemyAIController` (от AEnemyAIController) и `BP_WolfAIController` (от AWolfAIController); в BP_EnemyBandit и BP_Wolf назначить AIControllerClass на новые BP. Числа НЕ менять — дефолты уже верные.
- `Content/Environment/Props/AbandonedCar/BP_AbandonedCar` (от AAbandonedCar). Проверь в деталях: петли створок (поля «Петля …») выставить по реальным пивотам мешей, чтобы двери/капот/багажник открывались правдоподобно; имена параметров материалов — открой MI_CarPaint и M_CarGlass, найди реальные имена параметров цвета/битости и впиши в поля BP (если параметра битости в M_CarGlass нет — оставь как есть, код скроет стекло).
- BP предметов по спеке §а: BP_Ammo9mm, BP расходников, BP_WolfPelt, BP_Laptop, BP_Knife (от соответствующих классов; у брони — один BP_ArmorBase от AArmor, строки таблицы сами несут слот/защиту/меш) — в `Content/Items/`. В строках DT_Items поле ItemClass направить на эти BP.

### 5. Живой пример «новый контент без кода» (приёмка ТЗ издателя)
На ВРЕМЕННОМ пустом уровне (НЕ на боевых картах L_World_C/L_World — их не открывать на запись и не сохранять!) поставь два экземпляра BP_AbandonedCar с разными настройками (одна целая закрытая, вторая — без капота и передних колёс, двери настежь, битые стёкла, другой цвет кузова) и сними кадры вьюпорта обоих. Временный уровень НЕ коммитить, кадры — в `Saved/Showcase/tools/`.

### 6. Сдача
- Сохранить ассеты, `git add` только новые/изменённые ассеты и DefaultGame.ini, коммит в `feature/tools-0822` (`git commit -- <пути>`).
- Доклад мне: список созданных ассетов, пути кадров, что не получилось/отличается от спеки — честно.

## Правила
- Редактор открывай/закрывай сам, молча. РОВНО ОДИН редактор; о начале и конце работы с редактором сообщи мне (я не запускаю headless, пока ты в редакторе).
- Боевые карты не трогать. Расстановка по уровням — за Ринатом, мы делаем ИНСТРУМЕНТЫ (ADR-028).
- Каждое значение — из спеки/кода/дампа, не по памяти. Чего нет в источниках — спроси меня, не выдумывай.
