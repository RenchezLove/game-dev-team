# Захват содержимого окна Chrome через PrintWindow (без вмешательства в окно).
# -List            : показать все видимые окна Chrome с заголовками
# -TitleLike <str> : подстрока заголовка окна для захвата
# -Out <path>      : путь PNG
param(
    [switch]$List,
    [string]$TitleLike,
    [string]$Out
)

Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public class WinCap {
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc cb, IntPtr lp);
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lp);
    [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr hWnd, StringBuilder sb, int max);
    [DllImport("user32.dll")] public static extern int GetClassName(IntPtr hWnd, StringBuilder sb, int max);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT r);
    [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdc, uint flags);
    public struct RECT { public int Left, Top, Right, Bottom; }
}
"@

$windows = New-Object System.Collections.ArrayList
$cb = {
    param($h, $l)
    if ([WinCap]::IsWindowVisible($h)) {
        $sbT = New-Object System.Text.StringBuilder 512
        $sbC = New-Object System.Text.StringBuilder 256
        [void][WinCap]::GetWindowText($h, $sbT, 512)
        [void][WinCap]::GetClassName($h, $sbC, 256)
        if ($sbC.ToString() -eq "Chrome_WidgetWin_1" -and $sbT.Length -gt 0) {
            [void]$windows.Add(@{ H = $h; Title = $sbT.ToString() })
        }
    }
    return $true
}
[void][WinCap]::EnumWindows($cb, [IntPtr]::Zero)

if ($List) {
    foreach ($w in $windows) { Write-Output ("{0} | {1}" -f $w.H, $w.Title) }
    exit 0
}

$target = $windows | Where-Object { $_.Title -like "*$TitleLike*" } | Select-Object -First 1
if (-not $target) { Write-Error "Окно с заголовком *$TitleLike* не найдено"; exit 1 }

$r = New-Object WinCap+RECT
[void][WinCap]::GetWindowRect($target.H, [ref]$r)
$w = $r.Right - $r.Left; $h = $r.Bottom - $r.Top
if ($w -le 0 -or $h -le 0) { Write-Error "Нулевой размер окна"; exit 1 }

Add-Type -AssemblyName System.Drawing
$bmp = New-Object System.Drawing.Bitmap $w, $h
$g = [System.Drawing.Graphics]::FromImage($bmp)
$hdc = $g.GetHdc()
# 2 = PW_RENDERFULLCONTENT (нужно для Chrome)
$ok = [WinCap]::PrintWindow($target.H, $hdc, 2)
$g.ReleaseHdc($hdc)
$g.Dispose()
if (-not $ok) { Write-Error "PrintWindow вернул ошибку"; $bmp.Dispose(); exit 1 }
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()
Write-Output ("OK {0}x{1} -> {2} | {3}" -f $w, $h, $Out, $target.Title)
