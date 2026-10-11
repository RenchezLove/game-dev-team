# Две белые картинки для синей метки побочного задания (цвет задаётся в файле окна):
# ромб-контур (метка над целью) и стрелка-контур остриём вверх (цель за краем экрана).
Add-Type -AssemblyName System.Drawing
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path

function New-Canvas([int]$size) {
    $bmp = New-Object System.Drawing.Bitmap $size, $size, ([System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $g.Clear([System.Drawing.Color]::Transparent)
    return $bmp, $g
}

function Draw-Outline($g, [System.Drawing.PointF[]]$points) {
    # Тёмная подложка шире белой линии — контур читается на светлой земле.
    $dark = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(230, 0, 0, 0)), 11
    $white = New-Object System.Drawing.Pen ([System.Drawing.Color]::White), 6
    foreach ($pen in $dark, $white) {
        $pen.LineJoin = [System.Drawing.Drawing2D.LineJoin]::Round
        $g.DrawPolygon($pen, $points)
        $pen.Dispose()
    }
}

# Ромб 64 на 64.
$bmp, $g = New-Canvas 64
Draw-Outline $g @(
    (New-Object System.Drawing.PointF 32, 7), (New-Object System.Drawing.PointF 57, 32),
    (New-Object System.Drawing.PointF 32, 57), (New-Object System.Drawing.PointF 7, 32))
$g.Dispose(); $bmp.Save((Join-Path $dir 'T_QuestSideMarker.png'), [System.Drawing.Imaging.ImageFormat]::Png); $bmp.Dispose()

# Стрелка-треугольник остриём вверх 64 на 64.
$bmp, $g = New-Canvas 64
Draw-Outline $g @(
    (New-Object System.Drawing.PointF 32, 8), (New-Object System.Drawing.PointF 55, 54),
    (New-Object System.Drawing.PointF 9, 54))
$g.Dispose(); $bmp.Save((Join-Path $dir 'T_QuestEdgeArrow.png'), [System.Drawing.Imaging.ImageFormat]::Png); $bmp.Dispose()
"готово"
