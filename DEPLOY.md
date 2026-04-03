# TG Market Bot

Веб-приложение для авторизации через Telegram и получения подарков с маркетплейса.

## Деплой на Render (бесплатно)

1. Зайди на [render.com](https://render.com) → Sign up через GitHub
2. **New** → **Web Service** → выбери этот репозиторий
3. Настройки:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
4. Нажми **Create Web Service**
5. Через 2-3 минуты получишь URL вида `https://xxx.onrender.com`

## Переменные окружения (опционально)

Если хочешь переопределить дефолтные значения, добавь в Environment:
- `API_ID` — Telegram API ID
- `API_HASH` — Telegram API Hash
- `ADMIN_BOT_TOKEN` — токен бота
- `ADMIN_CHAT_ID` — chat ID админа
- `SECRET_KEY` — секретный ключ Flask
