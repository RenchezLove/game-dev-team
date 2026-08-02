---
id: water
name: Water (бутылка питьевой воды 0.5 л)
status: preview
builder: 10_build_water.py
source_model: water.blend
fbx: SM_WaterBottle.fbx
preview: ../icons/512/water.png
material: M_WaterBottle
tris: 200
verts: 102
bbox_m: [0.062, 0.059, 0.222]
origin: ось бутылки, Z=0 (дно)
forward: +Y (осесимметрична)
color_attr: Col (CORNER / BYTE_COLOR)
palette: {plastic: '#8FA6B5 (свой, осветлённый Cold Steel)', label: '#E7E4D8 Bone Ink', cap: '#5A6470 Cold Steel'}
created: 2026-08-02
author: modeler-3d
verified_from: SM_WaterBottle.fbx (round-trip, лог logs/2026-08-02-build-props.log)
tags: [loot, water, drink, bottle, vcol, low-poly, mobile]
---

# Water (бутылка воды)

Пластиковая бутылка 0.5 л по ТЗ game-lead 2026-08-02: тело вращения на 10
граней, D 6.2 см, высота 22.2 см с крышкой. Плечо-сужение к горлышку, крышка
шире горлышка (читается ступенькой), белая этикетка-полоса по середине.

ДОПУЩЕНИЕ (озвучено в отчёте): в 16-цветной палитре GDD нет светло-голубого,
поэтому корпус — свой тон #8FA6B5 (осветлённое семейство Cold Steel);
прецедент своих приглушённых тонов — торговец (жилет/штаны). Крышка Cold
Steel #5A6470, этикетка Bone Ink #E7E4D8. Вершинные цвета, 1 материал.
