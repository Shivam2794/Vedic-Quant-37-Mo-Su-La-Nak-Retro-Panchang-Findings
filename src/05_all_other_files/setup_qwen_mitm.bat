@echo off
echo Applying 9Router MITM DNS overrides...
echo 127.0.0.1 daily-cloudcode-pa.googleapis.com >> C:\Windows\System32\drivers\etc\hosts
echo 127.0.0.1 cloudcode-pa.googleapis.com >> C:\Windows\System32\drivers\etc\hosts
ipconfig /flushdns
echo Setup complete. Please restart Antigravity to begin using Qwen 3.8 Max in the GPT-OSS slot.
pause
