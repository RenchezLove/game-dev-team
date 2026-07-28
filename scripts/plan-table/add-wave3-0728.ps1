$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.Encoding]::UTF8

$target = 'E:\game-dev-team\docs\contrary-survivor\DemoPlanTemplateRec.xlsx'
$row = 10  # Этап G

$nl = [char]10
$extra = '- Окна диалога и экрана смерти переведены на канвас-раскладку: кнопки тянутся и двигаются мышкой, как в магазине; расстановка, сделанная мышкой, теперь автоматически переносится при пересборках окон (починен перенос геометрии слотов).' + $nl +
  '- Туман границы мира переделан: узор из мировых координат без растяжки и швов, два слоя с медленным клублением, рваный мягкий край, углы без двойной яркости; у невидимой стены — отдельная ручка отступа от края карты.'

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
try {
    $wb = $excel.Workbooks.Open($target)
    if ($wb.ReadOnly) { throw 'FILE_IS_LOCKED_READONLY' }
    $ws = $wb.Worksheets.Item(1)

    $before = $ws.Cells.Item($row, 3).Text
    if ($before.Substring(0, 6) -ne 'Этап G') { throw ('row mismatch: ' + $before.Substring(0, 30)) }
    if ($before -match 'клублением') { Write-Host 'ALREADY_PRESENT'; $wb.Close($false); exit 0 }

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
    Write-Host ('VERIFY_FOG3=' + ($txt -match 'клублением'))
    Write-Host ('VERIFY_DIALOG=' + ($txt -match 'экрана смерти'))
    Write-Host ('VERIFY_WALL=' + ($txt -match 'отступа от края'))
    $wb2.Close($false)
}
finally {
    $excel2.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel2) | Out-Null
}
Write-Host 'ALL_DONE'
