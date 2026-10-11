# RuStore publishing steps. Key file: line 1 = private key (base64 PKCS#8), line 2 = key ID. The key and the token are never printed.
# Docs: https://www.rustore.ru/help/work-with-rustore-api/api-upload-publication-app/
# Steps: draft (create a draft version), apk (upload the main apk), shots (list screenshots), shot-up, shot-del, shot-get, commit, status
# NOTE: keep this file ASCII-only (Windows PowerShell 5.1 misreads UTF-8 without BOM). Russian text is read from UTF-8 files.
param(
    [Parameter(Mandatory=$true)][ValidateSet('draft','apk','shots','shot-up','shot-del','shot-get','commit','status','detail')][string]$Step,
    [string]$Package = "com.renchezlove.contrarysurvivor",
    [string]$VersionId,
    [string]$WhatsNewFile,
    [string]$PublishType = "INSTANTLY",
    [string]$File,
    [string]$Orientation = "LANDSCAPE",
    [int]$Ordinal = -1,
    [string]$ShotId,
    [string]$Url,
    [string]$KeyFile = "E:\ContrarySurvior\ContrarySurvivor\Saved\RuStoreAPIKey.txt"
)
$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
[Console]::OutputEncoding = [Text.Encoding]::UTF8
Add-Type -AssemblyName System.Net.Http
$base = 'https://public-api.rustore.ru'

$lines = @(Get-Content -LiteralPath $KeyFile | ForEach-Object { $_.Trim() } | Where-Object { $_ })
if ($lines.Count -lt 2) { throw "Key file must have two lines: private key and key ID" }
$keyId = $lines[1]
$cng = [System.Security.Cryptography.CngKey]::Import([Convert]::FromBase64String($lines[0]), [System.Security.Cryptography.CngKeyBlobFormat]::Pkcs8PrivateBlob)
$rsa = New-Object System.Security.Cryptography.RSACng($cng)
$ts = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss.fffzzz")
$sig = [Convert]::ToBase64String($rsa.SignData([Text.Encoding]::UTF8.GetBytes($keyId + $ts), [System.Security.Cryptography.HashAlgorithmName]::SHA512, [System.Security.Cryptography.RSASignaturePadding]::Pkcs1))

$client = New-Object System.Net.Http.HttpClient
$client.Timeout = [TimeSpan]::FromMinutes(30)

function Send($method, $path, $content) {
    $req = New-Object System.Net.Http.HttpRequestMessage((New-Object System.Net.Http.HttpMethod($method)), ($base + $path))
    if ($script:token) { $req.Headers.Add('Public-Token', $script:token) }
    if ($content) { $req.Content = $content }
    $resp = $client.SendAsync($req).Result
    $text = [Text.Encoding]::UTF8.GetString($resp.Content.ReadAsByteArrayAsync().Result)
    Write-Output ("HTTP {0} {1} {2}" -f [int]$resp.StatusCode, $method, $path)
    Write-Output $text
}
function JsonBody($obj) {
    $json = $obj | ConvertTo-Json -Depth 6
    return (New-Object System.Net.Http.StringContent($json, [Text.Encoding]::UTF8, 'application/json'))
}
function FileBody($path) {
    # .NET puts the boundary in quotes; some servers answer 415 to that, so the header is rewritten without quotes.
    $boundary = 'rsb' + [Guid]::NewGuid().ToString('N')
    $mp = New-Object System.Net.Http.MultipartFormDataContent($boundary)
    $mp.Headers.Remove('Content-Type') | Out-Null
    $mp.Headers.TryAddWithoutValidation('Content-Type', 'multipart/form-data; boundary=' + $boundary) | Out-Null
    $fs = [IO.File]::OpenRead($path)
    $sc = New-Object System.Net.Http.StreamContent($fs)
    $types = @{ '.apk' = 'application/vnd.android.package-archive'; '.png' = 'image/png'; '.jpg' = 'image/jpeg' }
    $sc.Headers.ContentType = [System.Net.Http.Headers.MediaTypeHeaderValue]::Parse($types[[IO.Path]::GetExtension($path).ToLower()])
    $name = [IO.Path]::GetFileName($path)
    $sc.Headers.TryAddWithoutValidation('Content-Disposition', 'form-data; name="file"; filename="' + $name + '"') | Out-Null
    $mp.Add($sc)
    return ,$mp   # the comma keeps PowerShell from unrolling the multipart content into its parts
}

$authOut = Send 'POST' '/public/auth/' (JsonBody @{ keyId = $keyId; timestamp = $ts; signature = $sig })
$authJson = ($authOut | Select-Object -Last 1) | ConvertFrom-Json
if (-not $authJson.body.jwe) { Write-Output "AUTH FAILED"; Write-Output ($authOut | Select-Object -First 1); exit 1 }
$script:token = $authJson.body.jwe
Write-Output "AUTH: OK"

$app = "/public/v1/application/$Package"
$app2 = "/public/v2/application/$Package"
switch ($Step) {
    'status'   { Send 'GET' "$app/version?page=0&size=3" $null }
    'detail'   { Send 'GET' "$app2/version/$VersionId" $null }
    'draft'    {
        $body = @{ publishType = $PublishType }
        if ($WhatsNewFile) { $body.whatsNew = [IO.File]::ReadAllText($WhatsNewFile, [Text.Encoding]::UTF8).Trim() }
        Send 'POST' "$app/version" (JsonBody $body)
    }
    'apk'      { Send 'POST' "$app/version/$VersionId/apk?isMainApk=true&servicesType=Unknown" (FileBody $File) }
    'shots'    { Send 'GET' "$app2/version/$VersionId/image/screenshot?page=0&size=20" $null }
    'shot-up'  { Send 'POST' "$app2/version/$VersionId/image/screenshot/$Orientation/$Ordinal/SCREENSHOT" (FileBody $File) }
    'shot-del' { Send 'DELETE' "$app2/version/$VersionId/image/screenshot/$ShotId" $null }
    'shot-get' {
        $bytes = $client.GetByteArrayAsync($Url).Result
        [IO.File]::WriteAllBytes($File, $bytes)
        Write-Output ("saved {0} bytes to {1}" -f $bytes.Length, $File)
    }
    'commit'   { Send 'POST' "$app/version/$VersionId/commit?priorityUpdate=0" $null }
}
