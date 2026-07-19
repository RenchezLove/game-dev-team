Add-Type -AssemblyName System.Drawing
$pairs = @(
    @('ScreenShot00009.png', 'shot-01-spawn-village-hud.png'),
    @('ScreenShot00011.png', 'shot-04-onboarding-trader-prompt.png'),
    @('ScreenShot00012.png', 'shot-07-death-screen.png'),
    @('ScreenShot00015.png', 'shot-06-combat-wolves.png'),
    @('ScreenShot00017.png', 'shot-05-inventory.png')
)
$srcDir = 'E:\ContrarySurvior\ContrarySurvivor\Saved\Screenshots\WindowsEditor\'
$dstDir = 'E:\game-dev-team\docs\contrary-survivor\publisher-review-2026-07-19\'
foreach ($p in $pairs) {
    $img = [System.Drawing.Image]::FromFile($srcDir + $p[0])
    if ($img.Width -eq 2582) { $rect = New-Object System.Drawing.Rectangle 18, 176, 1973, 1053 }
    elseif ($img.Width -eq 2265) { $rect = New-Object System.Drawing.Rectangle 14, 170, 1730, 962 }
    else { Write-Output ('SKIP_UNKNOWN_SIZE ' + $p[0] + ' ' + $img.Width); $img.Dispose(); continue }
    $bmp = New-Object System.Drawing.Bitmap $rect.Width, $rect.Height
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.DrawImage($img, (New-Object System.Drawing.Rectangle 0, 0, $rect.Width, $rect.Height), $rect, [System.Drawing.GraphicsUnit]::Pixel)
    $g.Dispose(); $img.Dispose()
    $bmp.Save($dstDir + $p[1], [System.Drawing.Imaging.ImageFormat]::Png)
    $bmp.Dispose()
    Write-Output ('OK ' + $p[1])
}
