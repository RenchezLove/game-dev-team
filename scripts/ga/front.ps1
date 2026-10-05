Add-Type @"
using System; using System.Text; using System.Runtime.InteropServices;
public class G { public delegate bool P(IntPtr h, IntPtr lp);
 [DllImport("user32.dll")] public static extern bool EnumWindows(P cb, IntPtr lp);
 [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder sb, int max);
 [DllImport("user32.dll")] public static extern int GetClassName(IntPtr h, StringBuilder sb, int max);
 [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
 [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
 [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
 [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
 [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
 [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a, uint b, bool f);
 [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId(); }
"@
$script:t=$null
$cb={ param($h,$l) if([G]::IsWindowVisible($h)){ $a=New-Object System.Text.StringBuilder 512; $c=New-Object System.Text.StringBuilder 256; [void][G]::GetWindowText($h,$a,512); [void][G]::GetClassName($h,$c,256); if($c.ToString() -eq "Chrome_WidgetWin_1" -and $a.ToString() -like "*GameAnalytics*" -and -not $script:t){ $script:t=$h } } return $true }
[void][G]::EnumWindows($cb,[IntPtr]::Zero)
if(-not $script:t){ "NO WINDOW"; exit 1 }
$fg=[G]::GetForegroundWindow(); $p=0
$ft=[G]::GetWindowThreadProcessId($fg,[ref]$p); $me=[G]::GetCurrentThreadId()
[void][G]::AttachThreadInput($me,$ft,$true)
[void][G]::ShowWindow($script:t,6); Start-Sleep -Milliseconds 300; [void][G]::ShowWindow($script:t,3)
[void][G]::BringWindowToTop($script:t); [void][G]::SetForegroundWindow($script:t)
[void][G]::AttachThreadInput($me,$ft,$false)
Start-Sleep -Milliseconds 900
$sb=New-Object System.Text.StringBuilder 512; [void][G]::GetWindowText([G]::GetForegroundWindow(),$sb,512)
"FG: " + ($sb.ToString() -replace '[^\x20-\x7E]','?')
