if (-not ([System.Management.Automation.PSTypeName]'W').Type) {
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class W {
  [StructLayout(LayoutKind.Sequential)] public struct P { public int X; public int Y; }
  [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
  [DllImport("user32.dll")] public static extern bool GetCursorPos(out P p);
}
"@
}
[W]::SetProcessDPIAware() | Out-Null

Write-Host "Pozycja myszy (Ctrl+C = koniec)"
while ($true) {
    $pt = New-Object W+P
    [W]::GetCursorPos([ref]$pt) | Out-Null
    Write-Host ("`rX={0,5}  Y={1,5}   " -f $pt.X, $pt.Y) -NoNewline
    Start-Sleep -Milliseconds 50
}