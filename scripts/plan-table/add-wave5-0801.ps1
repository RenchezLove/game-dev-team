$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.Encoding]::UTF8

$target = 'E:\game-dev-team\docs\contrary-survivor\DemoPlanTemplateRec.xlsx'
$row = 10  # Этап G

$nl = [char]10
$extra = '- Сценка старосты после сдачи ноутбука переписана: он рассказывает про охоту на волков, шкуры и новый завоз у торговца (новая броня, скоро оружие), это заработок, а не квест.' + $nl +
  '- Через полминуты после этой сценки один раз за сохранение показывается компактное сообщение о конце сюжета текущей версии с кнопками «Написать мне» (ссылка появится позже) и «Играть дальше».' + $nl +
  '- Маркеры показываются по необходимости: после интро виден только маркер деревни, у деревни он сменяется маркером старосты, дальше остаются только квестовые.' + $nl +
  '- Три точки рекламы за награду по ТЗ издателя работают на временной заглушке ролика: спасение рюкзака на экране смерти, продажа на половину дороже у торговца и удвоение ежедневной награды; события аналитики уходят по-настоящему.' + $nl +
  '- Потери при смерти стали ощутимее: теряется 70 процентов расходников и половина денег, а после просмотра ролика — только по 10 процентов; половина потерянного падает мешком на месте гибели.' + $nl +
  '- Появились анимации смерти: бандиты ложатся на спину, волки на бок; волк перекрашен из коричневого в серый; серый шар лута заменён вещмешком, а у волков — свёртком шкуры.' + $nl +
  '- Положение пистолета в руке теперь настраивается наглядно перемещением сокета в редакторе скелета; торговец получил собственную модель по референсу.' + $nl +
  '- Всё собрано и проверено чистой пересборкой, 26 автотестами и проверками ассетов; волна ждёт живой приёмки в игре.'

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
try {
    $wb = $excel.Workbooks.Open($target)
    if ($wb.ReadOnly) { throw 'FILE_IS_LOCKED_READONLY' }
    $ws = $wb.Worksheets.Item(1)

    $before = $ws.Cells.Item($row, 3).Text
    if ($before.Substring(0, 6) -ne 'Этап G') { throw ('row mismatch: ' + $before.Substring(0, 30)) }
    if ($before -match 'конце сюжета') { Write-Host 'ALREADY_PRESENT'; $wb.Close($false); exit 0 }

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
    Write-Host ('VERIFY_STORY=' + ($txt -match 'конце сюжета'))
    Write-Host ('VERIFY_MARKERS=' + ($txt -match 'маркером старосты'))
    Write-Host ('VERIFY_ADS=' + ($txt -match 'заглушке ролика'))
    Write-Host ('VERIFY_LOSS=' + ($txt -match '70 процентов'))
    Write-Host ('VERIFY_DEATH=' + ($txt -match 'на спину'))
    Write-Host ('VERIFY_SOCKET=' + ($txt -match 'сокета'))
    Write-Host ('VERIFY_OLD_B11_KEPT=' + ($txt -match 'пульсирует'))
    $wb2.Close($false)
}
finally {
    $excel2.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel2) | Out-Null
}
Write-Host 'ALL_DONE'
