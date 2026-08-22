# Прокрутка окна Chrome колесом мыши: активирует окно, ставит курсор в центр, крутит колесо.
# -TitleLike <str> : подстрока заголовка окна
# -Clicks <int>    : сколько щелчков колеса (отрицательное = вниз)
param(
    [string]$TitleLike,
    [int]$Clicks = -10,
    [double]$XFrac = 0.5,
    [double]$YFrac = 0.5
)

Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public class WinScroll {
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc cb, IntPtr lp);
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lp);
    [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr hWnd, StringBuilder sb, int max);
    [DllImport("user32.dll")] public static extern int GetClassName(IntPtr hWnd, StringBuilder sb, int max);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT r);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint flags, int dx, int dy, int data, IntPtr extra);
    public struct RECT { public int Left, Top, Right, Bottom; }
}
"@

$windows = New-Object System.Collections.ArrayList
$cb = {
    param($h, $l)
    if ([WinScroll]::IsWindowVisible($h)) {
        $sbT = New-Object System.Text.StringBuilder 512
        $sbC = New-Object System.Text.StringBuilder 256
        [void][WinScroll]::GetWindowText($h, $sbT, 512)
        [void][WinScroll]::GetClassName($h, $sbC, 256)
        if ($sbC.ToString() -eq "Chrome_WidgetWin_1" -and $sbT.Length -gt 0) {
            [void]$windows.Add(@{ H = $h; Title = $sbT.ToString() })
        }
    }
    return $true
}
[void][WinScroll]::EnumWindows($cb, [IntPtr]::Zero)

$target = $windows | Where-Object { $_.Title -like "*$TitleLike*" } | Select-Object -First 1
if (-not $target) { Write-Error "Окно с заголовком *$TitleLike* не найдено"; exit 1 }

[void][WinScroll]::SetForegroundWindow($target.H)
Start-Sleep -Milliseconds 400
$r = New-Object WinScroll+RECT
[void][WinScroll]::GetWindowRect($target.H, [ref]$r)
$cx = [int]($r.Left + ($r.Right - $r.Left) * $XFrac)
$cy = [int]($r.Top + ($r.Bottom - $r.Top) * $YFrac)
[void][WinScroll]::SetCursorPos($cx, $cy)
Start-Sleep -Milliseconds 200

$dir = if ($Clicks -lt 0) { -120 } else { 120 }
$n = [Math]::Abs($Clicks)
for ($i = 0; $i -lt $n; $i++) {
    # 0x0800 = MOUSEEVENTF_WHEEL
    [WinScroll]::mouse_event(0x0800, 0, 0, $dir, [IntPtr]::Zero)
    Start-Sleep -Milliseconds 120
}
Write-Output ("OK scrolled {0} clicks at {1},{2} | {3}" -f $Clicks, $cx, $cy, $target.Title)
