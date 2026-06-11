# git-native pre-merge-commit hook (AUTHORITY gate) — Sh9 T1.
# Fires on `git merge` that CREATES a commit (i.e. --no-ff or a real merge),
# AFTER the merge succeeds and BEFORE the commit. Does NOT fire on fast-forward
# merges (they create no commit) — the team rule "always merge master with
# --no-ff" plus the pre-push gate close the ff vector.
# Aborts a merge whose current branch is master unless .claude/QA_OK is present.
# Messages kept ASCII to avoid PS 5.1 codepage issues in the git-sh hook path.

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path $PSScriptRoot -Parent
$marker   = Join-Path (Join-Path $repoRoot '.claude') 'QA_OK'

# during a merge, HEAD still points at the branch being merged INTO
$branch = ''
try { $branch = (& git symbolic-ref --short HEAD 2>$null).Trim() } catch { $branch = '' }

if ($branch -ne 'master') { exit 0 }
if (Test-Path -LiteralPath $marker) { exit 0 }

[Console]::Error.WriteLine("QA-GATE (git-native pre-merge-commit): merge into master but .claude/QA_OK marker is absent -> ABORTED. Get qa ATTEST, then game-lead creates .claude/QA_OK before merging into master.")
exit 1
