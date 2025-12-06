import os
import requests
from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI()

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")
TG_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# GPTBots
GPTBOTS_API_KEY = os.getenv("GPTBOTS_API_KEY")
GPTBOTS_BOT_ID = os.getenv("GPTBOTS_BOT_ID")


# --- GPTBots запрос ---
def ask_gptbots(user_id: str, text: str) -> str:
    url = "https://api.gptbots.ai/v1/messages"

    payload = {
        "bot_id": GPTBOTS_BOT_ID,
        "user_id": str(user_id),
        "inputs": {"query": text}
    }

    headers = {
        "Authorization": f"Bearer {GPTBOTS_API_KEY}",
        "Content-Type": "application/json"
    }

    r = requests.post(url, json=payload, headers=headers)
    print("GPTBots RAW:", r.text)

    try:
        data = r.json()
        return data.get("answer", "GPTBots не дал ответа.")
    except:
        return "Ошибка обработки ответа GPTBots."


# --- Telegram: отправка ---
def send_message(chat_id, text, reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup

    requests.post(f"{TG_API_URL}/sendMessage", json=payload)


# --- Главное меню vibegnews ---
def main_menu():
    return {
        "keyboard": [
            [{"text": "📚 История"}],
            [{"text": "🏡 Домоводство"}],
            [{"text": "💻 IT для «чайников»"}],
            [{"text": "❓ FAQ"}, {"text": "ℹ️ О боте"}]
        ],
        "resize_keyboard": True
    }


# Telegram update модель
class Update(BaseModel):
    update_id: int
    message: dict | None = None


# --- Webhook ---
@app.post("/webhook")
async def webhook(update: Update):

    if update.message:
        chat_id = update.message["chat"]["id"]
        text = update.message.get("text", "")

        # /start
        if text == "/start":
            send_message(
                chat_id,
                "Добро пожаловать! Выберите раздел:",
                reply_markup=main_menu()
            )
            return {"ok": True}

        # --- История ---
        if text == "📚 История":
            send_message(
                chat_id,
                "Раздел <b>История</b> — факты о Лазурном, Причерноморье и краеведении.\n\n"
                "📘 На сайте есть книги, документы и подборки.",
                reply_markup=main_menu()
            )
            send_message(
                chat_id,
                "Открыть раздел:",
                reply_markup={
                    "inline_keyboard": [
                        [{"text": "📘 Перейти", "url": "https://vibegnews.tilda.ws/history"}]
                    ]
                }
            )
            return {"ok": True}

        # --- Домоводство ---
        if text == "🏡 Домоводство":
            send_message(
                chat_id,
                "Раздел <b>Домоводство</b>: садоводство, бытовые советы, виноградарство, экономия.",
                reply_markup=main_menu()
            )
            send_message(
                chat_id,
                "Открыть раздел:",
                reply_markup={
                    "inline_keyboard": [
                        [{"text": "🏡 Перейти", "url": "https://vibegnews.tilda.ws/home"}]
                    ]
                }
            )
            return {"ok": True}

        # --- IT для чайников ---
        if text == "💻 IT для «чайников»":
            send_message(
                chat_id,
                "Раздел <b>IT для начинающих</b>: смартфоны, компьютеры, интернет, нейросети.",
                reply_markup=main_menu()
            )
            send_message(
                chat_id,
                "Открыть раздел:",
                reply_markup={
                    "inline_keyboard": [
                        [{"text": "💻 Перейти", "url": "https://vibegnews.tilda.ws/it"}]
                    ]
                }
            )
            return {"ok": True}

        # --- FAQ ---
        if text == "❓ FAQ":
            send_message(
                chat_id,
                "В FAQ собраны популярные вопросы пользователей и ответы на них.",
                reply_markup=main_menu()
            )
            send_message(
                chat_id,
                "Открыть FAQ:",
                reply_markup={
                    "inline_keyboard": [
                        [{"text": "❓ Перейти", "url": "https://vibegnews.tilda.ws/faq"}]
                    ]
                }
            )
            return {"ok": True}

        # --- О боте ---
        if text == "ℹ️ О боте":
            send_message(
                chat_id,
                "<b>Бот vibegnews</b> — ассистент по темам сайта.\n"
                "• Работает на GPTBots.ai\n"
                "• Отвечает на бытовые и IT-вопросы\n"
                "• Использует материалы vibegnews",
                reply_markup=main_menu()
            )
            return {"ok": True}

        # --- GPTBots основной режим ---
        reply = ask_gptbots(chat_id, text)
        send_message(chat_id, reply, reply_markup=main_menu())

    return {"ok": True}


# Корневой маршрут
@app.get("/")
async def root():
    return {"status": "bot_running", "menu": "vibegnews"}
