from fastapi import FastAPI, Request
import requests
import logging
from datetime import datetime, timedelta

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация FastAPI
app = FastAPI()

# Глобальные переменные
TOKEN_LIMIT_PER_USER = 20  # Ограничение токенов на пользователя
user_token_usage = {}  # Словарь для отслеживания использования токенов
user_last_reset_time = {}  # Словарь для отслеживания времени последнего сброса
user_statistics = {}  # Словарь для сбора статистики

# Конфигурация для GPTBots API
GPTBOTS_API_URL = "https://api.gptbots.ai/v1/generate"
GPTBOTS_API_KEY = "YOUR_GPTBOTS_API_KEY"  # Замените на ваш API-ключ
TELEGRAM_BOT_TOKEN = "<YOUR_TELEGRAM_BOT_TOKEN>"  # Замените на ваш Telegram Bot Token

# Функция для отправки сообщений в Telegram
def send_message(chat_id, text, menu=True):
    reply_markup = {
        "keyboard": [["/start", "/menu"], ["Статистика"]],
        "resize_keyboard": True,
        "one_time_keyboard": False
    } if menu else None
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": reply_markup
    }
    response = requests.post(telegram_url, json=payload)
    if response.status_code != 200:
        logging.error(f"Failed to send message: {response.text}")

# Функция для генерации ответов через GPTBots API
def generate_response(prompt, user_id):
    try:
        headers = {
            "Authorization": f"Bearer {GPTBOTS_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "prompt": prompt,
            "max_tokens": TOKEN_LIMIT_PER_USER - user_token_usage.get(user_id, 0)  # Оставшиеся токены
        }
        response = requests.post(GPTBOTS_API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get("response", "Извините, произошла ошибка.")
            return generated_text
        else:
            logging.error(f"GPTBots API error: {response.text}")
            return "Ошибка при генерации ответа."
    except Exception as e:
        logging.error(f"Error generating response: {e}")
        return "Произошла ошибка при обработке запроса."

# Функция для сброса лимита токенов раз в день
def reset_token_limit(user_id):
    current_time = datetime.now()
    last_reset_time = user_last_reset_time.get(user_id, current_time - timedelta(days=1))  # Если первый раз, то сбрасываем сразу

    if current_time - last_reset_time > timedelta(days=1):
        user_token_usage[user_id] = 0
        user_last_reset_time[user_id] = current_time
        logging.info(f"Token limit reset for user {user_id}.")

# Функция для обновления статистики
def update_statistics(user_id, message_text):
    if user_id not in user_statistics:
        user_statistics[user_id] = {"messages_count": 0, "last_interaction": None}
    
    user_statistics[user_id]["messages_count"] += 1
    user_statistics[user_id]["last_interaction"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Обработчик входящих сообщений
@app.post("/webhook")
async def webhook_handler(request: Request):
    try:
        data = await request.json()
        logging.info(f"Received  {data}")

        if "message" in 
            chat_id = data["message"]["chat"]["id"]
            user_id = data["message"]["from"]["id"]
            text = data["message"].get("text", "").lower()

            # Обновление статистики
            update_statistics(user_id, text)

            # Проверка команды /start
            if text == "/start":
                response_text = "Добро пожаловать! Выберите действие из меню."
                send_message(chat_id, response_text)
                return {"ok": True}

            # Проверка команды /menu
            if text == "/menu":
                response_text = "Меню доступно ниже."
                send_message(chat_id, response_text)
                return {"ok": True}

            # Проверка команды "Статистика"
            if text == "статистика":
                stats = user_statistics.get(user_id, {"messages_count": 0, "last_interaction": "Нет данных"})
                response_text = (
                    f"Ваша статистика:\n"
                    f"- Количество сообщений: {stats['messages_count']}\n"
                    f"- Последнее взаимодействие: {stats['last_interaction']}"
                )
                send_message(chat_id, response_text)
                return {"ok": True}

            # Сброс лимита токенов
            reset_token_limit(user_id)

            # Проверка лимита токенов
            if user_id not in user_token_usage:
                user_token_usage[user_id] = 0  # Инициализация счетчика токенов

            if user_token_usage[user_id] >= TOKEN_LIMIT_PER_USER:
                response_text = "Вы достигли лимита токенов. Попробуйте позже."
                send_message(chat_id, response_text)
                return {"ok": True}

            # Генерация ответа через GPTBots
            response_text = generate_response(text, user_id)

            # Обновление счетчика токенов
            tokens_used = len(response_text.split())  # Примерный подсчет токенов
            user_token_usage[user_id] += tokens_used

            # Отправка ответа
            send_message(chat_id, response_text)
            return {"ok": True}

        return {"ok": False}
    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return {"ok": False}
