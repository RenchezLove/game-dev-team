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

    # Ищем строку этапа E по колонке C (Value2 — не .Text, эмодзи ломают .Text)
    $rowE = 0
    for ($r = 2; $r -le 25; $r++) {
        $v = $ws.Cells.Item($r, 3).Value2
        if ($v -and $v.ToString().TrimStart().StartsWith('Этап E')) { $rowE = $r; break }
    }
    if ($rowE -eq 0) { throw 'ROW_E_NOT_FOUND' }
    $cur = $ws.Cells.Item($rowE, 3).Value2.ToString()
    Write-Host ('FOUND row=' + $rowE + ' first60=[' + $cur.Substring(0, [Math]::Min(60, $cur.Length)).Replace([string][char]10,' / ') + ']')

    # Статус: зелёная галочка шрифтом Segoe UI Emoji
    $check = [char]::ConvertFromUtf32(0x2705)
    $ws.Cells.Item($rowE, 2).Value2 = $check
    $ws.Cells.Item($rowE, 2).Font.Name = 'Segoe UI Emoji'

    # Дописываем блок «Дополнительно» ВНИЗ прочитанного содержимого (добавление, не перезапись)
    if ($cur -notmatch 'Дополнительно \(сверх плана этапа\)') {
        $extra = @(
            'Дополнительно (сверх плана этапа):',
            '- Игрок начинает совсем без брони; стартовый облик — одежда Т0 (не предмет, защиты не даёт), белого манекена больше нет',
            '- 9 новых иконок предметов брони (нарисованы concept, утверждены Ринатом) + иконки пустых слотов заведены в игру',
            '- Инвентарь: иконки в слотах, строка «Защита: N%», подписи переведены на русский',
            '- Магазин: показ прибавки защиты у брони до покупки; старая броня _01 убрана из каталога (ассет цел)',
            '- Цены (50/120/250 за слот) и защита тиров — настраиваемые на размещённом экземпляре в редакторе',
            '- Новый автотест «после старта защита нулевая»; сборка и тесты — независимый прогон qa'
        ) -join [char]10
        $ws.Cells.Item($rowE, 3).Value2 = $cur + [char]10 + $extra
        $ws.Cells.Item($rowE, 3).WrapText = $true
        $ws.Rows.Item($rowE).AutoFit() | Out-Null
        Write-Host 'EXTRA_APPENDED'
    } else {
        Write-Host 'EXTRA_ALREADY_PRESENT'
    }

    $wb.Save()
    $wb.Close($false)
    Write-Host 'SAVE_OK'
}
finally {
    $excel.Quit()
    [Runtime.InteropServices.Marshal]::ReleaseComObject($excel) | Out-Null
}
