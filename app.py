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


# ==============================
#      КНОПКИ / МЕНЮ
# ==============================

# ---- Главное меню ----
def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🛠 Советы по дому")
    kb.add("💻 IT-FAQ")
    kb.add("ℹ О проекте")
    return kb

# ---- Подменю: Советы по дому ----
def home_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🧹 Очистка диска C")
    kb.add("📶 Настройка Wi-Fi")
    kb.add("⚡ Ускорение компьютера")
    kb.add("⬅ Назад")
    return kb

# ---- Подменю: IT-FAQ ----
def it_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🐞 Ошибки Windows")
    kb.add("📦 Установка программ")
    kb.add("🔐 Безопасность")
    kb.add("⬅ Назад")
    return kb


# ==============================
#      ОБРАБОТЧИКИ
# ==============================

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(
        "Добро пожаловать в VibegNews бот!\nВыберите раздел:",
        reply_markup=main_menu()
    )


# -------- Главное меню --------
@dp.message_handler(lambda m: m.text == "🛠 Советы по дому")
async def home(message: types.Message):
    await message.answer("Выберите тему:", reply_markup=home_menu())

@dp.message_handler(lambda m: m.text == "💻 IT-FAQ")
async def it(message: types.Message):
    await message.answer("Выберите тему:", reply_markup=it_menu())

@dp.message_handler(lambda m: m.text == "ℹ О проекте")
async def about(message: types.Message):
    await message.answer("VibegNews — советы по дому и IT.\nАвтор: BegunAI")


# -------- Подменю: Советы по дому --------
@dp.message_handler(lambda m: m.text == "🧹 Очистка диска C")
async def clean_disk(message: types.Message):
    await message.answer(
        "🧹 Как очистить диск C:\n"
        "1. Очистка через «Параметры → Память»\n"
        "2. Удаление временных файлов\n"
        "3. Чистка корзины\n"
        "4. Программы: BleachBit, CCleaner\n"
    )

@dp.message_handler(lambda m: m.text == "📶 Настройка Wi-Fi")
async def wifi(message: types.Message):
    await message.answer(
        "📶 Настройка Wi-Fi:\n"
        "• Перезагрузка роутера\n"
        "• Смена канала на 1, 6 или 11\n"
        "• Пароль WPA2/WPA3\n"
    )

@dp.message_handler(lambda m: m.text == "⚡ Ускорение компьютера")
async def speed_pc(message: types.Message):
    await message.answer(
        "⚡ Ускорение ПК:\n"
        "• Отключение автозагрузки\n"
        "• Чистка диска\n"
        "• Замена HDD на SSD\n"
    )


# -------- Подменю: IT-FAQ --------
@dp.message_handler(lambda m: m.text == "🐞 Ошибки Windows")
async def win_errors(message: types.Message):
    await message.answer(
        "🐞 Ошибки Windows:\n"
        "• Синий экран — проверка драйверов\n"
        "• chkdsk /f /r\n"
        "• sfc /scannow\n"
    )

@dp.message_handler(lambda m: m.text == "📦 Установка программ")
async def install_soft(message: types.Message):
    await message.answer(
        "📦 Установка программ:\n"
        "Рекомендуемые источники: FileHippo, Softpedia, Microsoft Store."
    )

@dp.message_handler(lambda m: m.text == "🔐 Безопасность")
async def security(message: types.Message):
    await message.answer(
        "🔐 Безопасность:\n"
        "• Антивирус Defender достаточно хорош\n"
        "• Делайте резервные копии\n"
        "• Не открывайте вложения от неизвестных"
    )


# -------- Назад --------
@dp.message_handler(lambda m: m.text == "⬅ Назад")
async def back(message: types.Message):
    await message.answer("Вы вернулись в главное меню:", reply_markup=main_menu())


# -------- Прочее --------
@dp.message_handler()
async def fallback(message: types.Message):
    await message.answer("Пожалуйста, используйте кнопки меню 👇", reply_markup=main_menu())


# ==============================
#      ЗАПУСК
# ==============================
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
