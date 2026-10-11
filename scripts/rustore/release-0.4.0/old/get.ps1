$ProgressPreference='SilentlyContinue'
Get-Content -LiteralPath (Join-Path $PSScriptRoot 'list2.txt') | ForEach-Object { $p = $_.Split(' '); $ext = [IO.Path]::GetExtension($p[1]); Invoke-WebRequest -UseBasicParsing -Uri $p[1] -OutFile (Join-Path $PSScriptRoot ("shot_" + $p[0] + $ext)) -TimeoutSec 120 }
