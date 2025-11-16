from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

menu_keyboard = [
    [KeyboardButton('Тест 1'), KeyboardButton('Тест 2')],
    [KeyboardButton('Тест 3')]
]
menu_markup = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Получена команда /start от пользователя {update.effective_user.id}")
    await update.message.reply_text("Выберите кнопку:", reply_markup=menu_markup)

def main():
    app = ApplicationBuilder().token("7944320544:AAESvvcWqGi7kaPlRbON3WwAq_WMsjEcH3Y").build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == '__main__':
    main()
