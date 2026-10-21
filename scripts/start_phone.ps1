# Connects your Windows PC to WebDriverAgent on your iPhone.
# Run in PowerShell **as Administrator**, from the phone-agent folder:
#     .\scripts\start_phone.ps1
# or, if your WebDriverAgent has a different bundle ID:
#     .\scripts\start_phone.ps1 -BundleId "com.facebook.WebDriverAgentRunner.ABC123.xctrunner"
#
# It opens three windows. Leave them all open while you use the agent.

param(
    [string]$BundleId = "com.facebook.WebDriverAgentRunner.xctrunner"
)

$py = "python"
if (Test-Path ".\.venv\Scripts\python.exe") { $py = (Resolve-Path ".\.venv\Scripts\python.exe").Path }

Write-Host "1/4 Starting the secure tunnel to your iPhone (needed for iOS 17+)..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& '$py' -m pymobiledevice3 remote tunneld"
Start-Sleep -Seconds 8

Write-Host "2/4 Mounting the developer disk image (one-time per phone restart)..."
& $py -m pymobiledevice3 mounter auto-mount --tunnel ""

Write-Host "3/4 Launching WebDriverAgent ($BundleId) on the phone..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& '$py' -m pymobiledevice3 developer dvt xcuitest $BundleId --tunnel ''"
Start-Sleep -Seconds 10

Write-Host "4/4 Forwarding phone port 8100 to http://localhost:8100 ..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& '$py' -m pymobiledevice3 usbmux forward 8100 8100"
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "Done. Now, in a normal PowerShell window, run:  python test_connection.py"
