---
id: laptop
name: Laptop (приоткрытый ноутбук)
status: preview
builder: 10_build_laptop.py
source_model: laptop.blend
fbx: SM_Laptop.fbx
preview: ../icons/512/laptop.png
material: M_Laptop
tris: 60
verts: 40
bbox_m: [0.340, 0.332, 0.237]
origin: bbox center, Z=0 (основание)
forward: +Y (передняя кромка клавиатуры)
color_attr: Col (CORNER / BYTE_COLOR)
palette: {shell: '#5A6470 Cold Steel', screen_kbd: '#1B2018 Panel Dark', touchpad: '#6E6A60 Concrete Grey'}
created: 2026-08-02
author: modeler-3d
verified_from: SM_Laptop.fbx (round-trip, лог logs/2026-08-02-build-props.log)
tags: [loot, quest, laptop, electronics, vcol, low-poly, mobile]
---

# Laptop (ноутбук)

Открытый на 110° ноутбук по ТЗ game-lead 2026-08-02: база 34×24×1.6 см с
утопленной панелью клавиатуры и тачпадом, крышка с тёмным экраном откинута
за вертикаль (петля по задней кромке −Y). Экран выключен (Panel Dark) —
лутовый/квестовый предмет, свечения нет.

Палитра GDD: корпус Cold Steel #5A6470, клавиатура и экран Panel Dark
#1B2018, тачпад Concrete Grey #6E6A60. Вершинные цвета, 1 материал, flat
shade. Крышка и экран строятся закрытыми и поворачиваются вокруг петли
матрицей — угол раскрытия правится одной константой OPEN_DEG в билдере.
