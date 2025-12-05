import os
import requests
import json
import time
import logging
from datetime import datetime
from collections import defaultdict
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

# ---------------- ЛОГИРОВАНИЕ ----------------
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logging.info("Запуск app.py — версия DeepSeek 1.0")

# ---------------- ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ ----------------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

MESSAGE_LIMIT_PER_DAY = 30
FLOOD_DELAY = 1.5

user_last_message_time = defaultdict(lambda: 0)
user_message_count = defaultdict(lambda: {"date": datetime.utcnow().date(), "count": 0})

# ---------------- ТЕЛЕГРАМ МЕНЮ ----------------
menu_keyboard = [
    ["История", "Домоводство"],
    ["IT для \"чайников\"", "FAQ"],
    ["О боте"]
]

menu_markup = {"keyboard": menu_keyboard, "resize_keyboard": True}

# ---------------- SYSTEM PROMPT ----------------
SYSTEM_PROMPT = (
    "Вы — экспертный помощник сайта vibegnews.tilda.ws. "
    "Отвечайте понятно, полезно и дружелюбно. "
    "Если вопрос выходит за рамки сайта, всё равно помогайте, но кратко и по делу."
)

# ---------------- ЗАПРОС К DEEPSEEK ----------------
def ask_deepseek(user_text):
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ]
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=20)
        logging.info(f"DeepSeek статус: {r.status_code}")

        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]

        return f"DeepSeek ошибка {r.status_code}: {r.text}"

    except Exception as e:
        logging.error(f"DeepSeek EXCEPTION: {e}")
        return "Ошибка обработки запроса к ИИ. Попробуйте позже."


# ---------------- ОГРАНИЧЕНИЯ ----------------
def check_limit(user_id):
    today = datetime.utcnow().date()
    record = user_message_count[user_id]

    if record["date"] != today:
        user_message_count[user_id] = {"date": today, "count": 0}
        return True

    return record["count"] < MESSAGE_LIMIT_PER_DAY


def increment_limit(user_id):
    today = datetime.utcnow().date()
    record = user_message_count[user_id]

    if record["date"] != today:
        user_message_count[user_id] = {"date": today, "count": 1}
    else:
        record["count"] += 1


# ---------------- TELEGRAM SEND ----------------
def send_message(chat_id, text, reply_markup=menu_markup):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "reply_markup": json.dumps(reply_markup)
    }
    try:
        requests.post(url, json=data, timeout=10)
    except Exception as e:
        logging.error(f"Ошибка отправки сообщения: {e}")


def send_inline(chat_id, text, button_text, button_url):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    markup = {
        "inline_keyboard": [[{"text": button_text, "url": button_url}]]
    }
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "reply_markup": json.dumps(markup)
    }
    try:
        requests.post(url, json=data, timeout=10)
    except Exception as e:
        logging.error(f"Ошибка inline-кнопки: {e}")


# ---------------- FASTAPI ----------------
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "DeepSeek бот запущен! Webhook работает."}


@app.post("/webhook")
async def webhook(request: Request):
    update = await request.json()
    logging.info(f"Получено обновление: {update}")

    message = update.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    user_id = message.get("from", {}).get("id")
    text = message.get("text", "")

    if not chat_id or not user_id:
        return JSONResponse({"ok": True})

    # Антифлуд
    now = time.time()
    if now - user_last_message_time[user_id] < FLOOD_DELAY:
        return JSONResponse({"ok": True})
    user_last_message_time[user_id] = now

    # Лимиты
    if not check_limit(user_id):
        send_message(chat_id, f"Вы использовали дневной лимит ({MESSAGE_LIMIT_PER_DAY}) сообщений. Попробуйте завтра.")
        return JSONResponse({"ok": True})

    increment_limit(user_id)

    # ---------------- Обработчики меню ----------------
    try:
        if text == "/start":
            send_message(
                chat_id,
                "Привет! Я умный помощник vibegnews.tilda.ws.\n\nВыберите раздел меню:"
            )
            return JSONResponse({"ok": True})

        if text == "История":
            send_message(chat_id, "Раздел *История*: интересные факты о Лазурном и Причерноморье.")
            return JSONResponse({"ok": True})

        if text == "Домоводство":
            send_message(chat_id, "Домоводство: советы по дому, саду, винограду, быту.")
            return JSONResponse({"ok": True})

        if text == "IT для \"чайников\"":
            send_message(chat_id, "Простые советы по компьютерам, смартфонам и интернету.")
            return JSONResponse({"ok": True})

        if text == "FAQ":
            send_message(chat_id, "Задайте вопрос — я постараюсь помочь.")
            return JSONResponse({"ok": True})

        if text == "О боте":
            send_inline(
                chat_id,
                "Бот — помощник сайта vibegnews.tilda.ws.\nРаботает на DeepSeek.",
                "Перейти на сайт",
                "https://vibegnews.tilda.ws/"
            )
            return JSONResponse({"ok": True})

        # ----------- Генерация ответа через DeepSeek -----------
        reply = ask_deepseek(text)
        send_message(chat_id, reply)

    except Exception as e:
        logging.error(f"Ошибка обработки: {e}")

    return JSONResponse({"ok": True})
