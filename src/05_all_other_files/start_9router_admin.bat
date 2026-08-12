@echo off
:: Check if already running as Administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    goto :run_server
) else (
    echo Requesting Administrator privileges...
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

:run_server
echo ============================================
echo  9Router - Starting as Administrator
echo ============================================
echo.

:: Kill any existing 9Router process on port 20127
echo Stopping any existing 9Router instance...
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":20127 " ^| findstr "LISTENING"') do (
    taskkill /PID %%a /F >nul 2>&1
)
timeout /t 2 /nobreak >nul

:: Start 9Router in background (as admin)
echo Starting 9Router on port 20127...
start /B cmd /c "cd /d "C:\Users\Shivam Patel\.gemini\antigravity\scratch\9router" && npm run dev > "%TEMP%\9router.log" 2>&1"

:: Wait for server to be ready
echo Waiting for 9Router to start...
:wait_loop
timeout /t 2 /nobreak >nul
curl -s http://localhost:20127/api/auth/status >nul 2>&1
if %errorLevel% NEQ 0 goto :wait_loop

echo 9Router is up!
echo.

:: Now start the MITM server via API (we already have API key in DB)
echo Starting MITM server on port 443...
curl -s -X POST http://localhost:20127/api/cli-tools/antigravity-mitm ^
  -H "Content-Type: application/json" ^
  -d "{\"apiKey\": \"sk-9router\", \"mitmRouterBaseUrl\": \"http://localhost:20127\", \"forceKillPort443\": true}"

echo.
echo ============================================
echo  Done! 9Router MITM is now running.
echo  - Dashboard: http://localhost:20127
echo  - Antigravity traffic will route to Qwen
echo ============================================
echo.
pause
