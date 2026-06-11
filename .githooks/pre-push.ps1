# git-native pre-push hook (AUTHORITY gate) — Sh9 T1.
# Aborts any push that updates refs/heads/master on a remote unless the
# .claude/QA_OK marker is present. Tool-agnostic: enforced by git itself,
# regardless of how git was launched (Bash, PowerShell, external terminal).
# Reads ref lines on stdin: "<local-ref> <local-sha> <remote-ref> <remote-sha>".
# Messages kept ASCII to avoid PS 5.1 codepage issues in the git-sh hook path.

$ErrorActionPreference = 'Stop'

# repo root = parent of .githooks (this script's directory)
$repoRoot = Split-Path $PSScriptRoot -Parent
$marker   = Join-Path (Join-Path $repoRoot '.claude') 'QA_OK'

$raw = [Console]::In.ReadToEnd()
$touchesMaster = $false
foreach ($line in ($raw -split "`r?`n")) {
    if ([string]::IsNullOrWhiteSpace($line)) { continue }
    $parts = @($line -split '\s+' | Where-Object { $_ -ne '' })
    if ($parts.Count -lt 3) { continue }
    $remoteRef = $parts[2]                       # destination ref on the remote
    if ($remoteRef -eq 'refs/heads/master' -or $remoteRef -eq 'master') {
        $touchesMaster = $true
    }
}

if (-not $touchesMaster) { exit 0 }
if (Test-Path -LiteralPath $marker) { exit 0 }

[Console]::Error.WriteLine("QA-GATE (git-native pre-push): push updates refs/heads/master but .claude/QA_OK marker is absent -> ABORTED. Get qa ATTEST, then game-lead creates .claude/QA_OK before pushing master.")
exit 1
