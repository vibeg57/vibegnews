import os
import requests
from datetime import datetime
from collections import defaultdict

from telegram import ReplyKeyboardMarkup, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import Forbidden

# --- Переменные окружения ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GPTBOTS_API_KEY = os.getenv("GPTBOTS_API_KEY")  # Получи на gptbots.ai
GPTBOTS_AGENT_ID = os.getenv("GPTBOTS_AGENT_ID")  # Получи на gptbots.ai

# --- Лимит сообщений и игнор-лист ---
MESSAGE_LIMIT_PER_DAY = 20
user_message_count = defaultdict(lambda: {"date": datetime.utcnow().date(), "count": 0})
ignore_list = set()  # Добавляй user_id которых игнорировать

# --- Главное меню ---
menu_keyboard = [
    ["История", "Домоводство"],
    ["IT для \"чайников\"", "FAQ"],
    ["О боте"]
]
menu_markup = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)

# --- Генерация ответа через GPTBots.ai ---
def gptbots_generate(text, user_id):
    endpoint = "https://openapi.gptbots.ai/v1/chat"
    headers = {
        "X-API-Key": GPTBOTS_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "agent_id": GPTBOTS_AGENT_ID,
        "user_id": str(user_id),
        "query": text
    }
    try:
        r = requests.post(endpoint, headers=headers, json=data, timeout=12)
        if r.status_code == 200:
            resp = r.json()
            return resp.get('data', {}).get('reply', 'Сервис GPTBots не ответил.')
        elif r.status_code == 429:  # лимит запросов
            return "Лимит запросов GPTBots исчерпан, попробуйте позже."
        else:
            return f"Ошибка GPTBots ({r.status_code}): {r.text}"
    except Exception as e:
        return f"Ошибка запроса к GPTBots: {e}"

# --- Лимит сообщений ---
def check_limit(user_id):
    today = datetime.utcnow().date()
    record = user_message_count[user_id]
    if record["date"] != today:
        user_message_count[user_id] = {"date": today, "count": 0}
        return True
    if record["count"] < MESSAGE_LIMIT_PER_DAY:
        return True
    return False

def increment_limit(user_id):
    today = datetime.utcnow().date()
    record = user_message_count[user_id]
    if record["date"] != today:
        user_message_count[user_id] = {"date": today, "count": 1}
    else:
        record["count"] += 1

# --- Обработчик команды /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    print(f"Получена команда /start от пользователя {user_id}")
    if user_id in ignore_list:
        return
    try:
        await update.message.reply_text(
            "Привет! Я помощник сайта [vibegnews.tilda.ws](https://vibegnews.tilda.ws/). Выберите раздел меню:",
            reply_markup=menu_markup,
            parse_mode="Markdown"
        )
    except Forbidden:
        print(f"Пользователь {user_id} заблокировал бота, сообщение не отправлено.")

# --- Обработчик всех текстовых сообщений ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # Игнор-лист
    if user_id in ignore_list:
        print(f"Пользователь {user_id} в игнор-листе.")
        return

    # Лимит сообщений
    if not check_limit(user_id):
        await update.message.reply_text(
            f"Достигнут лимит ({MESSAGE_LIMIT_PER_DAY}) сообщений на сегодня. Попробуйте завтра!",
            reply_markup=menu_markup
        )
        return

    increment_limit(user_id)

    try:
        if text == "История":
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Подробнее на сайте", url="https://vibegnews.tilda.ws/")]
            ])
            await update.message.reply_text(
                "Лазурное — уютный поселок на берегу Черного моря в Херсонской области. "
                "Основан в 1803 году, известен своими пляжами и гостеприимством.", reply_markup=keyboard
            )
            await update.message.reply_text(
                "В разделе *История* вы можете узнать интересные исторические факты Причерноморья, "
                "прочитать или прослушать книги о Лазурном.", parse_mode="Markdown"
            )

        elif text == "Домоводство":
            await update.message.reply_text(
                "В разделе *Домоводство* представлены практические советы по уюту и эффективности в доме, "
                "рекомендации по экономии бюджета и виноградарству.",
                parse_mode="Markdown"
            )
            await update.message.reply_text(
                "*Например:*\n"
                "- Календарь садовода\n"
                "- Как быстро обменять деньги\n"
                "- Как выбрать стабилизатор напряжения\n"
                "- Можно ли бороться с растрескиванием ягод винограда",
                parse_mode="Markdown"
            )

        elif text == "IT для \"чайников\"":
            await update.message.reply_text(
                "*IT для «чайников»:* Простые и понятные советы по работе с компьютером, смартфоном и интернетом.",
                parse_mode="Markdown"
            )
            await update.message.reply_text(
                "*Например:*\n"
                "- Смартфон для пожилых\n"
                "- Статьи по искусственному интеллекту и нейросетям\n"
                "- Освоение компьютера",
                parse_mode="Markdown"
            )

        elif text == "FAQ":
            await update.message.reply_text(
                "В чате вы можете получить ответы на часто задаваемые вопросы и воспользоваться помощью бота.",
                parse_mode="Markdown"
            )

        elif text == "О боте":
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Перейти на сайт", url="https://vibegnews.tilda.ws/")]
            ])
            await update.message.reply_text(
                "Бот является помощником сайта [vibegnews.tilda.ws](https://vibegnews.tilda.ws/) "
                "и даёт ответы по его темам и другим вопросам в своей компетенции.\n\n"
                "*Основные возможности:*\n"
                f"- Лимит сообщений: {MESSAGE_LIMIT_PER_DAY} в сутки.\n"
                "- Сброс лимита: раз в день.\n"
                "- Ведение статистики использования.",
                parse_mode="Markdown", reply_markup=keyboard
            )

        else:
            # Свободный диалог через GPTBots.ai
            response = gptbots_generate(text, user_id)
            await update.message.reply_text(
                response or "Произошла ошибка при обращении к ИИ.",
                reply_markup=menu_markup
            )

    except Forbidden:
        print(f"Пользователь {user_id} заблокировал бота, сообщение не отправлено.")

# --- Запуск бота ---
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Бот запущен. Ожидание сообщений...")
    app.run_polling()

if __name__ == "__main__":
    main()

