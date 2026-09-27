$k=(Get-Content "E:\ContrarySurvior\ContrarySurvivor\Saved\TripoAPIKey.txt" -Raw).Trim()
$dir="E:\ContrarySurvior\ContrarySurvivor\Saved\Tripo\car2"
foreach($v in @("front34","left","back","right")){
  $bytes=[IO.File]::ReadAllBytes("$dir\$v.png")
  $bd=[Guid]::NewGuid().ToString()
  $enc=[Text.Encoding]::GetEncoding("iso-8859-1")
  $head="--$bd`r`nContent-Disposition: form-data; name=`"file`"; filename=`"$v.png`"`r`nContent-Type: image/png`r`n`r`n"
  $tail="`r`n--$bd--`r`n"
  $body=[byte[]]($enc.GetBytes($head)+$bytes+$enc.GetBytes($tail))
  try { $r=Invoke-WebRequest -UseBasicParsing -Method Post -Uri "https://openapi.tripo3d.ai/v3/files" -Headers @{Authorization="Bearer $k"} -ContentType "multipart/form-data; boundary=$bd" -Body $body; "$v $($r.Content)" } catch { "$v ERR $($_.Exception.Message) $($_.ErrorDetails.Message)" }
}
