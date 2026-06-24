# context: concept-artist

> Персональная память агента `concept-artist`. Сюда агент дистиллирует решения, ограничения и текущее состояние (правило H). Новые сессии стартуют с этого файла.

## Решения
- **Основной инструмент визуала — нативный code-render** (HTML/CSS+SVG → PNG/PDF через headless Edge). Навык `canvas-design` НЕ используем (ADR-004 пересмотрен: он не под скоуп роли, к тому же не был установлен). Внешние AI-генераторы изображений не вводим.
- Подтверждённая форма рендера: `"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --headless=new --disable-gpu --hide-scrollbars --no-sandbox --window-size=W,H --screenshot="ABS\OUT.png" "file:///E:/.../PAGE.html"`. PDF — тем же Edge с `--print-to-pdf`. Вёрстку фиксировать под вьюпорт (`html,body{width:Wpx;height:Hpx;overflow:hidden}`) — кадр совпадёт 1:1.
- Python/Pillow на машине НЕТ. Node v24 есть (puppeteer/sharp — запас).

## Ограничения
- Нативный тулсет НЕ закрывает фигуративные/живописные зарисовки — эскалировать game-lead, не имитировать.
- Работа только в фича-ветке, не в master.

## Текущее состояние

### Ш7 — валидация инструмента concept-artist (2026-06-08): ПРОЙДЕНА на нативном пути
- Итог 1-й попытки (через canvas-design): навык НЕдоступен (нет в реестре сессии, `Skill(canvas-design)`→Unknown, ФС-скан пуст) — и в teammate, и в главной сессии. Значит не баг #29441, а отсутствие навыка вообще. По решению Рината canvas-design признан не под скоуп роли (абстрактное искусство) → перешли на нативный code-render.
- Итог 2-й попытки (нативный путь): Я написал HTML/SVG стиль-лист `concept-art/contrarysurvivor-style-sheet.html` (палитра 8 HEX + мудборд 4 фактуры + 3 силуэта, настроение STALKER/LDoE) + `contrarysurvivor-style-notes.md`. РЕНДЕР отдал game-lead (см. ниже про Bash) → PNG 1600×1000 291832 B + PDF 109135 B, визуально подтверждён.
- **ВАЖНАЯ СРЕДОВАЯ НАХОДКА:** в той сессии `Bash` мне НЕ был доступен (`No such tool available: Bash`), хотя его добавили в `concept-artist.md`. Причина: дефиниция агента кешируется на старте сессии game-lead — правка frontmatter в середине сессии не подхватывается спавном. → В НОВОЙ сессии тулсет с `Bash` применится, и рендер смогу запускать сам. Если снова `No such tool: Bash` — значит сессию не перезапускали после правки дефиниции.
- Палитра/силуэты — ЧЕРНОВИК НА ОТБОР, не утверждённый канон (диздок не подключён). HEX выдуманы под описанное настроение. Силуэт «выживший» дан сбоку для читаемости формы, хотя игра top-down — допущение.

### Задача стиль-системы + промпты (2026-06-11): диздок подключён
- Фоторефы владельца (`E:/ForGameLead(Materials)/ФотоРеференсы/1.jpg,2.webp,3.webp`) ОТКРЫЛИСЬ через Read — это **Last Day on Earth (LDoE)**: изометрия ~45°, болотисто-зелёное окружение, лоуполи деревья с плоскими вееровыми кронами, фасеточные камни-кристаллы, мягкие косые тени, монохромные/малонасыщенные текстуры персонажей (выживший — тёмная одежда, зомби серо-зелёные с красным акцентом), тёплое дерево построек, жёлто-оранжевые акценты (растения/костёр/лут), кровь условная. Прямо совпадает с диздоком → это и есть целевое направление.
- Сделана **палитра 16 цветов** (4 группы: средовые / постройки-материалы / акцент-опасность / UI-HUD) под «слегка мрачно + мультяшно, без чернухи». HTML+CSS → headless Edge → PNG `context/concept-artist/tmp/cs-palette.png` (98361 B, 1600×1000), визуально подтверждён. HTML-исходник рядом.
- HEX базовые: Moss Field #3F5A31, Sun Grass #5C7A3E, Pine Shade #2B3A2C, Dry Earth #7D6A4E, Timber #8A5A32, Concrete #6E6A60, Cold Steel #5A6470, Faded Sage #9AA08C; акценты: Rust Alarm #C64B2C (враг/опасность), Amber Loot #E0A32E (лут), Toxic Lime #7E9B3A (мутант), Muted Blood #8A2F2A; UI: Panel #1B2018, Bone Ink #E7E4D8, HP Green #4E8C46, XP Gold #CAA54E.
- Также отдано 4 EN-промпта для image-gen (герой / бандит / деревня / keyframe) — это арт-дирекшн+промпты, не рисунок (мой скоуп).
- **Подтверждено:** Bash В ЭТОЙ сессии доступен, рендер запускаю сам. Edge-путь рабочий.

