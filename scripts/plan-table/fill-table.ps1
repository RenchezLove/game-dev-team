$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.Encoding]::UTF8

function RGB($r, $g, $b) { return $r + $g * 256 + $b * 65536 }

$target = 'E:\game-dev-team\docs\contrary-survivor\DemoPlanTemplate.xlsx'
$backup = $env:TEMP + '\DemoPlanTemplate.orig.xlsx'
$dataPath = $env:TEMP + '\xlsx_new\data2.json'

Copy-Item $backup $target -Force
Write-Host 'RESTORED_FROM_BACKUP'

$rows = Get-Content -Raw -Encoding UTF8 $dataPath | ConvertFrom-Json
Write-Host ('DATA_ROWS=' + $rows.Count)

$colTitleBg = RGB 55 86 35      # тёмно-зелёный (название)
$colHeadBg  = RGB 84 130 53     # зелёный (шапка)
$colDoneBg  = RGB 226 239 218   # бледно-зелёный (готово)
$colWipBg   = RGB 255 242 204   # бледно-жёлтый (в работе)
$white      = RGB 255 255 255

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
try {
    $wb = $excel.Workbooks.Open($target)
    $ws = $wb.Worksheets.Item(1)

    # Строка-название сверху (шапка уезжает в строку 2, данные начнутся с 3)
    $ws.Rows.Item(1).Insert() | Out-Null

    $ws.Cells.Item(1, 1) = 'ContrarySurvivor — план демки (тестируемый и монетизируемый срез)'
    $titleRange = $ws.Range('A1:D1')
    $titleRange.Merge() | Out-Null
    $titleRange.Font.Bold = $true
    $titleRange.Font.Size = 14
    $titleRange.Font.Color = $white
    $titleRange.Interior.Color = $colTitleBg
    $titleRange.HorizontalAlignment = -4108  # center
    $titleRange.VerticalAlignment = -4108    # center
    $ws.Rows.Item(1).RowHeight = 32

    # Шапка (строка 2)
    $headRange = $ws.Range('A2:D2')
    $headRange.Font.Bold = $true
    $headRange.Font.Color = $white
    $headRange.Interior.Color = $colHeadBg
    $headRange.HorizontalAlignment = -4108
    $headRange.VerticalAlignment = -4108

    # Данные (строки 3..14)
    for ($i = 0; $i -lt $rows.Count; $i++) {
        $r = $i + 3
        $row = $rows[$i]
        $full = $row.title + [char]10 + ($row.bullets -join [char]10)

        $ws.Cells.Item($r, 1) = ($i + 1)
        if ($row.mark -ne '') { $ws.Cells.Item($r, 2) = $row.mark }
        $ws.Cells.Item($r, 3) = $full
        $ws.Cells.Item($r, 4) = $row.note

        $ws.Cells.Item($r, 3).Characters(1, $row.title.Length).Font.Bold = $true

        if ($row.mark -eq '✅') { $ws.Range('A' + $r + ':D' + $r).Interior.Color = $colDoneBg }
        if ($row.mark -eq '🔄') { $ws.Range('A' + $r + ':D' + $r).Interior.Color = $colWipBg }
    }

    $lastRow = $rows.Count + 2
    $dataRange = $ws.Range('A3:D' + $lastRow)
    $dataRange.WrapText = $true
    $dataRange.VerticalAlignment = -4160   # top
    $ws.Range('A3:B' + $lastRow).HorizontalAlignment = -4108
    $ws.Range('A3:B' + $lastRow).VerticalAlignment = -4108  # center — номер и отметка по центру строки

    # Цветные эмодзи в колонке отметок
    $bCol = $ws.Range('B3:B' + $lastRow)
    $bCol.Font.Name = 'Segoe UI Emoji'
    $bCol.Font.Size = 14

    # Границы всей таблицы
    $all = $ws.Range('A1:D' + $lastRow)
    $all.Borders.LineStyle = 1   # continuous
    $all.Borders.Weight = 2      # thin

    $dataRange.Rows.AutoFit() | Out-Null

    $wb.Save()
    $wb.Close($false)
    Write-Host 'FILL_SAVE_OK'
}
finally {
    $excel.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
}

# Верификация вторым открытием
$excel2 = New-Object -ComObject Excel.Application
$excel2.Visible = $false
$excel2.DisplayAlerts = $false
try {
    $wb2 = $excel2.Workbooks.Open($target)
    $ws2 = $wb2.Worksheets.Item(1)
    Write-Host ('VERIFY_OPEN_OK usedRows=' + $ws2.UsedRange.Rows.Count)
    Write-Host ('VERIFY_A1=' + $ws2.Cells.Item(1, 1).Text)
    Write-Host ('VERIFY_B3=' + $ws2.Cells.Item(3, 2).Text)
    Write-Host ('VERIFY_B6=' + $ws2.Cells.Item(6, 2).Text)
    $c6 = $ws2.Cells.Item(6, 3).Text
    Write-Host ('VERIFY_C6_HAS_NAVMESH=' + ($c6 -match 'навме|навига'))
    Write-Host ('VERIFY_C6_LINES=' + ($c6.Split([char]10).Count))
    $wb2.Close($false)
}
finally {
    $excel2.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel2) | Out-Null
}
Write-Host 'ALL_DONE'
