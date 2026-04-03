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

:: Install dependencies one by one so we see errors
echo [1/4] Installing Python packages...
pip install flask
pip install pyrogram
pip install tgcrypto
pip install curl_cffi

:: Verify flask installed
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Flask did not install! Try manually: pip install flask
    pause
    exit /b 1
)
echo [OK] All packages installed

:: Download cloudflared if not present
if not exist cloudflared.exe (
    echo [2/4] Downloading cloudflared tunnel...
    echo This may take a minute...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile 'cloudflared.exe'"
)

if not exist cloudflared.exe (
    echo [ERROR] Failed to download cloudflared!
    echo Download manually: https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe
    echo Put cloudflared.exe in the same folder as this script
    pause
    exit /b 1
)
echo [OK] cloudflared ready

:: Start Flask server
echo [3/4] Starting web server on port 5000...
start /b python app.py

:: Wait for server
timeout /t 3 /nobreak >nul

:: Check server is running
powershell -Command "try { Invoke-WebRequest -Uri http://localhost:5000 -UseBasicParsing -TimeoutSec 3 | Out-Null; Write-Host '[OK] Server is running' } catch { Write-Host '[ERROR] Server failed to start'; exit 1 }"

:: Start tunnel
echo [4/4] Opening tunnel to the internet...
echo.
echo ==========================================
echo   Public URL will appear below
echo   Copy it and open in browser!
echo ==========================================
echo.
cloudflared.exe tunnel --url http://localhost:5000
pause
