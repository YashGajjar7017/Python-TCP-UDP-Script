# Set your Inverter IP Address
$TargetIP = "192.168.88.88"
$Ports = @(8899, 8889, 502, 500, 80, 81)

Write-Host "--- STARTING DIAGNOSTIC TEST FOR $TargetIP ---" -ForegroundColor Cyan

# 1. Standard ICMP Ping
$Ping = Test-Connection -ComputerName $TargetIP -Count 1 -Quiet
Write-Host "ICMP Ping: " -NoNewline
if ($Ping) { Write-Host "SUCCESS" -ForegroundColor Green } else { Write-Host "FAILED" -ForegroundColor Red }

# 2. TCP Port Tests
Write-Host "`n--- TESTING TCP PORTS ---" -ForegroundColor Yellow
foreach ($Port in $Ports) {
    $TcpTest = Test-NetConnection -ComputerName $TargetIP -Port $Port -WarningAction SilentlyContinue
    if ($TcpTest.TcpTestSucceeded) {
        Write-Host "Port ${Port} (TCP): OPEN" -ForegroundColor Green
    } else {
        Write-Host "Port ${Port} (TCP): CLOSED / TIMEOUT" -ForegroundColor Red
    }
}

# 3. HTTP / HTTPS Web Response Tests
Write-Host "`n--- TESTING HTTP/HTTPS WEB ENDPOINTS ---" -ForegroundColor Yellow
$HttpPorts = @(80, 81, 8899, 8889)
foreach ($Port in $HttpPorts) {
    foreach ($Proto in @("http", "https")) {
        $Url = "$($Proto)://${TargetIP}:${Port}"
        try {
            $Response = Invoke-WebRequest -Uri $Url -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
            Write-Host "$Url -> HTTP $($Response.StatusCode) OK" -ForegroundColor Green
        } catch {
            if ($_.Exception.Response) {
                $Status = [int]$_.Exception.Response.StatusCode
                Write-Host "$Url -> HTTP $Status Responded" -ForegroundColor Yellow
            } else {
                Write-Host "$Url -> No Web Server / Connection Refused" -ForegroundColor Red
            }
        }
    }
}

# 4. UDP Port Probe (UDP 500 & 8899)
Write-Host "`n--- TESTING UDP PROBE (UDP 500 & 8899) ---" -ForegroundColor Yellow
foreach ($UdpPort in @(500, 8899)) {
    $UdpClient = New-Object System.Net.Sockets.UdpClient
    try {
        $UdpClient.Connect($TargetIP, $UdpPort)
        $UdpClient.Client.ReceiveTimeout = 1000
        $Data = [System.Text.Encoding]::ASCII.GetBytes("PING")
        [void]$UdpClient.Send($Data, $Data.Length)
        Write-Host "UDP Port ${UdpPort}: Packet sent successfully" -ForegroundColor Green
    } catch {
        Write-Host "UDP Port ${UdpPort}: Failed to send packet" -ForegroundColor Red
    } finally {
        $UdpClient.Close()
    }
}

Write-Host "`n--- TEST COMPLETE ---" -ForegroundColor Cyan