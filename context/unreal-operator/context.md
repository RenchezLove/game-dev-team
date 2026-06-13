# context: unreal-operator

> Персональная память агента `unreal-operator`. Сюда агент дистиллирует решения, ограничения и текущее состояние (правило H). Новые сессии стартуют с этого файла.

## Решения
- **Инструмент: MCP-сервер `@runreal/unreal-mcp`** (UE Python / Remote Execution под капотом). Полностью — [ADR-003](../../docs/decisions.md). Только `unreal-operator` видит `mcp__unreal__*`.
- Скриншоты сцены: рецепт через `HighResShot` с окном UE в фокусе (см. ниже).

## Состояние MCP (провалидирован 2026-06-06)
Сервер `unreal` поднимается, **20 тулзов `mcp__unreal__*`** доступны. Смоук-тест пройден (project info / outliner / screenshot / create+delete) и подтверждён артефактами.
- Проект: **ContrarySurvivor**, путь `E:/ContrarySurvior/ContrarySurvivor/`.
- Движок: **UE 5.5.4** (`5.5.4-40574608+++UE5+Release-5.5`). **GAS + Enhanced Input** включены. ~7233 ассета. Карта `/Game/L_MainLevel`.

### 20 тулзов — краткое назначение
1. `editor_project_info()` — метаданные проекта, счётчики ассетов.
2. `editor_get_world_outliner()` — актёры мира с трансформами/компонентами.
3. `editor_get_map_info()` — инфо текущего уровня (счётчики типов, свет).
4. `editor_take_screenshot()` — скрин редактора (рендерит ок, НО пишет в эфемерный tmp — см. квирки).
5. `editor_create_object(object_class*, object_name*, location?, rotation?, scale?, properties?)` — создать актёра. Для StaticMeshActor меш в `properties.StaticMesh`.
6. `editor_update_object(actor_name*, new_name?, location?, rotation?, scale?, properties?)` — обновить актёра.
7. `editor_delete_object(actor_names*)` — удалить (по label работает надёжно).
8. `editor_run_python(code*)` — Python в редакторе (нужен `import unreal`).
9. `editor_console_command(command*)` — консольная команда (без вывода).
10. `editor_list_assets()` — список путей ассетов.
11. `editor_search_assets(search_term*, asset_class?)` — поиск ассетов (лимит 50).
12. `editor_get_asset_info(asset_path*)` — инфо ассета, LOD для мешей.
13. `editor_get_asset_references(asset_path*)` — рефы ассета.
14. `editor_export_asset(asset_path*)` — экспорт ассета (бинарь).
15. `editor_validate_assets(asset_paths?)` — валидация ассетов.
16. `editor_move_camera(location*, rotation*)` — камера вьюпорта.
17. `get_unreal_engine_path()` — путь движка.
18. `get_unreal_project_path()` — путь проекта (в обёртке = «not set», см. квирки).
19. `set_unreal_engine_path(path*)` — задать путь движка.
20. `set_unreal_project_path(path*)` — задать путь проекта.

## Ограничения / квирки (проверено живыми вызовами)
- **Предусловия запуска:** (а) **Multicast Bind Address = `0.0.0.0`** в Python Remote Execution (loopback не сходится с multicast от node); (б) **редактор UE открыт и полностью загружен ДО старта `claude`** — иначе сервер `exit → ✗ Failed to connect` и тулы не грузятся; (в) запуск сервера — абсолютный `node.exe` + абсолютный `dist/bin.js` (резолв `npx` в неинтерактивной оболочке не работает).
- **Скриншоты — рабочий рецепт:** окно UE **в фокусе** → `editor_console_command HighResShot <WxH>` → файл в `<ProjectDir>/Saved/Screenshots/WindowsEditor/`. Без фокуса high-res пайплайн не тикает (`is_task_done()` висит, файла нет). После команды поллить папку на новый PNG с size>0.
- **НЕ для артефактов:** `editor_take_screenshot` → эфемерный tmp (harness удаляет до след. вызова). SceneCapture2D из Python → неосвещённый/чёрный кадр.
- **`get_unreal_project_path()` = «not set»** → путь брать из `editor_project_info`/`unreal.Paths` (или разово `set_unreal_project_path`).
- **`editor_get_world_outliner` отдаёт внутренние имена, не labels** → резолвить label через Python; удалять/искать по label.

