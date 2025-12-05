import os
import requests
import json
import time
import logging
from datetime import datetime
from collections import defaultdict
from functools import lru_cache
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# ---- ЛОГИРОВАНИЕ ----
LOG_FILE = "logs/app.log"
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logging.info("Запуск app.py — версия 3.0")

# ---- ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ ----
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GPTBOTS_API_KEY = os.getenv("GPTBOTS_API_KEY")
GPTBOTS_AGENT_ID = os.getenv("GPTBOTS_AGENT_ID")
MESSAGE_LIMIT_PER_DAY = 30

user_message_count = defaultdict(lambda: {"date": datetime.utcnow().date(), "count": 0})
user_last_message_time = defaultdict(lambda: 0)
ignore_list = set()

FLOOD_DELAY = 1.5  # секунды между запросами

menu_keyboard = [
    ["История", "Домоводство"],
    ["IT для \"чайников\"", "FAQ"],
    ["О боте"]
]
menu_markup = {"keyboard": menu_keyboard, "resize_keyboard": True}

SYSTEM_PROMPT = (
    "Вы — экспертный помощник и гид по жизни в уникальном поселке Лазурное, Херсонской области. "
    "Отвечайте понятно, дружелюбно и по существу. Избегайте сложных терминов. "
    "Помогайте с вопросами по домоводству, IT для начинающих, истории поселка и локальным рекомендациям."
)

# ---- GPTBOTS ----
def gptbots_generate(text, user_id):
    url = "https://openapi.gptbots.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GPTBOTS_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GPTBOTS_AGENT_ID,
        "user": str(user_id),
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ]
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=15)
        logging.info(f"GPTBots статус: {r.status_code}")
        logging.info(f"GPTBots ответ: {r.text}")

        if r.status_code == 200:
            data = r.json()
            return data["choices"][0]["message"]["content"]
        elif r.status_code == 429:
            return "GPTBots: превышен лимит, попробуйте позже."
        else:
            return f"GPTBots ошибка {r.status_code}: {r.text}"

    except Exception as e:
        logging.error(f"GPTBots EXCEPTION: {e}")
        return f"Ошибка GPTBots: {e}"

@lru_cache(maxsize=2000)
def cache_answer(user_id, text):
    return gptbots_generate(text, user_id)

# ---- LIMITS ----
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

# ---- TELEGRAM ----
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
        logging.error(f"Ошибка отправки inline сообщения: {e}")

# ---- FASTAPI ----
app = FastAPI()

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

    now = time.time()
    if now - user_last_message_time[user_id] < FLOOD_DELAY:
        return JSONResponse({"ok": True})
    user_last_message_time[user_id] = now

    if user_id in ignore_list:
        return JSONResponse({"ok": True})

    if not check_limit(user_id):
        send_message(chat_id, f"Достигнут лимит ({MESSAGE_LIMIT_PER_DAY}) сообщений. Попробуйте завтра.")
        return JSONResponse({"ok": True})

    increment_limit(user_id)

    try:
        if text == "/start":
            send_message(chat_id, "Привет! Я помощник сайта vibegnews.tilda.ws. Выберите раздел меню:")

        elif text == "История":
            send_inline(chat_id, "История Лазурного — кратко", "Подробнее", "https://vibegnews.tilda.ws/")

        elif text == "Домоводство":
            send_message(chat_id, "Советы по дому, саду и хозяйству.")

        elif text == "IT для \"чайников\"":
            send_message(chat_id, "Понятные советы по смартфону и компьютеру.")

        elif text == "FAQ":
            send_message(chat_id, "Спросите любой вопрос — я помогу.")

        elif text == "О боте":
            send_inline(chat_id, "Информация о боте", "Сайт", "https://vibegnews.tilda.ws/")

        else:
            reply = cache_answer(user_id, text)
            send_message(chat_id, reply)

    except Exception as e:
        logging.error(f"Ошибка обработки update: {e}")

    return JSONResponse({"ok": True})
