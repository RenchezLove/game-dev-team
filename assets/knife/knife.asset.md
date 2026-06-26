---
id: knife
name: Knife (нож боевой, низкополи)
status: preview
source_model: SM_Knife.blend
builder: ForGameLead(Materials)/demo-assets/_build/build_weapons.py
fbx: SM_Knife.fbx
preview: knife_preview_v1.png
renders: [knife_front.png, knife_side.png, knife_threeq.png, knife_top.png, knife_wire_threeq.png, knife_wire_top.png]
material: M_Knife
tris: 80
verts: 48
bbox_m: [0.278, 0.028, 0.036]
origin: grip (hold point) at (0,0,0)
forward: +X (blade tip), up: +Z, depth: Y
color_attr: Col (CORNER / BYTE_COLOR)
created: 2026-06-26
author: modeler-3d
engine: blender-eevee
verified_from: SM_Knife.fbx
tags: [weapon, knife, melee, blade, steel, vcol, low-poly, mobile, stage-D]
---

# Knife (нож боевой)

Низкополи модель ножа для Этапа D (оружие). Силуэт по референсу
`context/concept-artist/tmp/hud-icons/knife.png`: стальной клинок с остриём,
небольшая гарда, цилиндрическая коричневая рукоять с навершием-упором.

Габариты: длина 0.278 м (X), высота 0.036 м (Z), ширина по гарде 0.028 м (Y).
Ориентация по контракту ассета: клинок смотрит по +X (forward), верх по +Z. Origin
(пивот) — в РУКОЯТИ (точка хвата, центр рукояти), в (0,0,0) — под крепление в сокет
руки. Все трансформы применены (rot 0, scale 1), нормали наружу (signed volume +,
проверено round-trip реимпортом FBX).

Материалы — vertex-color (1 материал M_Knife, нода VertexColor 'Col' → BaseColor):
клинок — светло-серая сталь; гарда — тёмный металл; рукоять и навершие — коричневые.
Клинок — плоская плита толщиной ~5 мм (X-Z профиль), читается как нож в силуэте под
изометрией. Деталей минимум — оружие на экране мелкое.

Назначение: оружие ближнего боя игрока (демо). Превью-ассет: vcol, без бейка текстур;
UE-импорт (ориентация/сокет в руке) согласуется при интеграции — за game-lead.
