---
id: SM_VillageHouse
name: Village House (деревенская изба)
status: preview            # vcol-low-poly, экспортирован в UE; без UV-бейка/LOD
source_model: ForGameLead(Materials)/demo-assets/_build/_qc_house.blend
builder: ForGameLead(Materials)/demo-assets/_build/build_house.py + recolor_house_roof.py
fbx: ForGameLead(Materials)/demo-assets/SM_VillageHouse.fbx
preview: SM_VillageHouse_preview_v1.png
material: M_VillageHouse
tris: 820                  # треугольники экспортированного FBX
verts: 548
bbox_m: [5.562, 4.72, 4.23]    # X, Y, Z в метрах
color_attr: Col (CORNER / BYTE_COLOR)   # один цвет-атрибут, без UV-текстур
created: 2026-06-24
updated: 2026-06-25        # B2: крыша перекрашена в светлый холодный
author: modeler-3d
engine: blender-eevee
verified_from: SM_VillageHouse.fbx   # tris/bbox/материал сняты из экспортированного FBX, не по памяти
tags: [building, village, izba, gable-roof, vcol, low-poly, mobile]
---

# Village House (деревенская изба)

Низкополи русская изба под top-down камеру: горизонтальные брёвна-срубы (стопка
банд-боксов с тёмными пазами-чинкингом), двускатная крыша с коньком вдоль Y и
фронтонами на торцах ±Y, каменный фундамент/ступень, каменная труба, окна с
наличниками, дверь с рамой. Стены-щели закрыты сплошной внутренней подложкой
(не просвечивают). Стиль — выветренное дерево по борду дома, ориентир —
референс `art/village.png`.

Крыша (B2, 2026-06-25): скаты перекрашены в СВЕТЛЫЙ холодный серо-зелёный
(#9AA08C Faded Sage доминанта, теневой скат #828A78), конёк/труба Cold Steel —
чтобы крыша читалась сверху и не сливалась с тёплой землёй/дорогой. Стены —
тёплое коричневое дерево. Геометрия при ре-тинте не менялась.

Назначение: основное здание демо-деревни (на уровне 6 экземпляров). Превью-ассет:
purely vertex-color, без UV-развёртки и запечённых текстур.

> **NB про тон (vcol):** реальный цвет на меше темнее hex-борда из-за пайплайна
> dcommon (слой 'Col' создаётся float-linear, хранится BYTE_COLOR → значение
> читается как уже-sRGB и затемняется дважды). Для крыши тон выставлен точно
> записью sRGB напрямую в BYTE_COLOR (`recolor_house_roof.py`). У остальных
> ассетов серии тон номинально темнее заявленного hex — это известно и
> ожидаемо, см. сайдкары других ассетов.
