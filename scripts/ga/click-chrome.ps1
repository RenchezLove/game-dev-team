# Клик левой кнопкой мыши в окне Chrome по координатам кадра (пиксели окна).
# -TitleLike <str> : подстрока заголовка окна
# -X, -Y           : координаты внутри окна (как на снятом кадре)
param(
    [string]$TitleLike,
    [int]$X,
    [int]$Y
)

Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public class WinClick {
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc cb, IntPtr lp);
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lp);
    [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr hWnd, StringBuilder sb, int max);
    [DllImport("user32.dll")] public static extern int GetClassName(IntPtr hWnd, StringBuilder sb, int max);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT r);
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint flags, int dx, int dy, int data, IntPtr extra);
    public struct RECT { public int Left, Top, Right, Bottom; }
}
"@

$windows = New-Object System.Collections.ArrayList
$cb = {
    param($h, $l)
    if ([WinClick]::IsWindowVisible($h)) {
        $sbT = New-Object System.Text.StringBuilder 512
        $sbC = New-Object System.Text.StringBuilder 256
        [void][WinClick]::GetWindowText($h, $sbT, 512)
        [void][WinClick]::GetClassName($h, $sbC, 256)
        if ($sbC.ToString() -eq "Chrome_WidgetWin_1" -and $sbT.Length -gt 0) {
            [void]$windows.Add(@{ H = $h; Title = $sbT.ToString() })
        }
    }
    return $true
}
[void][WinClick]::EnumWindows($cb, [IntPtr]::Zero)

$target = $windows | Where-Object { $_.Title -like "*$TitleLike*" } | Select-Object -First 1
if (-not $target) { Write-Error "Окно с заголовком *$TitleLike* не найдено"; exit 1 }

$r = New-Object WinClick+RECT
[void][WinClick]::GetWindowRect($target.H, [ref]$r)
$cx = $r.Left + $X
$cy = $r.Top + $Y
[void][WinClick]::SetCursorPos($cx, $cy)
Start-Sleep -Milliseconds 250
# 0x0002 = LEFTDOWN, 0x0004 = LEFTUP
[WinClick]::mouse_event(0x0002, 0, 0, 0, [IntPtr]::Zero)
Start-Sleep -Milliseconds 80
[WinClick]::mouse_event(0x0004, 0, 0, 0, [IntPtr]::Zero)
Write-Output ("OK click at window {0},{1} (screen {2},{3}) | {4}" -f $X, $Y, $cx, $cy, $target.Title)
