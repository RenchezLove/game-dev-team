$p = Get-Process UnrealEditor -ErrorAction SilentlyContinue
if ($null -eq $p) { Write-Output 'NO_PROCESS' }
else { $p | ForEach-Object { Write-Output ("PID=" + $_.Id + " START=" + $_.StartTime + " MEM_GB=" + [math]::Round($_.WorkingSet64/1GB,2)) } }
