import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

API_TOKEN = os.getenv("BOT_TOKEN")

# ---- Logging ----
logging.basicConfig(
    level=logging.INFO,
    filename="logs/bot.log",
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


# ---- Главное меню (reply-кнопки) ----
def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🛠 Советы по дому"))
    kb.add(KeyboardButton("💻 IT-FAQ"))
    kb.add(KeyboardButton("ℹ О проекте"))
    return kb


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(
        "Добро пожаловать в VibegNews бот!\nВыберите раздел:",
        reply_markup=main_menu()
    )


# ---- Обработка кнопок ----
@dp.message_handler(lambda m: m.text == "🛠 Советы по дому")
async def home_tips(message: types.Message):
    await message.answer(
        "🛠 Советы по дому:\n\n"
        "• Как очистить диск C\n"
        "• Как ускорить компьютер\n"
        "• Как настроить Wi-Fi\n"
    )


@dp.message_handler(lambda m: m.text == "💻 IT-FAQ")
async def it_faq(message: types.Message):
    await message.answer(
        "💻 IT-FAQ:\n\n"
        "• Ошибки Windows\n"
        "• Установка программ\n"
        "• Безопасность и резервные копии\n"
    )


@dp.message_handler(lambda m: m.text == "ℹ О проекте")
async def about(message: types.Message):
    await message.answer(
        "ℹ VibegNews — практические советы по дому и IT.\nАвтор: BegunAI"
    )


# ---- Обработка обычного текста ----
@dp.message_handler()
async def fallback(message: types.Message):
    await message.answer(
        "Пожалуйста, используйте кнопки ниже 👇",
        reply_markup=main_menu()
    )


# ---- Запуск ----
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
