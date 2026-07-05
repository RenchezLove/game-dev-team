$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.Encoding]::UTF8

$target = 'E:\game-dev-team\docs\contrary-survivor\DemoPlanTemplateRec.xlsx'

$addD9  = 'D9. Журнал заданий в экране инвентаря (инвентарь слева, задания справа; без отдельной кнопки) + фикс маркера: после выполнения условий вести к квестодателю (вопрос издателю отправлен)'
$addD10 = 'D10. Обыск контейнеров: подсветка машины/ящика при подходе, кнопка действия, окно «инвентарь слева / находки справа» как в LDoE (вопрос издателю: Build 1 или Build 2)'

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
try {
    $wb = $excel.Workbooks.Open($target)
    if ($wb.ReadOnly) { throw 'FILE_IS_LOCKED_READONLY - закрой файл в Excel' }
    $ws = $wb.Worksheets.Item(1)

    $r = 7  # строка этапа D
    $before = $ws.Cells.Item($r, 3).Text
    if ($before -notmatch 'D') { throw ('row 7 не похожа на этап D: ' + $before.Substring(0, [Math]::Min(30, $before.Length))) }
    if ($before -match 'D9\.') { throw 'D9 уже есть в ячейке — не дублирую' }

    $titleLen = $before.Split([char]10)[0].Length
    $full = $before.TrimEnd() + [char]10 + $addD9 + [char]10 + $addD10
    $ws.Cells.Item($r, 3).Value2 = $full
    $ws.Cells.Item($r, 3).WrapText = $true
    $ws.Cells.Item($r, 3).Characters(1, $titleLen).Font.Bold = $true
    $ws.Rows.Item($r).AutoFit() | Out-Null
    Write-Host ('APPENDED row=7 total_lines=' + $full.Split([char]10).Count)

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
    $wb2 = $excel2.Workbooks.Open($target)
    $ws2 = $wb2.Worksheets.Item(1)
    Write-Host ('VERIFY_D9='  + ($ws2.Cells.Item(7, 3).Text -match 'D9\.'))
    Write-Host ('VERIFY_D10=' + ($ws2.Cells.Item(7, 3).Text -match 'D10\.'))
    $wb2.Close($false)
}
finally {
    $excel2.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel2) | Out-Null
}
Write-Host 'ALL_DONE'
