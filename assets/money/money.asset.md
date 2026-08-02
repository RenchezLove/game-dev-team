---
id: money
name: Money (пачка купюр с бандеролью)
status: approved
builder: 10_build_money.py
source_model: money.blend
fbx: SM_Money.fbx
preview: ../icons/512/money.png
material: M_Money
tris: 48
verts: 32
bbox_m: [0.161, 0.080, 0.053]
origin: bbox center, Z=0 (base)
forward: +Y
color_attr: Col (CORNER / BYTE_COLOR)
palette: {paper: '#D6CFBC', bill: '#7C8A66', band: '#C4A05F'}
created: 2026-08-02
author: modeler-3d
verified_from: SM_Money.fbx (round-trip, лог logs/2026-08-02-build-props.log)
tags: [loot, money, currency, vcol, low-poly, mobile]
---

# Money (пачка купюр)

Предмет «Деньги» для тайлового инвентаря и лута. Модели в проекте не было —
самодельное предложение modeler-3d, УТВЕРЖДЕНО game-lead 2026-08-02 по
рендеру иконки. Замечание лида учтено: разлёт двух верхних купюр поджат
(сдвиги/повороты уменьшены), пачка выглядит собранной.

Геометрия: стопка купюр (брусок 15.6×6.7×4.0 см) + крафт-бандероль вокруг
середины + две чуть повёрнутые купюры сверху (повороты 5° и −4°). Между
частями воздушные зазоры 0.5 мм — совпадающих плоскостей нет (анти-мерцание).

Цвета — свои приглушённые тона в духе палитры GDD (утверждены вместе с
рендером): торцы бумаги #D6CFBC, «зелень» купюр #7C8A66 (семейство Faded
Sage), бандероль #C4A05F (семейство XP Gold). Вершинные цвета, 1 материал.
