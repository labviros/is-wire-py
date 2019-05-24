Write-Host "Installing RabbitMQ..." -ForegroundColor Cyan

Write-Host "Downloading..."
$exePath = "$($env:USERPROFILE)\rabbitmq-server-3.6.4.exe"
(New-Object Net.WebClient).DownloadFile('http://www.rabbitmq.com/releases/rabbitmq-server/v3.6.4/rabbitmq-server-3.6.4.exe', $exePath)

Write-Host "Installing..."
cmd /c start /wait $exePath /S

$rabbitPath = (which rabbitmq-server.bat)
Write-Host "RabbitMQ path: $rabbitPath"

Write-Host "Installing service..."
Start-Process -Wait "$rabbitPath" "install"

Write-Host "Starting service..."
Start-Process -Wait "$rabbitPath" "start"

Get-Service "RabbitMQ"

Write-Host "RabbitMQ installed and started" -ForegroundColor Green