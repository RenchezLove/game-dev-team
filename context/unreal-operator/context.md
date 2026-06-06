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
