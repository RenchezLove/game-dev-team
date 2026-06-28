---
id: awning
name: Market Awning (тент-навес частичный, низкополи)
status: preview
source_model: SM_Awning.blend
builder: ForGameLead(Materials)/demo-assets/_build/build_villageprops.py
fbx: SM_Awning.fbx
preview: awning_preview_v1.png
renders: [awning_pthreeq.png, awning_pfront.png, awning_side.png, awning_top.png, awning_bthreeq.png, awning_wire_pthreeq.png, awning_wire_top.png]
material: M_Awning
tris: 120
verts: 83
bbox_m: [2.2, 1.37, 2.435]
origin: base centre on ground (Z=0)
forward: +Y (open low side), up: +Z
color_attr: Col (CORNER / BYTE_COLOR)
two_sided: tarp (single-layer plane) -> set material Two-Sided in UE
created: 2026-06-26
revised: 2026-06-28
author: modeler-3d
engine: blender-eevee
verified_from: SM_Awning.fbx
tags: [village, prop, awning, tarp, cloth, wood, vcol, low-poly, mobile, stage-C]
---

# Market Awning (тент-навес частичный)

Частичный навес-лин-ту (Этап C3, спек `docs/contrary-survivor/props-village-spec.draft.md` §1):
4 деревянные жерди + 2 верхние перекладины + натянутый брезент со скатом (задняя
кромка выше, передняя ниже) и лёгким провисанием/обвисшими краями. Открытая сторона —
по +Y (forward), чтобы под навес вставал прилавок/торговец и был виден сверху.

Удешевлено 2026-06-28: жерди и перекладины переведены с круглого (6-гранного)
профиля на КВАДРАТНЫЙ 4-гранный (квадратный брус) — дешевле по трисам (168 → 120).

Габариты 2.2 × 1.37 × 2.43 м (Ш×Г×В; задняя кромка 2.43, передняя ~2.03). Origin —
центр основания на земле (Z=0). rot 0 / scale 1, нормали наружу (проверено round-trip).
1 материал vcol (M_Awning, нода VertexColor 'Col' → BaseColor): жерди — дерево Timber,
брезент — выцветший Faded Sage с полосой-акцентом Dry Earth и парой грязевых пятен.

ВАЖНО для UE: брезент — однослойная плоскость → материал поставить **Two-Sided**
(видно с изнанки), иначе сверху/снизу пропадёт. Превью-ассет (vcol, без бейка);
импорт/коллизия/расстановка — за game-lead/Ринатом.
