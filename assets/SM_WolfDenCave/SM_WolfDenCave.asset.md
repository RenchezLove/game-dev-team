---
id: SM_WolfDenCave
name: Wolf Den Cave (логово волков — скальное устье)
status: preview
source_model: ForGameLead(Materials)/demo-assets/_build/_qc_wolfden.blend
builder: ForGameLead(Materials)/demo-assets/_build/build_wolfden.py
fbx: ForGameLead(Materials)/demo-assets/SM_WolfDenCave.fbx
preview: SM_WolfDenCave_preview_v1.png
material: M_WolfDenCave
tris: 208
verts: 128
bbox_m: [4.331, 3.068, 3.617]
color_attr: Col (CORNER / BYTE_COLOR)
created: 2026-06-24
author: modeler-3d
engine: blender-eevee
verified_from: SM_WolfDenCave.fbx
tags: [enemy-base, wolf-den, cave, rock, vcol, low-poly, mobile]
---

# Wolf Den Cave (логово волков)

Скальное устье-логово (север демо-локации, спек `enemy-locations-spec.draft.md` §1).
Форма скалы концептом не задана → минимальный честный силуэт: рамка устья из
наклонённых off-axis блоков + тело из гранёных icosphere-валунов. Покраска ПО
НОРМАЛИ грани (верх → Faded Sage свет, средние → Concrete, низ/тень → Cold Steel),
тёмное устье Pine Shade — фасеты читаются как холодный камень с мхом. Земля-проплешина
у входа — это материал/декаль грунта (этап C2), не в меше.

Назначение: точка спавна базы волков (BP_WolfDen). Превью-ассет (vcol, без UV/бейка).

> NB: реальный тон темнее hex-борда (пайплайн dcommon, double-darken vcol) — известно,
> для каменного материала приемлемо (камень тёмный по задумке).
