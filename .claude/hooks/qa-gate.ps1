# QA-гейт (PreToolUse / Bash).
# Блокирует (exit 2) `git push` в master/origin master и `git merge` в master,
# если нет файла-маркера .claude/QA_OK. Маркер создаёт game-lead вручную только
# после того, как qa дал добро, и удаляет сразу после merge.
#
# Контракт хука Claude Code:
#   stdin  — JSON вида { "tool_name": "...", "tool_input": { "command": "..." } }
#   exit 0 — разрешить инструмент
#   exit 2 — заблокировать; текст из stderr возвращается агенту
#
# Детект — по ГЛАГОЛУ команды, а не по подстроке: команда режется на выражения
# по разделителям (; && || | & и переводам строк), и проверяется, с чего каждое
# выражение НАЧИНАЕТСЯ. Так `git commit -m "...git push..."` не ловится по тексту
# сообщения, а реальный `... && git push origin master` — ловится.
#
# Файл сохранён в UTF-8 с BOM (иначе Windows PowerShell 5.1 читает кириллицу в
# системной ANSI-кодировке и падает на парсинге). Сообщение в stderr пишется
# сырыми UTF-8-байтами — Claude Code читает поток как UTF-8.

$ErrorActionPreference = 'Stop'

# .claude/QA_OK относительно расположения скрипта (.claude/hooks/qa-gate.ps1)
$claudeDir = Split-Path $PSScriptRoot -Parent
$marker    = Join-Path $claudeDir 'QA_OK'

# --- читаем и парсим payload ---
$raw = [Console]::In.ReadToEnd()
if ([string]::IsNullOrWhiteSpace($raw)) { exit 0 }
try { $data = $raw | ConvertFrom-Json } catch { exit 0 }

$cmd = $null
if ($data.tool_input) { $cmd = $data.tool_input.command }
if ([string]::IsNullOrWhiteSpace($cmd)) { exit 0 }

# текущая ветка (нужна для bare-push и merge)
$branch = ''
try { $branch = (& git rev-parse --abbrev-ref HEAD 2>$null).Trim() } catch { $branch = '' }

# режем на отдельные выражения по разделителям оболочки.
# Включаем скобки подоболочек ( ) и редиректы < > — иначе трейлинг-метасимвол
# приклеивается к токену рефспека: `(git push origin master)` -> 'master)' != 'master'.
$segments = [regex]::Split($cmd, '\r?\n|&&|\|\||;|\||&|\(|\)|<|>')

$blocked = $false
$reason  = ''

foreach ($seg in $segments) {
    # срезаем ведущие скобки/пробелы подоболочек: ( { пробелы
    $s = ($seg -replace '^[\s\(\{]+', '').Trim()

    # --- git push, обновляющий origin/master ---
    # Блокируем ТОЛЬКО реальное обновление ветки master на remote. Разбираем
    # рефспеки и смотрим на ЦЕЛЬ пуша, а не на наличие подстроки 'master':
    #   - bare push / 'git push origin' / 'git push -u origin'  → текущая ветка
    #   - 'git push origin master' / 'HEAD:master' / ':master'  → цель master
    #   - 'git push origin --delete feature/x'                  → удаление чужой
    #     ветки на remote, master НЕ трогает → НЕ блокируем (это и был баг Ш8).
    if ($s -match '^git\s+push\b') {
        $tok = @([regex]::Split($s, '\s+') | Where-Object { $_ -ne '' })
        $rest = @()
        if ($tok.Count -gt 2) { $rest = @($tok[2..($tok.Count - 1)]) }

        $isDelete   = $false
        $positional = @()
        foreach ($t in $rest) {
            if ($t -eq '--delete' -or $t -eq '-d') { $isDelete = $true; continue }
            if ($t -like '-*') { continue }   # прочие опции/флаги пропускаем
            $positional += $t
        }
        # первый позиционный аргумент — repository (remote); остальные — рефспеки
        $refspecs = @()
        if ($positional.Count -gt 1) { $refspecs = @($positional[1..($positional.Count - 1)]) }

        $pushesMaster = $false
        if ($refspecs.Count -eq 0) {
            # нет рефспека: push текущей ветки (delete без рефспека невалиден — не блокируем)
            if (-not $isDelete -and $branch -eq 'master') { $pushesMaster = $true }
        } else {
            foreach ($rs in $refspecs) {
                # цель = часть после ':' (src:dst), иначе сам реф
                if ($rs -match ':') { $dst = ($rs -split ':', 2)[1] } else { $dst = $rs }
                # подчищаем налипшие шелл-метасимволы по краям (защита от сегментации)
                $dst = $dst -replace '^[\s\(\{]+', '' -replace '[\s\)\}<>&|;]+$', ''
                $dst = $dst -replace '^refs/heads/', ''
                if ($dst -eq 'HEAD') { $dst = $branch }   # HEAD → текущая ветка
                if ($dst -eq 'master') { $pushesMaster = $true; break }
            }
        }
        if ($pushesMaster) { $blocked = $true; $reason = 'git push в master/origin master'; break }
    }

    # --- git merge в master (мерж идёт в текущую ветку) ---
    if (($s -match '^git\s+merge\b') -and $branch -eq 'master') {
        $blocked = $true; $reason = 'git merge в master'; break
    }
}

if (-not $blocked) { exit 0 }

# заблокированная операция: пропускаем только при наличии маркера QA_OK
if (Test-Path -LiteralPath $marker) { exit 0 }

$lines = @(
    "QA-ГЕЙТ ЗАБЛОКИРОВАЛ: $reason.",
    "Маркер .claude/QA_OK не найден — ветка не прошла ревью qa.",
    "Порядок: (1) game-lead отдаёт фича-ветку qa на ревью; (2) только после 'добро' от qa game-lead вручную создаёт .claude/QA_OK; (3) merge в master; (4) game-lead сразу удаляет .claude/QA_OK.",
    "Напарникам работать в master запрещено — только в фича-ветках."
)
$msg    = ($lines -join "`n") + "`n"
$stderr = [Console]::OpenStandardError()
$bytes  = [System.Text.Encoding]::UTF8.GetBytes($msg)
$stderr.Write($bytes, 0, $bytes.Length)
$stderr.Flush()
exit 2