## Текущее состояние
MCP-проводка завершена и провалидирована. Сцена `L_MainLevel`: 5 актёров (BP_PlayerCharacter, DirectionalLight, PlayerStart, 2× StaticMeshActor — пол + куб). Следующие задачи по сценам/ассетам/сборке — по постановке от `game-lead`.

## Headless переимпорт волка (2026-06-13, Фаза 3) — коммит 5c6eb14 (feature/phase3-combat)
- Путь: `UnrealEditor-Cmd.exe <uproject> -ExecutePythonScript=<abs.py> -unattended -nopause -nosplash` (ADR-021), редактор закрыт, stdout пуст → пруфы из `Saved/Logs/ContrarySurvivor.log` по префиксу-маркеру.
- Движок: `E:/UnrealEngine/UE_5.5/Engine/Binaries/Win64/UnrealEditor-Cmd.exe`. Проект-репо = **отдельный git** в `E:/ContrarySurvior/ContrarySurvivor` (НЕ game-dev-team), uasset под git-LFS.
- Переимпорт overwrite: `AssetImportTask(replace_existing=True, automated, save)`; skeletal — `skeleton=existing SK_Wolf_Skeleton` + `skeletal_mesh_import_data.update_skeleton_reference_pose=True` (обновляет ref-позу из FBX, скелет НЕ плодится). Пруфы: `SkeletalMesh.has_vertex_colors()` (метод, НЕ property — property `has_vertex_colors` отсутствует на SkeletalMesh в 5.5), anim `skeleton` path, `number_of_sampled_frames`.
- **Квирк материала skeletal:** assign-back `mats[0].set_editor_property('material_interface',m); sk.set_editor_property('materials',mats)` для SkeletalMesh НЕ персистится (re-fetch показал WorldGridMaterial). Рабочий путь: собрать НОВЫЙ `unreal.SkeletalMaterial()` (с сохранением `material_slot_name`), `sk.set_editor_property('materials',[new_slot,...])`, save, проверять по `unreal.load_asset` заново. Слот волка зовётся `M_Wolf` → slot0 = `/Game/Materials/M_VColor`.
- Скрипты: `E:/game-dev-team/logs/phase3-py/reimport_wolf.py`, `.../fix_wolf_material.py`.

## Повторный переимпорт волка (2026-06-13 13:37, Фаза 3) — коммит 1a9aba1 (feature/phase3-combat)
- Обновлённые FBX (modeler перезаписал 13:33: фикс скиннинга + откат вредного 180°). Единый скрипт `.../reimport_wolf_v2.py` (reimport SK+3 anim + материал рабочим паттерном SkeletalMaterial + re-load verify), лог `.../reimport_wolf_v2.log` (через `-abslog`).
- Пруфы (лог, маркер `WOLFREIMPORT2:`): `has_vertex_colors()`=True (метод); anim Idle/Run/Bite → SK_Wolf_Skeleton, frames 47/15/19; RELOAD slot0 name=M_Wolf material_interface=/Game/Materials/M_VColor. 0 `Error:`, FBX-ошибок нет.
- На этот раз slot0 «before» уже был M_VColor (import_materials=False сохранил), но переназначение/верификация выполнены штатно. Обновился и `SK_Wolf_Skeleton.uasset` (из-за update_skeleton_reference_pose=True) — это ожидаемо, закоммичен вместе с остальными 4.
- Квирк лога: в unattended source-control (Plastic) кидает диалоги «Unable to Check Out From Revision Control» — авто-закрываются (Ok), на сохранение в .uasset не влияют.

## Headless импорт брони (2026-06-13, Фаза 4) — коммит d83bfd3 (feature/phase4-inventory)
- 5 SK брони (`SK_Armor_Head_01/02`, `SK_Armor_Torso_01/02`, `SK_Armor_Legs_01`) из `E:/ForGameLead(Materials)/phase4-assets/` → `/Game/Characters/Armor/`. Скрипт `E:/game-dev-team/logs/phase4-py/import_armor.py`, лог `import_armor.log`, маркер `ARMORIMPORT:`.
- **ОБЩИЙ скелет** — НЕ задавал по памяти: скрипт грузит `SK_Bandit_Head`, берёт его `skeleton` и импортит против него. Оказался `/Game/TestContentAndCode/PreProduction/HeadAndSkeletonfbx_Head_Skeleton` (27 костей). Новый скелет НЕ создан — VERIFY SAME_AS_SHARED=True у всех 5.
- Опции: REPLACE vertex color, create_physics_asset=False, import_materials=False, `update_skeleton_reference_pose=False` (броня НЕ должна менять ref-позу общего скелета — отличие от волка). has_vertex_colors()=True у всех. 0 `Error:`, 0 skeleton-mismatch warnings.
- Материал slot0: рабочий паттерн SkeletalMaterial (rebuild, keep slot_name). slot0 «before» назывался `M_Armor_Flat`, после → `/Game/Materials/M_VColor`, подтверждено RELOAD.
- merge/push НЕ делал.

