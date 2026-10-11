$desktop = [Environment]::GetFolderPath('Desktop')
$lnk = Join-Path $desktop 'Моя команда.lnk'
$sh = New-Object -ComObject WScript.Shell
$s = $sh.CreateShortcut($lnk)
$s.TargetPath = 'E:\game-dev-team\apps\team-dashboard\start.cmd'
$s.WorkingDirectory = 'E:\game-dev-team\apps\team-dashboard'
$s.WindowStyle = 7
$s.Save()
Write-Output ('created: ' + (Test-Path -LiteralPath $lnk))
