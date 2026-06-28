---
id: choppingblock
name: Chopping Block (колода с топором, низкополи)
status: preview
source_model: SM_ChoppingBlock.blend (Rinat hand-authored; источник NewChoppingBlock/)
builder: none — ручная правка Рината (НЕ процедурный build_villageprops)
fbx: SM_ChoppingBlock.fbx
preview: choppingblock_preview_v1.png
renders: [choppingblock_pthreeq.png, choppingblock_pfront.png, choppingblock_side.png, choppingblock_top.png, choppingblock_bthreeq.png, choppingblock_wire_pthreeq.png, choppingblock_wire_top.png]
material: M_ChoppingBlock
tris: 100
verts: 64
bbox_m: [0.79, 0.38, 0.903]
origin: block base centre on ground (Z=0)
forward: +Y (axe handle leans +Y), up: +Z
color_attr: Col (CORNER / BYTE_COLOR)
created: 2026-06-26
revised: 2026-06-28
author: modeler-3d
engine: blender-eevee
verified_from: SM_ChoppingBlock.fbx
tags: [village, prop, chopping-block, axe, wood, metal, vcol, low-poly, mobile, stage-C]
---

# Chopping Block (колода с топором)

Место для рубки дров (Этап C3, спек §4): пень-колода (цилиндр 10 граней, светлый
торец-срез сверху с тёмными зарубками) + воткнутый топор (стальной клин-лезвие с ржавой
кромкой, погружённое в верх колоды; деревянное топорище торчит вверх и наружу по +Y) +
2 расколотых полена на земле рядом (треугольные призмы, светлый скол сверху).

Габариты группы 0.79 × 0.38 × 0.903 м (колода Ø~0.38; топор над колодой). Origin —
центр основания колоды на земле (Z=0). rot 0 / scale 1, нормали наружу
(signed_vol +0.053, round-trip из FBX). 1 материал vcol (M_ChoppingBlock): кора —
Timber + щели Pine Shade, срезы — светлый распил, лезвие — Cold Steel + ржавчина
Rust Alarm по кромке, топорище — Dry Earth.

КАНОН 2026-06-28 = РУЧНОЙ файл Рината (`assets/choppingblock/NewChoppingBlock/
SM_ChoppingBlock.blend`), экспортирован сюда КАК ЕСТЬ (применены трансформы — уже были
identity, нормали пересчитаны наружу, посажен на землю Z=0). Геометрия уже минимальная
(100 трис, всё треугольники) — «оптимизировать/снижать поли» было нечего без потери
силуэта. Прежний процедурный вариант (build_villageprops) ЗАМЕНЁН этим файлом.

Топор — часть того же меша (не разбирать), читается силуэтом сверху (лезвие поперёк,
топорище наружу). Превью-ассет (vcol, без бейка). Импорт/коллизия — за game-lead/Ринатом.
