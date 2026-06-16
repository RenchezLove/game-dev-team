# UserPromptSubmit hook: инъекция короткого GATE-маяка в контекст на каждый ход.
#
# Контракт хука Claude Code (UserPromptSubmit):
#   stdin  — JSON события (prompt и пр.); нам достаточно просто отработать.
#   exit 0 — успех; JSON со stdout обрабатывается. Поле additionalContext
#            внутри hookSpecificOutput добавляется в контекст модели.
#
# Доп. артефакт: пишем таймстамп-строку в gate-inject.log — детерминированный
# пруф, что хук реально сработал на этом ходу (не «настроил», а отработал).
#
# Файл сохранён в UTF-8 с BOM (иначе Windows PowerShell 5.1 читает кириллицу в
# системной ANSI-кодировке и манглит литералы). stdout пишем сырыми UTF-8-байтами.

$ErrorActionPreference = 'Stop'

# consume stdin (payload не обязателен для инъекции)
$null = [Console]::In.ReadToEnd()

$gate = @"
GATE (CLAUDE.md, перед КАЖДЫМ ответом и действием):
1) Факт != догадка: «готово/работает/нашёл/корень» — только с артефактом (лог/git/дамп/живой PIE/лично просмотренный скрин загруженного уровня). Не уверен → пиши «НЕ ПРОВЕРЕНО».
2) Проверь логику и причинный порядок шагов (что нужно раньше — раньше; шаг не ломает предыдущий).
3) Сверь каждое утверждение с реальным артефактом/докой нужной версии, не «по памяти».
Не прошёл gate — перепиши, не отправляй. Полный протокол №0/№0.1/A–I в CLAUDE.md.
"@

# --- детерминированный пруф срабатывания: таймстамп в лог ---
$log = Join-Path $PSScriptRoot 'gate-inject.log'
$ts  = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
Add-Content -LiteralPath $log -Value "[$ts] UserPromptSubmit fired -> gate injected" -Encoding UTF8

# --- вывод JSON на stdout (exit 0 -> обрабатывается) ---
$payload = @{
  hookSpecificOutput = @{
    hookEventName     = 'UserPromptSubmit'
    additionalContext = $gate
  }
}
$json = $payload | ConvertTo-Json -Depth 5 -Compress

$stdout = [Console]::OpenStandardOutput()
$bytes  = [System.Text.Encoding]::UTF8.GetBytes($json)
$stdout.Write($bytes, 0, $bytes.Length)
$stdout.Flush()
exit 0
