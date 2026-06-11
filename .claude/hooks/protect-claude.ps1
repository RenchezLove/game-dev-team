# protect-claude.ps1 - PreToolUse guard for the .claude / .githooks config tree.
#
# Purpose: a SUBAGENT / teammate must not be able to edit the team's own guard
# rails (hooks, settings, agent defs, git hooks). Only the MAIN session
# (game-lead) may touch them.
#
# Hook contract (Claude Code PreToolUse):
#   stdin  - JSON: { tool_name, tool_input{...}, agent_id?, agent_type?, ... }
#   exit 0 - allow the tool
#   exit 2 - block; stderr text is returned to the calling agent
#
# Subagent detection (verified against code.claude.com/docs/en/hooks.md,
# 2026-06-09): the payload carries `agent_id` ONLY for subagent/teammate calls.
# The main session started via `claude --agent game-lead` has NO `agent_id`.
# So: no agent_id  -> main session -> always allow (exit 0).
#
# Protected set (for subagents): everything under `.claude/` and `.githooks/`.
# This is a deliberate superset of the explicit list (settings.json,
# settings.local.json, hooks/**, agents/**, CLAUDE.md, .githooks/**) so that
# any throwaway file dropped into .claude is also refused.
# Carve-out: `.claude/QA_OK` is always allowed (the merge gate marker).
#
# Coverage: Write/Edit tools (via file_path) AND Bash/PowerShell command writes
# (redirects > / >>, Set-Content, Add-Content, Out-File, Tee-Object,
# sed -i, cp, mv, rm, Copy-Item, Move-Item, New-Item, Remove-Item, ...).
# Read-only commands (cat / Get-Content / git show / grep) are NOT blocked.
#
# ASCII-only on purpose: no BOM dependency, safe under Windows PowerShell 5.1.

$ErrorActionPreference = 'Stop'

$raw = [Console]::In.ReadToEnd()
if ([string]::IsNullOrWhiteSpace($raw)) { exit 0 }
try { $data = $raw | ConvertFrom-Json } catch { exit 0 }

# --- main session passes through (no agent_id) ---
$agentId = $null
if ($data.PSObject.Properties.Name -contains 'agent_id') { $agentId = [string]$data.agent_id }
if ([string]::IsNullOrWhiteSpace($agentId)) { exit 0 }

$agentType = ''
if ($data.PSObject.Properties.Name -contains 'agent_type') { $agentType = [string]$data.agent_type }

$tool = [string]$data.tool_name

# Does a path string point inside the protected tree (excluding QA_OK)?
function Test-ProtectedPath([string]$p) {
    if ([string]::IsNullOrWhiteSpace($p)) { return $false }
    $n = ($p -replace '\\','/').ToLower()
    # carve-out: the QA_OK marker as an EXACT final segment only
    # (so .claude/QA_OK_evil.txt is NOT carved out).
    if ($n -match '(^|/)\.claude/qa_ok$') { return $false }
    return (($n -match '\.claude/') -or ($n -match '\.githooks/'))
}

$isWriteTool = ($tool -eq 'Write' -or $tool -eq 'Edit' -or $tool -eq 'MultiEdit' -or $tool -eq 'NotebookEdit')
$isCmdTool   = ($tool -eq 'Bash' -or $tool -eq 'PowerShell')

$blocked = $false
$detail  = ''

if ($isWriteTool) {
    $fp = ''
    if ($data.tool_input) {
        if     ($data.tool_input.file_path)     { $fp = [string]$data.tool_input.file_path }
        elseif ($data.tool_input.notebook_path) { $fp = [string]$data.tool_input.notebook_path }
    }
    if (Test-ProtectedPath $fp) { $blocked = $true; $detail = "$tool -> $fp" }
}
elseif ($isCmdTool) {
    $cmd = ''
    if ($data.tool_input) { $cmd = [string]$data.tool_input.command }
    if (-not [string]::IsNullOrWhiteSpace($cmd)) {
        $norm       = ($cmd -replace '\\','/').ToLower()
        # strip the QA_OK marker only when it is a whole token (not followed by
        # more filename chars OR a path separator) -> .claude/QA_OK_evil.txt and
        # the traversal .claude/QA_OK/../hooks/... stay protected.
        $normNoQaOk = $norm -replace '\.claude/qa_ok(?![\w./\-])',''
        $refsProtected = ($normNoQaOk -match '\.claude/') -or ($normNoQaOk -match '\.githooks/')
        if ($refsProtected) {
            # (a) a redirect ( > or >> ) whose target token is a protected path
            $redirToProtected = $normNoQaOk -match '>>?\s*["'']?[^\s|&;<>]*(\.claude/|\.githooks/)'
            # (b) an explicit write command/cmdlet/API anywhere (protected ref already present).
            # NOTE: this is a denylist and is NOT exhaustive (e.g. python/node/perl
            # `open(...,'w')` inline writes are not caught here without false-positives
            # on legit reads). Treated as best-effort defense-in-depth; master integrity
            # is independently held by the git-native hooks + QA_OK marker.
            $writeCmd = $normNoQaOk -match '(set-content|add-content|clear-content|out-file|tee-object|new-item|remove-item|move-item|copy-item|rename-item|set-itemproperty|sed\s+-i|sed\s+--in-place|\bcp\b|\bmv\b|\brm\b|\bdel\b|\bni\b|writealltext|appendalltext|writealllines|appendalllines|writeallbytes|appendallbytes|streamwriter|filestream|::create|::openwrite|\btee\b|\bdd\b|\btruncate\b|\binstall\b)'
            if ($redirToProtected -or $writeCmd) {
                $blocked = $true; $detail = "$tool cmd writes to protected path"
            }
        }
    }
}

if (-not $blocked) { exit 0 }

# --- best-effort decision log (never fail the hook on logging errors) ---
try {
    $claudeDir = Split-Path $PSScriptRoot -Parent
    $repoRoot  = Split-Path $claudeDir -Parent
    $logDir    = Join-Path $repoRoot 'logs'
    if (-not (Test-Path -LiteralPath $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }
    $stamp = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
    $line  = "$stamp DENY agent_type=$agentType agent_id=$agentId tool=$tool detail=$detail"
    Add-Content -LiteralPath (Join-Path $logDir 'protect-claude.log') -Value $line -Encoding UTF8
} catch {}

# --- block ---
$lines = @(
    "PROTECT-CLAUDE BLOCKED: subagent (agent_type=$agentType) may not write to protected config paths.",
    "Protected tree: .claude/** and .githooks/** . Carve-out: .claude/QA_OK only.",
    "Blocked: $detail",
    "Only the main session (game-lead) may change guard rails. Hand this change to game-lead."
)
$msg    = ($lines -join "`n") + "`n"
$stderr = [Console]::OpenStandardError()
$bytes  = [System.Text.Encoding]::UTF8.GetBytes($msg)
$stderr.Write($bytes, 0, $bytes.Length)
$stderr.Flush()
exit 2
