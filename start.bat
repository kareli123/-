@echo off
chcp 65001 >nul
title TG Market Bot

echo ========================================
echo   TG Market Bot - Setup and Launch
echo ========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Install from https://python.org
    pause
    exit /b 1
)

:: Install dependencies
echo [1/5] Installing Python packages...
pip install flask pyrogram requests
echo.

:: Verify
python -c "import flask; import pyrogram; import requests; print('[OK] All packages installed')"
if errorlevel 1 (
    echo [ERROR] Packages failed to install
    pause
    exit /b 1
)

:: Download cloudflared if not present
if not exist cloudflared.exe (
    echo [2/5] Downloading cloudflared...
    powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile 'cloudflared.exe'"
)
if not exist cloudflared.exe (
    echo [ERROR] Failed to download cloudflared!
    echo Download manually from:
    echo https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe
    echo and put cloudflared.exe in this folder
    pause
    exit /b 1
)
echo [OK] cloudflared ready

:: Start Flask server
echo [3/5] Starting web server on port 5000...
start /b python app.py
timeout /t 3 /nobreak >nul

:: Start cloudflared and capture URL
echo [4/5] Opening tunnel...
del tunnel.log >nul 2>&1
del tunnel_url.txt >nul 2>&1
start /b cmd /c "cloudflared.exe tunnel --url http://localhost:5000 > tunnel.log 2>&1"

echo Waiting for tunnel URL (up to 30 sec)...
set ATTEMPTS=0

:wait_url
timeout /t 3 /nobreak >nul
set /a ATTEMPTS+=1
if %ATTEMPTS% gtr 10 (
    echo [ERROR] Tunnel did not start. Check tunnel.log
    type tunnel.log
    pause
    exit /b 1
)

powershell -Command "$c = Get-Content tunnel.log -ErrorAction SilentlyContinue; if ($c -match 'https://[a-z0-9-]+\.trycloudflare\.com') { $Matches[0] | Out-File -Encoding ascii tunnel_url.txt; exit 0 } else { exit 1 }" >nul 2>&1
if errorlevel 1 goto wait_url

set /p TUNNEL_URL=<tunnel_url.txt

echo.
echo ==========================================
echo   PUBLIC URL: %TUNNEL_URL%
echo ==========================================
echo.

:: Start bot
echo [5/5] Starting Telegram bot...
start /b python bot.py %TUNNEL_URL%

echo.
echo [OK] Everything is running!
echo.
echo   Web: %TUNNEL_URL%
echo   Bot: send /start in Telegram
echo.
echo Close this window to stop everything.
pause >nul

taskkill /f /im cloudflared.exe >nul 2>&1
