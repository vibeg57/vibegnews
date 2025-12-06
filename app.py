import os
import requests
from fastapi import FastAPI, Request

app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GPTBOTS_API_KEY = os.getenv("GPTBOTS_API_KEY")
GPTBOTS_ASSISTANT_ID = os.getenv("GPTBOTS_ASSISTANT_ID")

TELEGRAM_SEND_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"


# ---------- GPTBOTS ----------
def ask_gptbots(user_message: str) -> str:
    url = "https://openapi.gptbots.ai/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GPTBOTS_API_KEY}",
    }

    payload = {
        "assistant_id": GPTBOTS_ASSISTANT_ID,
        "messages": [{"role": "user", "content": user_message}],
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=20)
        data = response.json()

        if "choices" in data:
            return data["choices"][0]["message"]["content"]

        return "Ошибка GPTBots: пустой ответ."

    except Exception as e:
        return f"Ошибка GPTBots: {e}"


# ---------- TELEGRAM ----------
def send_telegram_message(chat_id: int, text: str):
    """Отправка ответа + меню"""

    keyboard = {
        "keyboard": [
            [{"text": "История"}],
            [{"text": "Домоводство"}],
            [{"text": "IT для чайников"}],
            [{"text": "FAQ"}],
            [{"text": "О боте"}],
        ],
        "resize_keyboard": True,
    }

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": keyboard,
    }

    requests.post(TELEGRAM_SEND_URL, json=payload)


# ---------- WEBHOOK ----------
@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    print("Incoming:", data)

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if not text:
            send_telegram_message(chat_id, "Отправьте, пожалуйста, текстовое сообщение.")
            return {"ok": True}

        # --- Обработка кнопок ---
        if text == "История":
            answer = "Раздел «История». Что хотите узнать? 🙂"
        elif text == "Домоводство":
            answer = "Раздел «Домоводство» — советы по быту, уборке, ремонту."
        elif text == "IT для чайников":
            answer = "Раздел «IT для чайников» — простыми словами о технике."
        elif text == "FAQ":
            answer = "Раздел «FAQ» — полезные подсказки и ответы на частые вопросы."
        elif text == "О боте":
            answer = "Я помощник сайта Vibegnews. Задайте вопрос — и я подскажу!"
        else:
            # --- Отправляем в GPTBots ---
            answer = ask_gptbots(text)

        send_telegram_message(chat_id, answer)

    return {"ok": True}


@app.get("/")
def home():
    return {"status": "Bot running with menu"}
