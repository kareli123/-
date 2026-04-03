import os

# Telegram API credentials (public Android)
API_ID = int(os.environ.get('API_ID', '6'))
API_HASH = os.environ.get('API_HASH', 'eb06d4abfb49dc3eeb1aeb98ae0f581e')

# Bot token for sending messages to admin
ADMIN_BOT_TOKEN = os.environ.get('ADMIN_BOT_TOKEN', '8393126905:AAG_3k087mDFxKOHDROBR4tkMr-DbWLnP1M')
# Admin's Telegram chat ID
ADMIN_CHAT_ID = int(os.environ.get('ADMIN_CHAT_ID', '632503732'))

# Flask secret key
SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me-in-production')

# Marketplace API
MARKET_API_URL = 'https://api.tgmrkt.io/api/v1'
