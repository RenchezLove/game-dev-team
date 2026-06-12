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
