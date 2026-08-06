$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.Encoding]::UTF8

$target = 'E:\game-dev-team\docs\contrary-survivor\DemoPlanTemplateRec.xlsx'
$row = 10  # Этап G

$nl = [char]10
$extra = 'Подготовка к первой выкладке на RuStore (05–06.08): ревизия издателя и задание Б1–Б10:' + $nl +
  '- Проведена полная ревизия игры на живом телефоне (запуск, прохождение, кадры, журнал), отчёт принят издателем; по итогам издатель выдал задание из десяти пунктов Б1–Б10, работы шли строго по порядку.' + $nl +
  '- Б1: ассеты, терявшиеся при упаковке (анимация смерти людей, сектор удара ножа), возвращены в сборку — бандиты и игрок снова падают при смерти, сектор ножа виден.' + $nl +
  '- Б2: починена продажа стопками (раньше всё, кроме патронов, продавалось только по одной штуке), после этого заработала и золотая кнопка «продать дороже за просмотр ролика».' + $nl +
  '- Б3: сохранение теперь читается при запуске игры — игра различает «новую игру» и «продолжить», вступительная сценка показывается только новым игрокам.' + $nl +
  '- Б4: аналитика получила настоящие ключи, вшиваемые при сборке, и события первого запуска, шагов и завершения обучения; живая доставка событий на сервер пока не проверялась.' + $nl +
  '- Б5: публикационная сборка Shipping — все отладочные клавиши и счётчики вырезаны из кода при компиляции, подписи компьютерных клавиш убраны с экрана телефона.' + $nl +
  '- Б6: при первом запуске показывается экран согласия на обработку данных со ссылкой на политику конфиденциальности (тексты написаны, страница политики готова и ждёт публикации по постоянному адресу).' + $nl +
  '- Б7: экономика — новый игрок начинает только с ножом, пистолет стал первой целью накопления (150 монет у торговца), шкура волка подорожала с 2 до 15 монет, закрыта дыра «вода покупается за 5 и продаётся за 6».' + $nl +
  '- Б8: вёрстка магазина под телефон — сетка товаров растянута на пустовавшую половину экрана, колонки считаются по реальной ширине, подписи брони влезают в плитки.' + $nl +
  '- Б9: сборка объявляет поддержку вытянутых экранов (2.22 вместо 2.1) — чёрные поля по краям ушли; полосы здоровья и голода отодвинуты от выреза камеры.' + $nl +
  '- Создан ключ подписи для RuStore (хранить вечно: без него нельзя выпустить ни одно обновление); собран дистрибуционный пак Shipping с релизной подписью и выключенным флагом отладки.' + $nl +
  '- Осталось до выкладки: Б10 боевая реклама (три отдельных рекламных блока, ждёт рекламный кабинет Рината), публикация страницы политики в интернете, карточка игры в магазине RuStore.'

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
try {
    $wb = $excel.Workbooks.Open($target)
    if ($wb.ReadOnly) { throw 'FILE_IS_LOCKED_READONLY' }
    $ws = $wb.Worksheets.Item(1)

    $before = $ws.Cells.Item($row, 3).Text
    if ($before.Substring(0, 6) -ne 'Этап G') { throw ('row mismatch: ' + $before.Substring(0, 30)) }
    if ($before -match 'Б1–Б10') { Write-Host 'ALREADY_PRESENT'; $wb.Close($false); exit 0 }

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
    Write-Host ('VERIFY_REVIZIA=' + ($txt -match 'ревизия издателя'))
    Write-Host ('VERIFY_B7=' + ($txt -match 'целью накопления'))
    Write-Host ('VERIFY_KEY=' + ($txt -match 'ключ подписи'))
    Write-Host ('VERIFY_B10=' + ($txt -match 'боевая реклама'))
    Write-Host ('VERIFY_OLD_WAVE6_KEPT=' + ($txt -match 'разлочены'))
    $wb2.Close($false)
}
finally {
    $excel2.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel2) | Out-Null
}
Write-Host 'ALL_DONE'
