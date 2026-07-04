---
id: tent
name: Tent (потрёпанная туристическая палатка-домик)
status: preview             # плейсхолдер-уровень для мобильного теста (Этап D8)
source_model: _qc_tent.blend
builder: E:/ForGameLead(Materials)/demo-assets/_build/build_tent.py
fbx: E:/ForGameLead(Materials)/demo-assets/SM_Tent.fbx
preview: tent_preview_v1.png
material: M_Tent (vcol -> BaseColor; Two-Sided в UE — клапан и торцы однослойные)
tris: 116                   # бюджет <=200 OK
verts: 87
bbox_m: [1.56, 2.868, 1.223]   # Y с растяжками/колышками; сам домик 1.5 x 2.0 x 1.2
color_attr: Col (CORNER / BYTE_COLOR)
forward: +Y (вход) в Blender-сборке; ПОСЛЕ FBX-импорта в UE ось Y зеркалится => вход в UE = -Y. up +Z, origin центр домика на земле (Z=0)
created: 2026-07-04
author: modeler-3d
verified_from: round-trip импорт SM_Tent.fbx (verify_car.py) — rot0/scale1, нормали наружу (signed_volume +1.56)
---

# Tent — потрёпанная палатка (точка интереса на маршрутах, Этап D8)

Классическая двускатная тур-палатка (A-frame): выцветший тёмно-зелёный брезент
с выгоревшим верхом и грязным низом, провисшая ткань со вмятинами, конёк-жердь,
две растяжки с колышками, две заплатки разного тона, тёмный вход с приоткрытым
клапаном (+Y). Пол — тёмная подложка (меш замкнут снизу).

Допущение: «потрёпанность» передана провисом/заплатками/клапаном и выцветанием,
без рваных дыр (бюджет и читаемость top-down).
