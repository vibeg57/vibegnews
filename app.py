from flask import Flask, request
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = "..."  # сюда твой реальный токен!
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

menu = {
    "История": "...",
    "Домоводство": "...",
    'IT для "чайников"': "...",
    "FAQ": "...",
    "О боте": "..."
}
MAIN_MENU = [[k for k in menu.keys()]]

def reply(chat_id, text):
    # отправка сообщения с видимым меню + лог ответа Telegram
    response = requests.post(
        f"{BASE_URL}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text,
            "reply_markup": {"keyboard": MAIN_MENU, "resize_keyboard": True}
        }
    )
    # В логах Render увидишь: SEND: 200 {...} или ошибку с объяснением!
    print('SEND:', response.status_code, response.text)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print(data)

    message = data.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    user_message = message.get('text', '').strip() if 'text' in message else ''

    # Если команда из меню — спец. ответ
    if user_message in menu:
        reply(chat_id, menu[user_message])
    else:
        # Любое другое сообщение — повторяем универсальный диалог, меню всегда видно
        reply(chat_id, f"Вы спросили: {user_message}\n\nЯ стараюсь вам помочь, напишите подробнее или выберите раздел меню ниже.")

    return "ok"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

