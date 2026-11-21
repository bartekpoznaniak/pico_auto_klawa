& "$PSScriptRoot\ustaw_czas_pico.ps1"
Start-Sleep -Seconds 1
$p = New-Object System.IO.Ports.SerialPort COM13,115200
$p.Open(); $p.WriteLine("RUN,paint_test"); $p.Close()
