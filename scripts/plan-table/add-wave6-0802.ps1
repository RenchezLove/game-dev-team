$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.Encoding]::UTF8

$target = 'E:\game-dev-team\docs\contrary-survivor\DemoPlanTemplateRec.xlsx'
$row = 10  # Этап G

$nl = [char]10
$extra = 'Волна Build 1.2.1 (ночь 02.08, по замечаниям живой приёмки Build 1.2):' + $nl +
  '- Трупы волков и бандитов теперь можно обыскивать: подсказка у трупа, окно выбора добычи с забором по клику и кнопкой «Забрать всё», недобранное остаётся в трупе, труп лежит настраиваемые 60 секунд.' + $nl +
  '- Починены «серые» мешки и свёртки: в моделях сидел служебный шахматный материал движка, заменён на игровой; свёрток шкуры больше не микроскопический; у вещмешка появилось настраиваемое свечение с пульсацией (по умолчанию выключено).' + $nl +
  '- Порог доступности рекламы снижен с 15 до 6 минут и настраивается без пересборки; добавлена отладочная клавиша F, мгновенно открывающая рекламные кнопки для проверки.' + $nl +
  '- Шкуры, тушёнка и аптечки складываются в стопки как патроны: подбор, продажа ползунком, потери при смерти и зачёт квеста работают по штукам (покрыто автотестами).' + $nl +
  '- При гибели герой ложится на спину той же анимацией, что и бандиты, и штатно оживает при возрождении.' + $nl +
  '- Все 12 окон интерфейса разлочены по задаче Рината: каждый текст и каждая кнопка лежат на свободном поле и двигаются мышкой в редакторе; прежняя ручная расстановка перенесена один в один; памятка по окнам обновлена.' + $nl +
  '- Волна проверена полной чистой пересборкой, 32 автотестами и проверками всех окон; ждёт живой приёмки в игре, после неё обе волны вливаются в основную ветку.'

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
try {
    $wb = $excel.Workbooks.Open($target)
    if ($wb.ReadOnly) { throw 'FILE_IS_LOCKED_READONLY' }
    $ws = $wb.Worksheets.Item(1)

    $before = $ws.Cells.Item($row, 3).Text
    if ($before.Substring(0, 6) -ne 'Этап G') { throw ('row mismatch: ' + $before.Substring(0, 30)) }
    if ($before -match 'разлочены') { Write-Host 'ALREADY_PRESENT'; $wb.Close($false); exit 0 }

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
    Write-Host ('VERIFY_CORPSE=' + ($txt -match 'обыскивать'))
    Write-Host ('VERIFY_PICKUP=' + ($txt -match 'шахматный'))
    Write-Host ('VERIFY_ADS6=' + ($txt -match 'с 15 до 6'))
    Write-Host ('VERIFY_STACKS=' + ($txt -match 'стопки'))
    Write-Host ('VERIFY_UNLOCK=' + ($txt -match 'разлочены'))
    Write-Host ('VERIFY_OLD_WAVE5_KEPT=' + ($txt -match 'конце сюжета'))
    $wb2.Close($false)
}
finally {
    $excel2.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel2) | Out-Null
}
Write-Host 'ALL_DONE'
