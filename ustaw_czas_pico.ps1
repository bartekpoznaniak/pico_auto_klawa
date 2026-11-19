$port = [System.IO.Ports.SerialPort]::new("COM13", 115200)
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