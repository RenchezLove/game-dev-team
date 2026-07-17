$ErrorActionPreference='Stop'
$log='C:\Users\pgr40\AppData\Local\Temp\addJ.txt'
$add='Единый лут-конфиг по образцу STALKER (ADR-045): вся настройка выпадения добычи с врагов — в одной таблице данных (что падает, с каким шансом и в каком количестве); у врага есть ранг-опытность, который улучшает добычу (опытный враг даёт лут лучше, новичок — хуже); правится в редакторе без программиста.'
$excel=New-Object -ComObject Excel.Application
$excel.Visible=$false
$excel.DisplayAlerts=$false
try {
  $wb=$excel.Workbooks.Open('E:\game-dev-team\docs\contrary-survivor\DemoPlanTemplateRec.xlsx')
  if ($wb.ReadOnly) { throw 'FILE_IS_LOCKED_READONLY' }
  $ws=$wb.Worksheets.Item(1)
  $before=$ws.Cells.Item(13,3).Value2
  if ($before -notmatch 'J') { throw 'ROW13_NOT_STAGE_J' }
  if ($before -match 'ADR-045') { throw 'ALREADY_ADDED' }
  $titleLen=($before -split [char]10)[0].Length
  $full=$before.TrimEnd() + [char]10 + $add
  $ws.Cells.Item(13,3).Value2=$full
  $ws.Cells.Item(13,3).WrapText=$true
  $ws.Cells.Item(13,3).Characters(1,$titleLen).Font.Bold=$true
  $ws.Rows.Item(13).AutoFit() | Out-Null
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
  ('VERIFY_ADR045=' + ($ws2.Cells.Item(13,3).Value2 -match 'ADR-045')) | Out-File -FilePath $log -Append -Encoding UTF8
  $wb2.Close($false)
} finally { $excel2.Quit(); [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel2)|Out-Null }
