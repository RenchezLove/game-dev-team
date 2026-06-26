---
id: woodpile
name: Woodpile (поленница, низкополи)
status: preview
source_model: SM_Woodpile.blend
builder: ForGameLead(Materials)/demo-assets/_build/build_villageprops.py
fbx: SM_Woodpile.fbx
preview: woodpile_preview_v1.png
renders: [woodpile_pthreeq.png, woodpile_pfront.png, woodpile_side.png, woodpile_top.png, woodpile_bthreeq.png, woodpile_wire_pthreeq.png, woodpile_wire_top.png]
material: M_Woodpile
tris: 352
verts: 212
bbox_m: [1.32, 0.57, 0.815]
origin: base centre on ground (Z=0)
forward: +Y (cut-end face), up: +Z
color_attr: Col (CORNER / BYTE_COLOR)
created: 2026-06-26
author: modeler-3d
engine: blender-eevee
verified_from: SM_Woodpile.fbx
tags: [village, prop, woodpile, firewood, wood, vcol, low-poly, mobile, stage-C]
---

# Woodpile (поленница)

Штабель дров у дома (Этап C3, спек §2). 14 коротких поленьев-цилиндров (6 граней,
торцы-срезы наружу) в шахматном порядке на фасаде + 3 верхних полена внахлёст (неровный
силуэт сверху). Тёмный блок-заполнитель за ними даёт глубокие щели — главный читаемый
признак: СВЕТЛЫЕ срезы-торцы на тёмном фоне. Видимые срезы обращены по +Y (forward).

Габариты 1.32 × 0.57 × 0.815 м (Д×Г×В). Origin — центр основания на земле (Z=0).
rot 0 / scale 1, нормали наружу (round-trip). 1 материал vcol (M_Woodpile): кора —
Timber + выветренный Faded Sage на части поленьев, щели — Pine Shade тёмный, торцы-срезы
— светлый свежий распил (тёплый кремовый). Контраст кора/срез — ключевой.

Превью-ассет (vcol, без бейка). Импорт/коллизия/дубликаты — за game-lead/Ринатом.
