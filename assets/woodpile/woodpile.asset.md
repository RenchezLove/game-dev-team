---
id: woodpile
name: Woodpile (поленница, низкополи)
status: preview
source_model: SM_Woodpile.blend
builder: ForGameLead(Materials)/demo-assets/_build/build_villageprops.py
fbx: SM_Woodpile.fbx
preview: woodpile_pthreeq.png
renders: [woodpile_pthreeq.png, woodpile_pfront.png, woodpile_side.png, woodpile_top.png, woodpile_bthreeq.png, woodpile_wire_pthreeq.png, woodpile_wire_top.png]
material: M_Woodpile
tris: 200
verts: 120
bbox_m: [0.974, 0.296, 0.664]
origin: base centre on ground (Z=0)
forward: +Y (log lengths face viewer; cut ends face +/-X), up: +Z
color_attr: Col (CORNER / BYTE_COLOR)
created: 2026-06-26
revised: 2026-06-28
author: modeler-3d
engine: blender-eevee
verified_from: SM_Woodpile.fbx
tags: [village, prop, woodpile, firewood, wood, vcol, low-poly, mobile, stage-C]
---

# Woodpile (поленница)

Штабель дров у дома (Этап C3, спек §2). ПЕРЕДЕЛАН 2026-06-28 по правке Рината
(«убери лишнюю геометрию, просто аккуратно сложи дрова»): простая ОПРЯТНАЯ стопка —
10 коротких поленьев (низкополи цилиндр, 6 граней) уложены ГОРИЗОНТАЛЬНО вдоль X,
длиной к зрителю (видна длина, не торцы), в 5 ровных рядов по высоте × 2 ряда в глубину.
Лёгкий разнобой длины/смещения — натурально, но аккуратно. Прежний вариант (hex-«соты»
торцами + поперечные поленья + задник, 392 трис) ЗАМЕНЁН — это и была «лишняя геометрия».

Двухтонность лёгкая: кора-бока чуть темнее (Timber / тёмно-коричневый вариант через
ряд), торцы-срезы светлые (свежий распил) — видны по краям ±X. Без задника, без
поперечных, без hex-упаковки.

Габариты 0.974 × 0.296 × 0.664 м (Д×Г×В). Origin — центр основания на земле (Z=0).
rot 0 / scale 1, нормали наружу (round-trip из FBX, signed_vol +0.134). 200 трис /
120 верш, всё треугольники. 1 материал vcol M_Woodpile (ADR-032: нода VertexColor
'Col' → Base Color, без текстур), Col CORNER/BYTE_COLOR, 1 UVMap.

Превью-ассет (vcol, без бейка). Импорт/коллизия/дубликаты — за game-lead/Ринатом.
