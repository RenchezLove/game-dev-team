$ErrorActionPreference = 'Stop'
$target = 'E:\game-dev-team\docs\contrary-survivor\DemoPlanTemplateRec.xlsx'
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
try {
    $wb = $excel.Workbooks.Open($target)
    if ($wb.ReadOnly) { throw 'FILE_IS_LOCKED_READONLY' }
    $ws = $wb.Worksheets.Item(1)

    $inwork = [char]::ConvertFromUtf32(0x1F504)

    # --- Этап G (строка 10): статус "в работе" ---
    $ws.Cells.Item(10, 2).Value2 = $inwork
    $ws.Cells.Item(10, 2).Font.Name = 'Segoe UI Emoji'

    # Примечание G: добавить факт в прочитанное состояние ячейки
    $noteG = $ws.Cells.Item(10, 4).Value2
    $addG = [char]10 + [char]10 + [System.Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('MDctMTc6INC60L7QvdCy0LXQudC10YAg0YHQvtCx0YDQsNC9LCAyIEFQSyDQv9GA0L7QstC10YDQtdC90Ysg0LbQuNCy0YzRjiDQvdCwIHJlYWxtZSAoQURSLTA0NyksINGC0LDRhy3Rg9C/0YDQsNCy0LvQtdC90LjQtSDQv9GA0LjQvdGP0YLQviDQoNC40L3QsNGC0L7QvC4g0KDQuNGB0Log0LrQvtC90LLQtdC50LXRgNCwINGB0L3Rj9GCLg=='))
    $ws.Cells.Item(10, 4).Value2 = ($noteG + $addG)
    $ws.Cells.Item(10, 4).WrapText = $true

    # --- Этап I (строка 12): статус "в работе" ---
    $ws.Cells.Item(12, 2).Value2 = $inwork
    $ws.Cells.Item(12, 2).Font.Name = 'Segoe UI Emoji'

    $noteI = $ws.Cells.Item(12, 4).Value2
    $addI = [char]10 + [char]10 + [System.Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('0KHRgtCw0YDRgtC+0LLQsNC9INC00L7RgdGA0L7Rh9C90L4gMDctMTgg0L/QviDQutC+0LzQsNC90LTQtSDQoNC40L3QsNGC0LAgKEFEUi0wNDgpOiDRgtCw0Yct0YHQu9C+0Lkg0Lgg0L/QsNC90LXQu9C4INC/0LXRgNC10LLQvtC00Y/RgtGB0Y8g0L3QsCBVTUcsINCy0LXRgtC60LAgZmVhdHVyZS91bWctaHVkLg=='))
    $ws.Cells.Item(12, 4).Value2 = ($noteI + $addI)
    $ws.Cells.Item(12, 4).WrapText = $true

    $ws.Rows.Item(10).AutoFit() | Out-Null
    $ws.Rows.Item(12).AutoFit() | Out-Null

    $wb.Save()
    $wb.Close($false)
    Write-Output 'SAVE_OK'
}
finally {
    $excel.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
}

# верификация вторым открытием: коды символов, не глаза
$excel2 = New-Object -ComObject Excel.Application
$excel2.Visible = $false
try {
    $wb2 = $excel2.Workbooks.Open($target, 0, $true)
    $ws2 = $wb2.Worksheets.Item(1)
    $g = $ws2.Cells.Item(10, 2).Value2
    $i = $ws2.Cells.Item(12, 2).Value2
    Write-Output ('G_STATUS_CODE=' + [Char]::ConvertToUtf32($g, 0))
    Write-Output ('I_STATUS_CODE=' + [Char]::ConvertToUtf32($i, 0))
    Write-Output ('G_NOTE_HAS_ADR047=' + ($ws2.Cells.Item(10, 4).Value2 -match 'ADR-047'))
    Write-Output ('I_NOTE_HAS_ADR048=' + ($ws2.Cells.Item(12, 4).Value2 -match 'ADR-048'))
    $wb2.Close($false)
}
finally {
    $excel2.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel2) | Out-Null
}
Write-Output 'ALL_DONE'
