---
id: SM_Bush_01
name: Bush 01 (куст, вариант 1)
status: preview
source_model: ForGameLead(Materials)/demo-assets/_build/_qc_vegetation.blend
builder: ForGameLead(Materials)/demo-assets/_build/build_vegetation.py
fbx: ForGameLead(Materials)/demo-assets/SM_Bush_01.fbx
preview: SM_Bush_01_preview_v1.png
material: M_Bush          # общий материал на оба куста (Bush_01/02)
tris: 60
verts: 36
bbox_m: [1.04, 0.716, 0.6]
color_attr: Col (CORNER / BYTE_COLOR)
created: 2026-06-25
author: modeler-3d
engine: blender-eevee
verified_from: SM_Bush_01.fbx
tags: [nature, foliage, bush, vcol, low-poly, mobile]
---

# Bush 01 (куст)

Низкополи куст: icosphere-клампы (комки листвы) тёмно-зелёного тона. Меньший из
двух вариантов. Назначение: озеленение демо-локации. Превью-ассет (vcol, без UV/бейка).

> NB про тон: зелень тёмная — это и double-darken пайплайна dcommon, и сама тёмная
> палитра листвы. При импорте в UE листва-вариант может потребовать Two-Sided
> (тонкие/открытые грани), как у травы.
