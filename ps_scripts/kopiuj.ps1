# wyslij.ps1 -Nazwa olx_test   (bez -Nazwa kopiuje wszystkie skrypty)
param([string]$Nazwa)
$d = Get-Volume | Where-Object FileSystemLabel -eq 'CIRCUITPY' | Select-Object -First 1
if (-not $d) { Write-Host "Nie znaleziono dysku CIRCUITPY" -ForegroundColor Red; exit 1 }
$cel = "$($d.DriveLetter):\scripts"
New-Item -ItemType Directory -Force $cel | Out-Null
$zrodlo = Join-Path (Split-Path $PSScriptRoot -Parent) "scripts"
if ($Nazwa) { $pliki = Join-Path $zrodlo "$Nazwa.txt" } else { $pliki = Join-Path $zrodlo "*.txt" }
Copy-Item $pliki $cel -Force
Write-Host "Skopiowano do $cel" -ForegroundColor Green