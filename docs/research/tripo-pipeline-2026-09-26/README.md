# Исследование 26.09.2026: конвейер Tripo → Blender → UE 5.5

Сырые скачанные страницы: `tripo/`, `unreal/`, `tools/` (только текст; html/js удалены ради размера). Решение — ADR-092 в `docs/decisions.md`.

## Tripo (developers.tripo3d.ai, API v3, `https://openapi.tripo3d.ai/v3`)
- Серия P: «Optimized for low-poly output with clean topology». Лимит граней P1 50–20 000; P2 (preview) — с четырёхугольниками. Отдельного параметра стиля нет — стиль задаётся текстом запроса.
- Цена: 1 кредит = $0.01; серия P 30–50 кредитов за модель; риг 25, анимация 10; неудачные задачи не оплачиваются.
- Права (terms 5.2): у бесплатных пользователей права на результат остаются у Tripo; у платных — права есть, эксклюзивности нет. Считается ли покупатель кредитов API «платным» — НЕ ПОДТВЕРЖДЕНО.
- Tripo Studio (сайт, подписка с автопродлением) и Tripo API — разные продукты; входит ли API в подписку — НЕ ПРОВЕРЕНО (страница тарифов отвечает 403).
- Интеграции: tripo-mcp — альфа, работает только через аддон Blender; плагин UE — под 5.6; Python SDK — в основном API v2.
- Задачи асинхронные (task_id, опрос раз в 1–2 с); одновременно P-задач 5 или 3 (в документации расхождение).
- Результат по умолчанию GLB; `/models/convert` → FBX, `pivot_to_center_bottom`, `scale_factor`; ориентацию менять последним шагом.

## Unreal 5.5 (по исходникам движка)
- Импорт: `AssetTools.import_asset_tasks`; без factory FBX/glTF идут через Interchange. У Interchange по умолчанию Nanite ВКЛ, развёртка под карту освещения ВЫКЛ — задавать явно.
- Замена с сохранением всех ссылок: импорт поверх того же пути и имени (`replace_existing=True`).
- LOD/коллизия: `StaticMeshEditorSubsystem` (`set_lods`, `set_lod_group`, `add_simple_collisions`, `set_nanite_settings`).
- Авто-UV1 только переупаковывает UV0 — плохую развёртку чинить в Blender.

## Claude / Blender
- MCP-серверы можно объявить прямо у субагента (`mcpServers`), ключ — через `${TRIPO_API_KEY}` из переменной окружения.
- Локальный blender-mcp (Blender Lab) инструментов генерации не имеет; обработка — через `execute_blender_code`. Blender на машине, вероятно, 5.x (НЕ ПРОВЕРЕНО).
- Импорт glTF с `import_shading='FLAT'`; Decimate/Remesh; UV1 — `lightmap_pack`; запекание — только Cycles.
