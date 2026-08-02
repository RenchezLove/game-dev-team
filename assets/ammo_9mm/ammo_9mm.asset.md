---
id: ammo_9mm
name: Ammo 9mm (коробка патронов 9×19 + 3 патрона)
status: preview
builder: 10_build_ammo_9mm.py
source_model: ammo_9mm.blend
fbx: SM_Ammo9mm.fbx
preview: ../icons/512/ammo_9mm.png
material: M_Ammo9mm
tris: 216
verts: 118
bbox_m: [0.061, 0.086, 0.032]
origin: bbox center, Z=0 (основание)
forward: +Y (патроны лежат перед коробкой)
color_attr: Col (CORNER / BYTE_COLOR)
palette: {box: '#7D6A4E Dry Earth', stripe: '#C64B2C Rust Alarm', brass: '#CAA54E XP Gold', tip: '#8A5A32 Timber'}
created: 2026-08-02
author: modeler-3d
verified_from: SM_Ammo9mm.fbx (round-trip, лог logs/2026-08-02-build-props.log)
tags: [loot, ammo, 9mm, vcol, low-poly, mobile]
---

# Ammo 9mm (патроны)

Картонная коробка патронов (50 шт., 5.8×4.3×3.2 см) с красной печатной
полосой вокруг боков + три патрона 9×19 в реальный размер (30 мм, 8 граней),
лежат перед коробкой бок о бок с шагом 12 мм и лёгкими разворотами.

Палитра GDD: картон Dry Earth #7D6A4E, полоса Rust Alarm #C64B2C, латунные
гильзы XP Gold #CAA54E, пули Timber #8A5A32. Вершинные цвета, 1 материал.
Урок сборки: патроны с осью X раскладывать по Y — первая версия разложила их
по X (вдоль собственной оси), и они слились в «змейку» на рендере.
