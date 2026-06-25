---
id: iron_barrel
name: Iron Barrel (железная бочка)
status: preview            # нет UV / LOD / бейка текстур / экспорта в UE
source_model: iron_barrel_v1.blend
preview: iron_barrel_preview_v1.png
material: M_IronBarrel_Aged
faces: 4162                # полигоны evaluated-меша (Bevel-модификатор применён)
faces_base: 3906          # полигоны базового меша, до модификаторов
tris: 8444                # треугольники после триангуляции evaluated-меша (для движка)
bbox_m: [0.646, 0.646, 0.88]   # X, Y, Z в метрах (корпус Ø0.60; ободы/рёбра выступают)
created: 2026-06-19
author: modeler-3d
engine: blender-cycles
verified_from: iron_barrel_v1.blend   # все числа перепроверены из .blend, не по памяти
todo: reduce_polycount   # tris=8444 слишком много (Ринат, 2026-06-19); при game-ready — низкополи база + нормал-мап на ободы/рёбра. Бюджет согласовать по GDD-камере. См. ADR-022 / бэклог game-lead.
---

# Iron Barrel (железная бочка)

Классическая стальная бочка-«нефтянка» (стандарт 200 л): корпус Ø0.60 м, высота 0.88 м,
2 закатанных обода (верх/низ) и 3 опоясывающих ребра жёсткости. Стиль — survival,
состаренная сталь с пятнами ржавчины (процедурный материал `M_IronBarrel_Aged`).

Назначение: демо-проп для превью-каталога. Это превью-ассет — без UV-развёртки, LOD,
запечённых текстур и экспорта в UE; полибюджет под Android не утверждён.
