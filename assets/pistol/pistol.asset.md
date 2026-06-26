---
id: pistol
name: Pistol (пистолет полуавтоматический, низкополи)
status: preview
source_model: SM_Pistol.blend
builder: ForGameLead(Materials)/demo-assets/_build/build_weapons.py
fbx: SM_Pistol.fbx
preview: pistol_preview_v1.png
renders: [pistol_front.png, pistol_side.png, pistol_threeq.png, pistol_top.png, pistol_wire_threeq.png, pistol_wire_top.png]
material: M_Pistol
tris: 132
verts: 88
bbox_m: [0.199, 0.028, 0.137]
origin: grip (hold point) at (0,0,0)
forward: +X (muzzle), up: +Z, depth: Y
color_attr: Col (CORNER / BYTE_COLOR)
created: 2026-06-26
author: modeler-3d
engine: blender-eevee
verified_from: SM_Pistol.fbx
tags: [weapon, pistol, firearm, metal, vcol, low-poly, mobile, stage-D]
---

# Pistol (пистолет полуавтоматический)

Низкополи модель полуавтоматического пистолета для Этапа D (оружие). Силуэт по
референсу `context/concept-artist/tmp/hud-icons/pistol.png`: длинный затвор-ствол
сверху, рукоять с наклоном назад-вниз, спусковая скоба с крючком, мушка/целик.

Габариты: длина 0.199 м (X), высота 0.137 м (Z), толщина 0.028 м (Y). Ориентация по
контракту ассета: ствол смотрит по +X (forward), верх по +Z. Origin (пивот) — в РУКОЯТИ
(точка хвата), в (0,0,0) — под крепление в сокет руки. Все трансформы применены
(rot 0, scale 1), нормали наружу (signed volume +, проверено round-trip реимпортом FBX).

Материалы — vertex-color (1 материал M_Pistol, нода VertexColor 'Col' → BaseColor):
затвор/ствол — воронёная сталь сине-серая; рукоять — коричневая; рама/скоба/крючок —
тёмный воронёный металл; мушка/целик — почти чёрные. Камера в игре изометрическая,
оружие на экране мелкое → детали минимальны, важен читаемый силуэт.

Назначение: оружие игрока (демо). Превью-ассет: vcol, без бейка текстур; UE-импорт
(ориентация/сокет в руке) согласуется при интеграции — за game-lead. NB: в
demo-assets/ лежит старый `SM_Pistol.fbx` (прежний прототип) — каноничный экспорт
теперь ЗДЕСЬ (assets/pistol/SM_Pistol.fbx).
