$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.Encoding]::UTF8

$target = 'E:\game-dev-team\docs\contrary-survivor\DemoPlanTemplateRec.xlsx'

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
try {
    $wb = $excel.Workbooks.Open($target, 0, $true)  # read-only
    $ws = $wb.Worksheets.Item(1)
    $last = $ws.UsedRange.Rows.Count
    Write-Host ('USED_ROWS=' + $last)
    for ($r = 1; $r -le $last; $r++) {
        $b = $ws.Cells.Item($r, 2).Text
        $c = $ws.Cells.Item($r, 3).Text
        if ($b -or $c) {
            $cShort = $c -replace "`n", ' | '
            if ($cShort.Length -gt 220) { $cShort = $cShort.Substring(0, 220) + '...' }
            Write-Host ('ROW ' + $r + ' [B=' + $b + '] C=' + $cShort)
        }
    }
    $wb.Close($false)
}
finally {
    $excel.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
}
Write-Host 'READ_DONE'
