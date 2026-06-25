---
id: SM_GrassTuft_02
name: Grass Tuft 02 (пучок травы, вариант 2)
status: preview
source_model: ForGameLead(Materials)/demo-assets/_build/_qc_grasstuft.blend
builder: ForGameLead(Materials)/demo-assets/_build/build_grasstuft.py
fbx: ForGameLead(Materials)/demo-assets/SM_GrassTuft_02.fbx
preview: SM_GrassTuft_02_preview_v1.png
material: M_GrassTuft     # общий материал на оба пучка (GrassTuft_01/02); в UE — Two-Sided
tris: 26
verts: 52
bbox_m: [0.407, 0.384, 0.297]
color_attr: Col (CORNER / BYTE_COLOR)
created: 2026-06-25
author: modeler-3d
engine: blender-eevee
verified_from: SM_GrassTuft_02.fbx
tags: [nature, foliage, grass, two-sided, vcol, low-poly, mobile]
---

# Grass Tuft 02 (пучок травы)

Пучок травы, вариант 2: больше лопастей (26 трис), шире веер. Тот же per-loop
градиент Moss #3F5A31 → Sun Grass #5C7A3E. Два варианта дают разнообразие покрова.

⚠️ ВАЖНО для UE: материал ДОЛЖЕН быть Two-Sided (односторонние лопасти), как у
`SM_GrassTuft_01`.

Назначение: травяной покров демо-локации. Превью-ассет (vcol, без UV/бейка).
