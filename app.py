from fastapi import FastAPI, Request, HTTPException
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем FastAPI приложение
app = FastAPI()

# Читаем токен из переменных окружения
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не найден в переменных окружения.")

# Создаем приложение Telegram-бота
bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я работаю через вебхук.")

# Добавляем обработчики
bot_app.add_handler(CommandHandler("start", start))

# Маршрут для вебхука
@app.post("/webhook")
async def webhook(request: Request):
    try:
        # Получаем данные от Telegram
        data = await request.json()
        logger.info(f"Received update: {data}")
        
        # Преобразуем данные в объект Update
        update = Update.de_json(data, bot_app.bot)
        
        # Обрабатываем обновление
        await bot_app.process_update(update)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error processing update: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Метод для регистрации вебхука
@app.on_event("startup")
async def set_webhook():
    # URL вашего сервера
    webhook_url = "https://vibegnews.onrender.com/webhook"  # Замените на ваш реальный URL
    logger.info(f"Setting webhook to {webhook_url}")
    await bot_app.bot.set_webhook(url=webhook_url)

# Метод для удаления вебхука (опционально)
@app.on_event("shutdown")
async def unset_webhook():
    logger.info("Removing webhook")
    await bot_app.bot.delete_webhook()
