import os

# Telegram API credentials (get from https://my.telegram.org/auth)
API_ID = int(os.environ.get('API_ID', '0'))
API_HASH = os.environ.get('API_HASH', '')

# Bot token for sending messages to admin
ADMIN_BOT_TOKEN = os.environ.get('ADMIN_BOT_TOKEN', '')
# Admin's Telegram chat ID
ADMIN_CHAT_ID = int(os.environ.get('ADMIN_CHAT_ID', '0'))

# Flask secret key
SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me-in-production')

# Marketplace API
MARKET_API_URL = 'https://api.tgmrkt.io/api/v1'
