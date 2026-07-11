# context: concept-artist

> Персональная память агента `concept-artist`. Дистилляция решений/ограничений/состояния (правило H). Прошлое — в `archive.md` (read-on-demand).

## 🧭 СЕЙЧАС (2026-07-11)
**Фаза:** UI-иконки инвентаря (ADR-043: в занятом слоте брони видна иконка предмета).

**Сдано 07-11 (протокол B: ls + file, 9×PNG 128×128 RGBA):** иконки предметов брони `armor-t{1,2,3}-{head,torso,legs}.png` — рабочие в `context/concept-artist/tmp/hud-icons/`, финалы скопированы в `docs/contrary-survivor/ui/hud-icons/` (коммитит game-lead). Генератор расширен: `tmp/hud-icons/gen.js` — палитра `A` (хексы 1:1 из утверждённого armor-wearables-artdirection.md), 9 новых SVG; контакт-лист пересобран (25 иконок); проверка мелкого размера — `tmp/hud-icons/armor-icons-preview.png` (128/64/32 на фоне слота). Силуэты/цвета сверены с рендерами моделей `assets/armor_wearables/renders/SK_*_front.png` (все 9 просмотрены глазами). Статус: НА ОТБОР (Ринат через game-lead).

**Параллельно висит:** промпты NPC (староста/торговец) `docs/contrary-survivor/art/npc-elder-trader-prompts.md` — ждём отбора Рината по сгенерированным референсам.

**Контекст закрытого:** арт-дирекшн экипировки утверждён Ринатом 07-06; modeler сдал 12/12 мешей в UE.

**Следующий шаг:** правки иконок по отбору Рината; отбор NPC-референсов.

## Решения (постоянные)
- **Инструмент визуала — нативный code-render** (HTML/CSS+SVG → PNG/PDF, headless Edge). Без внешних AI-генераторов; canvas-design не используем (ADR-004).
- Рендер: `"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --headless=new --disable-gpu --hide-scrollbars --no-sandbox --window-size=W,H --screenshot="ABS\OUT.png" "file:///E:/...html"`. PDF — `--print-to-pdf`. Вёрстку фиксировать под вьюпорт (`html,body{width:Wpx;height:Hpx;overflow:hidden}`).
- Прозрачный PNG: `--default-background-color=00000000`. Python/Pillow НЕТ; Node v24 есть (запас).
- ⚠️ В bash-цикле путь `--screenshot` писать ПРЯМЫМИ слэшами (`E:/...$n.png`): `\\$n` в двойных кавычках экранирует доллар → Edge молча пишет файл с буквальным `$n` в имени.
- **Финал/утверждённые артефакты — в `docs/`**, не в `context/**/tmp/` (тот в .gitignore).
- **Длинный док → PNG:** Edge режет низ молча; сначала замерить scrollHeight через `--dump-dom`, потом `--window-size=W,(H+slack)`.
- cs-палитра проекта (16 hex) — в `archive.md`, раздел «Стиль-система».

## Ограничения
- Фигуративный/живописный концепт — НЕ мой тулсет: эскалировать game-lead, не имитировать.
- Только фича-ветка, не master; коммиты за game-lead.
