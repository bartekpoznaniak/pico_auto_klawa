param([string]$Nazwa = "test")
& "$PSScriptRoot\kopiuj.ps1" -Nazwa $Nazwa
Start-Sleep -Seconds 3
& "$PSScriptRoot\ustaw_czas_pico.ps1"
Start-Sleep -Seconds 1
$p = New-Object System.IO.Ports.SerialPort COM13,115200
$p.Open(); $p.WriteLine("RUN,$Nazwa"); $p.Close()
