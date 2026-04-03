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
echo [1/4] Installing dependencies...
pip install flask pyrogram tgcrypto curl_cffi gunicorn >nul 2>&1
if errorlevel 1 (
    echo [WARN] Some packages may have issues, trying anyway...
)

:: Download cloudflared if not present
if not exist cloudflared.exe (
    echo [2/4] Downloading cloudflared tunnel...
    curl -sL -o cloudflared.exe https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe
) else (
    echo [2/4] cloudflared already exists
)

:: Start Flask server
echo [3/4] Starting web server on port 5000...
start /b python app.py

:: Wait a bit for server to start
timeout /t 3 /nobreak >nul

:: Start tunnel
echo [4/4] Opening tunnel to the internet...
echo.
echo ==========================================
echo   Waiting for public URL below...
echo   Share this URL to access the app!
echo ==========================================
echo.
cloudflared.exe tunnel --url http://localhost:5000
pause
