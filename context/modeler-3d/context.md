# context: modeler-3d

> Персональная память агента `modeler-3d`. Сюда агент дистиллирует решения, ограничения и текущее состояние (правило H). Новые сессии стартуют с этого файла.

## Решения
- **Blender = v5.1** (build blender-v5.1-release, exe `E:\Programs\Blender\5.1`). API экспорта FBX сверял с живым RNA оператора, не по памяти. FBX-формат на экспорте = 7400.
- **Материал бандита = `M_Bandit_Flat`** — один материал на все 3 слота. Principled BSDF, Base Color из vertex-color атрибута `Col` (нода ShaderNodeVertexColor, layer "Col"). Metallic 0, Roughness 0.65, Specular 0.15. Без normal-map, baked-friendly (плоские регионы цвета + rust-акцент).
- **Палитра (hex):** skin C9A084, jacket 2B2B2E, tee 6E6E70, joggers 303033, sneaker ECECEC, cap 28282B, rust C64B2C. Vertex-color в линейном пространстве, домен CORNER (BYTE_COLOR).
- **Подход к одежде:** новые части (кепка, оболочка бомбера, лампас) строятся как добавленная геометрия и ДЖОЙНЯТСЯ в исходный слот-меш → 1 скинённый меш на слот. Веса новых вершин переносятся с ближайшей исходной вершины (KDTree) → корректная деформация. Проверено позой — clipping/отрыва нет.

## Ограничения
- **Общий скелет `RootAnim` (ADR-018):** 21 кость, шарится со всеми гуманоидами. НЕ переименовывать кости, включая аномальную `Pelvis.009_R.002`.
- **Пайплайн экспорта (docx — источник истины):** копия blend1 → правка → Object mode: выделить меш + скелет → Export FBX → галка "limit to selected objects" (use_selection=True), снять "Bake Animation" (bake_anim=False). Имена осмысленные. UE-импорт против скелета HeadAndSkeletonFBX, import skeletal meshes, без Create Physics Asset.
- **Перед экспортом базового меша — сбросить позу в rest** (Pose mode → select all → Clear Transforms; удалить action). База в blend1 приходит в РАН-позе (action "ArmatureAction", frame 3) — это поза анимации, не bind. Одежду авторить на rest.
- **Сокет Blender одноклиентный** (localhost:9876) — не спавнить 2 modeler параллельно.
- **CLI background Blender НЕ настроен** (нет BLENDER_PATH) — `execute_blender_code_for_cli` не работает. Проверка round-trip FBX — реимпортом в живом инстансе в factory-startup сцену (read_homefile use_factory_startup=True), потом reopen рабочего .blend.
- Импорт FBX в сцену, где УЖЕ есть armature RootAnim → KeyError C_Root (коллизия имён арматур). Артефакт импорта, не дефект FBX. Проверять в чистой сцене.
- **Bash-шелл здесь без Python и капризен к PowerShell-кириллице.** Для распаковки docx/прочего Python использовать через Blender bpy (zipfile есть). find работает.

