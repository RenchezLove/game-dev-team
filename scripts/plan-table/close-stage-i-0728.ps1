$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.Encoding]::UTF8

$target = 'E:\game-dev-team\docs\contrary-survivor\DemoPlanTemplateRec.xlsx'
$row = 12  # Этап I

$nl = [char]10
$extra = 'Итог этапа: весь интерфейс на UMG — проверено составом ассетов и C++-классов (Ринат закрыл этап 07-28).' + $nl +
  'Дополнительно (сверх плана этапа):' + $nl +
  '+ окна собираются не руками в редакторе, а кодом (инструмент GenerateWbp с режимами пересборки, проверки и снятия среза раскладки) — сборка воспроизводима и проверяема;' + $nl +
  '+ канвас-раскладка: любой элемент окна двигается и растягивается мышкой, начинка кнопок под замками, чтобы клик выделял саму кнопку;' + $nl +
  '+ ручная стилизация и расстановка владельца автоматически переносятся при пересборке окон;' + $nl +
  '+ добавлены экраны и виджеты сверх списка: вступление, пауза, тач-управление для телефона, подсказка хромоты, трекер целей квеста;' + $nl +
  '+ тексты интерфейса переведены на штатную систему локализации движка (ADR-050);' + $nl +
  '+ отклонение по букве плана: всплывающие цифры урона сделаны прямой отрисовкой в HUD, а не отдельным UMG-виджетом — так легче для слабых телефонов.'

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
try {
    $wb = $excel.Workbooks.Open($target)
    if ($wb.ReadOnly) { throw 'FILE_IS_LOCKED_READONLY' }
    $ws = $wb.Worksheets.Item(1)

    $before = $ws.Cells.Item($row, 3).Text
    if ($before.Substring(0, 6) -ne 'Этап I') { throw ('row mismatch: ' + $before.Substring(0, 30)) }
    if ($before -match 'Итог этапа') { Write-Host 'ALREADY_PRESENT'; $wb.Close($false); exit 0 }

    # статус этапа: ✅ вместо 🔄, шрифт Segoe UI Emoji (иначе ч/б)
    $ws.Cells.Item($row, 2).Value2 = [char]::ConvertFromUtf32(0x2705)
    $ws.Cells.Item($row, 2).Font.Name = 'Segoe UI Emoji'

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
    $status = $ws2.Cells.Item($row, 2).Text
    $codes = ($status.ToCharArray() | ForEach-Object { [int]$_ }) -join ','
    $txt = $ws2.Cells.Item($row, 3).Text
    Write-Host ('VERIFY_STATUS_CODES=' + $codes + ' (ожидается 9989 = галочка)')
    Write-Host ('VERIFY_FONT=' + $ws2.Cells.Item($row, 2).Font.Name)
    Write-Host ('VERIFY_ITOG=' + ($txt -match 'Итог этапа'))
    Write-Host ('VERIFY_EXTRA=' + ($txt -match 'Дополнительно'))
    $wb2.Close($false)
}
finally {
    $excel2.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel2) | Out-Null
}
Write-Host 'ALL_DONE'
