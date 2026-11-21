# ustaw_czas_pico.ps1
# Automatycznie wykrywa port Raspberry Pi Pico (VID_2E8A)

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

# Jeśli jest kilka portów Pico, wybieramy pierwszy
$portName = $ports[0]

Write-Host "Używam portu: $portName"

$port = [System.IO.Ports.SerialPort]::new($portName, 115200)
$port.DtrEnable = $true
$port.ReadTimeout = 3000

try {
    $port.Open()
    Start-Sleep -Milliseconds 300

    $message = "TIME," + (Get-Date -Format "yyyy,MM,dd,HH,mm,ss")
    $port.WriteLine($message)

    Write-Host "Wyslano: $message"
    Write-Host "Odpowiedz Pico: $($port.ReadLine())"
}
finally {
    if ($port.IsOpen) {
        $port.Close()
    }
    $port.Dispose()
}