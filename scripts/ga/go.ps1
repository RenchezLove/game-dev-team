param([int]$X=-1,[int]$Y=-1,[int]$Wait=5,[string]$Name="shot",[int]$Wheel=0)
Add-Type @"
using System; using System.Text; using System.Runtime.InteropServices;
public class F { [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
 [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder sb, int max); }
"@
$sb=New-Object System.Text.StringBuilder 512; [void][F]::GetWindowText([F]::GetForegroundWindow(),$sb,512)
if($sb.ToString() -notlike "*GameAnalytics*"){ Write-Output ("ABORT: foreground is not GA"); exit 2 }
$out=Join-Path $PSScriptRoot ($Name+".png")
& 'E:\game-dev-team\scripts\ga\panel.ps1' -X $X -Y $Y -Wait $Wait -Out $out -Wheel $Wheel
