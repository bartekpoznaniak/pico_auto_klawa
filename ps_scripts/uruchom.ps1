param(
    [string]$Nazwa = "test"
)

& "$PSScriptRoot\kopiuj.ps1" -Nazwa $Nazwa
Start-Sleep -Seconds 3
& "$PSScriptRoot\ustaw_czas_pico.ps1"
Start-Sleep -Seconds 1

$ports = Get-CimInstance Win32_PnPEntity |
    Where-Object {
        $_.PNPClass -eq "Ports" -and
        $_.DeviceID -match "VID_2E8A"
    } |
    ForEach-Object {
        if ($_.Name -match "COM(\d+)") {
            "COM$($Matches[1])"
        }
    }

if (-not $ports) {
    Write-Error "Nie znaleziono Raspberry Pi Pico (VID_2E8A)."
    exit 1
}

$portName = $ports[0]
Write-Host "Używam portu: $portName"

$p = New-Object System.IO.Ports.SerialPort($portName, 115200)
$p.Open()
$p.WriteLine("RUN,$Nazwa")
$p.Close()



