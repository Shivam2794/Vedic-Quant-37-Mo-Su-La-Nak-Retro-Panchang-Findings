@echo off
echo Installing 9Router MITM Root Certificate into Windows Trust Store...
echo This requires Administrator privileges.
echo.

:: Check admin
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo Requesting Administrator privileges...
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

set CERT_PATH=C:\Users\Shivam Patel\AppData\Roaming\9router\mitm\rootCA.crt

if not exist "%CERT_PATH%" (
    echo ERROR: Certificate not found at: %CERT_PATH%
    echo Make sure the MITM server has been started at least once.
    pause
    exit /b 1
)

echo Installing certificate: %CERT_PATH%
certutil -addstore -f "ROOT" "%CERT_PATH%"

if %errorLevel% == 0 (
    echo.
    echo SUCCESS! Root certificate trusted.
    echo Antigravity will no longer crash when connecting through MITM.
    echo.
    echo NEXT STEPS:
    echo 1. Fully restart Antigravity IDE
    echo 2. Select GPT-OSS 120B (Medium) model
    echo 3. Your requests will route to Qwen 3.8 Max
) else (
    echo.
    echo FAILED to install certificate. Please ensure you ran as Administrator.
)

pause
