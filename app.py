import os
import requests
from fastapi import FastAPI, Request

app = FastAPI()

# ----------------------------------
# ENV переменные
# ----------------------------------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GPTBOTS_API_KEY = os.getenv("GPTBOTS_API_KEY")
GPTBOTS_ASSISTANT_ID = os.getenv("GPTBOTS_ASSISTANT_ID")

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"


# ----------------------------------
#  GPTBOTS запрос
# ----------------------------------
def ask_gptbots(user_message: str) -> str:
    """Отправка текста в gptbots.ai и получение ответа"""

    url = "https://api.gptbots.ai/v1/chat/completions"   # стабильный домен

    headers = {
        "Authorization": f"Bearer {GPTBOTS_API_KEY}",
        "Content-Type": "application/json"
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

        print("GPTBots RAW:", data)

        # стандартный формат GPTBots
        if isinstance(data, dict) and "choices" in data:
            return data["choices"][0]["message"]["content"]

        return "Ошибка: пустой ответ от GPTBots."

    except Exception as e:
        print("GPTBots EXCEPTION:", e)
        return f"Ошибка GPTBots: {str(e)}"


# ----------------------------------
# Telegram отправка
# ----------------------------------
def send_telegram_message(chat_id: int, text: str):
    payload = {
        "chat_id": chat_id,
        "text": text[:4000],     # Telegram ограничение
        "parse_mode": "HTML"
    }

    try:
        requests.post(TELEGRAM_API_URL, json=payload)
    except Exception as e:
        print("Telegram send error:", e)


# ----------------------------------
# Telegram webhook
# ----------------------------------
@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    print("Incoming update:", data)

    message = data.get("message")
    if not message:
        return {"ok": True}

    chat_id = message["chat"]["id"]
    user_text = message.get("text")

    if not user_text:
        send_telegram_message(chat_id, "Отправьте, пожалуйста, текст.")
        return {"ok": True}

    # Получаем ответ GPTBots
    reply = ask_gptbots(user_text)

    # Отправляем его пользователю
    send_telegram_message(chat_id, reply)

    return {"ok": True}


# ----------------------------------
# корневая проверка
# ----------------------------------
@app.get("/")
def home():
    return {"status": "GPTBots Telegram bot running"}