## Демка: UI-черновики + NPC-спек (2026-06-24)
- **Попап «штраф за смерть» (A4):** черновик на утв. Рината. 3 текста (сухо-системный / нарративный-амнезия / промежуточный) + макет. PNG `docs/contrary-survivor/ui/death-penalty-popup.draft.png` (1280×720), HTML рядом. Факты (источник §10 demo-plan): −40% денег игрока, дроп ТОЛЬКО Consumable мешком на месте смерти (вернуть можно), снаряжение+квест-предметы целы, попап на неск. секунд при респауне у костра. Открытый вопрос: валюта — GDD «монеты» vs прежняя HUD-иконка «₽».
- **Спек на модульных NPC (C4, староста+торговец):** `docs/contrary-survivor/npc-humanoid-spec.draft.md` + палитра-борд `docs/contrary-survivor/ui/npc-palette-board.draft.png`. Читаемость сверху: староста=тёплый земляной (DryEarth/Timber), торговец=холодный серый+малый AmberLoot-акцент. Бюджет ~1.5–2.5k трисов (GDD ч.2: 1.5–4k; mobile-opt.md per-char НЕ даёт).
- **ВАЖНО — на диске уже есть модульный гардероб (ADR-018), не с нуля:** `Content/Characters/Shared/Humanoid/` (база Head/Torso/Legs + общий скелет `...Head_Skeleton` + `ABP_HumanoidCharacter` + Idle/Run/Walk + Material) и `Characters/Shared/Clothing/SK_Cloth_L1`/`L2` (Head/Torso/Legs каждый) + `M_Clothes_Flat`. Броня канон = `Armor/SK_Armor_*_01`; `Shared/Armor/_02` — орфан, не опираться. NPC собираются из этого + recolor. (Видел листингом, не открывал — визуал подтверждает modeler.)
- **Материал дома «выветренное дерево» (C1):** арт-дир-направление + мини-борд `docs/contrary-survivor/ui/house-material-board.draft.png`. Стены тёплые (Timber/DryEarth/PineShade), крыша ХОЛОДНАЯ и СВЕТЛЕЕ стен (FadedSage/Concrete/ColdSteel) — чтобы сверху отделяться от тёплой земли-дороги; крыша целая (C1). 1 материал (vertex-paint стена/крыша + baked AO), без normal/parallax/Lumen. Открытый вопрос: тон крыши холодный vs тёплый-тан (рек. холодный).
- Папка `docs/contrary-survivor/ui/` — складываю туда UI-черновики (HTML-исходник + PNG рядом).
- **demo-plan перерендер (06-24):** `demo-plan.html` пересобран из `demo-plan.source.md` (источник истины; старый HTML был устаревший) + `demo-plan.preview.png` (900×16550). CSS — print-ready (A4 @page, годится и в PDF через `--print-to-pdf`).
- **ПРИЁМ для длинных доков → 1 PNG (важно, иначе режется):** Edge `--screenshot` снимает РОВНО `--window-size H`; контент выше — РЕЖЕТ низ молча. Сначала ЗАМЕРЬ высоту: инжектни в копию HTML `<script>`, пишущий `document.documentElement.scrollHeight` в DOM → `msedge --headless=new --dump-dom file://...` → grep значение; потом рендерь `--window-size=W,(H+slack)` c `--force-device-scale-factor=1`. Низ доп-проверь срезом (`body{transform:translateY(-Npx)}` + короткий вьюпорт). Протокол B: exit 0 ≠ полный кадр (поймал обрезку 8200 vs 16493).

## HUD/inventory icons (полировка #18) — 2026-06-15
- 15 флэт-иконок 128×128 PNG (прозрачный фон, RGBA) + contact-sheet. Папка: `context/concept-artist/tmp/hud-icons/`.
- Генератор: `gen.js` (Node) — палитра-locked SVG → standalone HTML в `html/`, рендер msedge `--headless=new --default-background-color=00000000 --window-size=128,128 --screenshot`. Прозрачность даёт именно флаг `--default-background-color=00000000`.
- Стиль: плоская заливка + обводка Panel Dark #1b2018 width 5, round joins. 1-2 цвета из cs-palette на иконку.
- Набор: health(heart+cross HP Green), hunger(drumstick), thirst(drop steel), money(₽ coin gold); slot-head/torso/legs (sage placeholders — ЧЕРНОВИК); pistol, knife, ammo-box, wolf-hide(splayed pelt — draft-ish), notebook(rust ribbon=quest), food(can), medkit(rust cross), armor-generic(vest).
- Импорт в UE как текстуры — позже (game-lead/Сборщик).
