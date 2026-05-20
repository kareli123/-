#!/bin/bash
echo "========================================"
echo "  TG Market Bot - Setup and Launch"
echo "========================================"
echo

# Install deps
echo "[1/4] Installing dependencies..."
pip install flask pyrogram tgcrypto curl_cffi gunicorn -q

# Download cloudflared if needed
if ! command -v cloudflared &>/dev/null && [ ! -f ./cloudflared ]; then
    echo "[2/4] Downloading cloudflared..."
    curl -sL -o cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
    chmod +x cloudflared
    CF=./cloudflared
else
    echo "[2/4] cloudflared ready"
    CF=$(command -v cloudflared 2>/dev/null || echo ./cloudflared)
fi

# Start Flask
echo "[3/4] Starting web server on port 5000..."
python app.py &
FLASK_PID=$!
sleep 2

# Start tunnel
echo "[4/4] Opening tunnel..."
echo
echo "=========================================="
echo "  Public URL will appear below:"
echo "=========================================="
echo
$CF tunnel --url http://localhost:5000

kill $FLASK_PID 2>/dev/null
