param([Parameter(Mandatory)][string]$Nazwa)

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

$plik = Join-Path (Split-Path $PSScriptRoot -Parent) "scripts\$Nazwa.txt"
New-Item -ItemType Directory -Force (Split-Path $plik) | Out-Null

if (Test-Path $plik) {
    $odp = (Read-Host "Plik istnieje. [D]opisac czy [N]adpisac? (D/N)").Trim().ToLower()
    if ($odp -eq "n") { "# $Nazwa" | Set-Content $plik -Encoding ASCII }
} else {
    "# $Nazwa" | Set-Content $plik -Encoding ASCII
}

$krokMs  = 10    # przerwa miedzy powtorzeniami tej samej akcji (ms)
$pauzaMs = 100   # pauza po kazdej akcji (ms); 1000 = 1 s

Write-Host "Plik: $plik"
Write-Host "o[N]=MOVE+CLICK  m[N]=tylko MOVE  d[N]=DRAG  w[N]=WAIT(ms)  t[N]=TYPE  r[N]=Uruchom  k=koniec"
Write-Host "N = ile razy powtorzyc, np. o5"

function Zapisz($linie) { Add-Content $plik $linie -Encoding ASCII }
function Pobierz-Kursor {
    $pt = New-Object W+P
    [W]::GetCursorPos([ref]$pt) | Out-Null
    return $pt
}

while ($true) {
    $in = (Read-Host "Akcja").Trim().ToLower()
    if ($in -eq "") { continue }
    if ($in -eq "k") { break }

    if ($in -notmatch '^([omwtrd])(\d*)$') {
        Write-Host "Nieznana akcja: $in" -ForegroundColor Yellow
        continue
    }
    $akcja = $Matches[1]
    $n = if ($Matches[2]) { [int]$Matches[2] } else { 1 }
    if ($n -lt 1) { $n = 1 }

    $tresc = $null
    if ($akcja -eq "w") { $tresc = Read-Host "WAIT ms" }
    if ($akcja -eq "t") { $tresc = Read-Host "TYPE tekst" }
    if ($akcja -eq "r") { $tresc = Read-Host "Uruchom np. mspaint, chrome, https://olx.pl" }

    $p = $null
    $p2 = $null
    if ($akcja -eq "o" -or $akcja -eq "m") {
        3..1 | ForEach-Object { Write-Host $_; Start-Sleep 1 }
        $p = Pobierz-Kursor
    }
    if ($akcja -eq "d") {
        Write-Host "Ustaw mysz na POCZATKU przeciagniecia..." -ForegroundColor Cyan
        3..1 | ForEach-Object { Write-Host $_; Start-Sleep 1 }
        $p = Pobierz-Kursor
        Write-Host "Ustaw mysz na KONCU przeciagniecia..." -ForegroundColor Cyan
        3..1 | ForEach-Object { Write-Host $_; Start-Sleep 1 }
        $p2 = Pobierz-Kursor
    }

    for ($i = 1; $i -le $n; $i++) {
        switch ($akcja) {
            "o" { Zapisz "MOVE $($p.X) $($p.Y)"; Zapisz "CLICK" }
            "m" { Zapisz "MOVE $($p.X) $($p.Y)" }
            "d" { Zapisz "DRAG $($p.X) $($p.Y) $($p2.X) $($p2.Y)" }
            "w" { Zapisz "WAIT $([double]$tresc / 1000)" }
            "t" { Zapisz "TYPE $tresc" }
            "r" { Zapisz @("HOTKEY GUI R","WAIT 0.7","TYPE $tresc","KEY ENTER","WAIT 2.5") }
        }
        if ($i -lt $n) { Zapisz "WAIT $($krokMs / 1000)" }
    }

    if ($akcja -ne "w") { Zapisz "WAIT $($pauzaMs / 50)" }

    if ($p2)    { Write-Host "Zapisano DRAG $($p.X),$($p.Y) -> $($p2.X),$($p2.Y) x$n" -ForegroundColor Green }
    elseif ($p) { Write-Host "Zapisano $($p.X) $($p.Y) x$n" -ForegroundColor Green }
    else        { Write-Host "Zapisano x$n" -ForegroundColor Green }
}