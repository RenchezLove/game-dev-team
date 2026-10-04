param([string]$TitleLike="GameAnalytics",[int]$X=-1,[int]$Y=-1,[int]$Wait=6,[string]$Out,[int]$Wheel=0)
Add-Type @"
using System; using System.Text; using System.Runtime.InteropServices;
public class W {
  [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
  [DllImport("user32.dll")] public static extern bool EnumWindows(P cb, IntPtr lp);
  public delegate bool P(IntPtr h, IntPtr lp);
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder sb, int max);
  [DllImport("user32.dll")] public static extern int GetClassName(IntPtr h, StringBuilder sb, int max);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out R r);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr hdc, uint f);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f, int dx, int dy, int d, IntPtr e);
  public struct R { public int L, T, Rt, B; }
}
"@
[void][W]::SetProcessDPIAware()
$script:t=$null
$cb={ param($h,$l) if([W]::IsWindowVisible($h)){ $a=New-Object System.Text.StringBuilder 512; $c=New-Object System.Text.StringBuilder 256; [void][W]::GetWindowText($h,$a,512); [void][W]::GetClassName($h,$c,256); if($c.ToString() -eq "Chrome_WidgetWin_1" -and $a.ToString() -like "*$TitleLike*" -and -not $script:t){ $script:t=$h } } return $true }
[void][W]::EnumWindows($cb,[IntPtr]::Zero)
if(-not $script:t){ Write-Output "NO WINDOW"; exit 1 }
$r=New-Object W+R; [void][W]::GetWindowRect($script:t,[ref]$r)
if($X -ge 0){ [void][W]::SetCursorPos($r.L+$X,$r.T+$Y); Start-Sleep -Milliseconds 300; if($Wheel -ne 0){ for($i=0;$i -lt [Math]::Abs($Wheel);$i++){ [W]::mouse_event(0x0800,0,0,[int](-120*[Math]::Sign($Wheel)),[IntPtr]::Zero); Start-Sleep -Milliseconds 120 } } else { [W]::mouse_event(2,0,0,0,[IntPtr]::Zero); Start-Sleep -Milliseconds 80; [W]::mouse_event(4,0,0,0,[IntPtr]::Zero) }; Start-Sleep -Seconds $Wait }
if($Out){ Add-Type -AssemblyName System.Drawing; $w=$r.Rt-$r.L; $h=$r.B-$r.T; $bmp=New-Object System.Drawing.Bitmap $w,$h; $g=[System.Drawing.Graphics]::FromImage($bmp); $hdc=$g.GetHdc(); [void][W]::PrintWindow($script:t,$hdc,2); $g.ReleaseHdc($hdc); $bmp.Save($Out); Write-Output ("rect {0},{1} {2}x{3} -> {4}" -f $r.L,$r.T,$w,$h,$Out) }
