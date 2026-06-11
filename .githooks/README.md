# .githooks — git-native QA-гейт (Ш9 T1)

Авторитетный (инструмент-агностичный) слой мерж-гейта. В отличие от Claude Code
PreToolUse-хука (`.claude/hooks/qa-gate.ps1`, ранний фильтр на инструменты
`Bash|PowerShell`), эти хуки исполняет САМ git — поэтому они срабатывают независимо
от того, чем запущен git (Bash-тул, PowerShell-тул, внешний терминал).

## Хуки
- **`pre-push`** → `pre-push.ps1`: блокирует любой push, обновляющий `refs/heads/master`
  на remote (или удаляющий его), если нет файла-маркера `.claude/QA_OK`. Читает рефы
  со stdin, решает по реальной ЦЕЛИ пуша (не по строке команды).
- **`pre-merge-commit`** → `pre-merge-commit.ps1`: блокирует merge В master, создающий
  коммит (`--no-ff`/реальный merge), если нет `.claude/QA_OK`.
  ⚠️ НЕ срабатывает на fast-forward (ff не создаёт коммит). Поэтому правило команды —
  **мёрж в master ВСЕГДА `--no-ff`**; ff-вектор дополнительно закрыт pre-push (gate-of-record на push).

Маркер `.claude/QA_OK` создаёт `game-lead` вручную только после ATTEST от `qa` и
удаляет сразу после merge (не коммитится, в `.gitignore`).

## РАЗОВЫЙ БУТСТРАП (обязателен на каждой машине/клоне)
`core.hooksPath` — это ЛОКАЛЬНЫЙ git-конфиг (живёт в `.git/config`, НЕ коммитится и НЕ
переносится при клоне). Сами скрипты-хуки трекаются в `.githooks/`, но git не
использует их, пока не указать путь:

```
git config core.hooksPath .githooks
```

Проверка: `git config --get core.hooksPath` → должно вернуть `.githooks`.

Скрипты-обёртки `pre-push`/`pre-merge-commit` — sh (git на Windows запускает хуки своим
sh), они делегируют в одноимённые `.ps1`. Окончания строк обёрток ОБЯЗАНЫ быть LF
(зафиксировано в `.gitattributes`), иначе git-sh падает на CRLF-shebang.
