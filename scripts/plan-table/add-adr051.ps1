$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.Encoding]::UTF8

$target = 'E:\game-dev-team\docs\contrary-survivor\DemoPlanTemplateRec.xlsx'
$row = 10  # Этап G — Android-сборка + замер -> BUILD 1

$nl = [char]10
$block = 'Дополнительно (сверх плана этапа) — доводка Build 1 по живой приёмке (ADR-051):' + $nl +
  '- Интро-сценка принята; кнопки диалога заменены на живые реплики героя.' + $nl +
  '- Баннер ежедневной награды показывается после первого диалога со старостой, а не поверх интро.' + $nl +
  '- Квест «Шкуры для торговца» упразднён: вместо него намёк старосты (торговец платит за шкуры, вторая стая к югу).' + $nl +
  '- Новые инструменты для карты: спавнер волка возле игрока и граница мира (туман + невидимая стена); расстановка — Ринат.' + $nl +
  '- Окна магазина и инвентаря пересобраны на канвас-раскладку для настройки мышкой (доводка выделения кнопок — в работе).'

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
try {
    $wb = $excel.Workbooks.Open($target)
    if ($wb.ReadOnly) { throw 'FILE_IS_LOCKED_READONLY - закрой файл в Excel' }
    $ws = $wb.Worksheets.Item(1)

    $before = $ws.Cells.Item($row, 3).Text
    if ($before.Substring(0, 6) -ne 'Этап G') { throw ('row mismatch: ' + $before.Substring(0, 30)) }
    if ($before -match 'ADR-051') { Write-Host 'ALREADY_PRESENT - ничего не меняю'; $wb.Close($false); exit 0 }

    $titleLen = $before.IndexOf([string]$nl)
    if ($titleLen -lt 1) { $titleLen = $before.Length }

    $full = $before + $nl + $block
    $ws.Cells.Item($row, 3).Value2 = $full
    $ws.Cells.Item($row, 3).WrapText = $true
    $ws.Cells.Item($row, 3).Characters(1, $titleLen).Font.Bold = $true
    $ws.Rows.Item($row).AutoFit() | Out-Null
    Write-Host ('PATCHED row=' + $row + ' lines=' + $full.Split($nl).Count)

    $wb.Save()
    $wb.Close($false)
    Write-Host 'SAVE_OK'
}
finally {
    $excel.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
}

# Проверка отдельным процессом: блок реально записался
$excel2 = New-Object -ComObject Excel.Application
$excel2.Visible = $false
$excel2.DisplayAlerts = $false
try {
    $wb2 = $excel2.Workbooks.Open($target, 0, $true)
    $ws2 = $wb2.Worksheets.Item(1)
    $txt = $ws2.Cells.Item($row, 3).Text
    Write-Host ('VERIFY_ADR051=' + ($txt -match 'ADR-051'))
    Write-Host ('VERIFY_BORDER=' + ($txt -match 'граница мира'))
    Write-Host ('VERIFY_TITLE_KEPT=' + ($txt -match 'Этап G'))
    $wb2.Close($false)
}
finally {
    $excel2.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel2) | Out-Null
}
Write-Host 'ALL_DONE'
