$pythonPath = "C:\Users\Shivam Patel\.gemini\antigravity\scratch\nadi_env\Scripts\python.exe"
$scriptPath = "C:\Users\Shivam Patel\.gemini\antigravity\scratch\bootstrap_mcp_proxies.py"

# Start the Python proxy bootstrap script silently
Start-Process -FilePath $pythonPath -ArgumentList "`"$scriptPath`"" -WindowStyle Hidden
