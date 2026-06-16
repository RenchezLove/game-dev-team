# ARCHIVE-INDEX — карта памяти команды

Указатель верхнего уровня: где что живёт. Памятка по слоям памяти (правило «Гигиена памяти» в `CLAUDE.md`).

## Слои памяти (единый источник на каждый тип)
- **Живая память роли** = `context/<agent>/context.md` — блок «🧭 СЕЙЧАС» + постоянные директивы + текущая задача. ЭТО грунтуется при старте сессии.
- **Прошлое роли** = `context/<agent>/archive.md` — закрытые этапы, старые баг-раунды, отработанная инфра. **Read-on-demand: НЕ для грунтовки.** Читать только по поводу (чистка / онбординг / «как мы пришли к X»). Хранит только ПРОШЛОЕ; правда на «сейчас» — только в «🧭 СЕЙЧАС».
- **Ключевые решения** = `docs/decisions.md` — реестр ADR (одна запись = одно решение).
- **Полная история изменений** = git (коммиты, ветки).
- **Дизайн-правда по игре** = `docs/contrary-survivor/` (GDD, roadmap, tech-design). Единственный источник истины по лору/механикам/балансу/визуалу.

Архив / ADR / GDD / git между собой НЕ дублировать — ссылаться.

## Где что
| Роль | Живая память | Архив |
|---|---|---|
| game-lead | `context/game-lead/context.md` | `context/game-lead/archive.md` (инфра Ш7-Ш9, Фазы 0-5, END-OF-DAY, ПЛЕЙБУК, УРОКИ UE) |
| cpp-dev | `context/cpp-dev/context.md` | (ведёт сам по мере роста) |
| unreal-operator | `context/unreal-operator/context.md` | — |
| modeler-3d | `context/modeler-3d/context.md` | — |
| concept-artist | `context/concept-artist/context.md` | — |
| qa | `context/qa/context.md` | — |
| общее | `context/_shared.md` (стек/конвенции) | — |
