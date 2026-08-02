---
id: medkit
name: Medkit (аптечка)
status: preview
builder: 10_build_medkit.py
source_model: medkit.blend
fbx: SM_Medkit.fbx
preview: ../icons/512/medkit.png
material: M_Medkit
tris: 60
verts: 40
bbox_m: [0.256, 0.198, 0.114]
origin: bbox center, Z=0 (base)
forward: +Y (защёлка)
color_attr: Col (CORNER / BYTE_COLOR)
palette: {box: '#E7E4D8 Bone Ink', latch: '#5A6470 Cold Steel', cross: '#C64B2C Rust Alarm'}
created: 2026-08-02
author: modeler-3d
verified_from: SM_Medkit.fbx (round-trip, лог logs/2026-08-02-build-props.log)
tags: [loot, medkit, heal, vcol, low-poly, mobile]
---

# Medkit (аптечка)

Компактная аптечка первой помощи по ТЗ game-lead 2026-08-02: нижний корпус
25×18×6 см + крышка с выступом 3 мм, стальная защёлка на фронте (+Y) поверх
шва, красный крест из двух накладных брусков на крышке (бруски разной высоты
3 и 4 мм — в зоне пересечения нет совпадающих граней, мерцания нет).

Палитра GDD: корпус Bone Ink #E7E4D8, защёлка Cold Steel #5A6470, крест
Rust Alarm #C64B2C. Вершинные цвета, 1 материал, flat shade.
