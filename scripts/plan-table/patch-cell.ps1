$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.Encoding]::UTF8

$target = 'E:\game-dev-team\docs\contrary-survivor\DemoPlanTemplate.xlsx'
$dataPath = $env:TEMP + '\xlsx_new\data2.json'

$rows = Get-Content -Raw -Encoding UTF8 $dataPath | ConvertFrom-Json

# индексы данных → строки листа: данные i → строка i+3
$patchIdx = @(3, 6, 9)   # Этап C, Этап F, Этап I

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
try {
    $wb = $excel.Workbooks.Open($target)
    if ($wb.ReadOnly) { throw 'FILE_IS_LOCKED_READONLY - закрой файл в Excel' }
    $ws = $wb.Worksheets.Item(1)

    foreach ($i in $patchIdx) {
        $r = $i + 3
        $row = $rows[$i]
        $before = $ws.Cells.Item($r, 3).Text
        if ($before.Substring(0, 6) -ne $row.title.Substring(0, 6)) {
            throw ('row mismatch at sheet row ' + $r + ': ' + $before.Substring(0, 20))
        }
        $full = $row.title + [char]10 + ($row.bullets -join [char]10)
        $ws.Cells.Item($r, 3).Value2 = $full
        $ws.Cells.Item($r, 3).WrapText = $true
        $ws.Cells.Item($r, 3).Characters(1, $row.title.Length).Font.Bold = $true
        $ws.Rows.Item($r).AutoFit() | Out-Null
        Write-Host ('PATCHED row=' + $r + ' [' + $row.title + '] lines=' + $full.Split([char]10).Count)
    }

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
    Write-Host ('VERIFY_C_WEST=' + ($ws2.Cells.Item(6, 3).Text -match 'логово волков — запад'))
    Write-Host ('VERIFY_C_LOOP=' + ($ws2.Cells.Item(6, 3).Text -match 'ПОДТВЕРЖДЕНО'))
    Write-Host ('VERIFY_F_MARK=' + ($ws2.Cells.Item(9, 3).Text -match 'Метка цели квеста'))
    Write-Host ('VERIFY_I_MAP=' + ($ws2.Cells.Item(12, 3).Text -match 'Миникарта'))
    $wb2.Close($false)
}
finally {
    $excel2.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel2) | Out-Null
}
Write-Host 'ALL_DONE'
