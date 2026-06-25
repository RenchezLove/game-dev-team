---
id: SM_Campfire
name: Camp Campfire (лагерный костёр)
status: preview
source_model: ForGameLead(Materials)/demo-assets/_build/_qc_campfire.blend
builder: ForGameLead(Materials)/demo-assets/_build/build_campfire.py
fbx: ForGameLead(Materials)/demo-assets/SM_Campfire.fbx
preview: SM_Campfire_preview_v1.png
material: M_Campfire
tris: 456
verts: 276
bbox_m: [1.076, 1.05, 0.516]
color_attr: Col (CORNER / BYTE_COLOR)
created: 2026-06-25
author: modeler-3d
engine: blender-eevee
verified_from: SM_Campfire.fbx
tags: [prop, campfire, camp, hearth, vcol, low-poly, faceted, mobile]
---

# Camp Campfire (лагерный костёр)

Низкополи фасеточный лагерный костёр (референс `Screenshots/6/1.png`): поленья
шалашиком (6 брёвен конусом, основания на земле, вершины сходятся вверху, верхние
концы ОБУГЛЕННЫЕ почти-чёрные), кольцо из 10 гранёных низкополи камней-очага
(серые с per-камень вариацией тона + шейдинг по нормали грани), в центре плоская
тёмная кучка золы/углей с парой тёплых угольков. БЕЗ пламени и дыма — огонь это
VFX в движке.

Точка привязки VFX-огня: маркер `FireVFX_Socket` в центре основания (0, 0, ~0.12).
Empty НЕ экспортируется в MESH-only FBX — координаты переданы game-lead для сокета
на меше в UE.

Origin/pivot — центр основания (на земле, Z0). Масштаб метры (UE 100x). Нормали
наружу (signed_vol +0.103). 1 vcol-материал, цвет в UE = VertexColor('Col')→BaseColor,
импорт «Vertex Color = Replace». Бюджет ~800-1500 трис → 456 (запас для слабого
Android). Превью-ассет (vcol, без UV-бейка).

NB: уже существуют `SM_CampfireLogs` (деревня, save-point, 260т) и `SM_BanditCampfire`
(база бандитов, 248т). Этот `SM_Campfire` — отдельный обобщённый лагерный костёр по
референсу 1.png; выбор применения за game-lead.
