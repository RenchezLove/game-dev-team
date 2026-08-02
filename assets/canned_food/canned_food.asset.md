---
id: canned_food
name: Canned Food (консервы, тушёнка)
status: preview
builder: 10_build_canned_food.py
source_model: canned_food.blend
fbx: SM_CannedFood.fbx
preview: ../icons/512/canned_food.png
material: M_CannedFood
tris: 96
verts: 50
bbox_m: [0.075, 0.075, 0.108]
origin: ось цилиндра, Z=0 (дно)
forward: +Y (красная нашивка этикетки)
color_attr: Col (CORNER / BYTE_COLOR)
palette: {metal: '#6E6A60 Concrete Grey', label: '#E7E4D8 Bone Ink', patch: '#8A2F2A Muted Blood'}
created: 2026-08-02
author: modeler-3d
verified_from: SM_CannedFood.fbx (round-trip, лог logs/2026-08-02-build-props.log)
tags: [loot, food, can, vcol, low-poly, mobile]
---

# Canned Food (банка тушёнки)

Жестяная банка по ТЗ game-lead 2026-08-02: 12-гранный цилиндр D 7.5 см,
высота 10.8 см. Металлические крышки и узкие ободы сверху/снизу (Concrete
Grey), бумажная этикетка-полоса (Bone Ink) с узкой тёмно-красной нашивкой
(Muted Blood, 2 грани-колонки к +Y) — намёк на картинку этикетки.

На стенде иконок банка повёрнута на −45° (ручка подачи в реестре ITEMS),
чтобы нашивка смотрела в камеру; сам ассет ориентирован нашивкой по +Y.
Вершинные цвета, 1 материал, flat shade.
