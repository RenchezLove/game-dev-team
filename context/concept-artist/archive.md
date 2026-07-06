# archive: concept-artist

> Закрытая история. Читается ТОЛЬКО по поводу (чистка / онбординг / «как пришли к X»). Источник правды на «сейчас» — блок «🧭 СЕЙЧАС» в `context.md`.

## Демка: серия черновиков + иконки (2026-06-24 … 06-29) — ЗАКРЫТО, сдано game-lead

**Правки 2026-06-28/29 (по требованиям Рината, приняты):**
- **Карта** `docs/contrary-survivor/ui/scheme-map.png` (483131 B): восточная дорога к логову теряется (4 сегмента убывающей ширины 46→18, opacity 0.55→0.23 + 2 earth-scuff), убран круг-плаза на перекрёстке, легенда обновлена.
- **Иконка thirst** (4491 B): капля перекрашена в голубой `water #3C8AC8` + блик `waterHi #C2E6FA`.
- **Иконка knife** (4880 B): перерисована по 3D-модели — навершник + рукоять с рёбрами (timber) → гарда (dark) → drop-point клинок (steel) с бликом.
- **Иконка pistol** (4161 B): по обновлённой модели со стволом; правка скобы по Ринату (уменьшена 28×22, крючок к рукояти).
- **Иконка slot-head** (4322 B): переделана под шлем (sage) на нейтральной голове (concrete); slot-torso/legs утверждены ранее.
- **Иконка food — УТВЕРЖДЕНА (06-29):** по референсу CannedFood1.avif — серебристая крышка с кольцом, голубая этикетка, куриная ножка (meatHi #F3CD86 добавлен в палитру gen.js). Версия 06-28 (sage-крышка+вилка) отменена.
- **Утверждённые иконки перенесены под git (06-29):** 12 PNG скопированы в `docs/contrary-survivor/ui/hud-icons/` (`context/**/tmp/` в .gitignore — туда финал не класть). **Правило: финал/утв. артефакты — в `docs/`.**
- **Пакет 06-28:** food (отменён→переделан), water-bottle (3209 B, новая), money (6946 B: монета + «M» вместо ¤). contact-sheet 900×1080, 16 иконок.

**Сданные черновики демки (пути от `E:/game-dev-team/`):**
1. **Попап смерти (A4) — ФИНАЛ** (Ринат выбрал 06-24): «ВЫ ПОГИБЛИ» + череп, «монеты» (не ₽). `docs/contrary-survivor/ui/death-penalty-popup.final.png`. Текст ушёл cpp → DrawDeathScreen.
2. **NPC-гуманоид спек (C4)** — `npc-humanoid-spec.draft.md` + `ui/npc-palette-board.draft.png`. Староста=тёплый земляной, торговец=холодный+янтарь. 6 вопросов Ринату (припарковано к Этапу C).
3. **demo-plan** — перерендер из `demo-plan.source.md`. Принято.
4. **Материал дома (C1)** — `ui/house-material-board.draft.png`: стены тёплые, крыша холодная/светлее. Отдан modeler.
5. **Локации врагов (B/C)** — `enemy-locations-spec.draft.md` + борд. Логово=холодный камень+кости; база=рыжий акцент #C64B2C.
6. **Земля+дорога (C2)** — `ground-road-spec.draft.md` + борд. Трава тёплая зелень + тропа Dry Earth, vertex-blend края.
7. **Ground-текстуры (06-25):** `E:/ForGameLead(Materials)/ground-tex/grass_1024.png` + `dirt_1024.png` (бесшовные, генератор `docs/contrary-survivor/textures/gen-ground-tex.js`). **Приём бесшовности:** элемент рисуется 9× с офсетами {−S,0,+S}, viewBox клипит. **Урок QC:** монтаж 3×3 из вложенных `<svg>` Edge не прорисовывает — только из реального PNG через `<img>`. **Урок вида:** крупные блобы телеграфируют повтор тайла — мелкий радиус 55-125, opacity 0.18-0.4.
8. **Декали крови (06-25):** `textures/blood/blood-splat-01..03.png` (1024² RGBA, генератор gen-blood-splat.js, Catmull-Rom блоб). Альфа проверена декодером PNG на Node.
9. **Текстура пламени (06-25):** `textures/fire/flame-01/02.png` + флипбук 4×2. **Урок:** профиль без пуза даёт «колонну» — нужен teardrop (пузо шире плеч, узкая нога).
10. **Деревня + карта (06-26) — УТВЕРЖДЕНЫ:** `scheme-village.png` (два ряда домов вдоль дороги восток-запад, костёр-сейв в центре) + `scheme-map.png` (перекрёсток центр, деревня запад 150 м, логово восток 300 м, база юг 250 м, север теряется). Рисунок Рината = первоисточник раскладки. Извилистые дороги — helper smooth() Catmull-Rom. **Приём план-схем:** SVG строю inline-JS (seeded mulberry32), канвас title-bar(70)+map+legend(220). Пропсы-ТЗ: `props-village-spec.draft.md` (тент, поленница, верёвка, колода с топором).
- **Реюз-инвентарь FBX** (`E:/ForGameLead(Materials)/demo-assets/*.fbx`, глоб 06-26): дома/забор/колодец/костёр, сосны/камни/кусты/трава, бочки/ящики бандитские, SM_BonePile/SM_WolfDenCave/SM_BanditShed живы как FBX.

## HUD/inventory icons (2026-06-15) — ЗАКРЫТО
- 15+ флэт-иконок 128×128 RGBA, генератор `context/concept-artist/tmp/hud-icons/gen.js` (палитра-locked SVG → HTML → Edge `--default-background-color=00000000`). Стиль: плоская заливка + обводка Panel Dark #1b2018 w5.

## Ш7 — валидация инструмента (2026-06-08) — ЗАКРЫТО
- canvas-design недоступен и признан не под скоуп (ADR-004 пересмотрен) → нативный code-render (HTML/SVG → Edge). Стиль-лист `concept-art/contrarysurvivor-style-sheet.html` отрендерен, PNG/PDF подтверждены.
- Средовая находка: дефиниция агента кешируется на старте сессии game-lead — правка frontmatter в середине сессии спавном не подхватывается.

## Стиль-система (2026-06-11) — основа, актуальна как референс
- Фоторефы владельца = **Last Day on Earth**: изометрия ~45°, лоуполи, малонасыщенные цвета, тёплое дерево, жёлто-оранжевые акценты.
- **cs-палитра 16 цветов** (`context/concept-artist/tmp/cs-palette.png`): Moss Field #3F5A31, Sun Grass #5C7A3E, Pine Shade #2B3A2C, Dry Earth #7D6A4E, Timber #8A5A32, Concrete #6E6A60, Cold Steel #5A6470, Faded Sage #9AA08C; акценты Rust Alarm #C64B2C (враг/опасность), Amber Loot #E0A32E, Toxic Lime #7E9B3A, Muted Blood #8A2F2A; UI: Panel #1B2018, Bone Ink #E7E4D8, HP Green #4E8C46, XP Gold #CAA54E.
