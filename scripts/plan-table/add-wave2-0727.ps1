$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.Encoding]::UTF8

$target = 'E:\game-dev-team\docs\contrary-survivor\DemoPlanTemplateRec.xlsx'
$row = 10  # Этап G

$nl = [char]10
$oldLine = '- Окна магазина и инвентаря пересобраны на канвас-раскладку для настройки мышкой (доводка выделения кнопок — в работе).'
$newLine = '- Окна магазина, инвентаря и панель статов пересобраны на канвас-раскладку: каждый элемент тянется мышкой (замки на начинке), стилизация владельца перенесена автоматически.'
$extra = '- Индикация хромоты: плашка «Ранен: скорость снижена» + разовая подсказка, что скорость вернётся после лечения.' + $nl +
  '- Граница мира доведена: Volume-поведение при масштабировании, градиентный туман вместо заглушки, горизонтальные полосы тумана для вида сверху с ручкой «толщины» (FogDepth).'

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
try {
    $wb = $excel.Workbooks.Open($target)
    if ($wb.ReadOnly) { throw 'FILE_IS_LOCKED_READONLY' }
    $ws = $wb.Worksheets.Item(1)

    $before = $ws.Cells.Item($row, 3).Text
    if ($before.Substring(0, 6) -ne 'Этап G') { throw ('row mismatch: ' + $before.Substring(0, 30)) }
    if ($before -match 'FogDepth') { Write-Host 'ALREADY_PRESENT'; $wb.Close($false); exit 0 }

    $full = $before.Replace($oldLine, $newLine) + $nl + $extra
    if ($full -eq $before + $nl + $extra) { Write-Host 'WARN: старая строка про кнопки не найдена, добавляю только новые' }

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
    Write-Host ('VERIFY_FOGDEPTH=' + ($txt -match 'FogDepth'))
    Write-Host ('VERIFY_LIMP=' + ($txt -match 'хромоты'))
    Write-Host ('VERIFY_STATS=' + ($txt -match 'панель статов'))
    $wb2.Close($false)
}
finally {
    $excel2.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel2) | Out-Null
}
Write-Host 'ALL_DONE'
