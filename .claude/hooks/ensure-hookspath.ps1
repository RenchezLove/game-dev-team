# ensure-hookspath.ps1 - self-heal of the git-native QA gate (Sh9 T7a).
#
# WHY: Claude Code's `isolation:"worktree"` writes
#   core.hooksPath = <repo>/.git/hooks
# into the SHARED .git/config every time a worktree teammate is spawned. That
# silently replaces our authoritative .githooks gate (pre-push / pre-merge-commit)
# with the empty default hooks dir -> the git-native AUTHORITY layer goes OFF for
# the whole repo until re-asserted. This caused the T5 merge-gate incident.
#
# FIX: force core.hooksPath back to the repo's .githooks (ABSOLUTE path, so it
# resolves correctly even when git runs from inside a worktree cwd). Registered
# on BOTH:
#   - SessionStart  -> restore at session start
#   - PreToolUse (Bash|PowerShell) -> restore before any command, so a mid-session
#     worktree spawn cannot leave the gate silently off before a merge/push.
#
# Contract: this hook must NEVER break the session or block a tool. It only
# mutates local git config and logs. Always exits 0. Writes NOTHING to stdout
# (SessionStart injects hook stdout as context) - all output goes to the log.
# ASCII-only for Windows PowerShell 5.1 codepage safety.

$ErrorActionPreference = 'SilentlyContinue'

try {
    $repoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
    $desired  = Join-Path $repoRoot '.githooks'

    $current = (& git -C $repoRoot config --local --get core.hooksPath 2>$null)
    if ($current) { $current = $current.Trim() }

    # normalize for comparison (slashes + case)
    $normCur = ($current -replace '\\','/').ToLower()
    $normDes = ($desired -replace '\\','/').ToLower()

    if ($normCur -ne $normDes) {
        & git -C $repoRoot config core.hooksPath $desired 2>$null | Out-Null
        $logDir = Join-Path $repoRoot 'logs'
        if (-not (Test-Path -LiteralPath $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }
        $stamp = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
        $was   = if ([string]::IsNullOrWhiteSpace($current)) { '<unset>' } else { $current }
        $line  = "$stamp HEAL core.hooksPath was='$was' -> set='$desired'"
        Add-Content -LiteralPath (Join-Path $logDir 'gate-selfheal.log') -Value $line -Encoding UTF8
    }
} catch {}

exit 0
