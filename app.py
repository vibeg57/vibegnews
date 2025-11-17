from fastapi import FastAPI, Request
import requests
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Загрузка переменных из .env
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация FastAPI
app = FastAPI()

# Получение ключей и лимитов из env-переменных — для гибкости (fallback — прежние значения)
GPTBOTS_API_URL = os.getenv("GPTBOTS_API_URL", "https://api.gptbots.ai/v1/generate")
GPTBOTS_API_KEY = os.getenv("GPTBOTS_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TOKEN_LIMIT_PER_USER = int(os.getenv("TOKEN_LIMIT_PER_USER", 20))

# Глобальные переменные
user_token_usage = {}         # Следим за использованием токенов
user_last_reset_time = {}     # Следим за временем последнего сброса
user_statistics = {}          # Сохраняем статистику

def send_message(chat_id, text, menu=True):
    reply_markup = {
        "keyboard": [["/start", "/menu"], ["Статистика"]],
        "resize_keyboard": True,
        "one_time_keyboard": False
    } if menu else None
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    response = requests.post(telegram_url, json=payload)
    if response.status_code != 200:
        logging.error(f"Failed to send message: {response.text}")

def generate_response(prompt, user_id):
    if GPTBOTS_API_KEY is None:
        logging.error("GPTBOTS_API_KEY is not set.")
        return "Ошибка: не задан ключ GPTBOTS API."
    try:
        headers = {
            "Authorization": f"Bearer {GPTBOTS_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "prompt": prompt,
            "max_tokens": TOKEN_LIMIT_PER_USER - user_token_usage.get(user_id, 0)
        }
        response = requests.post(GPTBOTS_API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "Извините, произошла ошибка.")
        else:
            logging.error(f"GPTBots API error: {response.text}")
            return "Ошибка при генерации ответа."
    except Exception as e:
        logging.error(f"Error generating response: {e}")
        return "Произошла ошибка при обработке запроса."

def reset_token_limit(user_id):
    current_time = datetime.now()
    last_reset = user_last_reset_time.get(user_id, current_time - timedelta(days=1))
    if current_time - last_reset > timedelta(days=1):
        user_token_usage[user_id] = 0
        user_last_reset_time[user_id] = current_time
        logging.info(f"Token limit reset for user {user_id}.")

def update_statistics(user_id, message_text):
    if user_id not in user_statistics:
        user_statistics[user_id] = {"messages_count": 0, "last_interaction": None}
    user_statistics[user_id]["messages_count"] += 1
    user_statistics[user_id]["last_interaction"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@app.post("/webhook")
async def webhook_handler(request: Request):
    try:
        data = await request.json()
        logging.info(f"Received data: {data}")

        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            user_id = data["message"]["from"]["id"]
            text = data["message"].get("text", "").lower()

            update_statistics(user_id, text)

            if text == "/start":
                send_message(chat_id, "Добро пожаловать! Выберите действие из меню.")
                return {"ok": True}
            if text == "/menu":
                send_message(chat_id, "Меню доступно ниже.")
                return {"ok": True}
            if text == "статистика":
                stats = user_statistics.get(user_id, {"messages_count": 0, "last_interaction": "Нет данных"})
                send_message(
                    chat_id,
                    f"Ваша статистика:\n- Количество сообщений: {stats['messages_count']}\n- Последнее взаимодействие: {stats['last_interaction']}"
                )
                return {"ok": True}
            
            reset_token_limit(user_id)
            user_token_usage.setdefault(user_id, 0)
            if user_token_usage[user_id] >= TOKEN_LIMIT_PER_USER:
                send_message(chat_id, "Вы достигли лимита токенов. Попробуйте позже.")
                return {"ok": True}

            response_text = generate_response(text, user_id)
            tokens_used = len(response_text.split())
            user_token_usage[user_id] += tokens_used
            send_message(chat_id, response_text)
            return {"ok": True}

        return {"ok": False}
    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return {"ok": False}
