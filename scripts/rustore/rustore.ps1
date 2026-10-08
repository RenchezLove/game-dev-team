# RuStore public API access. Key file: line 1 = private key (base64 PKCS#8), line 2 = key ID.
# The key and the token are never printed.
# Docs: https://www.rustore.ru/help/work-with-rustore-api/api-authorization-token
# Example: rustore.ps1 -Path "/public/v1/application"
# NOTE: keep this file ASCII-only (Windows PowerShell 5.1 misreads UTF-8 without BOM).
param(
    [string]$Path = "/public/v1/application",
    [string]$Method = "GET",
    [string]$KeyFile = "E:\ContrarySurvior\ContrarySurvivor\Saved\RuStoreAPIKey.txt"
)
$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$base = 'https://public-api.rustore.ru'

$lines = @(Get-Content -LiteralPath $KeyFile | ForEach-Object { $_.Trim() } | Where-Object { $_ })
if ($lines.Count -lt 2) { throw "Key file must have two lines: private key and key ID" }
$keyId = $lines[1]

$cng = [System.Security.Cryptography.CngKey]::Import(
    [Convert]::FromBase64String($lines[0]),
    [System.Security.Cryptography.CngKeyBlobFormat]::Pkcs8PrivateBlob)
$rsa = New-Object System.Security.Cryptography.RSACng($cng)
$ts = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss.fffzzz")
$sig = [Convert]::ToBase64String($rsa.SignData(
    [Text.Encoding]::UTF8.GetBytes($keyId + $ts),
    [System.Security.Cryptography.HashAlgorithmName]::SHA512,
    [System.Security.Cryptography.RSASignaturePadding]::Pkcs1))

function Read-ErrorBody($err) {
    $resp = $err.Exception.Response
    if (-not $resp) { return $err.Exception.Message }
    $sr = New-Object IO.StreamReader($resp.GetResponseStream(), [Text.Encoding]::UTF8)
    return ("HTTP {0}: {1}" -f [int]$resp.StatusCode, $sr.ReadToEnd())
}

try {
    $authBody = @{ keyId = $keyId; timestamp = $ts; signature = $sig } | ConvertTo-Json
    $auth = Invoke-RestMethod -Uri ($base + '/public/auth/') -Method Post -ContentType 'application/json' -Body $authBody
} catch { Write-Output ("AUTH FAILED: " + (Read-ErrorBody $_)); exit 1 }

if (-not $auth.body.jwe) { Write-Output ("AUTH FAILED: " + ($auth | ConvertTo-Json -Depth 5)); exit 1 }
Write-Output ("AUTH: " + $auth.code + ", token length " + $auth.body.jwe.Length)

try {
    $r = Invoke-WebRequest -Uri ($base + $Path) -Method $Method -Headers @{ 'Public-Token' = $auth.body.jwe } -UseBasicParsing
    $out = [Text.Encoding]::UTF8.GetString($r.RawContentStream.ToArray())
    [Console]::OutputEncoding = [Text.Encoding]::UTF8
    Write-Output $out
} catch { Write-Output ("REQUEST FAILED: " + (Read-ErrorBody $_)); exit 1 }
