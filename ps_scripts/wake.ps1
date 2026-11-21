$port = [System.IO.Ports.SerialPort]::new("COM13", 115200)
$port.DtrEnable = $true
$port.Open()
$port.Write("WAKE,10`n")
Start-Sleep -Milliseconds 300
$port.Close()