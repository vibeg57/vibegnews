from telegram import ReplyKeyboardMarkup, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import Forbidden

# Кнопки главного меню (обычные)
menu_keyboard = [
    ['История', 'Домоводство'],
    ['IT для "чайников"', 'FAQ'],
    ['О боте']
]
menu_markup = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Получена команда /start от пользователя {update.effective_user.id}")
    try:
        await update.message.reply_text(
            "Привет! Выберите раздел меню:", reply_markup=menu_markup)
    except Forbidden:
        user_id = update.effective_user.id if update.effective_user else "неизвестный"
        print(f"Пользователь {user_id} заблокировал бота, сообщение не отправлено.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    try:
        if text == 'История':
            await update.message.reply_text(
                "Лазурное — уютный поселок на берегу Черного моря в Херсонской области. Основан в 1803 году, известен своими пляжами и гостеприимством."
            )
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Подробнее на сайте", url="https://vibegnews.tilda.ws/")]
            ])
            await update.message.reply_text(
                "В разделе История Вы можете узнать интересные исторические факты Причерноморья, прочитать или прослушать книги о Лазурном.",
                reply_markup=keyboard
            )

        elif text == 'Домоводство':
            await update.message.reply_text(
                "В разделе Домоводство представлены практические советы по уюту и эффективности в доме, рекомендации по экономии бюджета и виноградарству."
            )
            await update.message.reply_text(
                "Например:\n"
                "- Календарь садовода\n"
                "- Как быстро обменять деньги\n"
                "- Как выбрать стабилизатор напряжения\n"
                "- Можно ли бороться с растрескиванием ягод винограда"
            )

        elif text == 'IT для \"чайников\"':
            await update.message.reply_text(
                "IT для «чайников»: Простые и понятные советы по работе с компьютером, смартфоном и интернетом."
            )
            await update.message.reply_text(
                "Например:\n"
                "- Смартфон для пожилых\n"
                "- Статьи по искусственному интеллекту и нейросетям\n"
                "- Освоение компьютера"
            )

        elif text == 'FAQ':
            await update.message.reply_text(
                "В чате Вы можете получить ответы на  задаваемые вопросы и воспользоваться помощником telegram_bota."
            )

        elif text == 'О боте':
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Перейти на сайт", url="https://vibegnews.tilda.ws/")]
            ])
            await update.message.reply_text(
                "Бот является помощником сайта и даёт ответы по его темам и другим вопросам в его компетенции.",
                reply_markup=keyboard
            )

        else:
            await update.message.reply_text("Пожалуйста, выберите раздел из меню.", reply_markup=menu_markup)

    except Forbidden:
        user_id = update.effective_user.id if update.effective_user else "неизвестный"
        print(f"Пользователь {user_id} заблокировал бота, сообщение не отправлено.")

def main():
    # Замените на ваш реальный токен Telegram-бота
    app = ApplicationBuilder().token("7944320544:AAESvvcWqGi7kaPlRbON3WwAq_WMsjEcH3Y").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Бот запущен. Ожидание сообщений...")  # добавлен для понятности
    app.run_polling()

if __name__ == "__main__":
    main()
