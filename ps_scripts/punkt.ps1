# punkt.ps1 - NAGRYWANIE skryptow automatyzacji (scripts\NAZWA.txt)
#
# Uzycie:   .\punkt.ps1 -Nazwa olx_test
# Wynik:    dopisuje linie do ..\scripts\olx_test.txt (tworzy plik, jesli brak)
#
# Akcje (wpisz litere + Enter):
#   Enter  odliczanie 3 s, zapis "MOVE x y" + "CLICK" w miejscu kursora
#   m      jak Enter, ale tylko "MOVE x y" (bez klikniecia)
#   w      pyta o ms, zapis "WAIT ms"
#   t      pyta o tekst, zapis "TYPE tekst" (tylko ASCII, bez polskich znakow)
#   k      koniec (Ctrl+C tez dziala, zapisane linie zostaja)
#   r      pyta o program/adres, zapis: HOTKEY GUI R, WAIT 700, TYPE x, KEY ENTER, WAIT 2500
#
# Uwagi:
#   - w czasie odliczania ustaw mysz na celu; 3 s to czas na przejscie
#   - wspolrzedne sa w prawdziwych pikselach ekranu (skrypt ignoruje skalowanie DPI)
#   - plik na Pico trafia przez: .\uruchom.ps1 -Nazwa olx_test

# punkt.ps1 -Nazwa olx_test
param([Parameter(Mandatory)][string]$Nazwa)
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class W {
  [StructLayout(LayoutKind.Sequential)] public struct P { public int X; public int Y; }
  [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
  [DllImport("user32.dll")] public static extern bool GetCursorPos(out P p);
}
"@
[W]::SetProcessDPIAware() | Out-Null
$plik = Join-Path (Split-Path $PSScriptRoot -Parent) "scripts\$Nazwa.txt"
New-Item -ItemType Directory -Force (Split-Path $plik) | Out-Null
if (-not (Test-Path $plik)) { "# $Nazwa" | Set-Content $plik -Encoding ASCII }
Write-Host "Plik: $plik"
Write-Host "Enter = MOVE+CLICK, m = tylko MOVE, w = WAIT, t = TYPE, k = koniec,r=GUI"
while ($true) {
  $o = Read-Host "Akcja"
  if ($o -eq 'k') { break }
  if ($o -eq 'w') {
    $ms = Read-Host "WAIT ms"
    Add-Content $plik "WAIT $ms" -Encoding ASCII; continue
  }
  if ($o -eq 'r') {
    $cmd = Read-Host "Uruchom (np. mspaint, chrome, https://olx.pl)"
    Add-Content $plik @(
      "HOTKEY GUI R",
      "WAIT 700",
      "TYPE $cmd",
      "KEY ENTER",
      "WAIT 2500"
    ) -Encoding ASCII
    continue
  }
  if ($o -eq 't') {
    $tx = Read-Host "TYPE tekst"
    Add-Content $plik "TYPE $tx" -Encoding ASCII; continue
  }
  3..1 | ForEach-Object { Write-Host $_; Start-Sleep 1 }
  $p = New-Object W+P
  [W]::GetCursorPos([ref]$p) | Out-Null
  Add-Content $plik "MOVE $($p.X) $($p.Y)" -Encoding ASCII
  if ($o -ne 'm') { Add-Content $plik "CLICK" -Encoding ASCII }
  Write-Host "Zapisano: $($p.X) $($p.Y)" -ForegroundColor Green
}