# Шлёт клавиши в окно Chrome, найденное по подстроке заголовка (активирует по хендлу).
# -TitleLike <str> : подстрока заголовка
# -Keys <str>      : строка для SendKeys, например '^3' или '{PGDN}'
param(
    [string]$TitleLike,
    [string]$Keys
)

Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public class WinKeys {
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc cb, IntPtr lp);
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lp);
    [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr hWnd, StringBuilder sb, int max);
    [DllImport("user32.dll")] public static extern int GetClassName(IntPtr hWnd, StringBuilder sb, int max);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
}
"@
Add-Type -AssemblyName System.Windows.Forms

$windows = New-Object System.Collections.ArrayList
$cb = {
    param($h, $l)
    if ([WinKeys]::IsWindowVisible($h)) {
        $sbT = New-Object System.Text.StringBuilder 512
        $sbC = New-Object System.Text.StringBuilder 256
        [void][WinKeys]::GetWindowText($h, $sbT, 512)
        [void][WinKeys]::GetClassName($h, $sbC, 256)
        if ($sbC.ToString() -eq "Chrome_WidgetWin_1" -and $sbT.Length -gt 0) {
            [void]$windows.Add(@{ H = $h; Title = $sbT.ToString() })
        }
    }
    return $true
}
[void][WinKeys]::EnumWindows($cb, [IntPtr]::Zero)

$target = $windows | Where-Object { $_.Title -like "*$TitleLike*" } | Select-Object -First 1
if (-not $target) { Write-Error "Окно с заголовком *$TitleLike* не найдено"; exit 1 }

[void][WinKeys]::SetForegroundWindow($target.H)
Start-Sleep -Milliseconds 500
if ([WinKeys]::GetForegroundWindow() -ne $target.H) { Write-Error "Не удалось активировать окно, клавиши НЕ отправлены"; exit 1 }
[System.Windows.Forms.SendKeys]::SendWait($Keys)
Start-Sleep -Milliseconds 500
Write-Output ("OK sent '{0}' to | {1}" -f $Keys, $target.Title)
