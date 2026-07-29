$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.Encoding]::UTF8

$target = 'E:\game-dev-team\docs\contrary-survivor\DemoPlanTemplateRec.xlsx'
$row = 10  # Этап G

$nl = [char]10
$extra = '- Кнопка бега светится синим и пульсирует, пока включён режим бега.' + $nl +
  '- Перед игроком подсвечивается сектор в 100 градусов, и урон холодным оружием наносится ровно в нём: подсветка берёт угол и дальность из самого оружия, поэтому что видно, то и бьёт.' + $nl +
  '- Игрок и бандиты при стрельбе доворачивают корпус к противнику: поза прицеливания накладывается только на верх тела, ноги продолжают обычную ходьбу.' + $nl +
  '- Удар ножом получил размашистую анимацию замаха, и урон приходит в момент прохода клинка, а не по нажатию кнопки. Анимация не привязана к ножу и подойдёт другому холодному оружию.' + $nl +
  '- Собрано и проверено сборкой, автотестами и проверкой схемы анимации; ждёт живой приёмки в игре.'

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
try {
    $wb = $excel.Workbooks.Open($target)
    if ($wb.ReadOnly) { throw 'FILE_IS_LOCKED_READONLY' }
    $ws = $wb.Worksheets.Item(1)

    $before = $ws.Cells.Item($row, 3).Text
    if ($before.Substring(0, 6) -ne 'Этап G') { throw ('row mismatch: ' + $before.Substring(0, 30)) }
    if ($before -match 'пульсирует') { Write-Host 'ALREADY_PRESENT'; $wb.Close($false); exit 0 }

    $full = $before + $nl + $extra

    $titleLen = $full.IndexOf([string]$nl)
    $ws.Cells.Item($row, 3).Value2 = $full
    $ws.Cells.Item($row, 3).WrapText = $true
    $ws.Cells.Item($row, 3).Characters(1, $titleLen).Font.Bold = $true
    $ws.Rows.Item($row).AutoFit() | Out-Null

    $wb.Save()
    $wb.Close($false)
    Write-Host 'SAVE_OK'
}
finally {
    $excel.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
}

$excel2 = New-Object -ComObject Excel.Application
$excel2.Visible = $false
$excel2.DisplayAlerts = $false
try {
    $wb2 = $excel2.Workbooks.Open($target, 0, $true)
    $ws2 = $wb2.Worksheets.Item(1)
    $txt = $ws2.Cells.Item($row, 3).Text
    Write-Host ('VERIFY_RUNBTN=' + ($txt -match 'пульсирует'))
    Write-Host ('VERIFY_SECTOR=' + ($txt -match '100 градусов'))
    Write-Host ('VERIFY_AIM=' + ($txt -match 'доворачивают корпус'))
    Write-Host ('VERIFY_KNIFE=' + ($txt -match 'прохода клинка'))
    Write-Host ('VERIFY_STATUS=' + ($txt -match 'живой приёмки'))
    Write-Host ('VERIFY_OLD_FOG_KEPT=' + ($txt -match 'клублением'))
    $wb2.Close($false)
}
finally {
    $excel2.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel2) | Out-Null
}
Write-Host 'ALL_DONE'
