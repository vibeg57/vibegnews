import os
import requests
from fastapi import FastAPI, Request

app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

GPTBOTS_API_KEY = os.getenv("GPTBOTS_API_KEY")
GPTBOTS_ASSISTANT_ID = os.getenv("GPTBOTS_ASSISTANT_ID")


def ask_gptbots(user_message: str) -> str:
    """Отправка текста в gptbots.ai и получение ответа"""

    url = "https://openapi.gptbots.ai/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GPTBOTS_API_KEY}"
    }

    payload = {
        "assistant_id": GPTBOTS_ASSISTANT_ID,
        "messages": [
            {"role": "user", "content": user_message}
        ]
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=20)
        data = response.json()

        if "choices" in data:
            return data["choices"][0]["message"]["content"]

        return "Ошибка GPTBots: пустой ответ."

    except Exception as e:
        return f"Ошибка GPTBots: {str(e)}"


def send_telegram_message(chat_id: int, text: str):
    """Отправка ответа пользователю в Telegram"""

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }

    try:
        requests.post(TELEGRAM_API_URL, json=payload)
    except Exception:
        pass


@app.post("/webhook")
async def telegram_webhook(request: Request):
    """Обработка входящих Telegram-сообщений"""

    data = await request.json()
    print("Incoming update:", data)

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"].get("text", "")

        if not user_text:
            send_telegram_message(chat_id, "Я отвечаю только на текстовые сообщения.")
            return {"ok": True}

        bot_reply = ask_gptbots(user_text)

        send_telegram_message(chat_id, bot_reply)

    return {"ok": True}


@app.get("/")
def home():
    return {"status": "GPTBots Telegram Bot running"}
