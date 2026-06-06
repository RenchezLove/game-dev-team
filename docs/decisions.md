# Архитектурные решения (ADR)

> Каждое решение по инструментам и архитектуре фиксируется здесь. «Нативное проверено» означает живую проверку реестра коннекторов, а не память.

## ADR-001 — Движок системы: субагенты Claude Code, standalone, game-lead = корень
Система game-dev — самостоятельная (не вложена в другие системы агентов). Движок — субагенты Claude Code (`.claude/agents/*.md`). `game-lead` запускается как главная сессия (`claude --agent game-lead`) и порождает специалистов.
**Причина:** субагент Claude Code не может порождать субагентов (подтверждено по code.claude.com/docs). Делая `game-lead` корнем-главной-сессией, получаем рабочее дерево «лид → специалисты». Будь game-lead вложенным субагентом, он не смог бы звать специалистов. Запас на многоуровневость в будущем — через agent teams (отдельный механизм), не через субагенты.

## ADR-002 — modeler-3d: Blender через официальный сервер blender-mcp (CLI-уровень)
Инструмент 3D — официальный сервер **blender-mcp v1.0.0** (Blender Lab), заведённый в Claude Code **CLI**, НЕ через бандл Claude Desktop.
- Установка: `uv tool install` из `git+https://projects.blender.org/lab/blender_mcp.git#subdirectory=mcp`. Бинарь: `C:\Users\pgr40\.local\bin\blender-mcp.exe`.
- Регистрация: проектно в `.mcp.json` (сервер `blender`).
- Привязка к агенту `modeler-3d` через `mcpServers: [blender]` (только этот агент видит инструменты Blender).
- Сторона Blender: аддон **Blender Lab v1.0.0**, слушает `localhost:9876`, auto-start.
Самодельный MCP на `bpy` не используем — есть официальный сервер.
**Статус:** заведено и проверено живыми вызовами (get_objects_summary, get_object_detail_summary, render_viewport_to_path). Рабочие нюансы — см. [ADR-011](#adr-011--blender-рабочие-нюансы-один-клиент-на-сокет-output_path-у-render_viewport).

## ADR-003 — unreal-operator: UE Python/Remote Control (приоритет) или Computer Use
Нативного коннектора Unreal в реестре не найдено (проверено несколькими запросами — граница проверки). Приоритет — программный путь (UE Python / Remote Control), надёжнее на Windows; Computer Use — крайний случай.

## ADR-004 — concept-artist: навык canvas-design
Нативного коннектора-генератора изображений в реестре нет. Используем нативный навык canvas-design (png/pdf). Внешний генератор не вводим.
**Статус:** проводка навыка в Claude Code — на Фазе инструментов.

## ADR-005 — sound: коннектор Splice (Фаза расширения)
AI-генератора музыки нативного нет. Нативный коннектор Splice (prompt_to_stack, describe_a_sound, download_asset) — для SFX/сэмплов. Платный (подписка Splice). Оригинальная музыка — отдельный вопрос при необходимости.

## ADR-006 — Бэкап ассетов: нативный коннектор Google Drive
Нативный коннектор Google Drive подключён. Крупные ассеты бэкапятся через него.

## ADR-007 — cpp-dev / qa: Claude Code нативно
Код, git, сборка, тесты — через Claude Code (полный доступ к диску/bash). MCP не нужен.

## ADR-008 — Состав команды: расширение
База: game-lead + cpp-dev, unreal-operator, modeler-3d, concept-artist, qa. На Фазе расширения добавляются: game-designer, tech-artist, sound, плюс level-designer и ui-ux-designer (жанру top-down survival + RPG критичны зоны/лут и тяжёлый UI). narrative пока вложен в game-designer; аналитик отложен (нет прод-игры).

## ADR-009 — Платформы: Android (слабые устройства), iOS отложен
Цель — ПК + Android с прицелом на слабые устройства. iOS отложен. Точные min-spec — `game-lead` берёт из диздока на Фазе подключения проекта.

## ADR-010 — Делегирование: game-lead без ограничений
`game-lead` имеет `tools: Agent` без аллоулиста — может звать любого специалиста. Эффективная глубина делегирования = 1 уровень (ограничение субагентов). Параллелизм ≤3 — процессное правило.

## ADR-011 — Blender: рабочие нюансы (один клиент на сокет, output_path у render_viewport)
Эксплуатационные правила для сервера blender-mcp из [ADR-002](#adr-002--modeler-3d-blender-через-официальный-сервер-blender-mcp-cli-уровень):
- **Один клиент на сокет 9876.** Desktop-коннектор Blender держать **выключенным**: к аддону Blender Lab подключается один клиент. CLI-сервер `blender` и Desktop-коннектор одновременно на `localhost:9876` конфликтуют — оставляем только CLI-проводку.
- **`render_viewport_to_path` игнорирует `output_path`.** Инструмент пишет PNG в свой серверный temp (вида `…\AppData\Local\Temp\blender_*\blender_mcp\…`) и возвращает фактический путь в `filepath`; переданный `output_path` на место записи не влияет. **После рендера копировать из возвращённого `filepath` в целевую папку проекта** и подтверждать наличие файла там (протокол B). Проверено: рендер сцены `Scene` 1920×1080 → temp, скопирован в `E:\game-dev-team\logs\blender_viewport.png` (1 151 657 байт).
