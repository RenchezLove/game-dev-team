$ProgressPreference='SilentlyContinue'
$k=(Get-Content "E:\ContrarySurvior\ContrarySurvivor\Saved\TripoAPIKey.txt" -Raw).Trim()
$dir="E:\ContrarySurvior\ContrarySurvivor\Saved\Tripo\cloth_t1"
$H=@{Authorization="Bearer $k"}
function Bal { (Invoke-WebRequest -UseBasicParsing -Uri "https://openapi.tripo3d.ai/v3/account/balance" -Headers $H).Content }
"BALANCE before: "+(Bal)
$bytes=[IO.File]::ReadAllBytes("$dir\ref.png")
$bd=[Guid]::NewGuid().ToString(); $enc=[Text.Encoding]::GetEncoding("iso-8859-1")
$head="--$bd`r`nContent-Disposition: form-data; name=`"file`"; filename=`"ref.png`"`r`nContent-Type: image/png`r`n`r`n"; $tail="`r`n--$bd--`r`n"
$body=[byte[]]($enc.GetBytes($head)+$bytes+$enc.GetBytes($tail))
try { $r=Invoke-WebRequest -UseBasicParsing -Method Post -Uri "https://openapi.tripo3d.ai/v3/files" -Headers $H -ContentType "multipart/form-data; boundary=$bd" -Body $body } catch { "UPLOAD ERR $($_.Exception.Message) $($_.ErrorDetails.Message)"; exit 1 }
"UPLOAD: "+$r.Content
$j=$r.Content | ConvertFrom-Json
$tok=$j.data.file_token; if(-not $tok){ $tok=$j.data.image_token }
if(-not $tok){ "NO TOKEN"; exit 1 }
$req=@{model="P1-20260311";input=$tok;face_limit=2500;auto_size=$true;pbr=$false} | ConvertTo-Json -Compress
[IO.File]::WriteAllText("$dir\body.json",$req)
try { $r=Invoke-WebRequest -UseBasicParsing -Method Post -Uri "https://openapi.tripo3d.ai/v3/generation/image-to-model" -Headers $H -ContentType "application/json" -Body $req } catch { "CREATE ERR $($_.Exception.Message) $($_.ErrorDetails.Message)"; exit 1 }
"CREATE: "+$r.Content
$tid=($r.Content | ConvertFrom-Json).data.task_id
[IO.File]::WriteAllText("$dir\task.txt",$tid)
for($i=0;$i -lt 90;$i++){
  Start-Sleep -Seconds 8
  $s=(Invoke-WebRequest -UseBasicParsing -Uri "https://openapi.tripo3d.ai/v3/tasks/$tid" -Headers $H).Content
  $d=($s | ConvertFrom-Json).data
  if($d.status -in @('success','failed','cancelled','banned','expired')){ break }
}
[IO.File]::WriteAllText("$dir\result.json",$s)
"STATUS: "+$d.status+" credits="+$d.credits_consumed
if($d.status -eq 'success'){
  $o=$d.output
  $o | ConvertTo-Json -Depth 5
  $mu=$o.model_url; if(-not $mu){ $mu=$o.pbr_model_url }; if(-not $mu){ $mu=$o.base_model_url }
  if($mu){ Invoke-WebRequest -UseBasicParsing -Uri $mu -OutFile "$dir\cloth_t1.glb" }
  if($o.rendered_image_url){ Invoke-WebRequest -UseBasicParsing -Uri $o.rendered_image_url -OutFile "$dir\cloth_t1_render.webp" }
}
"BALANCE after: "+(Bal)
Get-ChildItem $dir | ForEach-Object { "{0} {1}" -f $_.Name,$_.Length }
