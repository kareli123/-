import sys
import time
import json
import requests
import config

BOT_URL = f'https://api.telegram.org/bot{config.ADMIN_BOT_TOKEN}'
WEB_APP_URL = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:5000'


def get_updates(offset=None):
    params = {'timeout': 30}
    if offset:
        params['offset'] = offset
    try:
        r = requests.get(f'{BOT_URL}/getUpdates', params=params, timeout=35)
        return r.json().get('result', [])
    except Exception:
        return []


def send_message(chat_id, text, reply_markup=None):
    data = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
    if reply_markup:
        data['reply_markup'] = json.dumps(reply_markup)
    requests.post(f'{BOT_URL}/sendMessage', json=data)


def handle_start(chat_id, first_name):
    reply_markup = {
        'inline_keyboard': [[
            {
                'text': '🔑 Войти',
                'web_app': {'url': WEB_APP_URL}
            }
        ]]
    }
    send_message(
        chat_id,
        f'Привет, <b>{first_name}</b>!\n\n'
        f'Нажми кнопку ниже, чтобы войти:',
        reply_markup=reply_markup,
    )


def main():
    print(f'[BOT] Started! Web App URL: {WEB_APP_URL}')

    # Delete old webhook if any
    requests.post(f'{BOT_URL}/deleteWebhook')

    offset = None
    while True:
        updates = get_updates(offset)
        for update in updates:
            offset = update['update_id'] + 1
            msg = update.get('message')
            if not msg:
                continue
            text = msg.get('text', '')
            chat_id = msg['chat']['id']
            first_name = msg['from'].get('first_name', 'User')

            if text == '/start':
                handle_start(chat_id, first_name)
            else:
                send_message(chat_id, 'Нажми /start чтобы начать')


if __name__ == '__main__':
    main()
