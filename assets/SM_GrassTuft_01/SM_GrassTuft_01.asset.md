---
id: SM_GrassTuft_01
name: Grass Tuft 01 (пучок травы, вариант 1)
status: preview
source_model: ForGameLead(Materials)/demo-assets/_build/_qc_grasstuft.blend
builder: ForGameLead(Materials)/demo-assets/_build/build_grasstuft.py
fbx: ForGameLead(Materials)/demo-assets/SM_GrassTuft_01.fbx
preview: SM_GrassTuft_01_preview_v1.png
material: M_GrassTuft     # общий материал на оба пучка (GrassTuft_01/02); в UE — Two-Sided
tris: 18
verts: 36
bbox_m: [0.358, 0.257, 0.324]
color_attr: Col (CORNER / BYTE_COLOR)
created: 2026-06-25
author: modeler-3d
engine: blender-eevee
verified_from: SM_GrassTuft_01.fbx
tags: [nature, foliage, grass, two-sided, vcol, low-poly, mobile]
---

# Grass Tuft 01 (пучок травы)

Пучок травы: V-сложенные лопасти веером, БЕЗ альфа-текстуры. Per-loop градиент
vcol снизу вверх: Moss #3F5A31 (база) → Sun Grass #5C7A3E (кончик) (GDD §2).
Самый дешёвый ассет серии (18 трис). Заменяет старый `SM_GrassTuft.fbx` (06-15).

⚠️ ВАЖНО для UE: материал ДОЛЖЕН быть Two-Sided — лопасти односторонние/открытые
(signed_volume ~0 ожидаемо, это не дефект). Без Two-Sided трава будет пропадать
с одной стороны.

Назначение: травяной покров демо-локации. Превью-ассет (vcol, без UV/бейка).
