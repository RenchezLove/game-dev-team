$ErrorActionPreference='Stop'
$log='C:\Users\pgr40\AppData\Local\Temp\closeF.txt'
$nl=[char]10
$add='Дополнительно (сверх плана этапа):' + $nl +
'Лут бандитов: деньги + 1-2 расходника с равной вероятностью из настраиваемой таблицы (Консервы / Вода / Бинт), русские имена расходников во всей игре (решения Рината 07-17).' + $nl +
'Звук: исправлены бесконечные «охи» при попадании (короткий случайный кусок звука + защита от спама), выстрел вдвое громче; птички и шаги не тронуты.' + $nl +
'Для аналитики заведён латинский идентификатор товара — русские имена ломали бы статистику покупок.' + $nl +
'Починена тестовая обвязка: тест NavWalkingFixed позеленел (15 из 16 зелёных).' + $nl +
'Правки по приёмке 07-12: тон диалога Q3 (староста предлагает, а не приказывает), высота панели диалога по числу строк, метки квестов работают в BP из коробки.'
$excel=New-Object -ComObject Excel.Application
$excel.Visible=$false
$excel.DisplayAlerts=$false
try {
  $wb=$excel.Workbooks.Open('E:\game-dev-team\docs\contrary-survivor\DemoPlanTemplateRec.xlsx')
  if ($wb.ReadOnly) { throw 'FILE_IS_LOCKED_READONLY' }
  $ws=$wb.Worksheets.Item(1)
  $before=$ws.Cells.Item(9,3).Value2
  if ($before -notmatch 'F') { throw 'ROW9_NOT_STAGE_F' }
  if ($before -match 'сверх плана') { throw 'ALREADY_ADDED' }
  $titleLen=($before -split [char]10)[0].Length
  $full=$before.TrimEnd() + $nl + $add
  $ws.Cells.Item(9,3).Value2=$full
  $ws.Cells.Item(9,3).WrapText=$true
  $ws.Cells.Item(9,3).Characters(1,$titleLen).Font.Bold=$true
  $ws.Cells.Item(9,2).Value2=[char]::ConvertFromUtf32(0x2705)
  $ws.Cells.Item(9,2).Font.Name='Segoe UI Emoji'
  $ws.Rows.Item(9).AutoFit() | Out-Null
  $wb.Save()
  $wb.Close($false)
  'SAVE_OK' | Out-File -FilePath $log -Encoding UTF8
} catch {
  ('ERROR: ' + $_.Exception.Message) | Out-File -FilePath $log -Encoding UTF8
} finally { $excel.Quit(); [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel)|Out-Null }
$excel2=New-Object -ComObject Excel.Application
$excel2.Visible=$false
$excel2.DisplayAlerts=$false
try {
  $wb2=$excel2.Workbooks.Open('E:\game-dev-team\docs\contrary-survivor\DemoPlanTemplateRec.xlsx',$null,$true)
  $ws2=$wb2.Worksheets.Item(1)
  $statusCode=[int][char](($ws2.Cells.Item(9,2).Value2)[0])
  ('VERIFY_EXTRA=' + ($ws2.Cells.Item(9,3).Value2 -match 'сверх плана')) | Out-File -FilePath $log -Append -Encoding UTF8
  ('VERIFY_STATUS_CODEPOINT=' + $statusCode) | Out-File -FilePath $log -Append -Encoding UTF8
  $wb2.Close($false)
} finally { $excel2.Quit(); [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel2)|Out-Null }
