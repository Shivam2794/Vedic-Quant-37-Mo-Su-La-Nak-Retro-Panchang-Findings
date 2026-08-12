$releases = Invoke-RestMethod -Uri 'https://api.github.com/repos/rustdesk/rustdesk/releases/latest'
$url = $releases.assets | Where-Object { $_.name -match '-x86_64\.exe$' } | Select-Object -ExpandProperty browser_download_url -First 1
$installerPath = "$env:USERPROFILE\Desktop\RustDesk_Installer.exe"
Write-Host "Downloading RustDesk from $url to $installerPath..."
Invoke-WebRequest -Uri $url -OutFile $installerPath
Write-Host "Download complete. Launching installer..."
Start-Process -FilePath $installerPath