## Переимпорт переделанной брони (2026-06-13 ~16:0x, Фаза 4) — коммит 87eacc0 (feature/phase4-inventory)
- modeler перезаписал FBX 15:58: меши = тело ГГ + броня объединённые (раньше броня-only → парила). Переимпорт overwrite ТОЛЬКО `_01` (`SK_Armor_Head_01/Torso_01/Legs_01`). Head_02/Torso_02 НЕ трогал.
- Скрипт `E:/game-dev-team/logs/phase4-py/reimport_armor_body.py`, лог `reimport_armor_body.log`, маркер `ARMORREIMPORT:`. Тот же паттерн что import_armor.py: общий скелет берётся из `SK_Bandit_Head.skeleton` (НЕ по памяти), `replace_existing=True`, VColor REPLACE, create_physics_asset=False, `update_skeleton_reference_pose=False`, материал slot0 рабочим паттерном rebuild SkeletalMaterial.
- Пруфы (лог): все 3 SAME_AS_SHARED=True (`/Game/TestContentAndCode/PreProduction/HeadAndSkeletonfbx_Head_Skeleton`, 27 костей, новый скелет НЕ создан), has_vertex_colors()=True, slot0=/Game/Materials/M_VColor (before=M_Armor_Flat). 0 `Error:`, 0 mismatch.
- **Квирк:** `EditorAssetLibrary.save_directory(only_if_is_dirty=False, recursive=True)` ре-сериализует ВСЕ ассеты папки → Head_02/Torso_02 пометились modified хотя их не импортил. Откатил их `git checkout -- ...` перед коммитом, чтобы «не трогать». На будущее: для точечного коммита либо save только нужных ассетов, либо ревертить лишние.
- Закоммичены 3 `_01.uasset` (LFS pointers обновлены: Head oid 77a1542d, Legs b707f512, Torso baeab9ab). merge/push НЕ делал.

## БЛОКЕР сессии 2026-06-12 (Фаза 1, раунд правок бандита)
- **Симптом:** `mcp__unreal__*` тулы НЕ инжектятся в эту спавн-сессию (`mcp__unreal__editor_run_python` и `..._project_info` → "No such tool available"). При этом `claude mcp list` → `unreal: ✔ Connected`, агент-дефиниция содержит `mcpServers: [unreal]`. Редактор жив: `UnrealEditor.exe` PID 6804, ~1.6 ГБ, лог пишется (22:18), PythonScriptPlugin смонтирован, UDP multicast bridge `0.0.0.0→230.0.0.1:6666` поднят. → Это **дыра инжекта тулов в сессию**, не мёртвый редактор. Python на машине нет (только Store-заглушка) → сырой Remote-Exec клиент в обход MCP не написать без изобретения обхода.
- **Следствие:** live-интроспекция BP (SkeletalMesh/AnimClass/leader_pose/трансформы), импорт vertex-color, ориентация ассета, создание/назначение материала, автоскрин — НЕ выполнимы в этой сессии. Вернул `game-lead`: перезапустить `claude`/сессию `unreal-operator` так, чтобы тулы `mcp__unreal__*` подхватились.
- **Что выяснено из C++ (ФС-факт, не требует редактора):** риг модульных мешей собирается в `AMasterHumanoidCharacter` (ctor): `HeadMesh=GetMesh()`, `TorsoMesh`/`LegsMesh`=`CreateDefaultSubobject` + `SetupAttachment(HeadMesh)`. **НЕТ** в C++ ни `SetLeaderPoseComponent`/`SetMasterPose`, ни `SetSkeletalMesh`, ни `SetAnimInstanceClass`, ни relative-transform мешей (единственный `SetRelativeRotation` — на SpringArm камеры в `PlayerCharacter.cpp`). EnemyCharacter наследует базу «как есть» (ADR-018), доп. рига нет. → Значит SkeletalMesh/AnimClass/LeaderPose/трансформы игрока заданы **в дефолтах BP_PlayerCharacter.uasset** (бинарь, нужна Python-интроспекция). Бандиту воспроизводить ту же конфигурацию в BP_EnemyBandit.
