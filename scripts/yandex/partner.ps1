# Yandex Partner (RSYa) statistics API. Key file: line 1 = statistics OAuth token,
# line 2 (optional) = ad unit settings OAuth token. Tokens are never printed.
# Docs: https://yandex.ru/dev/partner-statistics/doc/ru/
# Example: partner.ps1 -Path "/api/statistics2/tree.json?lang=ru" -OutFile out.json
# NOTE: keep this file ASCII-only (Windows PowerShell 5.1 misreads UTF-8 without BOM).
param(
    [string]$Path = "/api/statistics2/tree.json?lang=ru",
    [string]$OutFile = "",
    [int]$TokenLine = 1,
    [string]$KeyFile = "E:\ContrarySurvior\ContrarySurvivor\Saved\YandexPartnerKey.txt"
)
$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$lines = @(Get-Content -LiteralPath $KeyFile | ForEach-Object { $_.Trim() } | Where-Object { $_ })
if ($lines.Count -lt $TokenLine) { throw "Key file has no line $TokenLine" }
try {
    $r = Invoke-WebRequest -Uri ('https://partner.yandex.ru' + $Path) -Headers @{ Authorization = ('OAuth ' + $lines[$TokenLine - 1]) } -UseBasicParsing
    $bytes = $r.RawContentStream.ToArray()
    Write-Output ("HTTP {0}, {1} bytes" -f [int]$r.StatusCode, $bytes.Length)
    if ($OutFile) { [IO.File]::WriteAllBytes($OutFile, $bytes) }
    else { [Console]::OutputEncoding = [Text.Encoding]::UTF8; Write-Output ([Text.Encoding]::UTF8.GetString($bytes)) }
} catch {
    $resp = $_.Exception.Response
    if (-not $resp) { Write-Output ("REQUEST FAILED: " + $_.Exception.Message); exit 1 }
    $sr = New-Object IO.StreamReader($resp.GetResponseStream(), [Text.Encoding]::UTF8)
    Write-Output ("REQUEST FAILED: HTTP {0}: {1}" -f [int]$resp.StatusCode, $sr.ReadToEnd()); exit 1
}
