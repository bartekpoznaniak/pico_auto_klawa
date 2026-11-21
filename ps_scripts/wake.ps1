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

$port = [System.IO.Ports.SerialPort]::new($portName, 115200)
$port.DtrEnable = $true
$port.Open()
$port.Write("WAKE,10`n")
Start-Sleep -Milliseconds 300
$port.Close()

