$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.Encoding]::UTF8

$target = 'E:\game-dev-team\docs\contrary-survivor\DemoPlanTemplateRec.xlsx'

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
try {
    $wb = $excel.Workbooks.Open($target)
    if ($wb.ReadOnly) { throw 'FILE_IS_LOCKED_READONLY - закрой файл в Excel' }
    $ws = $wb.Worksheets.Item(1)

    $found = $false
    for ($r = 2; $r -le 40; $r++) {
        $txt = $ws.Cells.Item($r, 3).Text
        if ($txt -and $txt.StartsWith('Этап D')) {
            $before = $ws.Cells.Item($r, 2).Text
            $ws.Cells.Item($r, 2).Value2 = [char]::ConvertFromUtf32(0x1F504)  # 🔄
            $ws.Cells.Item($r, 2).Font.Name = 'Segoe UI Emoji'
            Write-Host ('FOUND row=' + $r + ' status_before=[' + $before + '] -> IN_WORK')
            $found = $true
            break
        }
    }
    if (-not $found) { throw 'STAGE_D_ROW_NOT_FOUND' }

    $wb.Save()
    $wb.Close($false)
    Write-Host 'SAVE_OK'
}
finally {
    $excel.Quit()
    [Runtime.InteropServices.Marshal]::ReleaseComObject($excel) | Out-Null
}
