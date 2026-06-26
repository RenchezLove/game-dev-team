---
id: clothesline
name: Clothesline (бельевая верёвка, низкополи)
status: preview
source_model: SM_Clothesline.blend
builder: ForGameLead(Materials)/demo-assets/_build/build_villageprops.py
fbx: SM_Clothesline.fbx
preview: clothesline_preview_v1.png
renders: [clothesline_pthreeq.png, clothesline_pfront.png, clothesline_side.png, clothesline_top.png, clothesline_bthreeq.png, clothesline_wire_pthreeq.png, clothesline_wire_top.png]
material: M_Clothesline
tris: 160
verts: 109
bbox_m: [2.569, 0.12, 1.8]
origin: centre between posts on ground (Z=0)
forward: +Y, up: +Z
color_attr: Col (CORNER / BYTE_COLOR)
two_sided: cloth items (single-layer planes) -> set material Two-Sided in UE
created: 2026-06-26
author: modeler-3d
engine: blender-eevee
verified_from: SM_Clothesline.fbx
tags: [village, prop, clothesline, cloth, wood, vcol, low-poly, mobile, stage-C]
---

# Clothesline (бельевая верёвка)

Бельевая верёвка для оживления двора (Этап C3, спек §3): 2 деревянных столба с косыми
подпорками у основания + провисающая (катенария ~13 см) джутовая верёвка + 3 висящие
вещи (простыня, рубаха, штаны) — драпированные плоскости с перегибом через верёвку и
лёгкой волной по низу, разной ширины для ритма. Низ вещей ≥ 0.78 м над землёй (не
касаются земли).

Габариты 2.569 × 0.12 × 1.8 м (пролёт между столбами ~2.5, высота 1.8). Origin — центр
между столбами на земле (Z=0). rot 0 / scale 1, нормали наружу (round-trip). 1 материал
vcol (M_Clothesline): столбы — Timber, верёвка — джут Dry Earth, вещи — выцветшие
Bone Ink / Faded Sage / Dry Earth (по одной на вещь).

ВАЖНО для UE: ткань — однослойные плоскости → материал **Two-Sided**. Превью-ассет
(vcol, без бейка). Импорт/коллизия — за game-lead/Ринатом.