## Текущее состояние (2026-06-12)
- **Бандит-гопник готов и экспортирован.** Рабочая папка `E:\ForGameLead(Materials)\bandit-work\`.
  - `bandit_work.blend` — копия MasterHumanoidCharacterSeparatedMesh.blend1, rest-поза, action удалён.
  - `SK_Bandit_Head.fbx` (101 v, 156 tris) — голова skin + тёмная кепка-kepka.
  - `SK_Bandit_Torso.fbx` (202 v, 332 tris) — тёмный бомбер + серая футболка-воротник + rust-нашивка на левом плече + skin-кисти.
  - `SK_Bandit_Legs.fbx` (64 v, 102 tris) — тёмные спортивки + rust-лампас на левой ноге + белые кроссы.
  - **Суммарно 590 трисов** (бюджет был 1.5–2.5k, потолок 4k → большой запас).
  - Все 3 слота: 1 материал M_Bandit_Flat, vertex-color "Col", Armature-модификатор, чистые Smart-UV (0–1, без overlap), 21-костный RootAnim в каждом FBX. Round-trip реимпортом подтверждён.
- **Бэкап на Google Drive — НЕ делал** (нет конвенции/доступа в постановке; уточнить у game-lead).
- **Прежние SK_BanditTorsoArmor1/2/3.fbx** — старые эксперименты, не использовались.

## Раунд 3 (2026-06-12): диагностика «БАГ 2 ОРИЕНТАЦИЯ» — экспорт НЕ виноват
- Гипотеза баг-репорта (ось экспорта Blender→UE перевёрнута) НЕ подтвердилась. Сравнил мой `SK_Bandit_Torso.fbx` с эталоном `SK_BanditTorsoArmor3.fbx` (тот же пайплайн docx, импортится в UE верно), парсером `io_scene_fbx.parse_fbx`:
  - GlobalSettings ИДЕНТИЧНЫ: UpAxis=Y(1), FrontAxis=Z(2), CoordAxis=X(0), все знаки +1. FBX 7400.
  - Model-узлы ИДЕНТИЧНЫ: RootAnim(Null) Lcl Rot[-90,0,0] scale100; меш Lcl Rot[-90,0,0]; C_Root(LimbNode) Trans[0,-0.001,0.839] Rot[+90,0,0]. Это стандартная Blender Z-up→FBX Y-up конверсия — как у эталона.
  - Геометрия (bbox в Blender-local) совпадает по ориентации: torso Z[0.9,1.55], head Z[1.53,1.82], legs Z[0,0.9] — вертикальный гуманоид Z-up, ground=Z0.
- Round-trip: реимпорт моего FBX в factory-сцену (через temp_override с VIEW_3D-area, иначе mode_set падает «Context missing active object») → RootAnim rot[0,0,0] высота Z=1.569 вертикально; меш rot[0,0,0]; vertex-color «Col» (CORNER/BYTE_COLOR) + материал M_Bandit_Flat НА МЕСТЕ. Скрин — стоит вертикально, цвет виден.
- **⚠️ ДОПОЛНЕНО game-lead 2026-06-13 (конец дня) — НОВАЯ ЗАДАЧА РАУНД 5:** ориентация/ось действительно были НЕ виноваты (флип оказался размещением актора в UE). НО при нормальном свете (BugReport 6) вскрылась ДРУГАЯ проблема — **РЕГИОНЫ vertex-color в UE сдвинуты vs Blender:** низ ног (голени) БЕЛЫЙ выше щиколотки (в Blender тёмные джоггеры до щиколотки, белые только ступни-кроссы); оранжевая rust-зона оказалась на ПРАВОМ ПРЕДПЛЕЧЬЕ (в Blender — на плечах + полоса). Color-space (sRGB→linear) UE закрыл материалом Power(2.2) — торс стал правильно тёмным. Осталась именно ГЕОМЕТРИЯ ГРАНИЦ ЦВЕТА. Гипотеза: BYTE_COLOR домен CORNER → FBX → UE схлопывается в per-vertex/интерполируется → на low-poly без рёбер по границам зон цвет «расплывается»/сдвигается. **ЗАДАЧА завтра:** выбрать и сделать (а) разрез геометрии по границам цветовых зон, ЛИБО (б) **бейк vertex-color/зон в ТЕКСТУРУ** (UV уже чистые 0-1, модель готова под бейк — рекомендация game-lead, надёжнее на low-poly + снимает gamma), ЛИБО (в) проверить настройки экспорта/импорта color-атрибута. Прежний вывод «в Blender чинить нечего» относился ТОЛЬКО к ориентации — по ЦВЕТУ/ГРАНИЦАМ работа есть.
- ВЫВОД (про ОРИЕНТАЦИЮ): экспорт корректен и байт-в-байт по ориентации = рабочий пайплайн. Менять Forward/Up НЕЛЬЗЯ — сломает относительно меша игрока. Флип 180° и «нет текстур» — UE-сторона (трансформ компонента/сокета модульных мешей; vertex-color: import «Replace» + материал с VertexColor-нодой). FBX НЕ переэкспортировал (нечего чинить). Эскалировано game-lead → unreal/cpp.
